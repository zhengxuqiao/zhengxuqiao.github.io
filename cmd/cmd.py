import re
import json
import time
import subprocess
from datetime import datetime
import os

def parse_access_log(log_file_path):
    # 定义要查找的关键字
    keywords = ['01.ssh', '02.website']
    tunnel_info = {}
    
    try:
        with open(log_file_path, 'r') as file:
            for line in file:
                for keyword in keywords:
                    if keyword in line:
                        # 使用正则表达式匹配URL
                        url_pattern = r'(tcp://[^\s]+|http://[^\s]+|https://[^\s]+)'
                        matches = re.findall(url_pattern, line)
                        if matches:
                            # 如果有多个匹配，保留最后一个
                            tunnel_info[keyword] = matches[-1]
    except FileNotFoundError:
        print(f"日志文件 {log_file_path} 未找到")
        return {}
    
    return tunnel_info

def write_tunnel_info(tunnel_info, json_file_path):
    try:
        # 清理转义字符并构造正确的JSON
        cleaned_info = {}
        for key, value in tunnel_info.items():
            # 移除多余的转义字符
            cleaned_value = value.replace('\\', '')
            # 尝试解析为JSON对象
            try:
                # 查找第一个完整的URL
                url_match = re.search(r'(tcp://[^\s\"]+|http://[^\s\"]+|https://[^\s\"]+)', cleaned_value)
                if url_match:
                    cleaned_info[key] = url_match.group(1)
                else:
                    cleaned_info[key] = cleaned_value
            except:
                # 如果解析失败，直接使用清理后的字符串
                url_match = re.search(r'(tcp://[^\s\"]+|http://[^\s\"]+|https://[^\s\"]+)', cleaned_value)
                if url_match:
                    cleaned_info[key] = url_match.group(1)
                else:
                    cleaned_info[key] = cleaned_value
        
        with open(json_file_path, 'w') as file:
            json.dump(cleaned_info, file, indent=4)
        print(f"隧道信息已写入 {json_file_path}")
    except Exception as e:
        print(f"写入文件时出错: {e}")

def commit_and_push():
    try:
        # 执行 upload-cmd.sh 脚本中的命令
        subprocess.run(['git', 'add', '-A'], check=True)
        subprocess.run(['git', 'commit', '-m', 'test'], check=True)
        subprocess.run(['git', 'push', '-u', 'origin', 'master', '-f'], check=True)
        
        print("代码已成功提交并推送到GitHub")
    except subprocess.CalledProcessError as e:
        print(f"Git操作失败: {e}")

def main():
    # 日志文件和JSON文件路径

    # log_file_path  = '/home/user/Desktop/zhengxuqiao.github.io-master/cmd/access.log'
    # json_file_path = '/home/user/Desktop/zhengxuqiao.github.io-master/tunnel.json'

    log_file_path = '/var/log/cpolar/access.log'
    json_file_path = '/home/pi/zhengxuqiao.github.io/zhengxuqiao.github.io/tunnel.json'
    
    # 解析日志文件
    tunnel_info = parse_access_log(log_file_path)
    
    # 如果解析到信息，则写入JSON文件
    if tunnel_info:
        write_tunnel_info(tunnel_info, json_file_path)
        commit_and_push()
    else:
        print("未找到隧道信息")

if __name__ == "__main__":
    # 每分钟执行一次
    while True:
        main()
        time.sleep(60)