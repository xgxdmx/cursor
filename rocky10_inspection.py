#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rocky Linux 10 系统巡检脚本
功能：全面检查系统状态、硬件资源、网络、安全等关键指标
作者：AI Assistant
版本：1.0
"""

import os
import sys
import subprocess
import json
import datetime
import platform
import psutil
import socket
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from report_generator import ReportGenerator

class Rocky10Inspector:
    """Rocky Linux 10 系统巡检器"""
    
    def __init__(self):
        self.report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'hostname': socket.gethostname(),
            'system_info': {},
            'hardware': {},
            'network': {},
            'security': {},
            'services': {},
            'logs': {},
            'performance': {},
            'issues': []
        }
    
    def run_command(self, command: str, shell: bool = True) -> tuple:
        """执行系统命令并返回结果"""
        try:
            result = subprocess.run(
                command, 
                shell=shell, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "命令执行超时"
        except Exception as e:
            return -1, "", str(e)
    
    def check_system_info(self):
        """检查系统基本信息"""
        print("🔍 检查系统基本信息...")
        
        # 操作系统信息
        self.report['system_info'] = {
            'os': platform.system(),
            'os_version': platform.release(),
            'architecture': platform.machine(),
            'hostname': socket.gethostname(),
            'uptime': self.get_uptime(),
            'kernel': platform.release(),
            'python_version': platform.python_version()
        }
        
        # Rocky Linux 特定信息
        try:
            with open('/etc/os-release', 'r') as f:
                os_release = {}
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os_release[key] = value.strip('"')
                self.report['system_info']['os_release'] = os_release
        except Exception as e:
            self.report['issues'].append(f"无法读取系统版本信息: {e}")
    
    def get_uptime(self) -> str:
        """获取系统运行时间"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                return f"{days}天 {hours}小时 {minutes}分钟"
        except:
            return "未知"
    
    def check_hardware_resources(self):
        """检查硬件资源"""
        print("🔍 检查硬件资源...")
        
        # CPU信息
        cpu_info = {
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
        
        # 内存信息
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        memory_info = {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'free': memory.free,
            'percent': memory.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_free': swap.free,
            'swap_percent': swap.percent
        }
        
        # 磁盘信息
        disk_info = []
        for partition in psutil.disk_partitions():
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': partition_usage.total,
                    'used': partition_usage.used,
                    'free': partition_usage.free,
                    'percent': (partition_usage.used / partition_usage.total) * 100
                })
            except PermissionError:
                continue
        
        self.report['hardware'] = {
            'cpu': cpu_info,
            'memory': memory_info,
            'disk': disk_info
        }
        
        # 检查资源使用率警告
        if memory_info['percent'] > 80:
            self.report['issues'].append(f"内存使用率过高: {memory_info['percent']:.1f}%")
        
        for disk in disk_info:
            if disk['percent'] > 85:
                self.report['issues'].append(f"磁盘 {disk['device']} 使用率过高: {disk['percent']:.1f}%")
    
    def check_network_status(self):
        """检查网络状态"""
        print("🔍 检查网络状态...")
        
        # 网络接口信息
        network_info = {}
        for interface, addrs in psutil.net_if_addrs().items():
            interface_info = []
            for addr in addrs:
                if addr.family == socket.AF_INET:  # IPv4
                    interface_info.append({
                        'type': 'IPv4',
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                elif addr.family == socket.AF_INET6:  # IPv6
                    interface_info.append({
                        'type': 'IPv6',
                        'address': addr.address
                    })
            network_info[interface] = interface_info
        
        # 网络连接统计
        connections = psutil.net_connections()
        connection_stats = {
            'total': len(connections),
            'established': len([c for c in connections if c.status == 'ESTABLISHED']),
            'listening': len([c for c in connections if c.status == 'LISTEN']),
            'time_wait': len([c for c in connections if c.status == 'TIME_WAIT'])
        }
        
        # 检查常用端口
        common_ports = [22, 80, 443, 3306, 5432, 6379, 8080, 9000]
        open_ports = []
        for port in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        
        self.report['network'] = {
            'interfaces': network_info,
            'connections': connection_stats,
            'open_ports': open_ports
        }
    
    def check_services(self):
        """检查系统服务状态"""
        print("🔍 检查系统服务...")
        
        # 检查systemd服务
        services_to_check = [
            'sshd', 'firewalld', 'chronyd', 'NetworkManager',
            'rsyslog', 'systemd-resolved', 'crond'
        ]
        
        service_status = {}
        for service in services_to_check:
            code, stdout, stderr = self.run_command(f"systemctl is-active {service}")
            service_status[service] = {
                'status': stdout.strip() if code == 0 else 'unknown',
                'enabled': self.is_service_enabled(service)
            }
        
        self.report['services'] = service_status
        
        # 检查关键服务是否运行
        critical_services = ['sshd', 'chronyd']
        for service in critical_services:
            if service in service_status and service_status[service]['status'] != 'active':
                self.report['issues'].append(f"关键服务 {service} 未运行")
    
    def is_service_enabled(self, service: str) -> bool:
        """检查服务是否启用"""
        code, stdout, stderr = self.run_command(f"systemctl is-enabled {service}")
        return stdout.strip() == 'enabled'
    
    def check_security(self):
        """检查安全相关配置"""
        print("🔍 检查安全配置...")
        
        security_info = {}
        
        # 检查防火墙状态
        code, stdout, stderr = self.run_command("firewall-cmd --state")
        security_info['firewall'] = {
            'status': stdout.strip() if code == 0 else 'unknown',
            'running': code == 0
        }
        
        # 检查SELinux状态
        code, stdout, stderr = self.run_command("getenforce")
        security_info['selinux'] = {
            'status': stdout.strip() if code == 0 else 'unknown'
        }
        
        # 检查SSH配置
        ssh_config = self.check_ssh_config()
        security_info['ssh'] = ssh_config
        
        # 检查用户和权限
        security_info['users'] = self.check_user_security()
        
        self.report['security'] = security_info
    
    def check_ssh_config(self) -> Dict:
        """检查SSH配置"""
        ssh_config = {}
        try:
            with open('/etc/ssh/sshd_config', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                        elif ' ' in line:
                            parts = line.split()
                            key, value = parts[0], ' '.join(parts[1:])
                        else:
                            continue
                        ssh_config[key] = value
        except Exception as e:
            ssh_config['error'] = str(e)
        
        return ssh_config
    
    def check_user_security(self) -> Dict:
        """检查用户安全配置"""
        users_info = {}
        
        # 检查root用户
        code, stdout, stderr = self.run_command("grep '^root:' /etc/passwd")
        if code == 0:
            users_info['root_exists'] = True
        
        # 检查空密码用户
        code, stdout, stderr = self.run_command("awk -F: '($2 == \"\") {print $1}' /etc/shadow")
        if code == 0 and stdout.strip():
            users_info['empty_password_users'] = stdout.strip().split('\n')
            self.report['issues'].append("发现空密码用户")
        
        # 检查sudo权限
        code, stdout, stderr = self.run_command("grep -E '^%wheel|^%sudo' /etc/group")
        users_info['sudo_groups'] = stdout.strip().split('\n') if code == 0 else []
        
        return users_info
    
    def check_logs(self):
        """检查系统日志"""
        print("🔍 检查系统日志...")
        
        log_info = {}
        
        # 检查系统日志中的错误
        code, stdout, stderr = self.run_command("journalctl --since '1 hour ago' --priority=err --no-pager | wc -l")
        if code == 0:
            log_info['error_count_1h'] = int(stdout.strip())
        
        # 检查内核日志
        code, stdout, stderr = self.run_command("dmesg | grep -i error | wc -l")
        if code == 0:
            log_info['kernel_errors'] = int(stdout.strip())
        
        # 检查磁盘错误
        code, stdout, stderr = self.run_command("dmesg | grep -i 'i/o error' | wc -l")
        if code == 0:
            log_info['disk_io_errors'] = int(stdout.strip())
        
        self.report['logs'] = log_info
        
        # 如果有错误，添加到问题列表
        if log_info.get('error_count_1h', 0) > 10:
            self.report['issues'].append(f"最近1小时系统错误较多: {log_info['error_count_1h']}条")
        
        if log_info.get('kernel_errors', 0) > 0:
            self.report['issues'].append(f"发现内核错误: {log_info['kernel_errors']}条")
    
    def check_performance(self):
        """检查系统性能指标"""
        print("🔍 检查系统性能...")
        
        # 进程信息
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                if proc_info['cpu_percent'] > 5 or proc_info['memory_percent'] > 5:
                    processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # 按CPU使用率排序
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        performance_info = {
            'top_processes': processes[:10],  # 前10个进程
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
        
        self.report['performance'] = performance_info
    
    def generate_report(self) -> str:
        """生成巡检报告"""
        print("\n" + "="*60)
        print("🔍 Rocky Linux 10 系统巡检报告")
        print("="*60)
        
        # 系统基本信息
        print(f"\n📋 系统信息:")
        print(f"  主机名: {self.report['hostname']}")
        print(f"  操作系统: {self.report['system_info'].get('os', 'Unknown')}")
        print(f"  内核版本: {self.report['system_info'].get('kernel', 'Unknown')}")
        print(f"  系统运行时间: {self.report['system_info'].get('uptime', 'Unknown')}")
        
        # 硬件资源
        print(f"\n💻 硬件资源:")
        cpu = self.report['hardware'].get('cpu', {})
        print(f"  CPU核心数: {cpu.get('cpu_count', 'Unknown')}")
        print(f"  CPU使用率: {cpu.get('cpu_percent', 0):.1f}%")
        
        memory = self.report['hardware'].get('memory', {})
        print(f"  内存使用率: {memory.get('percent', 0):.1f}%")
        print(f"  内存总量: {memory.get('total', 0) // (1024**3):.1f} GB")
        
        # 磁盘使用情况
        print(f"\n💾 磁盘使用情况:")
        for disk in self.report['hardware'].get('disk', []):
            print(f"  {disk['device']} ({disk['mountpoint']}): {disk['percent']:.1f}%")
        
        # 网络状态
        print(f"\n🌐 网络状态:")
        connections = self.report['network'].get('connections', {})
        print(f"  总连接数: {connections.get('total', 0)}")
        print(f"  已建立连接: {connections.get('established', 0)}")
        print(f"  监听端口: {connections.get('listening', 0)}")
        
        open_ports = self.report['network'].get('open_ports', [])
        if open_ports:
            print(f"  开放端口: {', '.join(map(str, open_ports))}")
        
        # 服务状态
        print(f"\n🔧 服务状态:")
        for service, info in self.report['services'].items():
            status = info.get('status', 'unknown')
            enabled = info.get('enabled', False)
            status_icon = "✅" if status == 'active' else "❌"
            enabled_icon = "🔧" if enabled else "⏸️"
            print(f"  {service}: {status_icon} {status} {enabled_icon}")
        
        # 安全配置
        print(f"\n🔒 安全配置:")
        security = self.report['security']
        firewall_status = security.get('firewall', {}).get('status', 'unknown')
        selinux_status = security.get('selinux', {}).get('status', 'unknown')
        print(f"  防火墙: {firewall_status}")
        print(f"  SELinux: {selinux_status}")
        
        # 日志信息
        print(f"\n📝 日志信息:")
        logs = self.report['logs']
        print(f"  最近1小时错误数: {logs.get('error_count_1h', 0)}")
        print(f"  内核错误数: {logs.get('kernel_errors', 0)}")
        print(f"  磁盘I/O错误数: {logs.get('disk_io_errors', 0)}")
        
        # 性能信息
        print(f"\n⚡ 性能信息:")
        performance = self.report['performance']
        load_avg = performance.get('load_average')
        if load_avg:
            print(f"  系统负载: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
        
        top_processes = performance.get('top_processes', [])
        if top_processes:
            print(f"  高CPU使用率进程:")
            for proc in top_processes[:5]:
                print(f"    {proc['name']} (PID: {proc['pid']}): CPU {proc['cpu_percent']:.1f}%")
        
        # 问题汇总
        if self.report['issues']:
            print(f"\n⚠️  发现的问题:")
            for i, issue in enumerate(self.report['issues'], 1):
                print(f"  {i}. {issue}")
        else:
            print(f"\n✅ 未发现明显问题")
        
        print("\n" + "="*60)
        print(f"巡检完成时间: {self.report['timestamp']}")
        print("="*60)
        
        return json.dumps(self.report, indent=2, ensure_ascii=False)
    
    def save_report(self, output_formats: List[str] = None, filename_prefix: str = None):
        """保存报告到文件"""
        if output_formats is None:
            output_formats = ['json']
        
        if filename_prefix is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_prefix = f"rocky10_inspection_report_{timestamp}"
        
        saved_files = []
        
        # 保存JSON格式
        if 'json' in output_formats:
            json_filename = f"{filename_prefix}.json"
            try:
                report_json = json.dumps(self.report, indent=2, ensure_ascii=False)
                with open(json_filename, 'w', encoding='utf-8') as f:
                    f.write(report_json)
                saved_files.append(json_filename)
                print(f"📄 JSON报告已保存到: {json_filename}")
            except Exception as e:
                print(f"❌ 保存JSON报告失败: {e}")
        
        # 保存DOCX格式
        if 'docx' in output_formats:
            try:
                generator = ReportGenerator(self.report)
                docx_filename = generator.generate_docx_report(f"{filename_prefix}.docx")
                saved_files.append(docx_filename)
                print(f"📄 DOCX报告已保存到: {docx_filename}")
            except Exception as e:
                print(f"❌ 保存DOCX报告失败: {e}")
                print("请确保已安装python-docx: pip install python-docx")
        
        # 保存PDF格式
        if 'pdf' in output_formats:
            try:
                generator = ReportGenerator(self.report)
                pdf_filename = generator.generate_pdf_report(f"{filename_prefix}.pdf")
                saved_files.append(pdf_filename)
                print(f"📄 PDF报告已保存到: {pdf_filename}")
            except Exception as e:
                print(f"❌ 保存PDF报告失败: {e}")
                print("请确保已安装reportlab: pip install reportlab")
        
        return saved_files
    
    def run_inspection(self, output_formats: List[str] = None, show_console: bool = True):
        """执行完整巡检"""
        print("🚀 开始Rocky Linux 10系统巡检...")
        print(f"巡检时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        try:
            self.check_system_info()
            self.check_hardware_resources()
            self.check_network_status()
            self.check_services()
            self.check_security()
            self.check_logs()
            self.check_performance()
            
            # 生成并显示报告
            if show_console:
                self.generate_report()
            
            # 保存报告
            saved_files = self.save_report(output_formats)
            
            print("\n✅ 巡检完成!")
            if saved_files:
                print(f"📁 报告文件: {', '.join(saved_files)}")
            
        except KeyboardInterrupt:
            print("\n\n⏹️  巡检被用户中断")
        except Exception as e:
            print(f"\n❌ 巡检过程中发生错误: {e}")
            import traceback
            traceback.print_exc()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Rocky Linux 10 系统巡检工具')
    parser.add_argument('-f', '--format', nargs='+', 
                       choices=['json', 'docx', 'pdf'], 
                       default=['json'],
                       help='输出格式 (默认: json)')
    parser.add_argument('--no-console', action='store_true',
                       help='不显示控制台输出，仅生成文件')
    parser.add_argument('--prefix', type=str,
                       help='输出文件名前缀')
    
    args = parser.parse_args()
    
    # 检查是否为root用户
    if os.geteuid() != 0:
        print("⚠️  警告: 建议以root用户运行此脚本以获得完整信息")
        print("某些检查可能需要管理员权限")
        print()
    
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
        sys.exit(1)
    
    # 创建巡检器并运行
    inspector = Rocky10Inspector()
    inspector.run_inspection(
        output_formats=args.format,
        show_console=not args.no_console
    )

if __name__ == "__main__":
    main()