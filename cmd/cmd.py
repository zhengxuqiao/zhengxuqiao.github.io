import re
import json
import time
from datetime import datetime


def extract_latest_urls(log_file):
    urls = {}
    
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 从后往前遍历日志，找到最新的网址信息
    for line in reversed(lines):
        # 匹配Tunnel established行
        # 正则表达式解析：
        # - Tunnel established at 匹配日志中的固定文本
        # - (tcp|http|https) 捕获协议类型
        # - :// 匹配URL分隔符
        # - ([^\s]+) 匹配任意非空白字符（URL主体）
        tunnel_match = re.search(r'Tunnel established at (tcp|http|https)://([^\s]+)', line)
        if tunnel_match:
            protocol = tunnel_match.group(1)
            url = f"{protocol}://{tunnel_match.group(2)}"
            # 去除任何可能的引号
            url = url.rstrip('"')
            
            # 确定隧道名称
            if 'ssh' in line.lower() or 'tcp' in protocol:
                tunnel_name = 'ssh'
            elif 'website' in line.lower() or 'http' in protocol:
                tunnel_name = 'website'
            else:
                continue
            
            # 如果已经有了该隧道的最新信息，跳过
            if tunnel_name not in urls:
                urls[tunnel_name] = url
            
            # 如果已经找到了所有隧道，提前退出
            if len(urls) >= 2:  # ssh和website
                break
        
        # 匹配JSON消息中的Url字段
        # 正则表达式解析：
        # - "Url":" 匹配JSON中的"Url"字段
        # - ((tcp|http|https)://[^"]+) 匹配URL部分
        #   - (tcp|http|https) 捕获协议类型
        #   - :// 匹配URL分隔符
        #   - [^"]+ 匹配任意非引号字符（URL主体）
        # - " 匹配JSON字段结束引号
        json_url_match = re.search(r'"Url":"((tcp|http|https)://[^"]+)"', line)
        if json_url_match:
            # 从匹配结果中提取完整URL（组1）和协议类型（组2）
            url = json_url_match.group(1)
            protocol = json_url_match.group(2)
            # 去除URL中可能存在的尾部引号
            url = url.rstrip('"')
            
            # 根据日志内容和协议类型确定隧道名称
            if 'ssh' in line.lower() or 'tcp' in protocol:
                # SSH隧道通常使用TCP协议
                tunnel_name = 'ssh'
            elif 'website' in line.lower() or 'http' in protocol:
                # 网站隧道使用HTTP或HTTPS协议
                tunnel_name = 'website'
            else:
                # 其他类型的隧道暂时不处理
                continue
            
            # 如果已经有了该隧道的最新信息，跳过
            if tunnel_name not in urls:
                urls[tunnel_name] = url
            
            # 如果已经找到了所有隧道，提前退出
            if len(urls) >= 2:  # ssh和website
                break
    
    return urls


def write_to_tunnel_json(urls, json_file):
    # 按照tunnel.json的格式组织数据
    tunnel_data = {
        "01.ssh": urls.get("ssh", ""),
        "02.website": urls.get("website", "")
    }
    
    # 写入JSON文件
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(tunnel_data, f, indent=4)
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 已更新tunnel.json")
    print(f'SSH隧道: {urls.get("ssh", "未找到")}')
    print(f'Website隧道: {urls.get("website", "未找到")}')


import subprocess

def main():
    log_file = "/var/log/cpolar/access.log"
    json_file = "./../tunnel.json"
    upload_script = "./../upload-cmd.sh"
    
    while True:
        try:
            urls = extract_latest_urls(log_file)
            write_to_tunnel_json(urls, json_file)
            
            # 执行upload-cmd.sh脚本
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行upload-cmd.sh脚本")
            result = subprocess.run(["bash", upload_script], capture_output=True, text=True, cwd="./../")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] upload-cmd.sh脚本执行结果:")
            print(f"stdout: {result.stdout}")
            if result.stderr:
                print(f"stderr: {result.stderr}")
            print(f"返回码: {result.returncode}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 错误: {str(e)}")
        
        # 每分钟执行一次
        time.sleep(60)


if __name__ == "__main__":
    main()