#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rocky Linux 10 巡检脚本使用示例
演示如何使用不同的输出格式和选项
"""

import subprocess
import os
import sys

def run_command(cmd):
    """执行命令并显示输出"""
    print(f"执行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ 命令执行成功")
        if result.stdout:
            print("输出:", result.stdout)
    else:
        print("❌ 命令执行失败")
        if result.stderr:
            print("错误:", result.stderr)
    print("-" * 50)

def main():
    """主函数"""
    print("🚀 Rocky Linux 10 巡检脚本使用示例")
    print("=" * 60)
    
    # 检查是否在正确目录
    if not os.path.exists('rocky10_inspection.py'):
        print("❌ 请在包含巡检脚本的目录中运行此示例")
        sys.exit(1)
    
    print("\n1. 基本用法 - 生成JSON格式报告")
    run_command("python3 rocky10_quick_inspection.py -f json")
    
    print("\n2. 生成DOCX格式报告")
    run_command("python3 rocky10_quick_inspection.py -f docx")
    
    print("\n3. 生成PDF格式报告")
    run_command("python3 rocky10_quick_inspection.py -f pdf")
    
    print("\n4. 生成多种格式报告")
    run_command("python3 rocky10_quick_inspection.py -f json docx pdf")
    
    print("\n5. 仅生成文件，不显示控制台输出")
    run_command("python3 rocky10_quick_inspection.py -f docx pdf --no-console")
    
    print("\n6. 使用自定义文件名前缀")
    run_command("python3 rocky10_quick_inspection.py -f docx --prefix my_custom_report")
    
    print("\n7. 完整巡检 - 生成多种格式")
    run_command("python3 rocky10_inspection.py -f json docx pdf --no-console")
    
    print("\n8. 查看帮助信息")
    run_command("python3 rocky10_inspection.py --help")
    
    print("\n✅ 示例演示完成!")
    print("\n📁 生成的文件:")
    run_command("ls -la *.json *.docx *.pdf 2>/dev/null | head -5")

if __name__ == "__main__":
    main()