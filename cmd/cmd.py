import re
import json
import time
import subprocess
from datetime import datetime  # 添加这个导入
import os

def parse_access_log(log_file_path):
    keywords = ['01.ssh', '02.website']
    tunnel_info = {}
    
    try:
        with open(log_file_path, 'r') as file:
            for line in file:
                for keyword in keywords:
                    if keyword in line:
                        url_pattern = r'(tcp://[^\s]+|http://[^\s]+|https://[^\s]+)'
                        matches = re.findall(url_pattern, line)
                        if matches:
                            tunnel_info[keyword] = matches[-1]
    except FileNotFoundError:
        print(f"日志文件 {log_file_path} 未找到")
        return {}
    
    return tunnel_info

def write_tunnel_info(tunnel_info, json_file_path):
    existing_info = {}
    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, 'r') as file:
                existing_info = json.load(file)
        except:
            existing_info = {}
    
    if tunnel_info != existing_info:
        with open(json_file_path, 'w') as file:
            json.dump(tunnel_info, file, indent=4)
        print(f"隧道信息已更新 {json_file_path}")
        return True
    else:
        print("隧道信息未变化，无需更新")
        return False

def git_push():
    try:
        # 1. 添加所有更改
        subprocess.run(['git', 'add', '-A'], check=True)
        
        # 2. 检查是否有实际更改
        status = subprocess.run(['git', 'status', '--porcelain'], 
                                stdout=subprocess.PIPE, 
                                text=True, 
                                check=True)
        
        if status.stdout.strip():
            # 3. 提交更改（添加了datetime导入）
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"自动更新隧道信息 {timestamp}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            print("提交成功")
        else:
            print("没有需要提交的更改")
            return True  # 没有更改但操作成功
        
        # 4. 尝试普通推送
        push_result = subprocess.run(['git', 'push', 'origin', 'master'], 
                                     capture_output=True,
                                     text=True)
        
        if push_result.returncode == 0:
            print("推送成功")
            return True
            
        # 5. 处理推送失败情况
        if "rejected" in push_result.stderr:
            print("推送被拒绝，执行强制推送")
            subprocess.run(['git', 'push', '-f', 'origin', 'master'], check=True)
            print("强制推送成功")
            return True
        else:
            # 抛出其他类型的错误
            push_result.check_returncode()
            
    except subprocess.CalledProcessError as e:
        print(f"Git操作失败: {e}")
        return False

def main():
    log_file_path = '/var/log/cpolar/access.log'
    json_file_path = '/home/pi/zhengxuqiao.github.io/zhengxuqiao.github.io/tunnel.json'
    
    tunnel_info = parse_access_log(log_file_path)
    
    if tunnel_info:
        if write_tunnel_info(tunnel_info, json_file_path):
            git_push()
    else:
        print("未找到隧道信息")

if __name__ == "__main__":
    while True:
        main()
        time.sleep(60)