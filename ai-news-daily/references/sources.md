# AI 新闻源参考文档

## 推荐使用的新闻源（已验证）

### 英文综合 AI 媒体（覆盖各大厂动态）

| 来源 | RSS 地址 | 特点 | 覆盖厂商 |
|------|----------|------|----------|
| **MarkTechPost** | https://www.marktechpost.com/feed/ | 更新频繁，技术教程丰富 | OpenAI, Google, Meta, 英伟达等 |
| **MIT Technology Review AI** | https://www.technologyreview.com/topic/artificial-intelligence/rss/ | MIT 权威科技评论 | 全球大厂 |
| **VentureBeat AI** | https://venturebeat.com/category/ai/feed/ | 商业新闻和融资动态 | 创业公司、大厂 |
| **Synced Review** | https://syncedreview.com/feed/ | 全球 AI 新闻，中英文都有 | 中美大厂 |
| **AI News** | https://www.artificialintelligence-news.com/feed/ | 英国 AI 媒体 | 欧洲、美国 |
| **Machine Learning Mastery** | https://machinelearningmastery.com/blog/feed/ | 教程丰富 | 通用 |
| **O'Reilly AI & ML** | https://www.oreilly.com/radar/topics/ai-ml/feed/index.xml | 深度洞察 | 行业趋势 |

### 中文 AI 媒体（覆盖国内大厂）

| 来源 | RSS 地址 | 特点 | 覆盖厂商 |
|------|----------|------|----------|
| **机器之心** | https://www.jiqizhixin.com/rss | 国内顶级 AI 媒体，学术+产业 | 阿里、字节、百度、智谱等 |
| **量子位** | https://www.qbitai.com/feed | 前沿技术和产品报道 | 国内大厂、创业公司 |
| **新智元** | https://www.ainews.cn/rss | 新闻报道快 | 国内外大厂 |

### 官方博客（作为补充）

| 公司 | RSS 地址 | 更新频率 |
|------|----------|----------|
| OpenAI | https://openai.com/blog/rss.xml | 双周 |
| Anthropic | https://www.anthropic.com/blog/rss.xml | 每周 |
| Google DeepMind | https://deepmind.google/blog/rss.xml | 每周 |
| Meta AI | https://ai.meta.com/blog/rss/ | 每周 |
| Google AI | https://ai.googleblog.com/feeds/posts/default | 每周 |

### 学术与研究

| 来源 | RSS 地址 | 内容类型 |
|------|----------|----------|
| arXiv cs.AI | http://export.arxiv.org/rss/cs.AI | AI 论文 |
| arXiv cs.CL | http://export.arxiv.org/rss/cs.CL | NLP 论文 |
| arXiv cs.LG | http://export.arxiv.org/rss/cs.LG | 机器学习论文 |
| Papers with Code | https://paperswithcode.com/rss | 论文+代码 |
| The Gradient | https://thegradient.pub/rss/ | 深度分析 |

### 社区与讨论

| 来源 | RSS 地址 | 类型 |
|------|----------|------|
| Hacker News AI | https://hnrss.org/newest?q=AI+LLM | 社区精选 |
| Reddit r/ML | https://www.reddit.com/r/MachineLearning/.rss | 讨论 |
| GitHub Trending | API 获取 | 开源项目 |

## 使用方法

### 默认配置（推荐）

脚本默认使用以下新闻源，覆盖各大 AI 厂商动态：

```bash
python scripts/fetch_ai_news.py --days 2 --translate --max-items 20
```

默认源：
- MarkTechPost（英文综合）
- MIT Technology Review（深度分析）
- VentureBeat AI（商业新闻）
- Synced Review（全球新闻）
- 机器之心（国内大厂）
- 量子位（前沿技术）

### 指定特定来源

```bash
# 只看中文新闻
python scripts/fetch_ai_news.py --sources "jiqizhixin,qbitai" --days 2

# 英文技术新闻
python scripts/fetch_ai_news.py --sources "marktechpost,mit-tech-review" --days 2

# 学术研究
python scripts/fetch_ai_news.py --sources "arxiv-ai,paperswithcode" --days 3
```

### 添加新的新闻源

在 `scripts/fetch_ai_news.py` 中的 `SOURCES` 字典添加：

```python
"source-key": {
    "name": "显示名称",
    "url": "https://example.com/feed.xml",
    "type": "rss",
    "category": "business",  # releases, research, business, products, community
    "language": "en",        # en, zh
    "description": "描述"
}
```

## 各大厂新闻覆盖情况

| 厂商 | 主要报道源 |
|------|-----------|
| **OpenAI** | MarkTechPost, Synced, 机器之心, 量子位, 官方博客 |
| **Google/DeepMind** | MarkTechPost, MIT Tech Review, Synced, 官方博客 |
| **Anthropic** | MarkTechPost, VentureBeat, 官方博客 |
| **Meta** | MarkTechPost, MIT Tech Review, 官方博客 |
| **NVIDIA** | MarkTechPost, VentureBeat, Synced |
| **阿里** | 机器之心, 量子位, Synced |
| **字节跳动** | 机器之心, 量子位 |
| **百度** | 机器之心, 量子位 |
| **智谱 AI** | 机器之心, 量子位 |
| **Kimi** | 机器之心, 量子位 |
| **Cursor** | Hacker News, 社区讨论 |

## 更新频率建议

- **每日推送**：使用 `--days 1`（可能内容较少）
- **推荐**：使用 `--days 2`（获取过去 48 小时新闻，内容更充足）
- **周报**：使用 `--days 7` 配合 `--format summary`

## 故障排除

### RSS 源无法获取
- 检查网络连接
- 某些 RSS 源可能有访问限制
- 尝试使用 `--sources` 指定其他源

### 翻译失败
- 检查 `translators` 库是否安装：`pip install translators`
- 某些语言可能需要科学上网
- 可使用 `--translate-fields "title"` 只翻译标题

### 日期过滤问题
- 使用 `--no-date-filter` 禁用日期过滤
- 使用 `--days N` 调整时间范围
