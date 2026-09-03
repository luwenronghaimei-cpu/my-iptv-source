import requests

# 1. 在这里填入你所有的源地址（无论它是 TXT 还是 M3U 格式，都可以混在一起写）
SOURCES = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/hk.m3u",
    "https://iptv.yang-1989.xyz/playlist.m3u",
    "https://live.445569.xyz/live.m3u",
    "https://raw.githubusercontent.com/YanG-1989/m3u/refs/heads/main/Migu.m3u"

]

# 2. 定义你【需要单独提取】的分类和关键词
CATEGORIES = {
    "央视频道": ["cctv", "央视", "cctv1", "cctv5", "cctv13"],
    "广东频道": ["广东", "南方卫视", "珠江", "大湾区"],
    "港澳频道": ["无线新闻", "無綫新聞", "tvb", "凤凰"]
}

def process_sources():
    # 用于存储原封不动拼接的全文
    merged_raw_content = ""
    # 用于存储过滤提取后的频道
    extracted_results = {cat: [] for cat in CATEGORIES}
    seen_urls = set()

    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in SOURCES:
        print(f"正在拉取: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                raw_text = response.text
                
                # 【任务一】：原封不动拼接内容（强制加换行符防止首尾粘连）
                merged_raw_content += raw_text + "\n\n"

                # 【任务二】：解析文本并提取指定的频道
                lines = raw_text.replace('\r', '').split('\n')
                for i in range(len(lines)):
                    line = lines[i].strip()
                    if not line:
                        continue
                        
                    channel_name = ""
                    stream_url = ""

                    # 兼容 M3U 和 TXT 格式的解析
                    if line.startswith("#EXTINF"):
                        if i + 1 < len(lines) and (lines[i+1].startswith("http") or lines[i+1].startswith("rtmp")):
                            channel_name = line.split(",")[-1].strip()
                            stream_url = lines[i+1].strip()
                    elif "," in line and "#genre#" not in line:
                        parts = line.split(",", 1)
                        if len(parts) == 2 and (parts[1].startswith("http") or parts[1].startswith("rtmp")):
                            channel_name = parts[0].strip()
                            stream_url = parts[1].strip()

                    # 过滤并分配到指定分类
                    if channel_name and stream_url:
                        if stream_url in seen_urls:
                            continue # 去重
                            
                        line_lower = channel_name.lower()
                        for cat_name, keywords in CATEGORIES.items():
                            if any(kw.lower() in line_lower for kw in keywords):
                                extracted_results[cat_name].append((channel_name, stream_url))
                                seen_urls.add(stream_url)
                                break
            else:
                print(f"  [拉取失败] 状态码: {response.status_code}")
        except Exception as e:
            print(f"  [请求异常] {e}")

    # --- 输出文件 1：全量拼接文件 ---
    file1_name = "merged_all.txt"
    with open(file1_name, "w", encoding="utf-8") as f1:
        f1.write(merged_raw_content)
    print(f"任务一完成：已生成全量合并文件 {file1_name}")

    # --- 输出文件 2：精简提取文件 ---
    file2_name = "extracted_live.txt"
    with open(file2_name, "w", encoding="utf-8") as f2:
        for cat_name, channels in extracted_results.items():
            if channels:
                f2.write(f"{cat_name},#genre#\n")
                for name, stream_url in channels:
                    f2.write(f"{name},{stream_url}\n")
    print(f"任务二完成：已生成精简提取文件 {file2_name}")

if __name__ == "__main__":
    process_sources()
