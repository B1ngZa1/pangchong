-- =============================================
-- 胖虫电商系统 - 数据库初始化脚本
-- 数据库: PostgreSQL 16+
-- =============================================

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================
-- 1. 用户表 (users)
-- =============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt 加密后的密码
    nickname VARCHAR(50),
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    is_admin BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 用户表索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_username ON users(username);

-- =============================================
-- 2. 用户地址表 (user_addresses)
-- =============================================
CREATE TABLE user_addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipient_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    province VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    district VARCHAR(50) NOT NULL,
    address VARCHAR(200) NOT NULL,
    postal_code VARCHAR(10),
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 地址表索引
CREATE INDEX idx_addresses_user_id ON user_addresses(user_id);

-- =============================================
-- 3. 商品分类表 (categories)
-- =============================================
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL,
    slug VARCHAR(50) NOT NULL UNIQUE,
    parent_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 分类表索引
CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE INDEX idx_categories_slug ON categories(slug);

-- =============================================
-- 4. 商品表 (products)
-- =============================================
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL UNIQUE,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,  -- 售价
    original_price DECIMAL(10, 2),  -- 原价（划线价）
    cost_price DECIMAL(10, 2),     -- 成本价
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    brand VARCHAR(50),
    model VARCHAR(100),
    stock INTEGER NOT NULL DEFAULT 0,
    sold_count INTEGER DEFAULT 0,
    image_url VARCHAR(500),
    images JSONB,  -- 商品图片数组
    specs JSONB,   -- 商品规格参数
    model_3d_url VARCHAR(500),
    model_3d_scale DECIMAL(8, 4) NOT NULL DEFAULT 1,
    model_3d_position JSONB,
    model_3d_rotation JSONB,
    asset_license VARCHAR(100),
    price_source_name VARCHAR(100),
    price_source_url VARCHAR(500),
    price_checked_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    is_featured BOOLEAN DEFAULT false,  -- 是否推荐
    weight DECIMAL(8, 2),  -- 重量(kg)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 商品表索引
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_slug ON products(slug);
CREATE INDEX idx_products_is_active ON products(is_active);
CREATE INDEX idx_products_is_featured ON products(is_featured);
CREATE INDEX idx_products_created_at ON products(created_at DESC);
CREATE INDEX idx_products_category_brand_price ON products(category_id, brand, price);
CREATE INDEX idx_products_specs_gin ON products USING GIN (specs);

-- 商品名称搜索索引（使用 GIN 索引支持中文搜索）
CREATE INDEX idx_products_name_search ON products USING GIN (to_tsvector('simple', name));

-- =============================================
-- 5. 购物车表 (cart_items)
-- =============================================
CREATE TABLE cart_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(100),  -- 未登录用户的会话 ID
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- 确保同一用户/会话的同一商品只有一条记录
    CONSTRAINT unique_user_product UNIQUE (user_id, product_id),
    CONSTRAINT unique_session_product UNIQUE (session_id, product_id)
);

-- 购物车表索引
CREATE INDEX idx_cart_user_id ON cart_items(user_id);
CREATE INDEX idx_cart_session_id ON cart_items(session_id);

-- =============================================
-- 6. 订单表 (orders)
-- =============================================
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_no VARCHAR(32) NOT NULL UNIQUE,  -- 订单号，格式: PC + 时间戳 + 随机数
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'paid', 'shipped', 'completed', 'cancelled', 'refunded')),
    total_amount DECIMAL(10, 2) NOT NULL,  -- 商品总金额
    shipping_fee DECIMAL(10, 2) DEFAULT 0, -- 运费
    discount_amount DECIMAL(10, 2) DEFAULT 0,  -- 优惠金额
    final_amount DECIMAL(10, 2) NOT NULL,  -- 最终支付金额

    -- 收货信息（快照，避免用户修改地址后影响历史订单）
    recipient_name VARCHAR(50),
    recipient_phone VARCHAR(20),
    shipping_address TEXT,

    -- 支付信息
    payment_method VARCHAR(20),  -- alipay, wechat
    payment_id VARCHAR(100),     -- 第三方支付流水号
    paid_at TIMESTAMP WITH TIME ZONE,

    -- 物流信息
    shipping_company VARCHAR(50),
    tracking_number VARCHAR(50),
    shipped_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    -- 备注
    remark TEXT,
    admin_note TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 订单表索引
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_order_no ON orders(order_no);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);

-- =============================================
-- 7. 订单商品表 (order_items)
-- =============================================
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE RESTRICT,
    item_type VARCHAR(20) NOT NULL DEFAULT 'product',
    product_name VARCHAR(200) NOT NULL,  -- 商品名称快照
    product_image VARCHAR(500),          -- 商品图片快照
    product_specs JSONB,
    price DECIMAL(10, 2) NOT NULL,       -- 下单时价格
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    subtotal DECIMAL(10, 2) NOT NULL,    -- 小计 = price * quantity
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 订单商品表索引
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- =============================================
-- 8. 价格历史表 (price_history)
-- =============================================
CREATE TABLE price_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    price DECIMAL(10, 2) NOT NULL,
    changed_by UUID REFERENCES users(id),
    source_name VARCHAR(100),
    source_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 价格历史索引
CREATE INDEX idx_price_history_product_id ON price_history(product_id);
CREATE INDEX idx_price_history_created_at ON price_history(created_at DESC);

-- =============================================
-- 9. 操作日志表 (audit_logs)
-- =============================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    details JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 操作日志索引
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- =============================================
-- 触发器：自动更新 updated_at
-- =============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表创建触发器
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cart_items_updated_at
    BEFORE UPDATE ON cart_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_addresses_updated_at
    BEFORE UPDATE ON user_addresses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- 视图：订单详情视图
-- =============================================
CREATE VIEW order_details AS
SELECT
    o.id,
    o.order_no,
    o.user_id,
    u.username,
    u.email,
    o.status,
    o.total_amount,
    o.shipping_fee,
    o.discount_amount,
    o.final_amount,
    o.recipient_name,
    o.recipient_phone,
    o.shipping_address,
    o.payment_method,
    o.payment_id,
    o.paid_at,
    o.shipping_company,
    o.tracking_number,
    o.shipped_at,
    o.completed_at,
    o.remark,
    o.created_at,
    o.updated_at
FROM orders o
JOIN users u ON o.user_id = u.id;

-- =============================================
-- 视图：商品销售统计
-- =============================================
CREATE VIEW product_sales_stats AS
SELECT
    p.id,
    p.name,
    p.price,
    p.stock,
    p.sold_count,
    COALESCE(SUM(oi.quantity), 0) as total_sold,
    COALESCE(SUM(oi.subtotal), 0) as total_revenue
FROM products p
LEFT JOIN order_items oi ON p.id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.id AND o.status IN ('paid', 'shipped', 'completed')
GROUP BY p.id, p.name, p.price, p.stock, p.sold_count;
