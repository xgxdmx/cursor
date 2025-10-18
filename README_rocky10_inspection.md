# Rocky Linux 10 系统巡检脚本

这是一个专为Rocky Linux 10设计的系统巡检Python脚本，可以全面检查系统状态、硬件资源、网络、安全等关键指标，并支持生成多种格式的详细报告。

## 功能特性

### 🔍 系统信息检查
- 操作系统版本和内核信息
- 系统运行时间
- 主机名和架构信息

### 💻 硬件资源监控
- CPU使用率和核心数
- 内存使用情况（总量、已用、可用、使用率）
- 磁盘使用情况（所有挂载点）
- 系统负载平均值

### 🌐 网络状态检查
- 网络接口配置（IPv4/IPv6）
- 网络连接统计
- 常用端口开放情况检查

### 🔧 服务状态监控
- systemd服务状态检查
- 关键服务运行状态
- 服务自启动配置

### 🔒 安全配置检查
- 防火墙状态（firewalld）
- SELinux状态
- SSH配置检查
- 用户安全配置

### 📝 日志分析
- 系统错误日志统计
- 内核错误检查
- 磁盘I/O错误监控

### ⚡ 性能监控
- 高CPU使用率进程
- 系统负载监控
- 资源使用率告警

## 安装和使用

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行巡检脚本

#### 基本用法
```bash
# 普通用户运行（部分功能受限）
python3 rocky10_inspection.py

# root用户运行（推荐，获得完整信息）
sudo python3 rocky10_inspection.py
```

#### 输出格式选项
```bash
# 生成JSON格式报告（默认）
python3 rocky10_inspection.py -f json

# 生成DOCX格式报告（Word文档）
python3 rocky10_inspection.py -f docx

# 生成PDF格式报告
python3 rocky10_inspection.py -f pdf

# 生成多种格式报告
python3 rocky10_inspection.py -f json docx pdf

# 仅生成文件，不显示控制台输出
python3 rocky10_inspection.py -f docx pdf --no-console

# 自定义文件名前缀
python3 rocky10_inspection.py -f docx --prefix my_inspection
```

#### 快速巡检
```bash
# 快速巡检（仅检查关键指标）
python3 rocky10_quick_inspection.py -f docx pdf
```

#### 交互式运行
```bash
# 使用交互式脚本（推荐新手使用）
./run_inspection.sh
```

### 3. 查看报告
脚本会：
- 在终端显示详细的巡检报告（除非使用--no-console参数）
- 自动保存指定格式的详细报告到文件
- 报告文件名格式：`rocky10_inspection_report_YYYYMMDD_HHMMSS.[json|docx|pdf]`

## 输出格式

### 控制台输出示例
```
🔍 Rocky Linux 10 系统巡检报告
============================================================

📋 系统信息:
  主机名: rocky10-server
  操作系统: Linux
  内核版本: 5.14.0-284.11.1.el9_2.x86_64
  系统运行时间: 15天 8小时 32分钟

💻 硬件资源:
  CPU核心数: 4
  CPU使用率: 12.5%
  内存使用率: 45.2%
  内存总量: 8.0 GB

💾 磁盘使用情况:
  /dev/sda1 (/): 67.3%
  /dev/sda2 (/home): 23.1%

🌐 网络状态:
  总连接数: 45
  已建立连接: 12
  监听端口: 8
  开放端口: 22, 80, 443

🔧 服务状态:
  sshd: ✅ active 🔧
  firewalld: ✅ active 🔧
  chronyd: ✅ active 🔧

🔒 安全配置:
  防火墙: running
  SELinux: Enforcing

📝 日志信息:
  最近1小时错误数: 2
  内核错误数: 0
  磁盘I/O错误数: 0

⚡ 性能信息:
  系统负载: 0.15, 0.12, 0.08
  高CPU使用率进程:
    systemd (PID: 1): CPU 0.5%
    kthreadd (PID: 2): CPU 0.1%

✅ 未发现明显问题
```

### 文件输出格式

#### JSON格式
- 机器可读的详细数据
- 包含所有检查结果和原始数据
- 适合程序处理和数据分析

#### DOCX格式
- 专业的Word文档格式
- 包含表格和格式化文本
- 适合打印和分享给管理层

#### PDF格式
- 跨平台兼容的文档格式
- 包含图表和格式化内容
- 适合归档和正式报告

## 注意事项

1. **权限要求**：建议以root用户运行以获得完整的系统信息
2. **依赖包**：需要安装基础依赖`psutil`，生成docx和PDF需要额外依赖
3. **执行时间**：完整巡检大约需要30-60秒
4. **报告保存**：每次运行都会生成带时间戳的报告文件
5. **输出格式**：支持JSON、DOCX、PDF三种格式，可同时生成多种格式
6. **文件大小**：PDF和DOCX文件通常比JSON文件大，但更易阅读

## 自定义配置

您可以根据需要修改脚本中的以下配置：

- `services_to_check`：要检查的服务列表
- `common_ports`：要检查的常用端口
- `critical_services`：关键服务列表
- 资源使用率告警阈值
- 报告模板和样式（在`report_generator.py`中）

## 命令行参数

### 完整巡检脚本 (rocky10_inspection.py)
```bash
python3 rocky10_inspection.py [选项]

选项:
  -f FORMAT, --format FORMAT  输出格式 [json|docx|pdf] (默认: json)
  --no-console               不显示控制台输出，仅生成文件
  --prefix PREFIX           输出文件名前缀
  -h, --help                显示帮助信息
```

### 快速巡检脚本 (rocky10_quick_inspection.py)
```bash
python3 rocky10_quick_inspection.py [选项]

选项:
  -f FORMAT, --format FORMAT  输出格式 [json|docx|pdf] (默认: json)
  --no-console               不显示控制台输出，仅生成文件
  --prefix PREFIX           输出文件名前缀
  -h, --help                显示帮助信息
```

## 故障排除

如果遇到权限错误，请确保：
1. 以root用户运行脚本
2. 安装了必要的依赖包
3. 系统支持systemd（Rocky Linux 10默认支持）

## 许可证

本脚本仅供学习和内部使用，请根据实际需求进行修改和优化。