#!/bin/bash
# Rocky Linux 10 巡检脚本运行器

echo "🚀 Rocky Linux 10 系统巡检工具"
echo "================================"

# 检查Python3是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到python3，请先安装Python3"
    exit 1
fi

# 检查psutil是否安装
if ! python3 -c "import psutil" 2>/dev/null; then
    echo "📦 正在安装依赖包 psutil..."
    pip3 install psutil
    if [ $? -ne 0 ]; then
        echo "❌ 依赖包安装失败，请手动运行: pip3 install psutil"
        exit 1
    fi
fi

echo ""
echo "请选择巡检模式:"
echo "1. 完整巡检 (详细报告)"
echo "2. 快速巡检 (关键指标)"
echo "3. 退出"
echo ""

read -p "请输入选择 (1-3): " choice

echo ""
echo "请选择输出格式:"
echo "1. JSON格式 (默认)"
echo "2. DOCX格式 (Word文档)"
echo "3. PDF格式"
echo "4. 多种格式 (JSON + DOCX + PDF)"
echo ""

read -p "请输入格式选择 (1-4): " format_choice

# 设置输出格式
case $format_choice in
    1) output_format="json" ;;
    2) output_format="docx" ;;
    3) output_format="pdf" ;;
    4) output_format="json docx pdf" ;;
    *) output_format="json" ;;
esac

case $choice in
    1)
        echo "🔍 开始完整巡检..."
        python3 rocky10_inspection.py -f $output_format
        ;;
    2)
        echo "🔍 开始快速巡检..."
        python3 rocky10_quick_inspection.py -f $output_format
        ;;
    3)
        echo "👋 退出巡检工具"
        exit 0
        ;;
    *)
        echo "❌ 无效选择，请重新运行脚本"
        exit 1
        ;;
esac

echo ""
echo "✅ 巡检完成！"
echo "📄 详细报告已保存为JSON文件"