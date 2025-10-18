#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成器模块
支持生成docx和PDF格式的巡检报告
"""

import os
import datetime
from typing import Dict, Any, List
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端

class ReportGenerator:
    """报告生成器类"""
    
    def __init__(self, report_data: Dict[str, Any]):
        self.report_data = report_data
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def generate_docx_report(self, filename: str = None) -> str:
        """生成docx格式报告"""
        if filename is None:
            filename = f"rocky10_inspection_report_{self.timestamp}.docx"
        
        # 创建文档
        doc = Document()
        
        # 设置文档标题
        title = doc.add_heading('Rocky Linux 10 系统巡检报告', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 添加报告信息
        info_para = doc.add_paragraph()
        info_para.add_run(f"巡检时间: {self.report_data['timestamp']}\n").bold = True
        info_para.add_run(f"主机名: {self.report_data['hostname']}\n")
        info_para.add_run(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 系统信息部分
        self._add_system_info_section(doc)
        
        # 硬件资源部分
        self._add_hardware_section(doc)
        
        # 网络状态部分
        self._add_network_section(doc)
        
        # 服务状态部分
        self._add_services_section(doc)
        
        # 安全配置部分
        self._add_security_section(doc)
        
        # 日志信息部分
        self._add_logs_section(doc)
        
        # 性能信息部分
        self._add_performance_section(doc)
        
        # 问题汇总部分
        self._add_issues_section(doc)
        
        # 保存文档
        doc.save(filename)
        return filename
    
    def _add_system_info_section(self, doc):
        """添加系统信息部分"""
        doc.add_heading('系统信息', level=1)
        
        system_info = self.report_data.get('system_info', {})
        
        # 创建表格
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # 表头
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = '项目'
        hdr_cells[1].text = '值'
        
        # 添加数据行
        data_rows = [
            ('主机名', system_info.get('hostname', 'Unknown')),
            ('操作系统', system_info.get('os', 'Unknown')),
            ('内核版本', system_info.get('kernel', 'Unknown')),
            ('架构', system_info.get('architecture', 'Unknown')),
            ('运行时间', system_info.get('uptime', 'Unknown')),
            ('Python版本', system_info.get('python_version', 'Unknown'))
        ]
        
        for item, value in data_rows:
            row_cells = table.add_row().cells
            row_cells[0].text = item
            row_cells[1].text = str(value)
    
    def _add_hardware_section(self, doc):
        """添加硬件资源部分"""
        doc.add_heading('硬件资源', level=1)
        
        hardware = self.report_data.get('hardware', {})
        
        # CPU信息
        doc.add_heading('CPU信息', level=2)
        cpu = hardware.get('cpu', {})
        cpu_table = doc.add_table(rows=1, cols=2)
        cpu_table.style = 'Table Grid'
        
        hdr_cells = cpu_table.rows[0].cells
        hdr_cells[0].text = '项目'
        hdr_cells[1].text = '值'
        
        cpu_data = [
            ('CPU核心数', str(cpu.get('cpu_count', 'Unknown'))),
            ('CPU使用率', f"{cpu.get('cpu_percent', 0):.1f}%"),
            ('系统负载', str(cpu.get('load_avg', 'Unknown')))
        ]
        
        for item, value in cpu_data:
            row_cells = cpu_table.add_row().cells
            row_cells[0].text = item
            row_cells[1].text = value
        
        # 内存信息
        doc.add_heading('内存信息', level=2)
        memory = hardware.get('memory', {})
        memory_table = doc.add_table(rows=1, cols=2)
        memory_table.style = 'Table Grid'
        
        hdr_cells = memory_table.rows[0].cells
        hdr_cells[0].text = '项目'
        hdr_cells[1].text = '值'
        
        total_gb = memory.get('total', 0) // (1024**3)
        used_gb = memory.get('used', 0) // (1024**3)
        available_gb = memory.get('available', 0) // (1024**3)
        
        memory_data = [
            ('总内存', f"{total_gb:.1f} GB"),
            ('已用内存', f"{used_gb:.1f} GB"),
            ('可用内存', f"{available_gb:.1f} GB"),
            ('内存使用率', f"{memory.get('percent', 0):.1f}%"),
            ('交换分区使用率', f"{memory.get('swap_percent', 0):.1f}%")
        ]
        
        for item, value in memory_data:
            row_cells = memory_table.add_row().cells
            row_cells[0].text = item
            row_cells[1].text = value
        
        # 磁盘信息
        doc.add_heading('磁盘使用情况', level=2)
        disk_table = doc.add_table(rows=1, cols=4)
        disk_table.style = 'Table Grid'
        
        hdr_cells = disk_table.rows[0].cells
        hdr_cells[0].text = '设备'
        hdr_cells[1].text = '挂载点'
        hdr_cells[2].text = '文件系统'
        hdr_cells[3].text = '使用率'
        
        for disk in hardware.get('disk', []):
            row_cells = disk_table.add_row().cells
            row_cells[0].text = disk.get('device', 'Unknown')
            row_cells[1].text = disk.get('mountpoint', 'Unknown')
            row_cells[2].text = disk.get('fstype', 'Unknown')
            row_cells[3].text = f"{disk.get('percent', 0):.1f}%"
    
    def _add_network_section(self, doc):
        """添加网络状态部分"""
        doc.add_heading('网络状态', level=1)
        
        network = self.report_data.get('network', {})
        
        # 连接统计
        connections = network.get('connections', {})
        conn_table = doc.add_table(rows=1, cols=2)
        conn_table.style = 'Table Grid'
        
        hdr_cells = conn_table.rows[0].cells
        hdr_cells[0].text = '项目'
        hdr_cells[1].text = '数量'
        
        conn_data = [
            ('总连接数', str(connections.get('total', 0))),
            ('已建立连接', str(connections.get('established', 0))),
            ('监听端口', str(connections.get('listening', 0))),
            ('TIME_WAIT', str(connections.get('time_wait', 0)))
        ]
        
        for item, value in conn_data:
            row_cells = conn_table.add_row().cells
            row_cells[0].text = item
            row_cells[1].text = value
        
        # 开放端口
        open_ports = network.get('open_ports', [])
        if open_ports:
            doc.add_paragraph(f"开放端口: {', '.join(map(str, open_ports))}")
        else:
            doc.add_paragraph("未检测到开放端口")
    
    def _add_services_section(self, doc):
        """添加服务状态部分"""
        doc.add_heading('服务状态', level=1)
        
        services = self.report_data.get('services', {})
        service_table = doc.add_table(rows=1, cols=3)
        service_table.style = 'Table Grid'
        
        hdr_cells = service_table.rows[0].cells
        hdr_cells[0].text = '服务名'
        hdr_cells[1].text = '状态'
        hdr_cells[2].text = '自启动'
        
        for service, info in services.items():
            row_cells = service_table.add_row().cells
            row_cells[0].text = service
            row_cells[1].text = info.get('status', 'unknown')
            row_cells[2].text = '是' if info.get('enabled', False) else '否'
    
    def _add_security_section(self, doc):
        """添加安全配置部分"""
        doc.add_heading('安全配置', level=1)
        
        security = self.report_data.get('security', {})
        sec_table = doc.add_table(rows=1, cols=2)
        sec_table.style = 'Table Grid'
        
        hdr_cells = sec_table.rows[0].cells
        hdr_cells[0].text = '项目'
        hdr_cells[1].text = '状态'
        
        sec_data = [
            ('防火墙', security.get('firewall', {}).get('status', 'unknown')),
            ('SELinux', security.get('selinux', {}).get('status', 'unknown'))
        ]
        
        for item, value in sec_data:
            row_cells = sec_table.add_row().cells
            row_cells[0].text = item
            row_cells[1].text = str(value)
    
    def _add_logs_section(self, doc):
        """添加日志信息部分"""
        doc.add_heading('日志信息', level=1)
        
        logs = self.report_data.get('logs', {})
        log_table = doc.add_table(rows=1, cols=2)
        log_table.style = 'Table Grid'
        
        hdr_cells = log_table.rows[0].cells
        hdr_cells[0].text = '项目'
        hdr_cells[1].text = '数量'
        
        log_data = [
            ('最近1小时错误数', str(logs.get('error_count_1h', 0))),
            ('内核错误数', str(logs.get('kernel_errors', 0))),
            ('磁盘I/O错误数', str(logs.get('disk_io_errors', 0)))
        ]
        
        for item, value in log_data:
            row_cells = log_table.add_row().cells
            row_cells[0].text = item
            row_cells[1].text = value
    
    def _add_performance_section(self, doc):
        """添加性能信息部分"""
        doc.add_heading('性能信息', level=1)
        
        performance = self.report_data.get('performance', {})
        
        # 系统负载
        load_avg = performance.get('load_average')
        if load_avg:
            doc.add_paragraph(f"系统负载: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
        
        # 高CPU使用率进程
        top_processes = performance.get('top_processes', [])
        if top_processes:
            doc.add_heading('高CPU使用率进程', level=2)
            proc_table = doc.add_table(rows=1, cols=3)
            proc_table.style = 'Table Grid'
            
            hdr_cells = proc_table.rows[0].cells
            hdr_cells[0].text = '进程名'
            hdr_cells[1].text = 'PID'
            hdr_cells[2].text = 'CPU使用率'
            
            for proc in top_processes[:10]:  # 只显示前10个
                row_cells = proc_table.add_row().cells
                row_cells[0].text = proc.get('name', 'Unknown')
                row_cells[1].text = str(proc.get('pid', 'Unknown'))
                row_cells[2].text = f"{proc.get('cpu_percent', 0):.1f}%"
    
    def _add_issues_section(self, doc):
        """添加问题汇总部分"""
        doc.add_heading('问题汇总', level=1)
        
        issues = self.report_data.get('issues', [])
        if issues:
            for i, issue in enumerate(issues, 1):
                doc.add_paragraph(f"{i}. {issue}", style='List Number')
        else:
            doc.add_paragraph("✅ 未发现明显问题")
    
    def generate_pdf_report(self, filename: str = None) -> str:
        """生成PDF格式报告"""
        if filename is None:
            filename = f"rocky10_inspection_report_{self.timestamp}.pdf"
        
        # 创建PDF文档
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
        
        # 获取样式
        styles = getSampleStyleSheet()
        
        # 标题样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # 添加标题
        story.append(Paragraph('Rocky Linux 10 系统巡检报告', title_style))
        story.append(Spacer(1, 12))
        
        # 报告信息
        info_text = f"""
        <b>巡检时间:</b> {self.report_data['timestamp']}<br/>
        <b>主机名:</b> {self.report_data['hostname']}<br/>
        <b>生成时间:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        story.append(Paragraph(info_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # 系统信息
        self._add_pdf_system_info(story, styles)
        
        # 硬件资源
        self._add_pdf_hardware_info(story, styles)
        
        # 网络状态
        self._add_pdf_network_info(story, styles)
        
        # 服务状态
        self._add_pdf_services_info(story, styles)
        
        # 安全配置
        self._add_pdf_security_info(story, styles)
        
        # 日志信息
        self._add_pdf_logs_info(story, styles)
        
        # 性能信息
        self._add_pdf_performance_info(story, styles)
        
        # 问题汇总
        self._add_pdf_issues_info(story, styles)
        
        # 构建PDF
        doc.build(story)
        return filename
    
    def _add_pdf_system_info(self, story, styles):
        """添加PDF系统信息"""
        story.append(Paragraph('系统信息', styles['Heading1']))
        
        system_info = self.report_data.get('system_info', {})
        data = [
            ['项目', '值'],
            ['主机名', system_info.get('hostname', 'Unknown')],
            ['操作系统', system_info.get('os', 'Unknown')],
            ['内核版本', system_info.get('kernel', 'Unknown')],
            ['架构', system_info.get('architecture', 'Unknown')],
            ['运行时间', system_info.get('uptime', 'Unknown')],
            ['Python版本', system_info.get('python_version', 'Unknown')]
        ]
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
    
    def _add_pdf_hardware_info(self, story, styles):
        """添加PDF硬件信息"""
        story.append(Paragraph('硬件资源', styles['Heading1']))
        
        hardware = self.report_data.get('hardware', {})
        
        # CPU信息
        story.append(Paragraph('CPU信息', styles['Heading2']))
        cpu = hardware.get('cpu', {})
        cpu_data = [
            ['项目', '值'],
            ['CPU核心数', str(cpu.get('cpu_count', 'Unknown'))],
            ['CPU使用率', f"{cpu.get('cpu_percent', 0):.1f}%"],
            ['系统负载', str(cpu.get('load_avg', 'Unknown'))]
        ]
        
        cpu_table = Table(cpu_data)
        cpu_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(cpu_table)
        story.append(Spacer(1, 12))
        
        # 内存信息
        story.append(Paragraph('内存信息', styles['Heading2']))
        memory = hardware.get('memory', {})
        total_gb = memory.get('total', 0) // (1024**3)
        used_gb = memory.get('used', 0) // (1024**3)
        available_gb = memory.get('available', 0) // (1024**3)
        
        memory_data = [
            ['项目', '值'],
            ['总内存', f"{total_gb:.1f} GB"],
            ['已用内存', f"{used_gb:.1f} GB"],
            ['可用内存', f"{available_gb:.1f} GB"],
            ['内存使用率', f"{memory.get('percent', 0):.1f}%"],
            ['交换分区使用率', f"{memory.get('swap_percent', 0):.1f}%"]
        ]
        
        memory_table = Table(memory_data)
        memory_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(memory_table)
        story.append(Spacer(1, 20))
    
    def _add_pdf_network_info(self, story, styles):
        """添加PDF网络信息"""
        story.append(Paragraph('网络状态', styles['Heading1']))
        
        network = self.report_data.get('network', {})
        connections = network.get('connections', {})
        
        conn_data = [
            ['项目', '数量'],
            ['总连接数', str(connections.get('total', 0))],
            ['已建立连接', str(connections.get('established', 0))],
            ['监听端口', str(connections.get('listening', 0))],
            ['TIME_WAIT', str(connections.get('time_wait', 0))]
        ]
        
        conn_table = Table(conn_data)
        conn_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(conn_table)
        
        # 开放端口
        open_ports = network.get('open_ports', [])
        if open_ports:
            story.append(Paragraph(f"开放端口: {', '.join(map(str, open_ports))}", styles['Normal']))
        else:
            story.append(Paragraph("未检测到开放端口", styles['Normal']))
        
        story.append(Spacer(1, 20))
    
    def _add_pdf_services_info(self, story, styles):
        """添加PDF服务信息"""
        story.append(Paragraph('服务状态', styles['Heading1']))
        
        services = self.report_data.get('services', {})
        service_data = [['服务名', '状态', '自启动']]
        
        for service, info in services.items():
            service_data.append([
                service,
                info.get('status', 'unknown'),
                '是' if info.get('enabled', False) else '否'
            ])
        
        service_table = Table(service_data)
        service_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(service_table)
        story.append(Spacer(1, 20))
    
    def _add_pdf_security_info(self, story, styles):
        """添加PDF安全信息"""
        story.append(Paragraph('安全配置', styles['Heading1']))
        
        security = self.report_data.get('security', {})
        sec_data = [
            ['项目', '状态'],
            ['防火墙', security.get('firewall', {}).get('status', 'unknown')],
            ['SELinux', security.get('selinux', {}).get('status', 'unknown')]
        ]
        
        sec_table = Table(sec_data)
        sec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(sec_table)
        story.append(Spacer(1, 20))
    
    def _add_pdf_logs_info(self, story, styles):
        """添加PDF日志信息"""
        story.append(Paragraph('日志信息', styles['Heading1']))
        
        logs = self.report_data.get('logs', {})
        log_data = [
            ['项目', '数量'],
            ['最近1小时错误数', str(logs.get('error_count_1h', 0))],
            ['内核错误数', str(logs.get('kernel_errors', 0))],
            ['磁盘I/O错误数', str(logs.get('disk_io_errors', 0))]
        ]
        
        log_table = Table(log_data)
        log_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(log_table)
        story.append(Spacer(1, 20))
    
    def _add_pdf_performance_info(self, story, styles):
        """添加PDF性能信息"""
        story.append(Paragraph('性能信息', styles['Heading1']))
        
        performance = self.report_data.get('performance', {})
        
        # 系统负载
        load_avg = performance.get('load_average')
        if load_avg:
            story.append(Paragraph(f"系统负载: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}", styles['Normal']))
        
        # 高CPU使用率进程
        top_processes = performance.get('top_processes', [])
        if top_processes:
            story.append(Paragraph('高CPU使用率进程', styles['Heading2']))
            proc_data = [['进程名', 'PID', 'CPU使用率']]
            
            for proc in top_processes[:10]:
                proc_data.append([
                    proc.get('name', 'Unknown'),
                    str(proc.get('pid', 'Unknown')),
                    f"{proc.get('cpu_percent', 0):.1f}%"
                ])
            
            proc_table = Table(proc_data)
            proc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(proc_table)
        
        story.append(Spacer(1, 20))
    
    def _add_pdf_issues_info(self, story, styles):
        """添加PDF问题信息"""
        story.append(Paragraph('问题汇总', styles['Heading1']))
        
        issues = self.report_data.get('issues', [])
        if issues:
            for i, issue in enumerate(issues, 1):
                story.append(Paragraph(f"{i}. {issue}", styles['Normal']))
        else:
            story.append(Paragraph("✅ 未发现明显问题", styles['Normal']))