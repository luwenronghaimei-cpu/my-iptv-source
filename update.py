import requests
import time

# 目标数据源（常见的开源直播 m3u 聚合项目）
# 目标数据源：替换为更新更频繁的综合源
SOURCES = [
    "https://live.fanmingming.com/tv/m3u/global.m3u",
    "https://raw.githubusercontent.com/YueChan/Live/main/IPTV.m3u",
    "https://raw.githubusercontent.com/vbsky/TVBox/main/tv/iptv.m3u"
]

# 需要提取的频道关键词
KEYWORDS = ["无线新闻", "TVB News"]

def fetch_and_parse(sources, keywords):
    results = []
    for url in sources:
        try:
            # 加上 headers 防止部分服务器拒绝请求
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                lines = response.text.splitlines()
                # 遍历 m3u 内容寻找关键词
                for i in range(len(lines)):
                    if lines[i].startswith("#EXTINF"):
                        if any(kw.lower() in lines[i].lower() for kw in keywords):
                            # 确保下一行是有效的 http 视频流链接
                            if i + 1 < len(lines) and lines[i+1].startswith("http"):
                                # 提取频道名称（通常在逗号后）
                                channel_name = lines[i].split(",")[-1].strip()
                                stream_url = lines[i+1].strip()
                                results.append((channel_name, stream_url))
        except Exception as e:
            print(f"抓取 {url} 失败: {e}")
    return results

def save_to_txt(data, filename="tvb_live.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("香港频道,#genre#\n")
        seen_urls = set()
        for name, url in data:
            if url not in seen_urls:
                f.write(f"{name},{url}\n")
                seen_urls.add(url) # 去重处理
    print(f"更新完成，已保存至 {filename}")

if __name__ == "__main__":
    print("开始获取最新源...")
    live_data = fetch_and_parse(SOURCES, KEYWORDS)
    if live_data:
        save_to_txt(live_data)
    else:
        print("未抓取到匹配的频道源。")
