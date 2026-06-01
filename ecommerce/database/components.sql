-- =============================================
-- 胖虫电商 - 八大件产品数据
-- 生成时间: 2026-05-26
-- 基于真实2026年5月市场行情
-- =============================================

-- =============================================
-- 1. 新增八大件分类
-- =============================================
INSERT INTO categories (id, name, slug, icon, sort_order) VALUES
    ('d1000000-0000-0000-0000-000000000001', 'CPU处理器', 'cpu', '🧠', 10),
    ('d1000000-0000-0000-0000-000000000002', '显卡', 'gpu', '🎮', 11),
    ('d1000000-0000-0000-0000-000000000003', '主板', 'motherboard', '🔌', 12),
    ('d1000000-0000-0000-0000-000000000004', '内存', 'ram', '💾', 13),
    ('d1000000-0000-0000-0000-000000000005', '固态硬盘', 'ssd', '💿', 14),
    ('d1000000-0000-0000-0000-000000000006', '散热器', 'cooler', '❄️', 15),
    ('d1000000-0000-0000-0000-000000000007', '电源', 'psu', '⚡', 16),
    ('d1000000-0000-0000-0000-000000000008', '机箱', 'case', '🏠', 17)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    slug = EXCLUDED.slug,
    icon = EXCLUDED.icon,
    sort_order = EXCLUDED.sort_order;

-- =============================================
-- 2. CPU处理器 (8款)
-- =============================================
INSERT INTO products (id, name, slug, description, price, original_price, cost_price, category_id, brand, model, stock, sold_count, image_url, images, specs, is_active, is_featured, weight) VALUES

-- AMD Ryzen 5 9600X
('c1000000-0000-0000-0000-000000000001',
 'AMD Ryzen 5 9600X 处理器',
 'amd-r5-9600x',
 '6核12线程，Zen 5架构，4nm工艺，智能加速至5.4GHz，65W均衡功耗。中坚生产力首选，多任务性价比之王。',
 1499.00, 1799.00, 1424.00,
 'd1000000-0000-0000-0000-000000000001',
 'AMD', 'Ryzen 5 9600X',
 45, 210,
 '/images/components/r5-9600x.jpg', '[]',
 '{"cores":"6核12线程","arch":"Zen 5","process":"4nm","base_clock":"3.9GHz","boost_clock":"5.4GHz","tdp":"65W","socket":"AM5","cache":"38MB","memory_support":"DDR5-5600"}',
 true, true, 0.12),

-- AMD Ryzen 7 7800X3D
('c1000000-0000-0000-0000-000000000002',
 'AMD Ryzen 7 7800X3D 处理器',
 'amd-r7-7800x3d',
 '8核16线程，搭载104MB游戏高速缓存（3D V-CACHE），目前消费级桌面平台最大L3缓存配置。游戏发烧友标杆。',
 3099.00, 3599.00, 2944.00,
 'd1000000-0000-0000-0000-000000000001',
 'AMD', 'Ryzen 7 7800X3D',
 25, 156,
 '/images/components/r7-7800x3d.jpg', '[]',
 '{"cores":"8核16线程","arch":"Zen 4 + 3D V-Cache","process":"5nm","base_clock":"4.2GHz","boost_clock":"5.0GHz","tdp":"120W","socket":"AM5","cache":"104MB (96MB L3)","memory_support":"DDR5-5200"}',
 true, true, 0.15),

-- AMD Ryzen 9 9900X
('c1000000-0000-0000-0000-000000000003',
 'AMD Ryzen 9 9900X 处理器',
 'amd-r9-9900x',
 '12核24线程，Zen 5架构，加速至5.6GHz，120W TDP。高端游戏与创作全能处理器。',
 4599.00, 5299.00, 4369.00,
 'd1000000-0000-0000-0000-000000000001',
 'AMD', 'Ryzen 9 9900X',
 15, 67,
 '/images/components/r9-9900x.jpg', '[]',
 '{"cores":"12核24线程","arch":"Zen 5","process":"4nm","base_clock":"4.4GHz","boost_clock":"5.6GHz","tdp":"120W","socket":"AM5","cache":"76MB","memory_support":"DDR5-5600"}',
 true, false, 0.15),

-- Intel Core i5-14600KF
('c1000000-0000-0000-0000-000000000004',
 'Intel Core i5-14600KF 处理器',
 'intel-i5-14600kf',
 '14核20线程（6P+8E），Raptor Lake Refresh架构，最高5.3GHz睿频。面向重度开发者的高性能选择。',
 2499.00, 2899.00, 2374.00,
 'd1000000-0000-0000-0000-000000000001',
 'Intel', 'Core i5-14600KF',
 35, 189,
 '/images/components/i5-14600kf.jpg', '[]',
 '{"cores":"14核20线程 (6P+8E)","arch":"Raptor Lake Refresh","process":"Intel 7","base_clock":"3.5GHz","boost_clock":"5.3GHz","tdp":"125W","socket":"LGA1700","cache":"24MB L3","memory_support":"DDR5-5600 / DDR4-3200"}',
 true, true, 0.10),

-- Intel Core i7-14700KF
('c1000000-0000-0000-0000-000000000005',
 'Intel Core i7-14700KF 处理器',
 'intel-i7-14700kf',
 '20核28线程（8P+12E），最高5.6GHz睿频，支持DDR5内存。高端游戏与生产力利器。',
 3299.00, 3799.00, 3134.00,
 'd1000000-0000-0000-0000-000000000001',
 'Intel', 'Core i7-14700KF',
 28, 134,
 '/images/components/i7-14700kf.jpg', '[]',
 '{"cores":"20核28线程 (8P+12E)","arch":"Raptor Lake Refresh","process":"Intel 7","base_clock":"3.4GHz","boost_clock":"5.6GHz","tdp":"125W","socket":"LGA1700","cache":"33MB L3","memory_support":"DDR5-5600 / DDR4-3200"}',
 true, true, 0.10),

-- Intel Core i9-12900K
('c1000000-0000-0000-0000-000000000006',
 'Intel Core i9-12900K 处理器',
 'intel-i9-12900k',
 '16核24线程（8P+8E），旗舰级混合架构桌面CPU，适合高强度渲染与AI训练。95W功耗设计。',
 4430.00, 5099.00, 4209.00,
 'd1000000-0000-0000-0000-000000000001',
 'Intel', 'Core i9-12900K',
 12, 45,
 '/images/components/i9-12900k.jpg', '[]',
 '{"cores":"16核24线程 (8P+8E)","arch":"Alder Lake","process":"Intel 7","base_clock":"3.2GHz","boost_clock":"5.2GHz","tdp":"125W (PBP) / 241W (MTP)","socket":"LGA1700","cache":"30MB L3","memory_support":"DDR5-4800 / DDR4-3200"}',
 true, false, 0.10),

-- Intel Core i9-14900K
('c1000000-0000-0000-0000-000000000007',
 'Intel Core i9-14900K 处理器',
 'intel-i9-14900k',
 '24核32线程（8P+16E），最高6.0GHz睿频，Intel消费级旗舰。极致性能释放。',
 4899.00, 5599.00, 4654.00,
 'd1000000-0000-0000-0000-000000000001',
 'Intel', 'Core i9-14900K',
 18, 78,
 '/images/components/i9-14900k.jpg', '[]',
 '{"cores":"24核32线程 (8P+16E)","arch":"Raptor Lake Refresh","process":"Intel 7","base_clock":"3.2GHz","boost_clock":"6.0GHz","tdp":"125W (PBP) / 253W (MTP)","socket":"LGA1700","cache":"36MB L3","memory_support":"DDR5-5600 / DDR4-3200"}',
 true, true, 0.10),

-- AMD Ryzen 7 9700X
('c1000000-0000-0000-0000-000000000008',
 'AMD Ryzen 7 9700X 处理器',
 'amd-r7-9700x',
 '8核16线程，Zen 5架构，加速至5.5GHz，65W低功耗。能效比标杆，游戏与创作兼顾。',
 2599.00, 2999.00, 2469.00,
 'd1000000-0000-0000-0000-000000000001',
 'AMD', 'Ryzen 7 9700X',
 30, 98,
 '/images/components/r7-9700x.jpg', '[]',
 '{"cores":"8核16线程","arch":"Zen 5","process":"4nm","base_clock":"3.8GHz","boost_clock":"5.5GHz","tdp":"65W","socket":"AM5","cache":"40MB","memory_support":"DDR5-5600"}',
 true, false, 0.12);

-- =============================================
-- 3. 显卡 (12款)
-- =============================================
INSERT INTO products (id, name, slug, description, price, original_price, cost_price, category_id, brand, model, stock, sold_count, image_url, images, specs, is_active, is_featured, weight) VALUES

-- 耕升 RTX 5070 Ti 踏雪OC 2.0
('c2000000-0000-0000-0000-000000000001',
 '耕升 RTX 5070 Ti 踏雪OC 2.0 16GB',
 'gainward-rtx5070ti-snow-oc',
 '白色主题美学，2497MHz核心频率，五根镀镍热管，满载温度低于72℃。16GB GDDR7大显存，AI创作利器。',
 6799.00, 7999.00, 6459.00,
 'd1000000-0000-0000-0000-000000000002',
 '耕升', 'RTX 5070 Ti 踏雪OC 2.0',
 20, 45,
 '/images/components/gainward-rtx5070ti-snow.jpg', '[]',
 '{"gpu":"RTX 5070 Ti","vram":"16GB GDDR7","core_clock":"2497MHz","cuda_cores":"8960","interface":"PCIe 5.0 x16","tdp":"300W","power_connector":"16pin","outputs":"3x DP 2.1 + 1x HDMI 2.1","cooling":"三风扇五热管","color":"白色","length":"323mm"}',
 true, true, 1.85),

-- 影驰 RTX 5070 名人堂HOF
('c2000000-0000-0000-0000-000000000002',
 '影驰 GeForce RTX 5070 名人堂HOF 12GB',
 'galax-rtx5070-hof',
 '黑白双色主题设计，12+4相数字供电，三风扇散热系统，支持双BIOS切换。名人堂系列旗舰做工。',
 5999.00, 6999.00, 5699.00,
 'd1000000-0000-0000-0000-000000000002',
 '影驰', 'GeForce RTX 5070 名人堂HOF',
 18, 32,
 '/images/components/galax-rtx5070-hof.jpg', '[]',
 '{"gpu":"RTX 5070","vram":"12GB GDDR7","cuda_cores":"6144","interface":"PCIe 5.0 x16","tdp":"250W","power_connector":"16pin","outputs":"3x DP 2.1 + 1x HDMI 2.1","cooling":"三风扇","color":"白色","bios":"双BIOS切换","length":"318mm"}',
 true, true, 1.72),

-- 索泰 RTX 5070 Ti SOLID CORE
('c2000000-0000-0000-0000-000000000003',
 '索泰 GeForce RTX 5070 Ti SOLID CORE 16GB',
 'zotac-rtx5070ti-solid',
 '满血CUDA核心，全新Tensor单元，面向AI与创作加速。紧凑三风扇设计，兼容性强。',
 7199.00, 8499.00, 6839.00,
 'd1000000-0000-0000-0000-000000000002',
 '索泰', 'GeForce RTX 5070 Ti SOLID CORE',
 15, 28,
 '/images/components/zotac-rtx5070ti-solid.jpg', '[]',
 '{"gpu":"RTX 5070 Ti","vram":"16GB GDDR7","cuda_cores":"8960","tensor_cores":"280","interface":"PCIe 5.0 x16","tdp":"300W","power_connector":"16pin","outputs":"3x DP 2.1 + 1x HDMI 2.1","cooling":"三风扇","color":"黑色","length":"305mm"}',
 true, false, 1.68),

-- 万丽 RTX 5070 OC
('c2000000-0000-0000-0000-000000000004',
 '万丽 RTX 5070 OC 12GB GDDR7',
 'manli-rtx5070-oc',
 '性价比甜点卡，988 TOPS AI算力，DLSS 4支持，8K三屏输出。RTX 50系入门首选。',
 4899.00, 5799.00, 4654.00,
 'd1000000-0000-0000-0000-000000000002',
 '万丽', 'RTX 5070 OC 12GB',
 25, 56,
 '/images/components/manli-rtx5070-oc.jpg', '[]',
 '{"gpu":"RTX 5070","vram":"12GB GDDR7","cuda_cores":"6144","ai_tops":"988","interface":"PCIe 5.0 x16","tdp":"250W","power_connector":"16pin","outputs":"3x DP 2.1 + 1x HDMI 2.1","cooling":"双风扇","color":"黑色","length":"267mm"}',
 true, true, 1.25),

-- NVIDIA RTX 5080 公版
('c2000000-0000-0000-0000-000000000005',
 'NVIDIA GeForce RTX 5080 Founders Edition 16GB',
 'nvidia-rtx5080-fe',
 'NVIDIA公版设计，双轴流散热，16GB GDDR7显存。高端游戏与AI创作的平衡之选。',
 8999.00, 9999.00, 8549.00,
 'd1000000-0000-0000-0000-000000000002',
 'NVIDIA', 'GeForce RTX 5080 FE',
 12, 34,
 '/images/components/rtx5080-fe.jpg', '[]',
 '{"gpu":"RTX 5080","vram":"16GB GDDR7","cuda_cores":"10752","tensor_cores":"336","interface":"PCIe 5.0 x16","tdp":"360W","power_connector":"16pin","outputs":"3x DP 2.1 + 1x HDMI 2.1","cooling":"双轴流风扇","color":"银黑色","length":"304mm"}',
 true, true, 2.10),

-- NVIDIA RTX 5090 公版
('c2000000-0000-0000-0000-000000000006',
 'NVIDIA GeForce RTX 5090 Founders Edition 32GB',
 'nvidia-rtx5090-fe',
 '消费级旗舰，32GB GDDR7显存，21760 CUDA核心。8K游戏、AI训练、专业创作无压力。',
 16999.00, 19999.00, 16149.00,
 'd1000000-0000-0000-0000-000000000002',
 'NVIDIA', 'GeForce RTX 5090 FE',
 8, 12,
 '/images/components/rtx5090-fe.jpg', '[]',
 '{"gpu":"RTX 5090","vram":"32GB GDDR7","cuda_cores":"21760","tensor_cores":"680","interface":"PCIe 5.0 x16","tdp":"575W","power_connector":"16pin x2","outputs":"3x DP 2.1 + 1x HDMI 2.1","cooling":"三风扇","color":"银黑色","length":"336mm"}',
 true, true, 2.80),

-- RTX 4090 D
('c2000000-0000-0000-0000-000000000007',
 'NVIDIA GeForce RTX 4090 D 24GB',
 'nvidia-rtx4090d',
 '国行特供版，24GB GDDR6X显存，16384 CUDA核心。旗舰级光追性能，DLSS 3加持。',
 11999.00, 13999.00, 11399.00,
 'd1000000-0000-0000-0000-000000000002',
 'NVIDIA', 'GeForce RTX 4090 D',
 10, 23,
 '/images/components/rtx4090d.jpg', '[]',
 '{"gpu":"RTX 4090 D","vram":"24GB GDDR6X","cuda_cores":"16384","tensor_cores":"512","interface":"PCIe 4.0 x16","tdp":"425W","power_connector":"16pin","outputs":"3x DP 1.4a + 1x HDMI 2.1","cooling":"三风扇","color":"黑色","length":"336mm"}',
 true, false, 2.40),

-- 华硕 RTX 5070 Ti TUF
('c2000000-0000-0000-0000-000000000008',
 '华硕 TUF-RTX5070TI-O16G-GAMING 16GB',
 'asus-tuf-rtx5070ti',
 'TUF军规品质，全自动化制程，三风扇散热，IP5X防尘。稳定耐用之选。',
 7499.00, 8699.00, 7124.00,
 'd1000000-0000-0000-0000-000000000002',
 '华硕', 'TUF-RTX5070TI-O16G-GAMING',
 14, 41,
 '/images/components/asus-tuf-rtx5070ti.jpg', '[]',
 '{"gpu":"RTX 5070 Ti","vram":"16GB GDDR7","cuda_cores":"8960","interface":"PCIe 5.0 x16","tdp":"300W","power_connector":"16pin","outputs":"3x DP 2.1 + 2x HDMI 2.1","cooling":"三风扇IP5X防尘","color":"黑色","length":"320mm","warranty":"3年"}',
 true, true, 1.90),

-- 微星 RTX 5070 GAMING TRIO
('c2000000-0000-0000-0000-000000000009',
 '微星 GeForce RTX 5070 GAMING TRIO 12GB',
 'msi-rtx5070-gaming-trio',
 'TRIO三风扇散热，TORX 5.0风扇，金属背板。微星旗舰非公版设计。',
 5699.00, 6699.00, 5414.00,
 'd1000000-0000-0000-0000-000000000002',
 '微星', 'GeForce RTX 5070 GAMING TRIO',
 16, 38,
 '/images/components/msi-rtx5070-gaming-trio.jpg', '[]',
 '{"gpu":"RTX 5070","vram":"12GB GDDR7","cuda_cores":"6144","interface":"PCIe 5.0 x16","tdp":"250W","power_connector":"16pin","outputs":"3x DP 2.1 + 1x HDMI 2.1","cooling":"TRIO三风扇TORX 5.0","color":"黑色","length":"325mm"}',
 true, false, 1.78),

-- AMD RX 9070 XT
('c2000000-0000-0000-0000-00000000000a',
 'AMD Radeon RX 9070 XT 16GB',
 'amd-rx9070xt',
 'RDNA 4架构，16GB GDDR6显存，FSR 4支持。A卡性价比旗舰，开放生态之选。',
 4599.00, 5499.00, 4369.00,
 'd1000000-0000-0000-0000-000000000002',
 'AMD', 'Radeon RX 9070 XT',
 22, 67,
 '/images/components/rx9070xt.jpg', '[]',
 '{"gpu":"RX 9070 XT","vram":"16GB GDDR6","stream_processors":"4096","interface":"PCIe 4.0 x16","tdp":"300W","power_connector":"16pin","outputs":"2x DP 2.1 + 2x HDMI 2.1","cooling":"三风扇","color":"黑色","length":"290mm"}',
 true, true, 1.55),

-- AMD RX 9070
('c2000000-0000-0000-0000-00000000000b',
 'AMD Radeon RX 9070 12GB',
 'amd-rx9070',
 'RDNA 4架构甜点卡，12GB GDDR6显存，256-bit位宽。1080P/2K游戏利器。',
 3499.00, 4199.00, 3324.00,
 'd1000000-0000-0000-0000-000000000002',
 'AMD', 'Radeon RX 9070',
 28, 89,
 '/images/components/rx9070.jpg', '[]',
 '{"gpu":"RX 9070","vram":"12GB GDDR6","stream_processors":"3584","interface":"PCIe 4.0 x16","tdp":"250W","power_connector":"8pin x2","outputs":"2x DP 2.1 + 2x HDMI 2.1","cooling":"双风扇","color":"黑色","length":"267mm"}',
 true, false, 1.30),

-- 蓝宝石 RX 9070 XT 超白金
('c2000000-0000-0000-0000-00000000000c',
 '蓝宝石 RX 9070 XT 超白金 16GB',
 'sapphire-rx9070xt-nitro',
 '蓝宝石超白金系列，三风扇Tri-X散热，ARGB灯效，金属背板。A卡非公版标杆。',
 5199.00, 6199.00, 4939.00,
 'd1000000-0000-0000-0000-000000000002',
 '蓝宝石', 'RX 9070 XT 超白金',
 12, 21,
 '/images/components/sapphire-rx9070xt-nitro.jpg', '[]',
 '{"gpu":"RX 9070 XT","vram":"16GB GDDR6","stream_processors":"4096","interface":"PCIe 4.0 x16","tdp":"300W","power_connector":"16pin","outputs":"2x DP 2.1 + 2x HDMI 2.1","cooling":"Tri-X三风扇ARGB","color":"银黑色","length":"310mm"}',
 true, false, 1.65);

-- =============================================
-- 4. 主板 (10款)
-- =============================================
INSERT INTO products (id, name, slug, description, price, original_price, cost_price, category_id, brand, model, stock, sold_count, image_url, images, specs, is_active, is_featured, weight) VALUES

-- 七彩虹 B760M-WHITE WIFI
('c3000000-0000-0000-0000-000000000001',
 '七彩虹 BATTLE-AX B760M-WHITE WIFI 主板',
 'colorful-b760m-white-wifi',
 '入门级性价比首选，12+1+1相强化供电，千元内实现全功能接口。白色主题颜值在线。',
 799.00, 999.00, 759.00,
 'd1000000-0000-0000-0000-000000000003',
 '七彩虹', 'BATTLE-AX B760M-WHITE WIFI',
 35, 120,
 '/images/components/colorful-b760m-white.jpg', '[]',
 '{"chipset":"B760M","socket":"LGA1700","form_factor":"M-ATX","memory":"DDR5 x2 max 96GB","pcie":"PCIe 4.0 x16 + PCIe 3.0 x1","m2":"2x M.2 PCIe 4.0","wifi":"WiFi 6","lan":"2.5G有线","usb":"USB 3.2 Gen2 Type-C","audio":"ALC897","vrm":"12+1+1相","color":"白色"}',
 true, true, 0.65),

-- 华硕 TUF B760M-PLUS II D5
('c3000000-0000-0000-0000-000000000002',
 '华硕 TUF GAMING B760M-PLUS II D5 重炮手主板',
 'asus-tuf-b760m-plus-d5',
 '扎实12+1路智能供电，DDR5-6000+超频，WIFI 6+2.5G有线网卡。TUF军规认证。',
 719.00, 899.00, 683.00,
 'd1000000-0000-0000-0000-000000000003',
 '华硕', 'TUF GAMING B760M-PLUS II D5',
 40, 167,
 '/images/components/asus-tuf-b760m.jpg', '[]',
 '{"chipset":"B760M","socket":"LGA1700","form_factor":"M-ATX","memory":"DDR5 x4 max 192GB","pcie":"PCIe 4.0 x16","m2":"2x M.2 PCIe 4.0","wifi":"WiFi 6","lan":"2.5G有线","usb":"USB 3.2 Gen2x2 Type-C","audio":"ALC897","vrm":"12+1相","color":"黑色"}',
 true, true, 0.72),

-- 华硕 ROG Z790-A 吹雪
('c3000000-0000-0000-0000-000000000003',
 '华硕 ROG STRIX Z790-A GAMING WIFI 吹雪主板',
 'asus-rog-z790-a-snow',
 '中高端白色主题，AI智能优化2.0，WiFi 6E，支持Intel 12/13/14代旗舰处理器。',
 2899.00, 3399.00, 2754.00,
 'd1000000-0000-0000-0000-000000000003',
 '华硕', 'ROG STRIX Z790-A GAMING WIFI',
 15, 45,
 '/images/components/asus-rog-z790-a.jpg', '[]',
 '{"chipset":"Z790","socket":"LGA1700","form_factor":"ATX","memory":"DDR5 x4 max 192GB","pcie":"PCIe 5.0 x16 + PCIe 4.0 x16","m2":"4x M.2 (1x PCIe 5.0 + 3x PCIe 4.0)","wifi":"WiFi 6E","lan":"2.5G有线","usb":"Thunderbolt 4","audio":"ALC4080","vrm":"16+1相","color":"白色","rgb":"Aura Sync"}',
 true, true, 1.05),

-- 华硕 PRIME Z790-P WIFI
('c3000000-0000-0000-0000-000000000004',
 '华硕 PRIME Z790-P WIFI 主板',
 'asus-prime-z790p-wifi',
 '14+1 DrMOS供电，6层PCB，Wi-Fi 6+2.5G有线，AURA SYNC灯效。Z790入门之选。',
 1999.00, 2399.00, 1899.00,
 'd1000000-0000-0000-0000-000000000003',
 '华硕', 'PRIME Z790-P WIFI',
 22, 78,
 '/images/components/asus-prime-z790p.jpg', '[]',
 '{"chipset":"Z790","socket":"LGA1700","form_factor":"ATX","memory":"DDR5 x4 max 192GB","pcie":"PCIe 5.0 x16 + PCIe 4.0 x16","m2":"3x M.2 PCIe 4.0","wifi":"WiFi 6","lan":"2.5G有线","usb":"USB 3.2 Gen2x2 Type-C","audio":"ALC897","vrm":"14+1 DrMOS","color":"黑色"}',
 true, false, 0.95),

-- 微星 B650M GAMING PLUS
('c3000000-0000-0000-0000-000000000005',
 '微星 MAG B650M GAMING PLUS WIFI 主板',
 'msi-b650m-gaming-plus',
 'AMD AM5平台入门之选，10+2+1相供电，DDR5支持，WiFi 6E。搭配Ryzen 7000/9000系列。',
 899.00, 1099.00, 854.00,
 'd1000000-0000-0000-0000-000000000003',
 '微星', 'MAG B650M GAMING PLUS WIFI',
 30, 95,
 '/images/components/msi-b650m-gaming-plus.jpg', '[]',
 '{"chipset":"B650M","socket":"AM5","form_factor":"M-ATX","memory":"DDR5 x4 max 128GB","pcie":"PCIe 4.0 x16","m2":"2x M.2 PCIe 4.0","wifi":"WiFi 6E","lan":"2.5G有线","usb":"USB 3.2 Gen2 Type-C","audio":"ALC897","vrm":"10+2+1相","color":"黑色"}',
 true, true, 0.68),

-- 微星 MAG Z790 TOMAHAWK
('c3000000-0000-0000-0000-000000000006',
 '微星 MAG Z790 TOMAHAWK WIFI 主板',
 'msi-z790-tomahawk',
 '战斧导弹系列，16+1+1相供电，PCIe 5.0 M.2，WiFi 6E。高端游戏主板性价比之选。',
 1899.00, 2299.00, 1804.00,
 'd1000000-0000-0000-0000-000000000003',
 '微星', 'MAG Z790 TOMAHAWK WIFI',
 18, 56,
 '/images/components/msi-z790-tomahawk.jpg', '[]',
 '{"chipset":"Z790","socket":"LGA1700","form_factor":"ATX","memory":"DDR5 x4 max 192GB","pcie":"PCIe 5.0 x16 + PCIe 4.0 x16","m2":"4x M.2 (1x PCIe 5.0)","wifi":"WiFi 6E","lan":"2.5G有线","usb":"USB 3.2 Gen2x2 Type-C","audio":"ALC4080","vrm":"16+1+1相","color":"黑色"}',
 true, false, 1.02),

-- 华硕 ROG X670E HERO
('c3000000-0000-0000-0000-000000000007',
 '华硕 ROG CROSSHAIR X670E HERO 主板',
 'asus-rog-x670e-hero',
 'AMD旗舰主板，18+2供电，PCIe 5.0全覆盖，WiFi 6E，ROG极致做工。AM5平台天花板。',
 3999.00, 4699.00, 3799.00,
 'd1000000-0000-0000-0000-000000000003',
 '华硕', 'ROG CROSSHAIR X670E HERO',
 8, 15,
 '/images/components/asus-rog-x670e-hero.jpg', '[]',
 '{"chipset":"X670E","socket":"AM5","form_factor":"ATX","memory":"DDR5 x4 max 128GB","pcie":"PCIe 5.0 x16 x2","m2":"5x M.2 (2x PCIe 5.0)","wifi":"WiFi 6E","lan":"2.5G有线","usb":"Thunderbolt 4 + USB 3.2 Gen2x2","audio":"ALC4082","vrm":"18+2相","color":"黑色","rgb":"Aura Sync"}',
 true, true, 1.35),

-- 技嘉 B760M AORUS ELITE
('c3000000-0000-0000-0000-000000000008',
 '技嘉 B760M AORUS ELITE AX 主板',
 'gigabyte-b760m-aorus-elite',
 '小雕系列，12+1+1相供电，DDR5超频支持，WiFi 6E。M-ATX高性价比之选。',
 749.00, 949.00, 712.00,
 'd1000000-0000-0000-0000-000000000003',
 '技嘉', 'B760M AORUS ELITE AX',
 32, 88,
 '/images/components/gigabyte-b760m-aorus.jpg', '[]',
 '{"chipset":"B760M","socket":"LGA1700","form_factor":"M-ATX","memory":"DDR5 x4 max 128GB","pcie":"PCIe 4.0 x16","m2":"2x M.2 PCIe 4.0","wifi":"WiFi 6E","lan":"2.5G有线","usb":"USB 3.2 Gen2 Type-C","audio":"ALC897","vrm":"12+1+1相","color":"黑色"}',
 true, false, 0.70),

-- 华硕 B760M-PLUS WIFI D4
('c3000000-0000-0000-0000-000000000009',
 '华硕 TUF GAMING B760M-PLUS WIFI D4 主板',
 'asus-tuf-b760m-d4',
 'DDR4版本重炮手，兼容DDR4内存降低装机成本。12+1相供电，WiFi 6。',
 649.00, 849.00, 617.00,
 'd1000000-0000-0000-0000-000000000003',
 '华硕', 'TUF GAMING B760M-PLUS WIFI D4',
 25, 102,
 '/images/components/asus-tuf-b760m-d4.jpg', '[]',
 '{"chipset":"B760M","socket":"LGA1700","form_factor":"M-ATX","memory":"DDR4 x4 max 128GB","pcie":"PCIe 4.0 x16","m2":"2x M.2 PCIe 4.0","wifi":"WiFi 6","lan":"2.5G有线","usb":"USB 3.2 Gen2 Type-C","audio":"ALC897","vrm":"12+1相","color":"黑色","note":"DDR4版本"}',
 true, false, 0.68),

-- 微星 PRO Z790-A WIFI
('c3000000-0000-0000-0000-00000000000a',
 '微星 PRO Z790-A WIFI 主板',
 'msi-pro-z790a',
 'PRO系列商务风格，14+1+1相供电，PCIe 5.0。稳定可靠的Z790选择。',
 1599.00, 1999.00, 1519.00,
 'd1000000-0000-0000-0000-000000000003',
 '微星', 'PRO Z790-A WIFI',
 20, 65,
 '/images/components/msi-pro-z790a.jpg', '[]',
 '{"chipset":"Z790","socket":"LGA1700","form_factor":"ATX","memory":"DDR5 x4 max 192GB","pcie":"PCIe 5.0 x16 + PCIe 4.0 x16","m2":"4x M.2 (1x PCIe 5.0)","wifi":"WiFi 6E","lan":"2.5G有线","usb":"USB 3.2 Gen2x2 Type-C","audio":"ALC4080","vrm":"14+1+1相","color":"银白色"}',
 true, false, 0.98);

-- =============================================
-- 5. 内存 (12款)
-- =============================================
INSERT INTO products (id, name, slug, description, price, original_price, cost_price, category_id, brand, model, stock, sold_count, image_url, images, specs, is_active, is_featured, weight) VALUES

-- 芝奇 幻锋戟 DDR5-6000 32GB
('c4000000-0000-0000-0000-000000000001',
 '芝奇 幻锋戟 DDR5-6000 32GB(16GBx2) 内存',
 'gskill-trident-z5-6000-32g',
 'DDR5-6000高频，CL30时序，铝合金散热马甲，RGB灯效。高端游戏内存标杆。',
 899.00, 1099.00, 854.00,
 'd1000000-0000-0000-0000-000000000004',
 '芝奇', '幻锋戟 DDR5-6000 32GB',
 40, 156,
 '/images/components/gskill-trident-z5-32g.jpg', '[]',
 '{"capacity":"32GB (16GBx2)","type":"DDR5","speed":"6000MHz","timing":"CL30-36-36-96","voltage":"1.35V","ecc":"Non-ECC","form_factor":"DIMM","rgb":"支持","heat_spreader":"铝合金","color":"银色"}',
 true, true, 0.12),

-- 芝奇 幻锋戟 DDR5-7200 32GB
('c4000000-0000-0000-0000-000000000002',
 '芝奇 幻锋戟 DDR5-7200 32GB(16GBx2) 内存',
 'gskill-trident-z5-7200-32g',
 'DDR5-7200超高频，CL34时序，极致性能释放。超频玩家与发烧友专属。',
 1299.00, 1599.00, 1234.00,
 'd1000000-0000-0000-0000-000000000004',
 '芝奇', '幻锋戟 DDR5-7200 32GB',
 20, 67,
 '/images/components/gskill-trident-z5-7200.jpg', '[]',
 '{"capacity":"32GB (16GBx2)","type":"DDR5","speed":"7200MHz","timing":"CL34-44-44-96","voltage":"1.40V","ecc":"Non-ECC","form_factor":"DIMM","rgb":"支持","heat_spreader":"铝合金","color":"黑色"}',
 true, true, 0.12),

-- 金士顿 FURY Beast DDR5-5600 32GB
('c4000000-0000-0000-0000-000000000003',
 '金士顿 FURY Beast DDR5-5600 32GB(16GBx2) 内存',
 'kingston-fury-beast-5600-32g',
 '即插即用，自动超频至5600MHz。稳定可靠，兼容性优秀。主流装机首选。',
 799.00, 999.00, 759.00,
 'd1000000-0000-0000-0000-000000000004',
 '金士顿', 'FURY Beast DDR5-5600 32GB',
 50, 210,
 '/images/components/kingston-fury-beast-32g.jpg', '[]',
 '{"capacity":"32GB (16GBx2)","type":"DDR5","speed":"5600MHz","timing":"CL36-36-36","voltage":"1.25V","ecc":"Non-ECC","form_factor":"DIMM","rgb":"无","heat_spreader":"铝合金","color":"黑色","pnp":"支持即插即用"}',
 true, true, 0.10),

-- 金士顿 FURY Beast DDR5-5600 16GB
('c4000000-0000-0000-0000-000000000004',
 '金士顿 FURY Beast DDR5-5600 16GB(8GBx2) 内存',
 'kingston-fury-beast-5600-16g',
 '入门DDR5套装，5600MHz自动超频。预算装机的高性价比选择。',
 499.00, 649.00, 474.00,
 'd1000000-0000-0000-0000-000000000004',
 '金士顿', 'FURY Beast DDR5-5600 16GB',
 60, 289,
 '/images/components/kingston-fury-beast-16g.jpg', '[]',
 '{"capacity":"16GB (8GBx2)","type":"DDR5","speed":"5600MHz","timing":"CL36-36-36","voltage":"1.25V","ecc":"Non-ECC","form_factor":"DIMM","rgb":"无","heat_spreader":"铝合金","color":"黑色"}',
 true, false, 0.08),

-- 海盗船 复仇者 DDR5-6000 32GB
('c4000000-0000-0000-0000-000000000005',
 '海盗船 复仇者 DDR5-6000 32GB(16GBx2) 内存',
 'corsair-vengeance-6000-32g',
 '经典复仇者系列，DDR5-6000高频，低调散热设计。稳定兼容，装机常客。',
 849.00, 1049.00, 807.00,
 'd1000000-0000-0000-0000-000000000004',
 '海盗船', '复仇者 DDR5-6000 32GB',
 35, 134,
 '/images/components/corsair-vengeance-32g.jpg', '[]',
 '{"capacity":"32GB (16GBx2)","type":"DDR5","speed":"6000MHz","timing":"CL36-36-36-76","voltage":"1.35V","ecc":"Non-ECC","form_factor":"DIMM","rgb":"无","heat_spreader":"铝合金","color":"黑色"}',
 true, false, 0.10),

-- 海盗船 统治者 DDR5-6400 32GB
('c4000000-0000-0000-0000-000000000006',
 '海盗船 统治者 Platinum RGB DDR5-6400 32GB(16GBx2) 内存',
 'corsair-dominator-6400-32g',
 '旗舰统治者系列，Capellix RGB灯效，DHX散热技术。极致颜值与性能。',
 1199.00, 1499.00, 1139.00,
 'd1000000-0000-0000-0000-000000000004',
 '海盗船', '统治者 DDR5-6400 32GB',
 18, 45,
 '/images/components/corsair-dominator-32g.jpg', '[]',
 '{"capacity":"32GB (16GBx2)","type":"DDR5","speed":"6400MHz","timing":"CL32-39-39-80","voltage":"1.40V","ecc":"Non-ECC","form_factor":"DIMM","rgb":"Capellix RGB","heat_spreader":"DHX铝合金","color":"白色"}',
 true, true, 0.12),

-- 英睿达 Pro DDR5-5600 32GB
('c4000000-0000-0000-0000-000000000007',
 '英睿达 Crucial Pro DDR5-5600 32GB(16GBx2) 内存',
 'crucial-pro-5600-32g',
 '美光原厂颗粒，即插即用，JEDEC标准。稳定可靠的原厂之选。',
 749.00, 949.00, 712.00,
 'd1000000-0000-0000-0000-000000000004',
 '英睿达', 'Crucial Pro DDR5-5600 32GB',
 45, 178,
 '/images/components/crucial-pro-32g.jpg', '[]',
 '{"capacity":"32GB (16GBx2)","type":"DDR5","speed":"5600MHz","timing":"CL46-45-45","voltage":"1.10V","ecc":"Non-ECC","form_factor":"DIMM","rgb":"无","heat_spreader":"铝合金","color":"黑色","note":"美光原厂颗粒"}',
 true, false, 0.09),

-- 英睿达 Pro DDR5-6400 64GB
('c4000000-0000-0000-0000-000000000008',
 '英睿达 Crucial Pro DDR5-6400 64GB(32GBx2) 内存',
 'crucial-pro-6400-64g',
 '64GB大容量，DDR5-6400高频。游戏+AI双修玩家首选。',
 1899.00, 2399.00, 1804.00,
 'd1000000-0000-0000-0000-000000000004',
 '英睿达', 'Crucial Pro DDR5-6400 64GB',
 15, 34,
 '/images/components/crucial-pro-64g.jpg', '[]',
 '{"capacity":"64GB (32GBx2)","type":"DDR5","speed":"6400MHz","timing":"CL38-38-38","voltage":"1.35V","ecc":"Non-ECC","form_factor":"DIMM","rgb":"无","heat_spreader":"铝合金","color":"黑色"}',
 true, true, 0.12),

-- 芝奇 炫锋戟 DDR5-6000 64GB
('c4000000-0000-0000-0000-000000000009',
 '芝奇 炫锋戟 DDR5-6000 64GB(32GBx2) 内存',
 'gskill-flare-x5-6000-64g',
 'AMD EXPO优化，64GB大容量，DDR5-6000高频。AM5平台大容量首选。',
 1699.00, 2099.00, 1614.00,
 'd1000000-0000-0000-0000-000000000004',
 '芝奇', '炫锋戟 DDR5-6000 64GB',
 18, 56,
 '/images/components/gskill-flare-x5-64g.jpg', '[]',
 '{"capacity":"64GB (32GBx2)","type":"DDR5","speed":"6000MHz","timing":"CL30-36-36-96","voltage":"1.35V","ecc":"Non-ECC","form_factor":"DIMM","rgb":"无","heat_spreader":"铝合金","color":"黑色","amd_expo":"支持"}',
 true, false, 0.12),

-- 金士顿 FURY Renegade DDR5-7200 32GB
('c4000000-0000-0000-0000-00000000000a',
 '金士顿 FURY Renegade DDR5-7200 32GB(16GBx2) 内存',
 'kingston-fury-renegade-7200-32g',
 'FURY旗舰系列，DDR5-7200超高频，CL38时序。极限超频玩家之选。',
 1399.00, 1699.00, 1329.00,
 'd1000000-0000-0000-0000-000000000004',
 '金士顿', 'FURY Renegade DDR5-7200 32GB',
 15, 42,
 '/images/components/kingston-fury-renegade-32g.jpg', '[]',
 '{"capacity":"32GB (16GBx2)","type":"DDR5","speed":"7200MHz","timing":"CL38-44-44","voltage":"1.45V","ecc":"Non-ECC","form_factor":"DIMM","rgb":"支持","heat_spreader":"铝合金","color":"银黑色"}',
 true, true, 0.12),

-- 海盗船 复仇者 DDR5-5600 64GB
('c4000000-0000-0000-0000-00000000000b',
 '海盗船 复仇者 DDR5-5600 64GB(32GBx2) 内存',
 'corsair-vengeance-5600-64g',
 '64GB大容量DDR5-5600，工作站与AI开发者首选。稳定可靠，兼容性广。',
 1599.00, 1999.00, 1519.00,
 'd1000000-0000-0000-0000-000000000004',
 '海盗船', '复仇者 DDR5-5600 64GB',
 22, 78,
 '/images/components/corsair-vengeance-64g.jpg', '[]',
 '{"capacity":"64GB (32GBx2)","type":"DDR5","speed":"5600MHz","timing":"CL40-40-40","voltage":"1.25V","ecc":"Non-ECC","form_factor":"DIMM","rgb":"无","heat_spreader":"铝合金","color":"黑色"}',
 true, false, 0.10),

-- 宏碁 掠夺者 DDR5-6400 32GB
('c4000000-0000-0000-0000-00000000000c',
 '宏碁 掠夺者 Vesta II DDR5-6400 32GB(16GBx2) 内存',
 'acer-predator-vesta2-6400-32g',
 '掠夺者系列，DDR5-6400高频，RGB灯效，铝合金散热。电竞内存新选择。',
 849.00, 1049.00, 807.00,
 'd1000000-0000-0000-0000-000000000004',
 '宏碁', '掠夺者 Vesta II DDR5-6400 32GB',
 25, 89,
 '/images/components/acer-predator-vesta2-32g.jpg', '[]',
 '{"capacity":"32GB (16GBx2)","type":"DDR5","speed":"6400MHz","timing":"CL32-39-39","voltage":"1.40V","ecc":"Non-ECC","form_factor":"DIMM","rgb":"支持","heat_spreader":"铝合金","color":"银白色"}',
 true, false, 0.11);

-- =============================================
-- 6. 固态硬盘 SSD (12款)
-- =============================================
INSERT INTO products (id, name, slug, description, price, original_price, cost_price, category_id, brand, model, stock, sold_count, image_url, images, specs, is_active, is_featured, weight) VALUES

-- 三星 990 Pro 1TB
('c5000000-0000-0000-0000-000000000001',
 '三星 990 Pro 1TB NVMe SSD',
 'samsung-990pro-1tb',
 'PCIe 4.0旗舰，读取7450MB/s，写入6900MB/s。三星V-NAND闪存，稳定可靠。',
 799.00, 999.00, 759.00,
 'd1000000-0000-0000-0000-000000000005',
 '三星', '990 Pro 1TB',
 45, 210,
 '/images/components/samsung-990pro-1tb.jpg', '[]',
 '{"capacity":"1TB","interface":"PCIe 4.0 x4","protocol":"NVMe 2.0","form_factor":"M.2 2280","read_speed":"7450MB/s","write_speed":"6900MB/s","nand":"Samsung V-NAND TLC","controller":"Samsung Pascal","cache":"1GB LPDDR4","tbw":"600TBW","warranty":"5年"}',
 true, true, 0.01),

-- 三星 990 Pro 2TB
('c5000000-0000-0000-0000-000000000002',
 '三星 990 Pro 2TB NVMe SSD',
 'samsung-990pro-2tb',
 '2TB大容量，读取7450MB/s，写入6900MB/s。内容创作者与游戏玩家首选。',
 1399.00, 1699.00, 1329.00,
 'd1000000-0000-0000-0000-000000000005',
 '三星', '990 Pro 2TB',
 30, 134,
 '/images/components/samsung-990pro-2tb.jpg', '[]',
 '{"capacity":"2TB","interface":"PCIe 4.0 x4","protocol":"NVMe 2.0","form_factor":"M.2 2280","read_speed":"7450MB/s","write_speed":"6900MB/s","nand":"Samsung V-NAND TLC","controller":"Samsung Pascal","cache":"2GB LPDDR4","tbw":"1200TBW","warranty":"5年"}',
 true, true, 0.01),

-- 西部数据 SN850X 1TB
('c5000000-0000-0000-0000-000000000003',
 '西部数据 WD_BLACK SN850X 1TB NVMe SSD',
 'wd-sn850x-1tb',
 '游戏模式加持，读取7300MB/s，写入6300MB/s。WD_BLACK旗舰游戏SSD。',
 749.00, 949.00, 712.00,
 'd1000000-0000-0000-0000-000000000005',
 '西部数据', 'WD_BLACK SN850X 1TB',
 40, 178,
 '/images/components/wd-sn850x-1tb.jpg', '[]',
 '{"capacity":"1TB","interface":"PCIe 4.0 x4","protocol":"NVMe 1.4","form_factor":"M.2 2280","read_speed":"7300MB/s","write_speed":"6300MB/s","nand":"BiCS5 TLC","controller":"WD自家","cache":"1GB DDR4","tbw":"600TBW","warranty":"5年","game_mode":"支持"}',
 true, false, 0.01),

-- 西部数据 SN850X 2TB
('c5000000-0000-0000-0000-000000000004',
 '西部数据 WD_BLACK SN850X 2TB NVMe SSD',
 'wd-sn850x-2tb',
 '2TB大容量游戏SSD，读取7300MB/s。大作库随心装。',
 1349.00, 1649.00, 1282.00,
 'd1000000-0000-0000-0000-000000000005',
 '西部数据', 'WD_BLACK SN850X 2TB',
 25, 98,
 '/images/components/wd-sn850x-2tb.jpg', '[]',
 '{"capacity":"2TB","interface":"PCIe 4.0 x4","protocol":"NVMe 1.4","form_factor":"M.2 2280","read_speed":"7300MB/s","write_speed":"6600MB/s","nand":"BiCS5 TLC","controller":"WD自家","cache":"2GB DDR4","tbw":"1200TBW","warranty":"5年"}',
 true, false, 0.01),

-- 金士顿 KC3000 1TB
('c5000000-0000-0000-0000-000000000005',
 '金士顿 KC3000 1TB NVMe SSD',
 'kingston-kc3000-1tb',
 '读取7000MB/s，写入6000MB/s。高性价比PCIe 4.0之选。',
 699.00, 899.00, 664.00,
 'd1000000-0000-0000-0000-000000000005',
 '金士顿', 'KC3000 1TB',
 50, 245,
 '/images/components/kingston-kc3000-1tb.jpg', '[]',
 '{"capacity":"1TB","interface":"PCIe 4.0 x4","protocol":"NVMe 2.0","form_factor":"M.2 2280","read_speed":"7000MB/s","write_speed":"6000MB/s","nand":"3D TLC","controller":"Phison E18","cache":"1GB DDR4","tbw":"800TBW","warranty":"5年"}',
 true, false, 0.01),

-- 金士顿 KC3000 2TB
('c5000000-0000-0000-0000-000000000006',
 '金士顿 KC3000 2TB NVMe SSD',
 'kingston-kc3000-2tb',
 '2TB大容量，读取7000MB/s。性价比大容量之选。',
 1299.00, 1599.00, 1234.00,
 'd1000000-0000-0000-0000-000000000005',
 '金士顿', 'KC3000 2TB',
 30, 134,
 '/images/components/kingston-kc3000-2tb.jpg', '[]',
 '{"capacity":"2TB","interface":"PCIe 4.0 x4","protocol":"NVMe 2.0","form_factor":"M.2 2280","read_speed":"7000MB/s","write_speed":"7000MB/s","nand":"3D TLC","controller":"Phison E18","cache":"2GB DDR4","tbw":"1600TBW","warranty":"5年"}',
 true, false, 0.01),

-- 致态 TiPlus 7100 1TB
('c5000000-0000-0000-0000-000000000007',
 '致态 TiPlus 7100 1TB NVMe SSD',
 'zhiti-tiplus7100-1tb',
 '长江存储自研颗粒，读取7000MB/s。国产高性能SSD代表之作。',
 599.00, 799.00, 569.00,
 'd1000000-0000-0000-0000-000000000005',
 '致态', 'TiPlus 7100 1TB',
 55, 289,
 '/images/components/zhiti-tiplus7100-1tb.jpg', '[]',
 '{"capacity":"1TB","interface":"PCIe 4.0 x4","protocol":"NVMe 2.0","form_factor":"M.2 2280","read_speed":"7000MB/s","write_speed":"6000MB/s","nand":"长江存储232层3D TLC","controller":"联芸MAP1602","cache":"HMB","tbw":"600TBW","warranty":"5年","note":"国产颗粒"}',
 true, true, 0.01),

-- 致态 TiPlus 7100 2TB
('c5000000-0000-0000-0000-000000000008',
 '致态 TiPlus 7100 2TB NVMe SSD',
 'zhiti-tiplus7100-2tb',
 '2TB国产大容量SSD，读取7000MB/s。国产存储性价比天花板。',
 1099.00, 1399.00, 1044.00,
 'd1000000-0000-0000-0000-000000000005',
 '致态', 'TiPlus 7100 2TB',
 35, 167,
 '/images/components/zhiti-tiplus7100-2tb.jpg', '[]',
 '{"capacity":"2TB","interface":"PCIe 4.0 x4","protocol":"NVMe 2.0","form_factor":"M.2 2280","read_speed":"7000MB/s","write_speed":"6000MB/s","nand":"长江存储232层3D TLC","controller":"联芸MAP1602","cache":"HMB","tbw":"1200TBW","warranty":"5年"}',
 true, false, 0.01),

-- 三星 990 EVO Plus 2TB
('c5000000-0000-0000-0000-000000000009',
 '三星 990 EVO Plus 2TB NVMe SSD',
 'samsung-990evo-plus-2tb',
 'PCIe 5.0 x2兼容，读取7250MB/s。新一代能效比标杆。',
 1599.00, 1999.00, 1519.00,
 'd1000000-0000-0000-0000-000000000005',
 '三星', '990 EVO Plus 2TB',
 20, 56,
 '/images/components/samsung-990evo-plus-2tb.jpg', '[]',
 '{"capacity":"2TB","interface":"PCIe 5.0 x2 / PCIe 4.0 x4","protocol":"NVMe 2.0","form_factor":"M.2 2280","read_speed":"7250MB/s","write_speed":"6300MB/s","nand":"Samsung V-NAND TLC","controller":"Samsung Piccolo","cache":"HMB","tbw":"1200TBW","warranty":"5年"}',
 true, false, 0.01),

-- 致态 TiPro 7000 2TB
('c5000000-0000-0000-0000-00000000000a',
 '致态 TiPro 7000 2TB NVMe SSD',
 'zhiti-tipro7000-2tb',
 '旗舰级国产SSD，读取7450MB/s，独立缓存。国产高端存储标杆。',
 1199.00, 1499.00, 1139.00,
 'd1000000-0000-0000-0000-000000000005',
 '致态', 'TiPro 7000 2TB',
 25, 98,
 '/images/components/zhiti-tipro7000-2tb.jpg', '[]',
 '{"capacity":"2TB","interface":"PCIe 4.0 x4","protocol":"NVMe 2.0","form_factor":"M.2 2280","read_speed":"7450MB/s","write_speed":"6750MB/s","nand":"长江存储232层3D TLC","controller":"英韧IG5236","cache":"2GB DDR4","tbw":"1200TBW","warranty":"5年"}',
 true, false, 0.01),

-- 三星 990 Pro 4TB
('c5000000-0000-0000-0000-00000000000b',
 '三星 990 Pro 4TB NVMe SSD',
 'samsung-990pro-4tb',
 '4TB超大容量旗舰SSD，读取7450MB/s。专业创作者与数据密集型用户专属。',
 3299.00, 3999.00, 3134.00,
 'd1000000-0000-0000-0000-000000000005',
 '三星', '990 Pro 4TB',
 10, 23,
 '/images/components/samsung-990pro-4tb.jpg', '[]',
 '{"capacity":"4TB","interface":"PCIe 4.0 x4","protocol":"NVMe 2.0","form_factor":"M.2 2280","read_speed":"7450MB/s","write_speed":"6900MB/s","nand":"Samsung V-NAND TLC","controller":"Samsung Pascal","cache":"4GB LPDDR4","tbw":"2400TBW","warranty":"5年"}',
 true, false, 0.01),

-- 西部数据 SN7100 1TB
('c5000000-0000-0000-0000-00000000000c',
 '西部数据 WD Blue SN7100 1TB NVMe SSD',
 'wd-sn7100-1tb',
 '主流级PCIe 4.0 SSD，读取5150MB/s。日常使用与轻度游戏性价比之选。',
 549.00, 699.00, 522.00,
 'd1000000-0000-0000-0000-000000000005',
 '西部数据', 'WD Blue SN7100 1TB',
 60, 312,
 '/images/components/wd-sn7100-1tb.jpg', '[]',
 '{"capacity":"1TB","interface":"PCIe 4.0 x4","protocol":"NVMe 1.4","form_factor":"M.2 2280","read_speed":"5150MB/s","write_speed":"4900MB/s","nand":"BiCS5 TLC","controller":"WD自家","cache":"HMB","tbw":"600TBW","warranty":"5年"}',
 true, false, 0.01);

-- =============================================
-- 7. 散热器 (12款)
-- =============================================
INSERT INTO products (id, name, slug, description, price, original_price, cost_price, category_id, brand, model, stock, sold_count, image_url, images, specs, is_active, is_featured, weight) VALUES

-- 九州风神 玄冰400
('c6000000-0000-0000-0000-000000000001',
 '九州风神 玄冰400 V5 风冷散热器',
 'deepcool-gammaxx400-v5',
 '百元级经典单塔散热器，4热管直触，120mm风扇。入门装机性价比之选。',
 89.00, 119.00, 85.00,
 'd1000000-0000-0000-0000-000000000006',
 '九州风神', '玄冰400 V5',
 80, 456,
 '/images/components/deepcool-gammaxx400.jpg', '[]',
 '{"type":"风冷单塔","heatpipes":"4根直触","fan":"120mm PWM","fan_speed":"500-1500RPM","noise":"≤26dB","tdp_support":"150W","height":"155mm","socket":"Intel LGA1700/1200 / AMD AM5/AM4","weight":"0.58kg"}',
 true, false, 0.58),

-- 利民 PA120
('c6000000-0000-0000-0000-000000000002',
 '利民 PA120 SE 双塔风冷散热器',
 'thermalright-pa120-se',
 '双塔6热管，同价位性能优于240水冷。静音与性能的完美平衡。',
 169.00, 219.00, 161.00,
 'd1000000-0000-0000-0000-000000000006',
 '利民', 'PA120 SE',
 55, 234,
 '/images/components/thermalright-pa120.jpg', '[]',
 '{"type":"风冷双塔","heatpipes":"6根","fan":"2x 120mm PWM","fan_speed":"300-1550RPM","noise":"≤25.6dB","tdp_support":"250W","height":"155mm","socket":"Intel LGA1700/1200 / AMD AM5/AM4","weight":"0.95kg"}',
 true, true, 0.95),

-- 利民 FC140
('c6000000-0000-0000-0000-000000000003',
 '利民 FC140 双塔风冷散热器',
 'thermalright-fc140',
 '双塔8热管旗舰风冷，媲美360水冷性能。极致散热，静音体验。',
 259.00, 329.00, 246.00,
 'd1000000-0000-0000-0000-000000000006',
 '利民', 'FC140',
 35, 98,
 '/images/components/thermalright-fc140.jpg', '[]',
 '{"type":"风冷双塔","heatpipes":"8根","fan":"2x 140mm PWM","fan_speed":"300-1500RPM","noise":"≤25.8dB","tdp_support":"280W","height":"163mm","socket":"Intel LGA1700/1200 / AMD AM5/AM4","weight":"1.25kg"}',
 true, false, 1.25),

-- 九州风神 大霜塔 V5
('c6000000-0000-0000-0000-000000000004',
 '九州风神 大霜塔 V5 风冷散热器',
 'deepcool-assassin-iv-v5',
 '旗舰双塔风冷，7热管设计，双风扇配置。九州风神风冷王者。',
 299.00, 399.00, 284.00,
 'd1000000-0000-0000-0000-000000000006',
 '九州风神', '大霜塔 V5',
 28, 67,
 '/images/components/deepcool-assassin-iv.jpg', '[]',
 '{"type":"风冷双塔","heatpipes":"7根","fan":"1x 140mm + 1x 120mm PWM","fan_speed":"300-1400RPM","noise":"≤24.4dB","tdp_support":"260W","height":"165mm","socket":"Intel LGA1700/1200 / AMD AM5/AM4","weight":"1.15kg"}',
 true, false, 1.15),

-- 猫头鹰 NH-D15
('c6000000-0000-0000-0000-000000000005',
 '猫头鹰 NH-D15 chromax.black 风冷散热器',
 'noctua-nh-d15-chromax',
 '顶级双塔风冷，极致静音与性能。几乎媲美360水冷，静音党信仰之选。',
 699.00, 849.00, 664.00,
 'd1000000-0000-0000-0000-000000000006',
 '猫头鹰', 'NH-D15 chromax.black',
 12, 34,
 '/images/components/noctua-nh-d15.jpg', '[]',
 '{"type":"风冷双塔","heatpipes":"6根","fan":"2x 140mm NF-A15 PWM","fan_speed":"300-1500RPM","noise":"≤24.6dB","tdp_support":"250W","height":"165mm","socket":"Intel LGA1700/1200 / AMD AM5/AM4","weight":"1.15kg","warranty":"6年"}',
 true, true, 1.15),

-- 瓦尔基里 C360
('c6000000-0000-0000-0000-000000000006',
 '瓦尔基里 C360 ARGB 一体式水冷散热器',
 'valkyrie-c360-argb',
 '360mm一体式水冷，ARGB灯效，铜底冷头。高性能水冷入门之选。',
 299.00, 399.00, 284.00,
 'd1000000-0000-0000-0000-000000000006',
 '瓦尔基里', 'C360 ARGB',
 40, 145,
 '/images/components/valkyrie-c360.jpg', '[]',
 '{"type":"360mm一体式水冷","radiator":"360mm铝排","fan":"3x 120mm ARGB","fan_speed":"500-1800RPM","noise":"≤28dB","pump_speed":"2800RPM","tdp_support":"300W","tube_length":"350mm","socket":"Intel LGA1700/1200 / AMD AM5/AM4","rgb":"ARGB"}',
 true, true, 1.20),

-- 瓦尔基里 V360
('c6000000-0000-0000-0000-000000000007',
 '瓦尔基里 V360 AMOLED 一体式水冷散热器',
 'valkyrie-v360-amoled',
 '360mm旗舰水冷，2.1寸AMOLED屏显，可视化温度监控。颜值与性能兼备。',
 599.00, 749.00, 569.00,
 'd1000000-0000-0000-0000-000000000006',
 '瓦尔基里', 'V360 AMOLED',
 22, 56,
 '/images/components/valkyrie-v360.jpg', '[]',
 '{"type":"360mm一体式水冷","radiator":"360mm铝排","fan":"3x 120mm PWM","fan_speed":"500-2000RPM","noise":"≤28dB","pump_speed":"3000RPM","tdp_support":"350W","tube_length":"380mm","socket":"Intel LGA1700/1200 / AMD AM5/AM4","display":"2.1寸AMOLED屏显"}',
 true, true, 1.35),

-- 华硕 ROG 飞龙360
('c6000000-0000-0000-0000-000000000008',
 '华硕 ROG RYUO III 360 ARGB 一体式水冷',
 'asus-rog-ryuo-360',
 'ROG飞龙三代，360mm水冷，Anime Matrix LED显示屏。ROG信仰旗舰水冷。',
 1499.00, 1899.00, 1424.00,
 'd1000000-0000-0000-0000-000000000006',
 '华硕', 'ROG RYUO III 360',
 10, 23,
 '/images/components/asus-rog-ryuo-360.jpg', '[]',
 '{"type":"360mm一体式水冷","radiator":"360mm铝排","fan":"3x 120mm ARGB","fan_speed":"600-2000RPM","noise":"≤30dB","pump_speed":"2800RPM","tdp_support":"350W","tube_length":"380mm","socket":"Intel LGA1700/1200 / AMD AM5/AM4","display":"Anime Matrix LED","rgb":"ARGB"}',
 true, false, 1.40),

-- 九州风神 冰堡垒 360
('c6000000-0000-0000-0000-000000000009',
 '九州风神 冰堡垒 360 ARGB 一体式水冷',
 'deepcool-ls720-360',
 '360mm水冷，第四代冷头设计，ARGB灯效。九州风神高端水冷代表。',
 449.00, 569.00, 427.00,
 'd1000000-0000-0000-0000-000000000006',
 '九州风神', '冰堡垒 360 ARGB',
 30, 89,
 '/images/components/deepcool-ls720.jpg', '[]',
 '{"type":"360mm一体式水冷","radiator":"360mm铝排","fan":"3x 120mm ARGB","fan_speed":"500-1800RPM","noise":"≤28dB","pump_speed":"3100RPM","tdp_support":"320W","tube_length":"350mm","socket":"Intel LGA1700/1200 / AMD AM5/AM4","rgb":"ARGB"}',
 true, false, 1.25),

-- 利民 Frozen Magic 240
('c6000000-0000-0000-0000-00000000000a',
 '利民 Frozen Magic 240 SCENIC 一体式水冷',
 'thermalright-frozen-magic-240',
 '240mm一体式水冷，静音水泵，铜底冷头。中端水冷性价比之选。',
 229.00, 299.00, 218.00,
 'd1000000-0000-0000-0000-000000000006',
 '利民', 'Frozen Magic 240 SCENIC',
 45, 167,
 '/images/components/thermalright-frozen-magic-240.jpg', '[]',
 '{"type":"240mm一体式水冷","radiator":"240mm铝排","fan":"2x 120mm PWM","fan_speed":"500-1800RPM","noise":"≤27dB","pump_speed":"2500RPM","tdp_support":"250W","tube_length":"300mm","socket":"Intel LGA1700/1200 / AMD AM5/AM4"}',
 true, false, 0.90),

-- 微星 MAG 360R
('c6000000-0000-0000-0000-00000000000b',
 '微星 MAG CORELIQUID E360 一体式水冷',
 'msi-mag-e360',
 '微星主流360水冷，双腔体冷头设计，ARGB灯效。品牌信仰之选。',
 599.00, 749.00, 569.00,
 'd1000000-0000-0000-0000-000000000006',
 '微星', 'MAG CORELIQUID E360',
 20, 45,
 '/images/components/msi-mag-e360.jpg', '[]',
 '{"type":"360mm一体式水冷","radiator":"360mm铝排","fan":"3x 120mm ARGB","fan_speed":"500-1800RPM","noise":"≤28dB","pump_speed":"2800RPM","tdp_support":"320W","tube_length":"350mm","socket":"Intel LGA1700/1200 / AMD AM5/AM4","rgb":"ARGB","feature":"双腔体冷头"}',
 true, false, 1.30),

-- 恩杰 Kraken 360
('c6000000-0000-0000-0000-00000000000c',
 '恩杰 Kraken 360 RGB 一体式水冷',
 'nzxt-kraken-360-rgb',
 '恩杰海妖系列，圆形LCD屏显，CAM软件控制。高端水冷颜值担当。',
 1199.00, 1499.00, 1139.00,
 'd1000000-0000-0000-0000-000000000006',
 '恩杰', 'Kraken 360 RGB',
 12, 28,
 '/images/components/nzxt-kraken-360.jpg', '[]',
 '{"type":"360mm一体式水冷","radiator":"360mm铝排","fan":"3x 120mm RGB","fan_speed":"500-1800RPM","noise":"≤28dB","pump_speed":"2800RPM","tdp_support":"320W","tube_length":"350mm","socket":"Intel LGA1700/1200 / AMD AM5/AM4","display":"1.54寸LCD圆形屏","software":"CAM"}',
 true, false, 1.35);

-- =============================================
-- 8. 电源 (10款)
-- =============================================
INSERT INTO products (id, name, slug, description, price, original_price, cost_price, category_id, brand, model, stock, sold_count, image_url, images, specs, is_active, is_featured, weight) VALUES

-- 金河田 Nexus Gold 750W
('c7000000-0000-0000-0000-000000000001',
 '金河田 Nexus Gold Ultra 750W 全模组电源',
 'goldfield-nexus-750w',
 '80PLUS金牌，全模组，LLC谐振+DC-DC架构。主流中高端平台标配。',
 549.00, 699.00, 522.00,
 'd1000000-0000-0000-0000-000000000007',
 '金河田', 'Nexus Gold Ultra 750W',
 40, 156,
 '/images/components/goldfield-nexus-750w.jpg', '[]',
 '{"wattage":"750W","efficiency":"80 PLUS Gold","modular":"全模组","topology":"LLC谐振 + DC-DC","fan":"120mm FDB风扇","protections":"OVP/UVP/OCP/OPP/SCP","atx_version":"ATX 3.0","pcie":"1x 12VHPWR + 4x PCIe 8pin","size":"150x140x86mm","warranty":"10年"}',
 true, true, 1.50),

-- 首席玩家 ACK 850W
('c7000000-0000-0000-0000-000000000002',
 '首席玩家 ACK 850W 金牌全模组电源',
 'firstplayer-ack-850w',
 '80PLUS金牌，全模组，适配中高端显卡+处理器。稳定可靠的850W选择。',
 699.00, 899.00, 664.00,
 'd1000000-0000-0000-0000-000000000007',
 '首席玩家', 'ACK 850W Gold',
 30, 89,
 '/images/components/firstplayer-ack-850w.jpg', '[]',
 '{"wattage":"850W","efficiency":"80 PLUS Gold","modular":"全模组","topology":"LLC谐振 + DC-DC","fan":"120mm FDB风扇","protections":"OVP/UVP/OCP/OPP/SCP","atx_version":"ATX 3.0","pcie":"1x 12VHPWR + 4x PCIe 8pin","size":"150x140x86mm","warranty":"10年"}',
 true, false, 1.60),

-- 振华 LEADEX III 850W
('c7000000-0000-0000-0000-000000000003',
 '振华 LEADEX III 850W 金牌全模组电源',
 'super-flower-leadex3-850w',
 '振华旗舰系列，80PLUS金牌，全模组，全日系电容。高端电源标杆之作。',
 649.00, 849.00, 617.00,
 'd1000000-0000-0000-0000-000000000007',
 '振华', 'LEADEX III 850W Gold',
 25, 67,
 '/images/components/super-flower-leadex3-850w.jpg', '[]',
 '{"wattage":"850W","efficiency":"80 PLUS Gold","modular":"全模组","topology":"LLC谐振 + DC-DC","fan":"140mm FDB风扇","protections":"OVP/UVP/OCP/OPP/SCP/OTP","capacitor":"全日系","size":"150x160x86mm","warranty":"10年"}',
 true, true, 1.75),

-- 海韵 FOCUS GX-850
('c7000000-0000-0000-0000-000000000004',
 '海韵 FOCUS GX-850 金牌全模组电源',
 'seasonic-focus-gx-850',
 '海韵经典系列，80PLUS金牌，全模组，半无扇模式。静音与性能兼备。',
 699.00, 899.00, 664.00,
 'd1000000-0000-0000-0000-000000000007',
 '海韵', 'FOCUS GX-850',
 22, 78,
 '/images/components/seasonic-focus-gx-850.jpg', '[]',
 '{"wattage":"850W","efficiency":"80 PLUS Gold","modular":"全模组","topology":"LLC谐振 + DC-DC","fan":"120mm FDB风扇","protections":"OVP/UVP/OCP/OPP/SCP/OTP","feature":"半无扇模式","size":"140x150x86mm","warranty":"10年"}',
 true, false, 1.55),

-- 金河田 Nexus Gold 1050W
('c7000000-0000-0000-0000-000000000005',
 '金河田 Nexus Gold Ultra 1050W 全模组电源',
 'goldfield-nexus-1050w',
 '1050W金牌全模组，高端i9+旗舰显卡双烤稳定。12VHPWR原生接口。',
 699.00, 899.00, 664.00,
 'd1000000-0000-0000-0000-000000000007',
 '金河田', 'Nexus Gold Ultra 1050W',
 20, 45,
 '/images/components/goldfield-nexus-1050w.jpg', '[]',
 '{"wattage":"1050W","efficiency":"80 PLUS Gold","modular":"全模组","topology":"LLC谐振 + DC-DC","fan":"135mm FDB风扇","protections":"OVP/UVP/OCP/OPP/SCP","atx_version":"ATX 3.0","pcie":"2x 12VHPWR + 4x PCIe 8pin","size":"150x160x86mm","warranty":"10年"}',
 true, false, 1.85),

-- 首席玩家 ACK 1050W
('c7000000-0000-0000-0000-000000000006',
 '首席玩家 ACK 1050W 金牌全模组电源',
 'firstplayer-ack-1050w',
 '1050W金牌全模组，ATX 3.0标准，12VHPWR原生接口。高端平台首选。',
 899.00, 1149.00, 854.00,
 'd1000000-0000-0000-0000-000000000007',
 '首席玩家', 'ACK 1050W Gold',
 18, 34,
 '/images/components/firstplayer-ack-1050w.jpg', '[]',
 '{"wattage":"1050W","efficiency":"80 PLUS Gold","modular":"全模组","topology":"LLC谐振 + DC-DC","fan":"135mm FDB风扇","protections":"OVP/UVP/OCP/OPP/SCP","atx_version":"ATX 3.0","pcie":"2x 12VHPWR + 4x PCIe 8pin","size":"150x160x86mm","warranty":"10年"}',
 true, false, 1.90),

-- 海韵 PRIME TX-1200
('c7000000-0000-0000-0000-000000000007',
 '海韵 PRIME TX-1200 钛金牌全模组电源',
 'seasonic-prime-tx-1200',
 '80PLUS钛金认证，1200W旗舰，全日系电容。工作站/AI服务器专用。',
 1899.00, 2399.00, 1804.00,
 'd1000000-0000-0000-0000-000000000007',
 '海韵', 'PRIME TX-1200',
 10, 15,
 '/images/components/seasonic-prime-tx-1200.jpg', '[]',
 '{"wattage":"1200W","efficiency":"80 PLUS Titanium","modular":"全模组","topology":"LLC谐振 + DC-DC","fan":"135mm FDB风扇","protections":"OVP/UVP/OCP/OPP/SCP/OTP","capacitor":"全日系","size":"150x170x86mm","warranty":"12年"}',
 true, true, 2.10),

-- 海盗船 RM1000x
('c7000000-0000-0000-0000-000000000008',
 '海盗船 RM1000x 金牌全模组电源',
 'corsair-rm1000x',
 '海盗船经典RMx系列，1000W金牌，零转速模式。静音高性能之选。',
 899.00, 1149.00, 854.00,
 'd1000000-0000-0000-0000-000000000007',
 '海盗船', 'RM1000x',
 18, 56,
 '/images/components/corsair-rm1000x.jpg', '[]',
 '{"wattage":"1000W","efficiency":"80 PLUS Gold","modular":"全模组","topology":"LLC谐振 + DC-DC","fan":"135mm FDB风扇","protections":"OVP/UVP/OCP/OPP/SCP","feature":"零转速模式","size":"150x160x86mm","warranty":"10年"}',
 true, false, 1.80),

-- 长城 V7 750W
('c7000000-0000-0000-0000-000000000009',
 '长城 V7 金牌全模组 750W 电源',
 'greatwall-v7-750w',
 '国产金牌全模组，性价比之选。稳定可靠，适合主流平台。',
 449.00, 599.00, 427.00,
 'd1000000-0000-0000-0000-000000000007',
 '长城', 'V7 750W Gold',
 35, 120,
 '/images/components/greatwall-v7-750w.jpg', '[]',
 '{"wattage":"750W","efficiency":"80 PLUS Gold","modular":"全模组","topology":"LLC + DC-DC","fan":"120mm风扇","protections":"OVP/UVP/OCP/OPP/SCP","size":"150x140x86mm","warranty":"5年"}',
 true, false, 1.45),

-- 银欣 SX1000
('c7000000-0000-0000-0000-00000000000a',
 '银欣 SX1000-LPT 铂金全模组 1000W 电源',
 'silverstone-sx1000',
 'SFX-L规格，1000W白金效率，全模组。小机箱大电源的极致之选。',
 1399.00, 1799.00, 1329.00,
 'd1000000-0000-0000-0000-000000000007',
 '银欣', 'SX1000-LPT',
 12, 23,
 '/images/components/silverstone-sx1000.jpg', '[]',
 '{"wattage":"1000W","efficiency":"80 PLUS Platinum","modular":"全模组","form_factor":"SFX-L","topology":"LLC + DC-DC","fan":"120mm风扇","protections":"OVP/UVP/OCP/OPP/SCP","size":"125x130x63mm","warranty":"5年","note":"SFX-L小规格"}',
 true, false, 1.10);

-- =============================================
-- 9. 机箱 (10款)
-- =============================================
INSERT INTO products (id, name, slug, description, price, original_price, cost_price, category_id, brand, model, stock, sold_count, image_url, images, specs, is_active, is_featured, weight) VALUES

-- 九州风神 CH560
('c8000000-0000-0000-0000-000000000001',
 '九州风神 CH560 智能版 海景房机箱',
 'deepcool-ch560-smart',
 '全景侧透海景房设计，上下分仓架构，支持360水冷。高颜值主流之选。',
 449.00, 599.00, 427.00,
 'd1000000-0000-0000-0000-000000000008',
 '九州风神', 'CH560 智能版',
 35, 134,
 '/images/components/deepcool-ch560.jpg', '[]',
 '{"type":"ATX中塔","style":"海景房/双侧透","material":"钢化玻璃+SPCC","mb_support":"ATX/M-ATX/ITX","gpu_length":"380mm","cooler_height":"175mm","radiator_support":"顶部360mm/240mm + 前部360mm","fans_included":"4x 120mm ARGB","drive_bays":"2x 3.5寸 + 2x 2.5寸","io_panel":"USB 3.0 x2 + USB-C + Audio","color":"黑色","weight":"7.8kg"}',
 true, true, 7.80),

-- 九州风神 CG530U
('c8000000-0000-0000-0000-000000000002',
 '九州风神 CG530U 曲面玻璃 海景房机箱',
 'deepcool-cg530u',
 '曲面玻璃全景侧透设计，支持背插主板。颜值党首选海景房。',
 499.00, 649.00, 474.00,
 'd1000000-0000-0000-0000-000000000008',
 '九州风神', 'CG530U',
 28, 98,
 '/images/components/deepcool-cg530u.jpg', '[]',
 '{"type":"ATX中塔","style":"曲面玻璃全景侧透","material":"曲面钢化玻璃+SPCC","mb_support":"ATX/M-ATX/ITX","gpu_length":"400mm","cooler_height":"175mm","radiator_support":"顶部360mm + 前部360mm","fans_included":"无","drive_bays":"2x 3.5寸 + 2x 2.5寸","io_panel":"USB 3.0 x2 + USB-C + Audio","color":"白色","weight":"8.2kg","feature":"背插主板支持"}',
 true, true, 8.20),

-- 乔思伯 D401
('c8000000-0000-0000-0000-000000000003',
 '乔思伯 D401 白色 海景房机箱',
 'jonsbo-d401-white',
 '全铝框架+钢化玻璃，简约海景房设计。桌面美学之选。',
 399.00, 529.00, 379.00,
 'd1000000-0000-0000-0000-000000000008',
 '乔思伯', 'D401 白色',
 25, 78,
 '/images/components/jonsbo-d401.jpg', '[]',
 '{"type":"ATX中塔","style":"海景房","material":"铝合金+钢化玻璃","mb_support":"ATX/M-ATX/ITX","gpu_length":"350mm","cooler_height":"165mm","radiator_support":"顶部240mm + 前部360mm","fans_included":"无","drive_bays":"2x 3.5寸 + 2x 2.5寸","io_panel":"USB 3.0 x2 + Audio","color":"白色","weight":"6.5kg"}',
 true, false, 6.50),

-- 鑫谷 无界1
('c8000000-0000-0000-0000-000000000004',
 '鑫谷 无界1 海景房机箱',
 'segotep-unbounded-1',
 '全景侧透，支持背插主板，理线优化设计。海景房性价比之选。',
 389.00, 499.00, 370.00,
 'd1000000-0000-0000-0000-000000000008',
 '鑫谷', '无界1',
 30, 112,
 '/images/components/segotep-unbounded-1.jpg', '[]',
 '{"type":"ATX中塔","style":"海景房/双侧透","material":"钢化玻璃+SPCC","mb_support":"ATX/M-ATX/ITX","gpu_length":"380mm","cooler_height":"170mm","radiator_support":"顶部360mm + 前部360mm","fans_included":"3x 120mm ARGB","drive_bays":"2x 3.5寸 + 2x 2.5寸","io_panel":"USB 3.0 x2 + USB-C + Audio","color":"黑色","weight":"7.5kg","feature":"背插主板支持"}',
 true, false, 7.50),

-- 安钛克 DF700 FLUX
('c8000000-0000-0000-0000-000000000005',
 '安钛克 DF700 FLUX 中塔机箱',
 'antec-df700-flux',
 'FLUX散热架构，网状前面板，高风流设计。散热性能型机箱。',
 429.00, 569.00, 408.00,
 'd1000000-0000-0000-0000-000000000008',
 '安钛克', 'DF700 FLUX',
 22, 67,
 '/images/components/antec-df700-flux.jpg', '[]',
 '{"type":"ATX中塔","style":"高风流网状","material":"SPCC+钢化玻璃侧透","mb_support":"ATX/M-ATX/ITX","gpu_length":"405mm","cooler_height":"175mm","radiator_support":"顶部360mm + 前部360mm","fans_included":"3x 120mm ARGB + 2x 120mm","drive_bays":"2x 3.5寸 + 2x 2.5寸","io_panel":"USB 3.0 x2 + USB-C + Audio","color":"黑色","weight":"7.2kg"}',
 true, false, 7.20),

-- 联力 O11D EVO
('c8000000-0000-0000-0000-000000000006',
 '联力 O11D EVO RGB 海景房机箱',
 'lianli-o11d-evo-rgb',
 '经典O11D升级版，双仓设计，支持双360水冷。海景房天花板之作。',
 799.00, 1049.00, 759.00,
 'd1000000-0000-0000-0000-000000000008',
 '联力', 'O11D EVO RGB',
 15, 45,
 '/images/components/lianli-o11d-evo.jpg', '[]',
 '{"type":"ATX中塔","style":"海景房/双仓","material":"铝合金+钢化玻璃","mb_support":"E-ATX/ATX/M-ATX/ITX","gpu_length":"425mm","cooler_height":"167mm","radiator_support":"顶部360mm + 底部360mm + 侧面360mm","fans_included":"无","drive_bays":"4x 3.5寸 + 4x 2.5寸","io_panel":"USB 3.0 x2 + USB-C x2 + Audio","color":"白色","weight":"10.5kg"}',
 true, true, 10.50),

-- 几何未来 M8
('c8000000-0000-0000-0000-000000000007',
 '几何未来 M8 带屏幕海景房机箱',
 'geometric-future-m8',
 '集成小尺寸IPS屏幕，全景侧透。科技感满满的海景房新形态。',
 599.00, 799.00, 569.00,
 'd1000000-0000-0000-0000-000000000008',
 '几何未来', 'M8',
 18, 34,
 '/images/components/geometric-future-m8.jpg', '[]',
 '{"type":"ATX中塔","style":"带屏幕海景房","material":"SPCC+钢化玻璃","mb_support":"ATX/M-ATX/ITX","gpu_length":"390mm","cooler_height":"170mm","radiator_support":"顶部360mm + 前部360mm","fans_included":"无","drive_bays":"2x 3.5寸 + 2x 2.5寸","io_panel":"USB 3.0 x2 + USB-C + Audio","display":"IPS副屏","color":"黑色","weight":"8.0kg"}',
 true, false, 8.00),

-- 乔思伯 UMX4
('c8000000-0000-0000-0000-000000000008',
 '乔思伯 UMX4 Plus Micro-ATX 机箱',
 'jonsbo-umx4-plus',
 '全铝机身M-ATX机箱，简约桌面美学。紧凑型高品质之选。',
 349.00, 469.00, 332.00,
 'd1000000-0000-0000-0000-000000000008',
 '乔思伯', 'UMX4 Plus',
 20, 56,
 '/images/components/jonsbo-umx4-plus.jpg', '[]',
 '{"type":"Micro-ATX","style":"紧凑型侧透","material":"铝合金+钢化玻璃","mb_support":"M-ATX/ITX","gpu_length":"320mm","cooler_height":"160mm","radiator_support":"顶部240mm","fans_included":"无","drive_bays":"1x 3.5寸 + 2x 2.5寸","io_panel":"USB 3.0 x2 + Audio","color":"银色","weight":"4.2kg"}',
 true, false, 4.20),

-- 鑫谷 昆仑 KL-1250G 机箱
('c8000000-0000-0000-0000-000000000009',
 '鑫谷 昆仑 KL-650M Mini-ITX 机箱',
 'segotep-kl-650m',
 'ITX迷你机箱，支持SFX电源，桌面小钢炮。迷你主机玩家首选。',
 359.00, 479.00, 341.00,
 'd1000000-0000-0000-0000-000000000008',
 '鑫谷', '昆仑 KL-650M',
 15, 42,
 '/images/components/segotep-kl-650m.jpg', '[]',
 '{"type":"Mini-ITX","style":"迷你机箱","material":"SPCC+钢化玻璃","mb_support":"ITX","gpu_length":"300mm","cooler_height":"140mm","radiator_support":"顶部120mm/240mm","psu_support":"SFX/SFX-L","fans_included":"1x 120mm","drive_bays":"1x 2.5寸","io_panel":"USB 3.0 x2 + Audio","color":"黑色","weight":"3.5kg"}',
 true, false, 3.50),

-- 联力 LANCOOL III
('c8000000-0000-0000-0000-00000000000a',
 '联力 LANCOOL III 全塔机箱',
 'lianli-lancool-iii',
 '全塔大空间，支持E-ATX主板+多显卡+分体水冷。旗舰级装机平台。',
 999.00, 1299.00, 949.00,
 'd1000000-0000-0000-0000-000000000008',
 '联力', 'LANCOOL III',
 10, 18,
 '/images/components/lianli-lancool-iii.jpg', '[]',
 '{"type":"全塔","style":"大面积侧透","material":"SPCC+钢化玻璃","mb_support":"E-ATX/ATX/M-ATX/ITX","gpu_length":"435mm","cooler_height":"187mm","radiator_support":"顶部420mm + 前部420mm + 底部360mm","fans_included":"4x 140mm PWM","drive_bays":"6x 3.5寸 + 4x 2.5寸","io_panel":"USB 3.0 x2 + USB-C x2 + Audio","color":"黑色","weight":"12.8kg"}',
 true, false, 12.80);

-- =============================================
-- 完成！
-- CPU: 8款 | 显卡: 12款 | 主板: 10款 | 内存: 12款
-- SSD: 12款 | 散热器: 12款 | 电源: 10款 | 机箱: 10款
-- 共计: 86款八大件产品
-- =============================================
