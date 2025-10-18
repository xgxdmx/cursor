#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rocky Linux 10 快速巡检脚本
简化版本，专注于关键指标检查
"""

import os
import subprocess
import json
import datetime
import psutil
import socket
import argparse
from report_generator import ReportGenerator

def run_command(cmd):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except:
        return False, "", "命令执行失败"

def check_system():
    """检查系统基本信息"""
    print("🔍 系统信息检查...")
    
    # 系统信息
    hostname = socket.gethostname()
    uptime = "未知"
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            uptime = f"{days}天{hours}小时"
    except:
        pass
    
    # 内存使用率
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    # CPU使用率
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # 磁盘使用率
    disk_usage = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            percent = (usage.used / usage.total) * 100
            disk_usage.append(f"{partition.mountpoint}: {percent:.1f}%")
        except:
            continue
    
    return {
        'hostname': hostname,
        'uptime': uptime,
        'memory_percent': memory_percent,
        'cpu_percent': cpu_percent,
        'disk_usage': disk_usage
    }

def check_services():
    """检查关键服务"""
    print("🔍 服务状态检查...")
    
    services = ['sshd', 'firewalld', 'chronyd', 'NetworkManager']
    service_status = {}
    
    for service in services:
        success, stdout, stderr = run_command(f"systemctl is-active {service}")
        if success:
            service_status[service] = stdout
        else:
            service_status[service] = "inactive"
    
    return service_status

def check_network():
    """检查网络状态"""
    print("🔍 网络状态检查...")
    
    # 检查常用端口
    ports = [22, 80, 443, 3306, 5432]
    open_ports = []
    
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    
    return open_ports

def check_security():
    """检查安全配置"""
    print("🔍 安全配置检查...")
    
    security = {}
    
    # 防火墙状态
    success, stdout, stderr = run_command("firewall-cmd --state")
    security['firewall'] = stdout if success else "unknown"
    
    # SELinux状态
    success, stdout, stderr = run_command("getenforce")
    security['selinux'] = stdout if success else "unknown"
    
    return security

def generate_report(system_info, services, network, security, output_formats=None, show_console=True):
    """生成巡检报告"""
    # 构建报告数据
    report_data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'hostname': system_info['hostname'],
        'system_info': {
            'hostname': system_info['hostname'],
            'uptime': system_info['uptime'],
            'cpu_percent': system_info['cpu_percent'],
            'memory_percent': system_info['memory_percent'],
            'os': 'Linux',
            'kernel': 'Unknown',
            'architecture': 'Unknown',
            'python_version': 'Unknown'
        },
        'hardware': {
            'cpu': {
                'cpu_percent': system_info['cpu_percent'],
                'cpu_count': 0,
                'load_avg': None
            },
            'memory': {
                'percent': system_info['memory_percent'],
                'total': 0,
                'used': 0,
                'available': 0,
                'swap_percent': 0
            },
            'disk': []
        },
        'network': {
            'open_ports': network,
            'connections': {
                'total': 0,
                'established': 0,
                'listening': 0,
                'time_wait': 0
            }
        },
        'services': {service: {'status': status, 'enabled': False} for service, status in services.items()},
        'security': {
            'firewall': {'status': security.get('firewall', 'unknown')},
            'selinux': {'status': security.get('selinux', 'unknown')}
        },
        'logs': {
            'error_count_1h': 0,
            'kernel_errors': 0,
            'disk_io_errors': 0
        },
        'performance': {
            'top_processes': [],
            'load_average': None
        },
        'issues': []
    }
    
    # 问题检查
    issues = []
    if system_info['memory_percent'] > 80:
        issues.append(f"内存使用率过高: {system_info['memory_percent']:.1f}%")
    
    if system_info['cpu_percent'] > 80:
        issues.append(f"CPU使用率过高: {system_info['cpu_percent']:.1f}%")
    
    critical_services = ['sshd', 'chronyd']
    for service in critical_services:
        if services.get(service) != 'active':
            issues.append(f"关键服务 {service} 未运行")
    
    report_data['issues'] = issues
    
    if show_console:
        print("\n" + "="*50)
        print("🔍 Rocky Linux 10 快速巡检报告")
        print("="*50)
        
        print(f"\n📋 系统概览:")
        print(f"  主机名: {system_info['hostname']}")
        print(f"  运行时间: {system_info['uptime']}")
        print(f"  CPU使用率: {system_info['cpu_percent']:.1f}%")
        print(f"  内存使用率: {system_info['memory_percent']:.1f}%")
        
        print(f"\n💾 磁盘使用:")
        for disk in system_info['disk_usage']:
            print(f"  {disk}")
        
        print(f"\n🔧 服务状态:")
        for service, status in services.items():
            icon = "✅" if status == "active" else "❌"
            print(f"  {service}: {icon} {status}")
        
        print(f"\n🌐 网络端口:")
        if network:
            print(f"  开放端口: {', '.join(map(str, network))}")
        else:
            print("  未检测到开放端口")
        
        print(f"\n🔒 安全配置:")
        print(f"  防火墙: {security['firewall']}")
        print(f"  SELinux: {security['selinux']}")
        
        if issues:
            print(f"\n⚠️  发现问题:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        else:
            print(f"\n✅ 系统状态正常")
        
        print("\n" + "="*50)
        print(f"巡检时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
    
    # 保存文件
    if output_formats:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_prefix = f"rocky10_quick_inspection_{timestamp}"
        saved_files = []
        
        # 保存JSON格式
        if 'json' in output_formats:
            json_filename = f"{filename_prefix}.json"
            try:
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(report_data, f, indent=2, ensure_ascii=False)
                saved_files.append(json_filename)
                print(f"📄 JSON报告已保存到: {json_filename}")
            except Exception as e:
                print(f"❌ 保存JSON报告失败: {e}")
        
        # 保存DOCX格式
        if 'docx' in output_formats:
            try:
                generator = ReportGenerator(report_data)
                docx_filename = generator.generate_docx_report(f"{filename_prefix}.docx")
                saved_files.append(docx_filename)
                print(f"📄 DOCX报告已保存到: {docx_filename}")
            except Exception as e:
                print(f"❌ 保存DOCX报告失败: {e}")
        
        # 保存PDF格式
        if 'pdf' in output_formats:
            try:
                generator = ReportGenerator(report_data)
                pdf_filename = generator.generate_pdf_report(f"{filename_prefix}.pdf")
                saved_files.append(pdf_filename)
                print(f"📄 PDF报告已保存到: {pdf_filename}")
            except Exception as e:
                print(f"❌ 保存PDF报告失败: {e}")
        
        return saved_files
    
    return []

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Rocky Linux 10 快速巡检工具')
    parser.add_argument('-f', '--format', nargs='+', 
                       choices=['json', 'docx', 'pdf'], 
                       default=['json'],
                       help='输出格式 (默认: json)')
    parser.add_argument('--no-console', action='store_true',
                       help='不显示控制台输出，仅生成文件')
    parser.add_argument('--prefix', type=str,
                       help='输出文件名前缀')
    
    args = parser.parse_args()
    
    print("🚀 Rocky Linux 10 快速巡检开始...")
    
    # 检查依赖
    missing_deps = []
    try:
        import psutil
    except ImportError:
        missing_deps.append('psutil')
    
    # 检查可选依赖
    if 'docx' in args.format:
        try:
            import docx
        except ImportError:
            missing_deps.append('python-docx')
    
    if 'pdf' in args.format:
        try:
            import reportlab
        except ImportError:
            missing_deps.append('reportlab')
    
    if missing_deps:
        print(f"❌ 缺少依赖包: {', '.join(missing_deps)}")
        print("请运行: pip install -r requirements.txt")
        return
    
    # 执行检查
    system_info = check_system()
    services = check_services()
    network = check_network()
    security = check_security()
    
    # 生成报告
    saved_files = generate_report(
        system_info, services, network, security,
        output_formats=args.format,
        show_console=not args.no_console
    )
    
    print("\n✅ 快速巡检完成!")
    if saved_files:
        print(f"📁 报告文件: {', '.join(saved_files)}")

if __name__ == "__main__":
    main()