import re
import json
import time
import sys
import os
from datetime import datetime


# 路径配置
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # 项目根目录
cmd_dir = os.path.dirname(__file__)  # 当前脚本目录

# PID文件路径（用于防止程序多次执行）
pid_file = os.path.join(cmd_dir, 'cmd.pid')

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
    # 程序退出时删除PID文件
    def cleanup():
        if os.path.exists(pid_file):
            try:
                os.remove(pid_file)
            except:
                pass
    
    # 添加信号处理，确保在用户中断程序时也能删除PID文件
    import signal
    def signal_handler(signum, frame):
        cleanup()
        print("\n程序已退出")
        sys.exit(0)
    
    # 注册信号处理函数
    signal.signal(signal.SIGINT, signal_handler)  # 处理Ctrl+C
    if os.name == 'posix':
        signal.signal(signal.SIGTSTP, signal_handler)  # 处理Ctrl+Z (Linux/Mac)
        signal.signal(signal.SIGTERM, signal_handler)  # 处理kill命令
    elif os.name == 'nt':  # Windows系统
        # Windows的Ctrl+Z (SIGTSTP)处理比较特殊
        # 我们可以通过捕获SIGBREAK来处理控制台中断
        signal.signal(signal.SIGBREAK, signal_handler)
    
    # 注册atexit，确保正常退出时也能清理
    import atexit
    atexit.register(cleanup)
    
    # 使用文件锁机制防止多个实例同时运行
    lock_file = None
    try:
        # 尝试打开PID文件并获取排他锁
        if os.name == 'posix':
            # Linux/Mac系统
            import fcntl
            lock_file = open(pid_file, 'a+')
            try:
                fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)  # 尝试获取排他锁，非阻塞
            except BlockingIOError:
                # 无法获取锁，说明已有进程在运行
                lock_file.close()
                print("程序已经在运行中！")
                cleanup()
                sys.exit(1)
            # 锁定成功，读取当前PID文件内容
            lock_file.seek(0)
            content = lock_file.read().strip()
            if content:
                try:
                    existing_pid = int(content)
                    if existing_pid != os.getpid():
                        # 检查已有PID是否真的在运行
                        try:
                            os.kill(existing_pid, 0)
                            print("程序已经在运行中！")
                            cleanup()
                            sys.exit(1)
                        except OSError:
                            # 进程不存在，继续执行
                            pass
                except ValueError:
                    # PID文件内容无效，继续执行
                    pass
            # 更新PID文件内容为当前进程ID
            lock_file.truncate(0)
            lock_file.write(str(os.getpid()))
            lock_file.flush()
        else:  # Windows系统
            # 尝试创建PID文件并获取独占访问权
            try:
                # 使用os.O_CREAT | os.O_EXCL标志确保只在文件不存在时创建
                import msvcrt
                fd = os.open(pid_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
                os.write(fd, str(os.getpid()).encode('utf-8'))
                os.close(fd)
            except FileExistsError:
                # 文件已存在，检查是否有进程在运行
                try:
                    with open(pid_file, 'r') as f:
                        existing_pid = int(f.read().strip())
                    import ctypes
                    kernel32 = ctypes.windll.kernel32
                    process_handle = kernel32.OpenProcess(1, False, existing_pid)
                    if process_handle != 0:
                        kernel32.CloseHandle(process_handle)
                        print("程序已经在运行中！")
                        cleanup()
                        sys.exit(1)
                    else:
                        # 进程不存在，删除旧的PID文件并创建新的
                        os.remove(pid_file)
                        with open(pid_file, 'w') as f:
                            f.write(str(os.getpid()))
                except (ValueError, IOError, OSError):
                    # PID文件无效或无法读取，删除后重新创建
                    try:
                        os.remove(pid_file)
                    except:
                        pass
                    with open(pid_file, 'w') as f:
                        f.write(str(os.getpid()))
    except Exception as e:
        print(f"检查进程状态时出错: {str(e)}")
        cleanup()
        sys.exit(1)
    
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