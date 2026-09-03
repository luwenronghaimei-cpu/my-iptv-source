import requests

# 1. 在这里填入你所有的源地址（无论它是 TXT 还是 M3U 格式，都可以混在一起写）
SOURCES = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/hk.m3u",
    "https://iptv.yang-1989.xyz/playlist.m3u",
    "https://raw.githubusercontent.com/YanG-1989/m3u/refs/heads/main/Migu.m3u"

]

# 2. 在这里定义你【真正想要保留】的分类和提取关键词。
# 逻辑：代码查找到频道名包含这些关键词时，就会把它收录进来。不在这里面的频道一律丢弃。
CATEGORIES = {
    "央视频道": ["cctv", "央视", "cctv1", "cctv5", "cctv13"],
    "广东频道": ["广东", "南方卫视", "珠江", "大湾区"],
    "港澳频道": ["无线新闻", "無綫新聞", "tvb", "凤凰"]
}

def fetch_and_merge():
    # 初始化结果字典
    results = {cat: [] for cat in CATEGORIES}
    # 用于全局去重，防止多个源里有完全一样的播放链接
    seen_urls = set()

    for url in SOURCES:
        print(f"正在拉取: {url}")
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                lines = response.text.replace('\r', '').split('\n')
                
                for i in range(len(lines)):
                    line = lines[i].strip()
                    if not line:
                        continue
                        
                    channel_name = ""
                    stream_url = ""

                    # 情况 A：兼容 M3U 格式的解析
                    if line.startswith("#EXTINF"):
                        if i + 1 < len(lines) and (lines[i+1].startswith("http") or lines[i+1].startswith("rtmp")):
                            channel_name = line.split(",")[-1].strip()
                            stream_url = lines[i+1].strip()

                    # 情况 B：兼容 TXT 格式的解析 (名称,http://...)，且排除掉 #genre# 分类行
                    elif "," in line and "#genre#" not in line:
                        parts = line.split(",", 1)
                        if len(parts) == 2 and (parts[1].startswith("http") or parts[1].startswith("rtmp")):
                            channel_name = parts[0].strip()
                            stream_url = parts[1].strip()

                    # 如果成功提取到了频道名和链接
                    if channel_name and stream_url:
                        # 检查链接是否已经存在，避免重复频道
                        if stream_url in seen_urls:
                            continue
                            
                        # 遍历我们想要的分类，看看这个频道名是否命中关键词
                        line_lower = channel_name.lower()
                        for cat_name, keywords in CATEGORIES.items():
                            if any(kw.lower() in line_lower for kw in keywords):
                                results[cat_name].append((channel_name, stream_url))
                                seen_urls.add(stream_url)
                                break # 命中一个分类后就跳出，防止重复归类
                                
            else:
                print(f"  [拉取失败] 状态码: {response.status_code}")
        except Exception as e:
            print(f"  [请求异常] {e}")

    # 3. 将提纯和合并后的数据写入最终的 TXT 文件
    filename = "my_custom_live.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for cat_name, channels in results.items():
            # 只有当这个分类下抓取到了频道，才生成这个分类的表头
            if channels:
                f.write(f"{cat_name},#genre#\n")
                for name, stream_url in channels:
                    f.write(f"{name},{stream_url}\n")
                    
    print(f"\n合并与提取完成，已成功生成 {filename}")

if __name__ == "__main__":
    fetch_and_merge()
