---
name: ai-news-daily
description: 自动化每日 AI 新闻聚合与推送。使用专业 AI 媒体（MarkTechPost、机器之心、量子位等）覆盖 OpenAI、Google、Anthropic、阿里、字节、智谱等各大厂动态。触发词包括"获取今日 AI 新闻"、"AI 新闻摘要"、"每日 AI 简报"。
---

# AI 每日新闻

从**专业 AI 新闻媒体**获取每日新闻，覆盖 OpenAI、Google、Anthropic、Meta、英伟达、阿里、字节、智谱、Kimi 等各大厂商动态。

## 快速开始

### 获取今日 AI 新闻（推荐）

```bash
python scripts/fetch_ai_news.py --days 2 --translate --max-items 20
```

此命令会：
- 从 6 个专业新闻网站获取过去 48 小时的新闻
- 自动翻译为中文
- 生成 20 条精选新闻

### 生成并保存报告

```bash
python scripts/fetch_ai_news.py \
    --days 2 \
    --translate \
    --format newsletter \
    --save-to "reports/ai-daily-$(date +%Y%m%d).md"
```

## 新闻源

### 默认新闻源（覆盖各大厂）

| 来源 | 语言 | 覆盖厂商 |
|------|------|----------|
| MarkTechPost | 英文 | OpenAI, Google, Meta, 英伟达 |
| MIT Technology Review | 英文 | 全球大厂深度分析 |
| VentureBeat AI | 英文 | 商业新闻、融资动态 |
| Synced Review | 英文 | 中美大厂 |
| 机器之心 | 中文 | 阿里、字节、百度、智谱 |
| 量子位 | 中文 | 前沿技术、国内大厂 |

### 指定特定来源

```bash
# 只看中文新闻
python scripts/fetch_ai_news.py --sources "jiqizhixin,qbitai"

# 英文技术媒体
python scripts/fetch_ai_news.py --sources "marktechpost,mit-tech-review,venturebeat-ai"

# 官方博客+社区
python scripts/fetch_ai_news.py --sources "openai,anthropic,deepmind,hacker-news-ai"
```

## 输出格式

### 1. Newsletter 格式（默认）

适合阅读的新闻简报格式：

```bash
python scripts/fetch_ai_news.py --format newsletter --title "🤖 AI 日报"
```

### 2. 标准报告格式

按分类组织的结构化报告：

```bash
python scripts/fetch_ai_news.py --format standard
```

分类包括：
- 🚀 新发布
- 🔬 研究动态
- 💰 商业资讯
- 💬 社区动态

### 3. 简洁摘要

```bash
python scripts/fetch_ai_news.py --format summary --max-items 10
```

## 使用模式

### 模式一：每日简报（推荐）

```bash
python scripts/fetch_ai_news.py \
  --days 2 \
  --translate \
  --format newsletter \
  --title "AI 每日精选" \
  --intro "过去 48 小时 AI 圈重要动态：" \
  --max-items 20 \
  --save-to "reports/ai-daily-$(date +%Y%m%d).md"
```

### 模式二：特定主题搜索

```bash
python scripts/fetch_ai_news.py \
  --search "GPT-5" \
  --days 7 \
  --max-items 15
```

### 模式三：学术研究

```bash
python scripts/fetch_ai_news.py \
  --sources "arxiv-ai,paperswithcode,mit-tech-review" \
  --days 3 \
  --categories "research"
```

## 脚本参考

### fetch_ai_news.py

**常用参数：**

| 参数 | 说明 | 示例 |
|------|------|------|
| `--days N` | 获取最近 N 天的新闻 | `--days 2` |
| `--translate` | 自动翻译为中文 | `--translate` |
| `--max-items N` | 最多输出 N 条新闻 | `--max-items 20` |
| `--sources` | 指定新闻源 | `--sources "marktechpost,jiqizhixin"` |
| `--search` | 关键词搜索 | `--search "OpenAI"` |
| `--format` | 输出格式 | `newsletter`, `standard`, `summary` |
| `--save-to` | 保存路径 | `--save-to "reports/today.md"` |
| `--categories` | 按分类筛选 | `--categories "business,research"` |

**完整参数：**

```bash
python scripts/fetch_ai_news.py --help
```

## 翻译功能

### 自动翻译（无需 API key）

使用 `translators` 库进行翻译，**免费、无需注册**。

```bash
pip install translators
```

```bash
# 翻译标题和摘要
python scripts/fetch_ai_news.py --translate --max-items 20

# 只翻译标题（更快）
python scripts/fetch_ai_news.py --translate --translate-fields "title" --max-items 20
```

## 邮件推送

### 配置邮箱

```bash
export EMAIL_USER="your@qq.com"
export EMAIL_PASSWORD="your-auth-code"
```

### 发送日报

```bash
./scripts/daily_email_report.sh your@qq.com
```

### 设置定时任务

```bash
# 每天早上 9 点自动获取并发送
0 9 * * * cd /home/admin/code/skills && ./ai-news-daily/scripts/daily_email_report.sh your@qq.com
```

## 新闻源列表

完整新闻源列表请参见 [references/sources.md](references/sources.md)。

### 添加新的新闻源

编辑 `scripts/fetch_ai_news.py`，在 `SOURCES` 字典中添加：

```python
"my-source": {
    "name": "显示名称",
    "url": "https://example.com/feed.xml",
    "type": "rss",
    "category": "business",
    "language": "en",
    "description": "描述"
}
```

## 故障排除

### 获取不到新闻？

1. 检查网络连接
2. 尝试扩大时间范围：`--days 3`
3. 禁用日期过滤：`--no-date-filter`
4. 检查特定源是否可用：`--sources "marktechpost"`

### 翻译失败？

1. 安装依赖：`pip install translators`
2. 减少翻译数量：`--max-items 10`
3. 只翻译标题：`--translate-fields "title"`

### 内容重复？

- 使用 `--days 1` 获取当天新闻
- 使用 `--date today` 配合 `--days 1`

## 更新日志

### 2026-02-08
- 重构新闻源，使用专业 AI 媒体替代单独公司博客
- 新增 MarkTechPost、机器之心、量子位等优质源
- 覆盖 OpenAI、Google、Anthropic、Meta、英伟达、阿里、字节、智谱等各大厂
- 修复日期过滤逻辑
