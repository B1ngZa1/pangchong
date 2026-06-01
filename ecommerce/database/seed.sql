-- =============================================
-- 胖虫电商系统 - 测试数据
-- =============================================

-- =============================================
-- 1. 插入商品分类
-- =============================================
INSERT INTO categories (id, name, slug, icon, sort_order) VALUES
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', '游戏笔记本', 'laptop-gaming', '🎮', 1),
    ('b2c3d4e5-f6a7-8901-bcde-f12345678901', '轻薄本', 'laptop-thin', '💼', 2),
    ('c3d4e5f6-a7b8-9012-cdef-123456789012', '台式主机', 'desktop', '🖥️', 3),
    ('d4e5f6a7-b8c9-0123-defa-234567890123', '工作站', 'workstation', '⚡', 4),
    ('e5f6a7b8-c9d0-1234-efab-345678901234', '迷你主机', 'mini', '📦', 5),
    ('f6a7b8c9-d0e1-2345-fabc-456789012345', 'DIY配件', 'parts', '🔧', 6),
    ('d1000000-0000-0000-0000-000000000001', 'CPU处理器', 'cpu', '🧠', 10),
    ('d1000000-0000-0000-0000-000000000002', '显卡', 'gpu', '🎮', 11);

-- =============================================
-- 2. 插入测试商品（10款）
-- =============================================
INSERT INTO products (id, name, slug, description, price, original_price, cost_price, category_id, brand, model, stock, sold_count, image_url, images, specs, is_active, is_featured, weight) VALUES
    -- 游戏笔记本
    ('11111111-1111-1111-1111-111111111111',
     '胖虫·毒刺 i7-RTX4060 游戏本',
     'pangchong-sting-i7-4060',
     '蓝天NH50模具，独显直连+MUX开关，双风扇四热管散热，100% sRGB高色域，RGB背光键盘。适合游戏玩家和内容创作者。',
     6299.00, 7499.00, 4800.00,
     'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
     '胖虫', '毒刺 i7-RTX4060',
     50, 128,
     '/images/products/sting-4060.jpg',
     '["/images/products/sting-4060-1.jpg", "/images/products/sting-4060-2.jpg"]',
     '{"cpu": "i7-13620H", "gpu": "RTX 4060 8G", "ram": "16GB DDR5", "storage": "512GB SSD", "screen": "15.6寸 2K 165Hz"}',
     true, true, 2.5),

    ('22222222-2222-2222-2222-222222222222',
     '胖虫·毒刺 i9-RTX4070 游戏本',
     'pangchong-sting-i9-4070',
     '蓝天NH50模具，独显直连，DDR5双通道，240Hz电竞屏，雷电4接口。高端游戏玩家首选。',
     8999.00, 10499.00, 6500.00,
     'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
     '胖虫', '毒刺 i9-RTX4070',
     30, 86,
     '/images/products/sting-4070.jpg',
     '["/images/products/sting-4070-1.jpg", "/images/products/sting-4070-2.jpg"]',
     '{"cpu": "i9-13900H", "gpu": "RTX 4070 8G", "ram": "32GB DDR5", "storage": "1TB SSD", "screen": "15.6寸 2K 240Hz"}',
     true, true, 2.6),

    ('33333333-3333-3333-3333-333333333333',
     '胖虫·暗影 i9-RTX4080 游戏本',
     'pangchong-shadow-i9-4080',
     '蓝天NH55模具，满血RTX4080 175W，液金散热，2.5K 240Hz P3色域，全尺寸RGB键盘。旗舰级性能。',
     12999.00, 14999.00, 9500.00,
     'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
     '胖虫', '暗影 i9-RTX4080',
     20, 45,
     '/images/products/shadow-4080.jpg',
     '["/images/products/shadow-4080-1.jpg", "/images/products/shadow-4080-2.jpg"]',
     '{"cpu": "i9-14900HX", "gpu": "RTX 4080 12G", "ram": "32GB DDR5", "storage": "1TB SSD", "screen": "16寸 2.5K 240Hz"}',
     true, true, 2.8),

    -- 轻薄本
    ('44444444-4444-4444-4444-444444444444',
     '胖虫·轻风 R7 轻薄本',
     'pangchong-breeze-r7',
     '全金属机身仅1.28kg，2.8K OLED 100% DCI-P3色域，67Wh大电池续航12h，USB4接口。商务办公首选。',
     4999.00, 5699.00, 3500.00,
     'b2c3d4e5-f6a7-8901-bcde-f12345678901',
     '胖虫', '轻风 R7',
     40, 92,
     '/images/products/breeze-r7.jpg',
     '["/images/products/breeze-r7-1.jpg", "/images/products/breeze-r7-2.jpg"]',
     '{"cpu": "R7 7840HS", "gpu": "Radeon 780M", "ram": "16GB LPDDR5x", "storage": "512GB SSD", "screen": "14寸 2.8K OLED"}',
     true, true, 1.28),

    -- 台式主机
    ('55555555-5555-5555-5555-555555555555',
     '胖虫·暗影猎手 RTX4060 游戏主机',
     'pangchong-hunter-4060',
     '一线品牌配件，全模组电源，360水冷散热，神光同步RGB，72小时烤机测试。性价比之选。',
     4999.00, 5999.00, 3800.00,
     'c3d4e5f6-a7b8-9012-cdef-123456789012',
     '胖虫', '暗影猎手 RTX4060',
     35, 156,
     '/images/products/hunter-4060.jpg',
     '["/images/products/hunter-4060-1.jpg", "/images/products/hunter-4060-2.jpg"]',
     '{"cpu": "i5-13400F", "gpu": "RTX 4060 8G", "ram": "16GB DDR4", "storage": "500GB NVMe", "case": "侧透机箱"}',
     true, true, 8.5),

    ('66666666-6666-6666-6666-666666666666',
     '胖虫·雷霆战甲 RTX4070Ti Super 主机',
     'pangchong-thunder-4070tis',
     '华硕/微星主板，海韵/振华电源，利民360水冷，联力侧透机箱，XMP内存超频。高端电竞主机。',
     10999.00, 12999.00, 8200.00,
     'c3d4e5f6-a7b8-9012-cdef-123456789012',
     '胖虫', '雷霆战甲 RTX4070TiS',
     15, 67,
     '/images/products/thunder-4070tis.jpg',
     '["/images/products/thunder-4070tis-1.jpg", "/images/products/thunder-4070tis-2.jpg"]',
     '{"cpu": "i7-14700KF", "gpu": "RTX 4070 Ti Super 16G", "ram": "32GB DDR5", "storage": "1TB Gen4 SSD"}',
     true, true, 12.0),

    -- 工作站
    ('77777777-7777-7777-7777-777777777777',
     '胖虫·创世者 TRX50 专业工作站',
     'pangchong-creator-trx50',
     'AMD TRX50平台，ECC纠错内存，专业显卡ISV认证，多盘位NAS扩展，静音工作站机箱。专业创作者首选。',
     42999.00, NULL, 32000.00,
     'd4e5f6a7-b8c9-0123-defa-234567890123',
     '胖虫', '创世者 TRX50',
     5, 12,
     '/images/products/creator-trx50.jpg',
     '["/images/products/creator-trx50-1.jpg", "/images/products/creator-trx50-2.jpg"]',
     '{"cpu": "Threadripper 7960X", "gpu": "RTX A5000", "ram": "128GB DDR5 ECC", "storage": "2TB NVMe"}',
     true, false, 15.0),

    -- 迷你主机
    ('88888888-8888-8888-8888-888888888888',
     '胖虫·虫卵 R7 迷你主机',
     'pangchong-egg-r7',
     '0.7L超小体积，Radeon 780M核显，支持4K输出，WiFi 6E + BT5.2，VESA壁挂安装。桌面整洁之选。',
     3299.00, 3999.00, 2400.00,
     'e5f6a7b8-c9d0-1234-efab-345678901234',
     '胖虫', '虫卵 R7',
     60, 203,
     '/images/products/egg-r7.jpg',
     '["/images/products/egg-r7-1.jpg", "/images/products/egg-r7-2.jpg"]',
     '{"cpu": "R7 7840HS", "gpu": "Radeon 780M", "ram": "32GB DDR5", "storage": "1TB SSD", "volume": "0.7L"}',
     true, true, 0.5),

    -- DIY配件
    ('99999999-9999-9999-9999-999999999999',
     'Intel i7-14700K 处理器',
     'intel-i7-14700k',
     '20核28线程，最高5.6GHz睿频，支持DDR5内存，LGA1700接口。高性能游戏和创作处理器。',
     3099.00, 3499.00, 2500.00,
     'd1000000-0000-0000-0000-000000000001',
     'Intel', 'i7-14700K',
     100, 89,
     '/images/products/i7-14700k.jpg',
     '["/images/products/i7-14700k-1.jpg"]',
     '{"cores": "20核28线程", "base_clock": "3.4GHz", "boost_clock": "5.6GHz", "tdp": "125W", "socket": "LGA1700"}',
     true, true, 0.1),

    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
     'NVIDIA RTX 4070 Ti Super 显卡',
     'nvidia-rtx-4070-ti-super',
     '8448 CUDA核心，16GB GDDR6X显存，支持DLSS 3和光线追踪。高端游戏和创作利器。',
     6499.00, 6999.00, 5200.00,
     'd1000000-0000-0000-0000-000000000002',
     'NVIDIA', 'RTX 4070 Ti Super',
     25, 34,
     '/images/products/rtx-4070-ti-super.jpg',
     '["/images/products/rtx-4070-ti-super-1.jpg"]',
     '{"cuda_cores": 8448, "memory": "16GB GDDR6X", "tdp": "285W", "interface": "PCIe 4.0 x16"}',
     true, true, 1.5);

-- =============================================
-- 3. 插入测试用户
-- =============================================
-- 密码: test123456 (bcrypt 加密)
INSERT INTO users (id, username, email, phone, password_hash, nickname, is_active, is_admin) VALUES
    ('a0000000-0000-0000-0000-000000000001', 'testuser', 'test@pangchong.com', '13800138000',
     '$2b$12$9Y.0vHm7ChTNOcc6oItjc.VRP7VeD5vs6OKqcR.V4iXI3r2Dd4Rne', '测试用户', true, false),
    ('a0000000-0000-0000-0000-000000000002', 'admin', 'admin@pangchong.com', '13800138001',
     '$2b$12$9Y.0vHm7ChTNOcc6oItjc.VRP7VeD5vs6OKqcR.V4iXI3r2Dd4Rne', '管理员', true, true);

-- =============================================
-- 4. 插入测试用户地址
-- =============================================
INSERT INTO user_addresses (id, user_id, recipient_name, phone, province, city, district, address, postal_code, is_default) VALUES
    ('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001',
     '张三', '13800138000', '广东省', '深圳市', '南山区',
     '科技园南路66号胖虫科技大厦', '518000', true),
    ('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001',
     '张三', '13800138000', '北京市', '朝阳区', '望京街道',
     '望京SOHO T1 2001', '100102', false);

-- =============================================
-- 5. 插入测试订单
-- =============================================
INSERT INTO orders (id, order_no, user_id, status, total_amount, shipping_fee, discount_amount, final_amount, recipient_name, recipient_phone, shipping_address, payment_method, paid_at) VALUES
    ('c0000000-0000-0000-0000-000000000001', 'PC202401150001',
     'a0000000-0000-0000-0000-000000000001', 'completed',
     6299.00, 0.00, 0.00, 6299.00,
     '张三', '13800138000', '广东省深圳市南山区科技园南路66号',
     'alipay', '2024-01-15 10:30:00+08');

INSERT INTO order_items (order_id, product_id, product_name, product_image, price, quantity, subtotal) VALUES
    ('c0000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111',
     '胖虫·毒刺 i7-RTX4060 游戏本', '/images/products/sting-4060.jpg',
     6299.00, 1, 6299.00);
