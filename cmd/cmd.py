import re
import json
import time
import sys
import os
from datetime import datetime


# 路径配置
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # 项目根目录
cmd_dir = os.path.dirname(__file__)  # 当前脚本目录

# 不使用PID文件，改用Linux服务管理

# 日志文件路径
cpolar_log_file = '/var/log/cpolar/access.log'  # cpolar日志文件路径
app_log_dir = os.path.join(cmd_dir, 'log')  # 应用日志目录
app_log_file = os.path.join(app_log_dir, 'log.txt')  # 应用日志文件

# JSON文件路径
tunnel_json_file = os.path.join(base_dir, 'tunnel.json')  # 隧道配置JSON文件

# 脚本路径
upload_script_file = os.path.join(base_dir, 'upload-cmd.sh')  # 上传脚本路径

# 日志配置
# LOG_ENABLED = True  # 设置为False可关闭日志文件写入功能
LOG_ENABLED = False  # 设置为False可关闭日志文件写入功能

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

def log_output(message):
    """将消息同时输出到控制台和日志文件"""
    print(message)
    # 写入日志文件（如果启用）
    if LOG_ENABLED:
        with open(app_log_file, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")


def write_to_tunnel_json(urls, json_file):
    # 按照tunnel.json的格式组织数据
    tunnel_data = {
        "01.ssh": urls.get("ssh", ""),
        "02.website": urls.get("website", "")
    }
    
    # 写入JSON文件
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(tunnel_data, f, indent=4)
    
    log_output(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 已更新tunnel.json")
    log_output(f'SSH隧道: {urls.get("ssh", "未找到")}')
    log_output(f'Website隧道: {urls.get("website", "未找到")}')


def main():
    
    log_file = cpolar_log_file
    json_file = tunnel_json_file
    upload_script = upload_script_file
    
    # 确保log目录存在
    os.makedirs(app_log_dir, exist_ok=True)
    
    try:
        while True:
            try:
                urls = extract_latest_urls(log_file)
                write_to_tunnel_json(urls, json_file)
                
                # 执行upload-cmd.sh脚本
                log_output(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行upload-cmd.sh脚本")
                result = subprocess.run(["bash", upload_script], capture_output=True, text=True, cwd=base_dir)
                log_output(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] upload-cmd.sh脚本执行结果:")
                log_output(f"stdout: {result.stdout}")
                if result.stderr:
                    log_output(f"stderr: {result.stderr}")
                log_output(f"返回码: {result.returncode}")
            except Exception as e:
                log_output(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 错误: {str(e)}")
            
            # 每分钟执行一次
            time.sleep(60)
    except Exception as e:
        # 捕获任何未处理的异常
        log_output(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 严重错误: {str(e)}")
        cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()