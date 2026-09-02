import requests

SOURCES = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/hk.m3u",
    "https://iptv.yang-1989.xyz/playlist.m3u",
    "https://live.445569.xyz/live.m3u",
    "https://raw.githubusercontent.com/YanG-1989/m3u/refs/heads/main/Migu.m3u"
]

# 扩大关键词范围，兼容繁体和英文大小写
CATEGORIES = {
    "港澳频道": ["无线新闻", "無綫新聞", "tvb", "明珠", "翡翠", "NOW","凤凰"],
    "央视频道": ["cctv1", "cctv-1", "cctv13", "cctv-13", "cctv5", "cctv-5" ],
    "咪咕频道": ["睛彩", "咪咕体育"],
    "广东频道": ["广东珠江", "广东"]
}

def fetch_and_parse():
    results = {cat: [] for cat in CATEGORIES}
    
    # 强制塞入一个备用直连源。无论抓取是否成功都会生成 txt 文件，防止电视端报错接口为空
    results["港澳频道"].append(("无线新闻台(保底)", "http://r.jdshipin.com/CkuBd"))

    for url in SOURCES:
        print(f"正在请求: {url}")
        try:
            # 增加标准浏览器请求头，降低被防爬虫策略拦截的概率
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                lines = response.text.splitlines()
                for i, line in enumerate(lines):
                    if line.startswith("#EXTINF"):
                        line_lower = line.lower()
                        # 验证下一行是有效的视频流格式
                        if i + 1 < len(lines) and (lines[i+1].startswith("http") or lines[i+1].startswith("rtmp")):
                            channel_name = line.split(",")[-1].strip()
                            stream_url = lines[i+1].strip()

                            for cat_name, keywords in CATEGORIES.items():
                                if any(kw in line_lower for kw in keywords):
                                    results[cat_name].append((channel_name, stream_url))
                                    print(f"  [成功匹配] {channel_name}")
                                    break
            else:
                print(f"  [请求失败] 状态码: {response.status_code}")
        except Exception as e:
            print(f"  [请求异常] {e}")

    # 写入文件（统一命名为 tvb_live.txt）
    filename = "tvb_live.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for cat_name, channels in results.items():
            if channels:
                f.write(f"{cat_name},#genre#\n")
                seen = set()
                for name, url in channels:
                    if url not in seen:
                        f.write(f"{name},{url}\n")
                        seen.add(url)
                        
    print(f"\n运行结束，已成功生成 {filename}")

if __name__ == "__main__":
    fetch_and_parse()
