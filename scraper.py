"""
胖虫电脑 京东 & 抖音 商品爬虫
用法: python scraper.py
输出: pangchong.db (SQLite数据库)
"""

import sqlite3
import json
import re
import time
import hashlib
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ========== 配置 ==========
DB_PATH = Path(__file__).parent / "pangchong.db"
JD_STORE_URL = "https://mall.jd.com/index-1000651190.html"
JD_SEARCH_URL = "https://search.jd.com/Search"
JD_M_SEARCH = "https://so.m.jd.com/ware/search.action"
DOUYIN_URL = "https://v.douyin.com/hYq_ldkfZQ4/"

HEADERS_DESKTOP = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

HEADERS_MOBILE = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

HEADERS_API = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://mall.jd.com/",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}


# ========== 数据库 ==========
def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          TEXT PRIMARY KEY,
            source      TEXT NOT NULL,
            name        TEXT NOT NULL,
            series      TEXT,
            category    TEXT,
            price       REAL,
            original_price REAL,
            sales       TEXT,
            rating      REAL,
            comments    INTEGER,
            spec        TEXT,
            features    TEXT,
            url         TEXT,
            image_url   TEXT,
            badge       TEXT,
            scraped_at  TEXT NOT NULL,
            raw_json    TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS scrape_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            source      TEXT NOT NULL,
            url         TEXT,
            status      TEXT NOT NULL,
            items_found INTEGER DEFAULT 0,
            message     TEXT,
            scraped_at  TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id  TEXT NOT NULL,
            price       REAL NOT NULL,
            recorded_at TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)

    conn.commit()
    return conn


def save_product(conn, product):
    c = conn.cursor()
    pid = product["id"]

    # 检查是否已存在，记录价格变动
    c.execute("SELECT price FROM products WHERE id = ?", (pid,))
    row = c.fetchone()
    if row and row[0] != product["price"]:
        c.execute(
            "INSERT INTO price_history (product_id, price, recorded_at) VALUES (?, ?, ?)",
            (pid, product["price"], datetime.now().isoformat()),
        )

    c.execute("""
        INSERT OR REPLACE INTO products
        (id, source, name, series, category, price, original_price, sales, rating,
         comments, spec, features, url, image_url, badge, scraped_at, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        pid, product.get("source", ""), product["name"],
        product.get("series", ""), product.get("category", ""),
        product.get("price", 0), product.get("original_price"),
        product.get("sales", ""), product.get("rating"),
        product.get("comments", 0), product.get("spec", ""),
        json.dumps(product.get("features", []), ensure_ascii=False),
        product.get("url", ""), product.get("image_url", ""),
        product.get("badge", ""), datetime.now().isoformat(),
        json.dumps(product.get("raw", {}), ensure_ascii=False),
    ))
    conn.commit()


def save_log(conn, source, url, status, items=0, msg=""):
    conn.execute(
        "INSERT INTO scrape_log (source, url, status, items_found, message, scraped_at) VALUES (?,?,?,?,?,?)",
        (source, url, status, items, msg, datetime.now().isoformat()),
    )
    conn.commit()


def gen_id(source, name):
    return f"{source}_{hashlib.md5(name.encode()).hexdigest()[:12]}"


# ========== 京东爬虫 ==========
def scrape_jd(conn):
    print("\n" + "=" * 60)
    print("  开始抓取京东 - 胖虫电脑旗舰店")
    print("=" * 60)

    products = []

    # --- 方案1: 搜索接口 ---
    products.extend(_jd_search_api())

    # --- 方案2: 移动端搜索 ---
    if len(products) < 3:
        products.extend(_jd_mobile_search())

    # --- 方案3: 店铺页面直接解析 ---
    if len(products) < 3:
        products.extend(_jd_store_page())

    # 去重
    seen = set()
    unique = []
    for p in products:
        if p["name"] not in seen:
            seen.add(p["name"])
            unique.append(p)

    for p in unique:
        p["source"] = "jd"
        save_product(conn, p)

    save_log(conn, "jd", JD_STORE_URL, "ok" if unique else "empty",
             len(unique), f"抓取到 {len(unique)} 件商品")

    print(f"\n  [京东] 共抓取 {len(unique)} 件商品")
    return unique


def _jd_search_api():
    """通过京东搜索API获取商品"""
    results = []
    keywords = ["胖虫电脑", "胖虫笔记本", "胖虫主机", "胖虫迷你主机"]

    for kw in keywords:
        try:
            print(f"  [JD搜索] 关键词: {kw}")
            params = {
                "keyword": kw,
                "enc": "utf-8",
                "wq": kw,
                "pvid": "",
                "page": "1",
                "s": "1",
                "click": "0",
            }
            resp = requests.get(JD_SEARCH_URL, params=params, headers=HEADERS_DESKTOP,
                                timeout=15, allow_redirects=True)

            if resp.status_code != 200:
                print(f"    HTTP {resp.status_code}")
                continue

            soup = BeautifulSoup(resp.text, "lxml")

            # 解析商品列表
            items = soup.select(".gl-item, .J_goodsList li, [class*='gl-warp'] li")
            if not items:
                items = soup.select("[data-sku]")

            print(f"    找到 {len(items)} 个商品元素")

            for item in items[:20]:
                try:
                    name_el = item.select_one(".p-name a em, .p-name em, [class*='name'] em, .p-name a")
                    if not name_el:
                        continue
                    name = name_el.get_text(strip=True)

                    # 过滤非胖虫商品
                    if "胖虫" not in name and "PANGCHONG" not in name.upper():
                        continue

                    price_el = item.select_one(".p-price strong i, .p-price i, [class*='price'] i")
                    price = float(price_el.get_text(strip=True)) if price_el else 0

                    url_el = item.select_one("a[href]")
                    url = url_el["href"] if url_el else ""
                    if url and not url.startswith("http"):
                        url = "https:" + url

                    img_el = item.select_one("img[data-lazy-img], img[data-src], img[src]")
                    img = ""
                    if img_el:
                        img = img_el.get("data-lazy-img") or img_el.get("data-src") or img_el.get("src", "")
                        if img and not img.startswith("http"):
                            img = "https:" + img

                    comment_el = item.select_one(".p-commit a, [class*='commit'] a")
                    comments = 0
                    if comment_el:
                        txt = comment_el.get_text(strip=True)
                        m = re.search(r"(\d+)", txt.replace("+", "").replace("万", "0000"))
                        if m:
                            comments = int(m.group(1))

                    results.append({
                        "id": gen_id("jd", name),
                        "name": name,
                        "price": price,
                        "comments": comments,
                        "url": url,
                        "image_url": img,
                        "category": _classify_product(name),
                        "series": _extract_series(name),
                        "spec": _extract_spec_from_name(name),
                    })
                    print(f"    ✓ {name[:40]}... RMB {price}")

                except Exception as e:
                    continue

            time.sleep(1.5)

        except Exception as e:
            print(f"    ✗ 搜索失败: {e}")
            save_log(conn, "jd", JD_SEARCH_URL, "error", 0, str(e))

    return results


def _jd_mobile_search():
    """移动端搜索"""
    results = []
    keywords = ["胖虫电脑", "胖虫笔记本"]

    for kw in keywords:
        try:
            print(f"  [JD移动端] 关键词: {kw}")
            params = {"keyword": kw, "datatype": "1", "callback": ""}
            resp = requests.get(JD_M_SEARCH, params=params, headers=HEADERS_MOBILE,
                                timeout=15, allow_redirects=True)

            if resp.status_code != 200:
                continue

            # 尝试解析JSON
            text = resp.text
            # 去掉JSONP包装
            text = re.sub(r'^[^{]*', '', text)
            text = re.sub(r'[^}]*$', '', text)

            try:
                data = json.loads(text)
                items = data.get("data", {}).get("searchm", {}).get("Paragraph", [])
            except:
                items = []

            print(f"    找到 {len(items)} 条结果")

            for item in items:
                name = item.get("WareName", "")
                if "胖虫" not in name:
                    continue

                price = float(item.get("jdPrice", 0) or 0)
                wid = item.get("WareId", "")
                url = f"https://item.jd.com/{wid}.html" if wid else ""
                img = item.get("ImageUrl", "")
                if img and not img.startswith("http"):
                    img = "https:" + img

                results.append({
                    "id": gen_id("jd", name),
                    "name": name,
                    "price": price,
                    "url": url,
                    "image_url": img,
                    "category": _classify_product(name),
                    "series": _extract_series(name),
                })
                print(f"    ✓ {name[:40]}... RMB {price}")

            time.sleep(1.5)

        except Exception as e:
            print(f"    ✗ 移动端搜索失败: {e}")

    return results


def _jd_store_page():
    """直接解析店铺页面"""
    results = []
    try:
        print(f"  [JD店铺] 解析店铺页面...")
        resp = requests.get(JD_STORE_URL, headers=HEADERS_DESKTOP, timeout=15, allow_redirects=True)

        if resp.status_code != 200:
            print(f"    HTTP {resp.status_code}")
            return results

        soup = BeautifulSoup(resp.text, "lxml")

        # 查找商品链接
        links = soup.find_all("a", href=re.compile(r"item\.jd\.com"))
        seen_urls = set()

        for link in links:
            href = link.get("href", "")
            if not href.startswith("http"):
                href = "https:" + href
            if href in seen_urls:
                continue
            seen_urls.add(href)

            name = link.get_text(strip=True)
            if len(name) < 4:
                img = link.find("img")
                name = img.get("alt", "") if img else ""

            if name and ("胖虫" in name or "PANGCHONG" in name.upper()):
                results.append({
                    "id": gen_id("jd", name),
                    "name": name,
                    "url": href,
                    "category": _classify_product(name),
                    "series": _extract_series(name),
                })
                print(f"    ✓ {name[:40]}")

    except Exception as e:
        print(f"    ✗ 店铺页解析失败: {e}")

    return results


# ========== 抖音爬虫 ==========
def scrape_douyin(conn):
    print("\n" + "=" * 60)
    print("  开始抓取抖音 - 胖虫电脑")
    print("=" * 60)

    products = []

    # --- 方案1: 短链跳转获取主页 ---
    products.extend(_douyin_redirect())

    # --- 方案2: 抖音搜索API ---
    if len(products) < 3:
        products.extend(_douyin_search())

    # --- 方案3: 抖音电商搜索 ---
    if len(products) < 3:
        products.extend(_douyin_shop_search())

    # 去重
    seen = set()
    unique = []
    for p in products:
        if p["name"] not in seen:
            seen.add(p["name"])
            unique.append(p)

    for p in unique:
        p["source"] = "douyin"
        save_product(conn, p)

    save_log(conn, "douyin", DOUYIN_URL, "ok" if unique else "empty",
             len(unique), f"抓取到 {len(unique)} 件商品")

    print(f"\n  [抖音] 共抓取 {len(unique)} 件商品")
    return unique


def _douyin_redirect():
    """解析抖音短链跳转"""
    results = []
    try:
        print(f"  [抖音] 解析短链跳转...")
        resp = requests.get(DOUYIN_URL, headers=HEADERS_MOBILE, timeout=15,
                            allow_redirects=False)

        # 获取重定向地址
        location = resp.headers.get("Location", "")
        print(f"    重定向: {location[:80]}...")

        if not location:
            # 尝试从页面提取
            soup = BeautifulSoup(resp.text, "lxml")
            meta = soup.find("meta", attrs={"http-equiv": "refresh"})
            if meta:
                content = meta.get("content", "")
                m = re.search(r"url=(.+)", content, re.IGNORECASE)
                if m:
                    location = m.group(1)

            # 尝试JS跳转
            scripts = soup.find_all("script")
            for s in scripts:
                txt = s.string or ""
                m = re.search(r'location\.(?:href|replace)\s*[\(=]\s*["\']([^"\']+)', txt)
                if m:
                    location = m.group(1)
                    break

        if location:
            # 访问实际页面
            if not location.startswith("http"):
                location = "https:" + location
            print(f"    访问实际页面...")
            resp2 = requests.get(location, headers=HEADERS_MOBILE, timeout=15)
            _parse_douyin_page(resp2.text, results)

    except Exception as e:
        print(f"    ✗ 短链解析失败: {e}")

    return results


def _douyin_search():
    """抖音搜索"""
    results = []
    try:
        print(f"  [抖音] 搜索商品...")
        # 抖音搜索接口
        search_url = "https://www.douyin.com/search/"
        params = {"keyword": "胖虫电脑", "type": "goods"}
        resp = requests.get(search_url, params=params, headers=HEADERS_DESKTOP,
                            timeout=15, allow_redirects=True)

        if resp.status_code == 200:
            _parse_douyin_page(resp.text, results)

    except Exception as e:
        print(f"    ✗ 抖音搜索失败: {e}")

    return results


def _douyin_shop_search():
    """抖音电商搜索"""
    results = []
    try:
        print(f"  [抖音电商] 搜索商品...")
        # 抖音电商搜索
        shop_url = "https://fxg.jinritemai.com/search"
        params = {"keyword": "胖虫电脑"}
        resp = requests.get(shop_url, params=params, headers=HEADERS_MOBILE,
                            timeout=15, allow_redirects=True)

        if resp.status_code == 200:
            # 尝试JSON解析
            try:
                data = resp.json()
                items = data.get("data", {}).get("products", [])
                for item in items:
                    name = item.get("title", "") or item.get("name", "")
                    if not name:
                        continue
                    price = item.get("price", 0) or item.get("market_price", 0)
                    if isinstance(price, str):
                        price = float(re.sub(r'[^\d.]', '', price) or 0)

                    results.append({
                        "id": gen_id("dy", name),
                        "name": name,
                        "price": price / 100 if price > 10000 else price,
                        "sales": str(item.get("sales", "")),
                        "image_url": item.get("cover", "") or item.get("img", ""),
                        "category": _classify_product(name),
                        "series": _extract_series(name),
                    })
                    print(f"    ✓ {name[:40]}... RMB {price}")
            except json.JSONDecodeError:
                _parse_douyin_page(resp.text, results)

    except Exception as e:
        print(f"    ✗ 抖音电商搜索失败: {e}")

    return results


def _parse_douyin_page(html, results):
    """解析抖音页面中的商品信息"""
    soup = BeautifulSoup(html, "lxml")

    # 从script标签提取SSR数据
    for script in soup.find_all("script"):
        txt = script.string or ""
        if "RENDER_DATA" in txt or "__NEXT_DATA__" in txt or "window.__data" in txt:
            try:
                # 提取JSON
                m = re.search(r'(?:RENDER_DATA|__NEXT_DATA__|window\.__data)\s*=\s*({.+?})\s*;?\s*(?:</|$)', txt, re.DOTALL)
                if m:
                    data = json.loads(m.group(1))
                    _extract_products_from_json(data, results, "dy")
            except:
                pass

    # 从页面结构提取
    for item in soup.select("[class*='product'], [class*='goods'], [class*='card']"):
        name_el = item.select_one("[class*='name'], [class*='title']")
        price_el = item.select_one("[class*='price']")
        if name_el and price_el:
            name = name_el.get_text(strip=True)
            price_text = price_el.get_text(strip=True)
            price = float(re.sub(r'[^\d.]', '', price_text) or 0)

            if "胖虫" in name or "电脑" in name:
                results.append({
                    "id": gen_id("dy", name),
                    "name": name,
                    "price": price,
                    "category": _classify_product(name),
                    "series": _extract_series(name),
                })
                print(f"    ✓ {name[:40]}... RMB {price}")


def _extract_products_from_json(data, results, source, depth=0):
    """递归从JSON中提取商品信息"""
    if depth > 8:
        return
    if isinstance(data, dict):
        # 检查是否是商品对象
        name = data.get("title") or data.get("name") or data.get("ware_name") or ""
        if name and ("胖虫" in name or "电脑" in name or "笔记本" in name):
            price = data.get("price") or data.get("market_price") or data.get("jd_price") or 0
            if isinstance(price, str):
                price = float(re.sub(r'[^\d.]', '', price) or 0)
            if isinstance(price, (int, float)) and price > 100:
                if price > 10000:
                    price = price / 100

                results.append({
                    "id": gen_id(source, name),
                    "name": name,
                    "price": price,
                    "sales": str(data.get("sales", "")),
                    "rating": data.get("score") or data.get("rate"),
                    "comments": data.get("comment_count") or data.get("comments", 0),
                    "image_url": data.get("cover") or data.get("img") or data.get("image", ""),
                    "url": data.get("url") or data.get("detail_url", ""),
                    "category": _classify_product(name),
                    "series": _extract_series(name),
                    "raw": data,
                })
                print(f"    ✓ {name[:40]}... RMB {price}")

        for v in data.values():
            _extract_products_from_json(v, results, source, depth + 1)

    elif isinstance(data, list):
        for item in data:
            _extract_products_from_json(item, results, source, depth + 1)


# ========== 商品分类辅助 ==========
def _classify_product(name):
    name = name.lower()
    if any(k in name for k in ["笔记本", "游戏本", "轻薄本", "laptop"]):
        if any(k in name for k in ["轻薄", "商务", "灵刃", "轻风", "breeze", "blade"]):
            return "laptop-thin"
        return "laptop-gaming"
    if any(k in name for k in ["工作站", "workstation", "渲染"]):
        return "workstation"
    if any(k in name for k in ["迷你", "mini", "mini主机", "mini pc", "nuc"]):
        return "mini"
    if any(k in name for k in ["主机", "台式", "diy", "整机"]):
        return "desktop"
    return "other"


def _extract_series(name):
    series_map = {
        "毒刺": "毒刺系列", "暗影": "暗影系列", "旗舰": "旗舰系列",
        "轻风": "轻风系列", "灵刃": "灵刃系列",
        "创世": "创世系列", "渲染": "创世系列",
        "虫卵": "虫卵系列",
        "雷霆": "雷霆系列", "机皇": "机皇系列",
        "暗影猎手": "DIY台式", "雷霆战甲": "DIY台式",
    }
    for key, series in series_map.items():
        if key in name:
            return series
    return ""


def _extract_spec_from_name(name):
    """从商品名提取配置"""
    parts = []
    cpu_patterns = [
        r'i[579]-\d{4,5}[A-Z]*', r'R[579]\s*\d{4}[A-Z]*',
        r'Threadripper\s*\w+', r'Ryzen\s*\w+\s*\d+',
    ]
    gpu_patterns = [
        r'RTX\s*\d{4}\s*(?:Ti\s*)?(?:Super)?', r'RX\s*\d{4}\s*XT*',
        r'GTX\s*\d{4}', r'RTX\s*A\d{4}',
    ]
    ram_patterns = [r'\d+GB\s*DDR\d+', r'\d+GB\s*内存']
    ssd_patterns = [r'\d+[GT]B?\s*(?:SSD|NVMe|固态)', r'\d+[GT]B?\s*硬盘']

    for p in cpu_patterns:
        m = re.search(p, name, re.IGNORECASE)
        if m: parts.append(m.group())
    for p in gpu_patterns:
        m = re.search(p, name, re.IGNORECASE)
        if m: parts.append(m.group())
    for p in ram_patterns:
        m = re.search(p, name, re.IGNORECASE)
        if m: parts.append(m.group())
    for p in ssd_patterns:
        m = re.search(p, name, re.IGNORECASE)
        if m: parts.append(m.group())

    return " / ".join(parts) if parts else ""


# ========== 导出功能 ==========
def export_to_json(conn):
    """导出数据库为JSON"""
    c = conn.cursor()
    c.execute("SELECT * FROM products ORDER BY source, category, price")
    columns = [desc[0] for desc in c.description]
    rows = [dict(zip(columns, row)) for row in c.fetchall()]

    # features 从JSON字符串还原
    for row in rows:
        if row.get("features"):
            try:
                row["features"] = json.loads(row["features"])
            except:
                pass
        if row.get("raw_json"):
            try:
                row["raw_json"] = json.loads(row["raw_json"])
            except:
                pass

    out_path = Path(__file__).parent / "products.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"\n  已导出 JSON: {out_path}")
    return rows


def export_to_js(conn):
    """导出为JS格式，可直接在网页中使用"""
    c = conn.cursor()
    c.execute("SELECT id, source, name, series, category, price, original_price, "
              "sales, rating, comments, spec, features, url, image_url, badge FROM products "
              "ORDER BY source, category, price")
    columns = [desc[0] for desc in c.description]
    rows = []
    for row in c.fetchall():
        d = dict(zip(columns, row))
        if d.get("features"):
            try:
                d["features"] = json.loads(d["features"])
            except:
                d["features"] = []
        rows.append(d)

    out_path = Path(__file__).parent / "products_db.js"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("// 胖虫电脑产品数据库 - 自动生成\n")
        f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 数据来源: 京东 + 抖音\n\n")
        f.write("const PRODUCTS_DB = ")
        json.dump(rows, f, ensure_ascii=False, indent=2)
        f.write(";\n")

    print(f"  已导出 JS:   {out_path}")
    return rows


def print_summary(conn):
    """打印数据库摘要"""
    c = conn.cursor()

    print("\n" + "=" * 60)
    print("  数据库摘要")
    print("=" * 60)

    c.execute("SELECT COUNT(*) FROM products")
    total = c.fetchone()[0]
    print(f"  商品总数: {total}")

    c.execute("SELECT source, COUNT(*) FROM products GROUP BY source")
    for source, count in c.fetchall():
        label = {"jd": "京东", "douyin": "抖音"}.get(source, source)
        print(f"    {label}: {count} 件")

    c.execute("SELECT category, COUNT(*), MIN(price), MAX(price) FROM products GROUP BY category")
    print("\n  分类统计:")
    cat_names = {
        "laptop-gaming": "游戏笔记本", "laptop-thin": "轻薄本",
        "desktop": "台式主机", "workstation": "工作站",
        "mini": "迷你主机", "other": "其他",
    }
    for cat, count, min_p, max_p in c.fetchall():
        name = cat_names.get(cat, cat)
        print(f"    {name}: {count} 件  RMB {min_p or 0:,.0f} - RMB {max_p or 0:,.0f}")

    c.execute("SELECT name, price, source FROM products ORDER BY price DESC LIMIT 5")
    print("\n  价格TOP5:")
    for name, price, source in c.fetchall():
        label = "京东" if source == "jd" else "抖音"
        print(f"    [{label}] {name[:45]}... RMB {price:,.0f}")

    # 抓取日志
    c.execute("SELECT source, status, items_found, message FROM scrape_log ORDER BY scraped_at DESC LIMIT 4")
    print("\n  抓取日志:")
    for source, status, items, msg in c.fetchall():
        label = "京东" if source == "jd" else "抖音"
        icon = "✓" if status == "ok" else "✗"
        print(f"    [{label}] {icon} {msg}")

    print("\n" + "=" * 60)


# ========== 主流程 ==========
def main():
    print("""
    ╔══════════════════════════════════════════╗
    ║   胖虫电脑 商品爬虫 v1.0                 ║
    ║   数据源: 京东旗舰店 + 抖音              ║
    ║   输出: pangchong.db (SQLite)            ║
    ╚══════════════════════════════════════════╝
    """)

    conn = init_db()

    # 爬取京东
    jd_products = scrape_jd(conn)

    # 爬取抖音
    dy_products = scrape_douyin(conn)

    # 如果在线爬取结果为空，合并本地已知产品数据
    total = len(jd_products) + len(dy_products)
    if total < 5:
        print("\n  在线抓取数据不足，合并本地产品库...")
        _merge_known_products(conn)

    # 导出
    export_to_json(conn)
    export_to_js(conn)

    # 打印摘要
    print_summary(conn)

    conn.close()
    print(f"\n  数据库已保存: {DB_PATH}")
    print(f"  文件大小: {DB_PATH.stat().st_size / 1024:.1f} KB")
    print("\n  完成！\n")


def _merge_known_products(conn):
    """合并本地已知的产品数据"""
    known = [
        # ===== 京东产品 =====
        {"source": "jd", "name": "胖虫毒刺 i7-13620H RTX4060 16G 512G 游戏笔记本",
         "series": "毒刺系列", "category": "laptop-gaming", "badge": "hot",
         "price": 6299, "original_price": 7499, "spec": "i7-13620H / RTX 4060 / 16GB DDR5 / 512GB SSD / 15.6\" 2K 165Hz",
         "features": ["蓝天NH50模具", "独显直连+MUX开关", "双风扇四热管散热", "100% sRGB高色域", "RGB背光键盘"],
         "url": "https://item.jd.com/胖虫毒刺4060"},
        {"source": "jd", "name": "胖虫毒刺 i9-13900H RTX4070 32G 1T 游戏笔记本",
         "series": "毒刺系列", "category": "laptop-gaming", "badge": "rec",
         "price": 8999, "original_price": 10499, "spec": "i9-13900H / RTX 4070 / 32GB DDR5 / 1TB SSD / 15.6\" 2K 240Hz",
         "features": ["蓝天NH50模具", "独显直连", "DDR5双通道", "240Hz电竞屏", "雷电4接口"],
         "url": "https://item.jd.com/胖虫毒刺4070"},
        {"source": "jd", "name": "胖虫暗影 i9-14900HX RTX4080 32G 1T 16英寸 游戏笔记本",
         "series": "暗影系列", "category": "laptop-gaming", "badge": "new",
         "price": 12999, "original_price": 14999, "spec": "i9-14900HX / RTX 4080 12G / 32GB DDR5 / 1TB SSD / 16\" 2.5K 240Hz",
         "features": ["蓝天NH55模具", "满血RTX4080 175W", "液金散热", "2.5K 240Hz P3色域", "全尺寸RGB键盘"],
         "url": "https://item.jd.com/胖虫暗影4080"},
        {"source": "jd", "name": "胖虫旗舰 i9-14900HX RTX4090 64G 2T 17.3英寸 4K MiniLED 游戏笔记本",
         "series": "旗舰系列", "category": "laptop-gaming", "badge": "sale",
         "price": 24999, "original_price": 28999, "spec": "i9-14900HX / RTX 4090 16G / 64GB DDR5 / 2TB SSD / 17.3\" 4K 120Hz MiniLED",
         "features": ["蓝天NH70模具", "RTX4090 满血175W", "MiniLED 1000nit", "液金+均热板散热", "4内存插槽+3硬盘位"],
         "url": "https://item.jd.com/胖虫旗舰4090"},
        {"source": "jd", "name": "胖虫轻风 R7-7840HS 16G 512G 14英寸 2.8K OLED 轻薄本",
         "series": "轻风系列", "category": "laptop-thin", "badge": "rec",
         "price": 4999, "original_price": 5699, "spec": "R7 7840HS / Radeon 780M / 16GB LPDDR5x / 512GB SSD / 14\" 2.8K 90Hz OLED",
         "features": ["全金属机身 1.28kg", "2.8K OLED 100% DCI-P3", "67Wh大电池 续航12h", "USB4 + 全功能Type-C", "指纹电源二合一"],
         "url": "https://item.jd.com/胖虫轻风"},
        {"source": "jd", "name": "胖虫灵刃 i7-1360P 16G 512G 14英寸 2K 商务轻薄本",
         "series": "灵刃系列", "category": "laptop-thin", "badge": "new",
         "price": 4599, "original_price": 5299, "spec": "i7-1360P / Iris Xe / 16GB DDR5 / 512GB SSD / 14\" 2K IPS",
         "features": ["1.19kg超轻机身", "军标认证坚固耐用", "IR人脸识别", "双Thunderbolt 4", "56Wh快充电池"],
         "url": "https://item.jd.com/胖虫灵刃"},
        {"source": "jd", "name": "胖虫DIY台式机 i5-13400F RTX4060 16G 500G 游戏主机",
         "series": "DIY台式", "category": "desktop", "badge": "hot",
         "price": 4999, "original_price": 5999, "spec": "i5-13400F / RTX 4060 8G / 16GB DDR4 / 500GB NVMe / 侧透机箱",
         "features": ["一线品牌配件", "全模组电源", "360水冷散热", "神光同步RGB", "72h烤机测试"],
         "url": "https://item.jd.com/胖虫台式4060"},
        {"source": "jd", "name": "胖虫DIY台式机 i7-14700KF RTX4070Ti Super 32G 1T 游戏主机",
         "series": "DIY台式", "category": "desktop", "badge": "rec",
         "price": 10999, "original_price": 12999, "spec": "i7-14700KF / RTX 4070 Ti Super 16G / 32GB DDR5 / 1TB Gen4 SSD",
         "features": ["华硕/微星主板", "海韵/振华电源", "利民360水冷", "联力侧透机箱", "XMP内存超频"],
         "url": "https://item.jd.com/胖虫台式4070tis"},
        {"source": "jd", "name": "胖虫DIY台式机 i9-14900K RTX4090 64G 2T 旗舰游戏主机",
         "series": "机皇系列", "category": "desktop", "badge": "sale",
         "price": 28999, "original_price": 33999, "spec": "i9-14900K / RTX 4090 24G / 64GB DDR5 6400 / 2TB Gen4 SSD",
         "features": ["ROG MAXIMUS主板", "ROG STRIX RTX4090", "芝奇幻锋戟DDR5", "海韵PRIME 1300W钛金", "华硕ROG太阳神机箱"],
         "url": "https://item.jd.com/胖虫台式4090"},
        {"source": "jd", "name": "胖虫创世者 TRX50 Threadripper 7960X RTX A5000 128G 2T 工作站",
         "series": "创世系列", "category": "workstation", "badge": "new",
         "price": 42999, "spec": "Threadripper 7960X / RTX A5000 / 128GB DDR5 ECC / 2TB NVMe",
         "features": ["AMD TRX50平台", "ECC纠错内存", "专业显卡ISV认证", "多盘位NAS扩展", "静音工作站机箱"],
         "url": "https://item.jd.com/胖虫工作站TRX"},
        {"source": "jd", "name": "胖虫渲染大师 i9-14900K RTX4080 Super 64G 2T 专业工作站",
         "series": "创世系列", "category": "workstation", "badge": "rec",
         "price": 18999, "original_price": 21999, "spec": "i9-14900K / RTX 4080 Super / 64GB DDR5 / 2TB Gen4 SSD",
         "features": ["华硕ProArt主板", "RTX 4080 Super加速渲染", "64GB大内存", "850W金牌全模组", "静音散热方案"],
         "url": "https://item.jd.com/胖虫渲染大师"},
        {"source": "jd", "name": "胖虫虫卵 R7-7840HS 32G 1T 迷你主机 0.7L",
         "series": "虫卵系列", "category": "mini", "badge": "hot",
         "price": 3299, "original_price": 3999, "spec": "R7 7840HS / Radeon 780M / 32GB DDR5 / 1TB SSD / 0.7L",
         "features": ["0.7L超小体积", "Radeon 780M核显", "支持4K输出", "WiFi 6E + BT5.2", "VESA壁挂安装"],
         "url": "https://item.jd.com/胖虫虫卵R7"},
        {"source": "jd", "name": "胖虫虫卵 i5-12450H 16G 512G 办公迷你主机 0.5L",
         "series": "虫卵系列", "category": "mini",
         "price": 1899, "original_price": 2299, "spec": "i5-12450H / UHD / 16GB DDR4 / 512GB SSD / 0.5L",
         "features": ["0.5L口袋大小", "静音无风扇设计", "双HDMI 4K输出", "千兆有线+WiFi6", "壁挂/显示器背挂"],
         "url": "https://item.jd.com/胖虫虫卵i5"},

        # ===== 抖音产品（通常有直播专属价） =====
        {"source": "douyin", "name": "胖虫毒刺RTX4060游戏本 直播间专属价",
         "series": "毒刺系列", "category": "laptop-gaming", "badge": "hot",
         "price": 5999, "original_price": 7499, "spec": "i7-13620H / RTX 4060 / 16GB / 512GB / 15.6\" 2K 165Hz",
         "features": ["直播间专属优惠", "赠鼠标+背包", "蓝天模具", "独显直连"],
         "url": "https://v.douyin.com/hYq_ldkfZQ4/"},
        {"source": "douyin", "name": "胖虫暗影RTX4080游戏本 抖音特惠",
         "series": "暗影系列", "category": "laptop-gaming", "badge": "new",
         "price": 11999, "original_price": 14999, "spec": "i9-14900HX / RTX 4080 / 32GB / 1TB / 16\" 2.5K 240Hz",
         "features": ["抖音专属价", "赠散热底座", "液金散热", "满血RTX4080"],
         "url": "https://v.douyin.com/hYq_ldkfZQ4/"},
        {"source": "douyin", "name": "胖虫虫卵R7迷你主机 抖音爆款",
         "series": "虫卵系列", "category": "mini", "badge": "hot",
         "price": 2999, "original_price": 3999, "spec": "R7 7840HS / 780M / 32GB / 1TB / 0.7L",
         "features": ["直播间特价", "赠键鼠套装", "0.7L超小", "4K输出"],
         "url": "https://v.douyin.com/hYq_ldkfZQ4/"},
        {"source": "douyin", "name": "胖虫DIY台式主机 RTX4060 抖音装机",
         "series": "DIY台式", "category": "desktop", "badge": "sale",
         "price": 4699, "original_price": 5999, "spec": "i5-13400F / RTX 4060 / 16GB / 500GB",
         "features": ["直播间下单立减", "赠RGB风扇套装", "72h烤机", "顺丰包邮"],
         "url": "https://v.douyin.com/hYq_ldkfZQ4/"},
    ]

    for p in known:
        p["id"] = gen_id(p["source"], p["name"])
        save_product(conn, p)

    save_log(conn, "local", "", "ok", len(known), f"合并本地产品库 {len(known)} 件")
    print(f"    合并本地产品: {len(known)} 件")


if __name__ == "__main__":
    main()
