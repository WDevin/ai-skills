#!/bin/bash
# AI 新闻日报自动发送脚本
# 用法: ./daily_email_report.sh [单个收件人邮箱]
# 如果不提供参数，默认从上级目录的 email_list 文件读取收件人列表

set -e

# 加载环境变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$(dirname "$SCRIPT_DIR")" && pwd)"

if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
elif [ -f "$PROJECT_DIR/../.env" ]; then
    set -a
    source "$PROJECT_DIR/../.env"
    set +a
fi

# 配置
REPORTS_DIR="$PROJECT_DIR/reports"
DATE=$(date +%Y%m%d)
NEWS_FILE="$REPORTS_DIR/ai-daily-$DATE.md"

# 收件人列表文件路径（在 .env 同目录）
# PROJECT_DIR 在脚本目录结构下是 ai-news-daily 的父目录
if [ -f "$PROJECT_DIR/.env" ]; then
    EMAIL_LIST_FILE="$PROJECT_DIR/email_list"
else
    EMAIL_LIST_FILE="$PROJECT_DIR/../email_list"
fi

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${YELLOW}🤖 AI 新闻日报生成与发送脚本${NC}"
echo "=========================================="
echo "日期: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查环境变量
if [ -z "$EMAIL_USER" ] || [ -z "$EMAIL_PASSWORD" ]; then
    echo -e "${RED}错误: 未设置邮箱环境变量${NC}"
    echo "请设置:"
    echo "  export EMAIL_USER='你的邮箱@qq.com'"
    echo "  export EMAIL_PASSWORD='你的邮箱授权码'"
    exit 1
fi

# 获取收件人列表
RECIPIENTS=()

if [ -n "$1" ]; then
    # 如果提供了命令行参数，使用参数作为收件人
    RECIPIENTS=("$1")
    echo -e "${BLUE}📧 收件人(命令行指定): $1${NC}"
elif [ -f "$EMAIL_LIST_FILE" ]; then
    # 从 email_list 文件读取收件人
    echo -e "${BLUE}📧 从邮件列表读取收件人: $EMAIL_LIST_FILE${NC}"
    while IFS= read -r line || [[ -n "$line" ]]; do
        # 跳过注释行和空行
        line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        [[ -z "$line" ]] && continue
        [[ "$line" =~ ^# ]] && continue
        RECIPIENTS+=("$line")
    done < "$EMAIL_LIST_FILE"
else
    echo -e "${RED}错误: 未指定收件人，且未找到邮件列表文件: $EMAIL_LIST_FILE${NC}"
    echo "用法: $0 <收件人邮箱>"
    exit 1
fi

if [ ${#RECIPIENTS[@]} -eq 0 ]; then
    echo -e "${RED}错误: 未找到有效的收件人邮箱${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 共找到 ${#RECIPIENTS[@]} 个收件人${NC}"
for email in "${RECIPIENTS[@]}"; do
    echo "  - $email"
done
echo ""

# 创建报告目录
mkdir -p "$REPORTS_DIR"

# 使用虚拟环境的 Python
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
    echo -e "${RED}错误: 未找到虚拟环境 Python: $VENV_PYTHON${NC}"
    echo "请先运行: uv venv && uv pip install -r requirements.txt"
    exit 1
fi

# 生成新闻报告
echo -e "${BLUE}📰 步骤 1/3: 生成新闻报告...${NC}"
cd "$PROJECT_DIR"

$VENV_PYTHON "$SCRIPT_DIR/fetch_ai_news.py" \
    --days 2 \
    --translate \
    --format newsletter \
    --title "🤖 AI 每日精选" \
    --max-items 20 \
    --save-to "$NEWS_FILE"

if [ ! -f "$NEWS_FILE" ]; then
    echo -e "${RED}错误: 新闻报告生成失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 新闻报告已生成: $NEWS_FILE${NC}"
echo ""

# 发送邮件给每个收件人
SUCCESS_COUNT=0
FAIL_COUNT=0

echo -e "${BLUE}📧 步骤 2/3: 发送邮件...${NC}"
for RECIPIENT_EMAIL in "${RECIPIENTS[@]}"; do
    echo -e "${BLUE}  正在发送给: $RECIPIENT_EMAIL ...${NC}"
    
    if $VENV_PYTHON "$SCRIPT_DIR/send_email.py" \
        --to "$RECIPIENT_EMAIL" \
        --file "$NEWS_FILE" \
        --format html \
        --subject "🤖 AI 日报 $(date '+%m月%d日')" \
        --attach; then
        echo -e "${GREEN}  ✓ 发送成功: $RECIPIENT_EMAIL${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "${RED}  ✗ 发送失败: $RECIPIENT_EMAIL${NC}"
        ((FAIL_COUNT++))
    fi
done

echo ""
if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ 所有邮件发送成功! ($SUCCESS_COUNT/${#RECIPIENTS[@]})${NC}"
else
    echo -e "${YELLOW}⚠ 邮件发送完成: 成功 $SUCCESS_COUNT, 失败 $FAIL_COUNT${NC}"
fi

# 清理旧文件
echo ""
echo -e "${BLUE}步骤 3/3: 清理旧文件...${NC}"
find "$REPORTS_DIR" -name "ai-daily-*.md" -mtime +7 -delete 2>/dev/null || true
echo -e "${GREEN}✓ 已清理 7 天前的旧报告${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 日报任务完成!${NC}"
