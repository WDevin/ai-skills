#!/bin/bash
# AI 新闻日报自动发送脚本
# 用法: ./daily_email_report.sh <收件人邮箱>

set -e

# 加载环境变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$(dirname "$(dirname "$SCRIPT_DIR")")" && pwd)"

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
RECIPIENT_EMAIL="${1:-your-email@example.com}"
REPORTS_DIR="$PROJECT_DIR/reports"
DATE=$(date +%Y%m%d)
NEWS_FILE="$REPORTS_DIR/ai-daily-$DATE.md"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${YELLOW}🤖 AI 新闻日报生成与发送脚本${NC}"
echo "=========================================="
echo "收件人: $RECIPIENT_EMAIL"
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

# 创建报告目录
mkdir -p "$REPORTS_DIR"

# 生成新闻报告
echo -e "${BLUE}📰 步骤 1/3: 生成新闻报告...${NC}"
cd "$PROJECT_DIR"

python "$SCRIPT_DIR/fetch_ai_news.py" \
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

# 发送邮件
echo -e "${BLUE}📧 步骤 2/3: 发送邮件...${NC}"
python "$SCRIPT_DIR/send_email.py" \
    --to "$RECIPIENT_EMAIL" \
    --file "$NEWS_FILE" \
    --format html \
    --subject "🤖 AI 日报 $(date '+%m月%d日')" \
    --attach

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 邮件发送成功!${NC}"
else
    echo -e "${RED}✗ 邮件发送失败${NC}"
    exit 1
fi

# 清理旧文件
echo ""
echo -e "${BLUE}步骤 3/3: 清理旧文件...${NC}"
find "$REPORTS_DIR" -name "ai-daily-*.md" -mtime +7 -delete 2>/dev/null || true
echo -e "${GREEN}✓ 已清理 7 天前的旧报告${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 日报任务完成!${NC}"
