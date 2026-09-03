import requests
import re

# 1. 在这里填入你所有的源地址（无论它是 TXT 还是 M3U 格式，都可以混在一起写）
SOURCES = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/hk.m3u",
    "https://iptv.yang-1989.xyz/playlist.m3u",
    "https://live.445569.xyz/live.m3u",
    "https://raw.githubusercontent.com/YanG-1989/m3u/refs/heads/main/Migu.m3u"

]

# 2. 定义【需要单独提取】的分类和关键词（已加入咪咕频道）
CATEGORIES = {
    "央视频道": ["cctv", "央视", "cctv1", "cctv5", "cctv13"],
    "广东频道": ["广东", "南方卫视", "珠江", "大湾区"],
    "港澳频道": ["无线新闻", "無綫新聞", "tvb", "凤凰"],
    "咪咕频道": ["咪咕", "migu", "睛彩"]
}

def process_sources():
    # 用于存储全量频道，格式为 (分组名, 频道名, 播放链接)
    all_channels = []
    # 用于存储过滤提取后的频道
    extracted_results = {cat: [] for cat in CATEGORIES}
    
    seen_urls_all = set()
    seen_urls_ext = set()

    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in SOURCES:
        print(f"正在拉取: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                lines = response.text.replace('\r', '').split('\n')
                
                current_group = "默认分类"
                i = 0
                
                while i < len(lines):
                    line = lines[i].strip()
                    if not line:
                        i += 1
                        continue
                        
                    channel_name = ""
                    stream_url = ""
                    
                    # 场景 A：解析 M3U 格式
                    if line.startswith("#EXTINF"):
                        # 尝试提取自带的 group-title 分组信息
                        group_match = re.search(r'group-title="([^"]+)"', line)
                        if group_match:
                            current_group = group_match.group(1)
                        else:
                            current_group = "未分类"
                            
                        channel_name = line.split(",")[-1].strip()
                        
                        # 检查下一行是否为链接
                        if i + 1 < len(lines) and (lines[i+1].startswith("http") or lines[i+1].startswith("rtmp")):
                            stream_url = lines[i+1].strip()
                            i += 1 # 成功读取链接，跳过下一行
                            
                    # 场景 B：解析 TXT 格式
                    elif "," in line:
                        if "#genre#" in line:
                            current_group = line.split(",")[0].strip()
                        else:
                            parts = line.split(",", 1)
                            if len(parts) == 2 and (parts[1].startswith("http") or parts[1].startswith("rtmp")):
                                channel_name = parts[0].strip()
                                stream_url = parts[1].strip()

                    # 分配处理提取到的有效频道
                    if channel_name and stream_url:
                        # 【任务一】：放入全量列表（去重）
                        if stream_url not in seen_urls_all:
                            all_channels.append((current_group, channel_name, stream_url))
                            seen_urls_all.add(stream_url)
                            
                        # 【任务二】：过滤并放入精简列表（去重）
                        if stream_url not in seen_urls_ext:
                            line_lower = channel_name.lower()
                            for cat_name, keywords in CATEGORIES.items():
                                if any(kw.lower() in line_lower for kw in keywords):
                                    extracted_results[cat_name].append((channel_name, stream_url))
                                    seen_urls_ext.add(stream_url)
                                    break
                    i += 1
            else:
                print(f"  [拉取失败] 状态码: {response.status_code}")
        except Exception as e:
            print(f"  [请求异常] {e}")

    # --- 输出文件 1：全量合并文件（标准 M3U 格式） ---
    file1_name = "merged_all.m3u"
    with open(file1_name, "w", encoding="utf-8") as f1:
        f1.write("#EXTM3U\n")
        for group, name, url in all_channels:
            # 统一输出带 group-title 标签的 M3U 格式，TiviMate 等软件能自动识别分类
            f1.write(f'#EXTINF:-1 tvg-name="{name}" group-title="{group}",{name}\n')
            f1.write(f"{url}\n")
    print(f"任务一完成：已生成全量 M3U 文件 {file1_name}")

    # --- 输出文件 2：精简提取文件（TXT 格式，适合 DIYP/TVBox） ---
    file2_name = "extracted_live.txt"
    with open(file2_name, "w", encoding="utf-8") as f2:
        for cat_name, channels in extracted_results.items():
            if channels:
                f2.write(f"{cat_name},#genre#\n")
                for name, url in channels:
                    f2.write(f"{name},{url}\n")
    print(f"任务二完成：已生成精简 TXT 文件 {file2_name}")

if __name__ == "__main__":
    process_sources()

if __name__ == "__main__":
    process_sources()
