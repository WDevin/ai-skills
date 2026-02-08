#!/usr/bin/env python3
"""
AI 每日新闻 - 从专业 AI 媒体获取新闻
特点：自动识别公司和机构，简洁美观的输出
"""

import argparse
import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin
import time

# 尝试导入可选依赖
try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# 翻译支持
try:
    import translators as ts
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False


# ============================================
# 专业 AI 新闻媒体配置
# ============================================
SOURCES = {
    # --- 英文综合 AI 媒体 ---
    "marktechpost": {
        "name": "MarkTechPost",
        "url": "https://www.marktechpost.com/feed/",
        "type": "rss",
        "category": "business",
        "language": "en",
    },
    "mit-tech-review": {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/rss/",
        "type": "rss",
        "category": "research",
        "language": "en",
    },
    "venturebeat-ai": {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "type": "rss",
        "category": "business",
        "language": "en",
    },
    "synced-review": {
        "name": "Synced Review",
        "url": "https://syncedreview.com/feed/",
        "type": "rss",
        "category": "business",
        "language": "en",
    },
    "ai-news": {
        "name": "AI News",
        "url": "https://www.artificialintelligence-news.com/feed/",
        "type": "rss",
        "category": "business",
        "language": "en",
    },
    "machinelearningmastery": {
        "name": "Machine Learning Mastery",
        "url": "https://machinelearningmastery.com/blog/feed/",
        "type": "rss",
        "category": "research",
        "language": "en",
    },
    
    # --- 中文 AI 媒体 ---
    "jiqizhixin": {
        "name": "机器之心",
        "url": "https://www.jiqizhixin.com/rss",
        "type": "rss",
        "category": "business",
        "language": "zh",
    },
    "qbitai": {
        "name": "量子位",
        "url": "https://www.qbitai.com/feed",
        "type": "rss",
        "category": "business",
        "language": "zh",
    },
    
    # --- 官方博客（可选）---
    "openai": {
        "name": "OpenAI 博客", 
        "url": "https://openai.com/blog/rss.xml",
        "type": "rss",
        "category": "releases",
        "language": "en"
    },
    "anthropic": {
        "name": "Anthropic 博客",
        "url": "https://www.anthropic.com/blog/rss.xml",
        "type": "rss",
        "category": "research",
        "language": "en"
    },
    "deepmind": {
        "name": "Google DeepMind",
        "url": "https://deepmind.google/blog/rss.xml",
        "type": "rss",
        "category": "research",
        "language": "en"
    },
    "meta-ai": {
        "name": "Meta AI 博客",
        "url": "https://ai.meta.com/blog/rss/",
        "type": "rss",
        "category": "research",
        "language": "en"
    },
    
    # --- 学术与研究 ---
    "arxiv-ai": {
        "name": "arXiv cs.AI",
        "url": "http://export.arxiv.org/rss/cs.AI",
        "type": "rss",
        "category": "research",
        "language": "en"
    },
    "paperswithcode": {
        "name": "Papers with Code",
        "url": "https://paperswithcode.com/rss",
        "type": "rss",
        "category": "research",
        "language": "en"
    },
}

# ============================================
# 公司和机构识别配置
# ============================================
COMPANY_KEYWORDS = {
    # 国外大厂
    "OpenAI": ["openai", "gpt", "chatgpt", "dall-e", "sora", "o1", "o3"],
    "Google": ["google", "deepmind", "gemini", "bard", "alphago", "alphafold", "waymo"],
    "Anthropic": ["anthropic", "claude"],
    "Meta": ["meta", "facebook", "llama", "pytorch"],
    "Microsoft": ["microsoft", "azure", "copilot", "bing"],
    "NVIDIA": ["nvidia", "geforce", "rtx", "cuda", "hopper", "blackwell"],
    "Amazon": ["amazon", "aws", "alexa"],
    "Apple": ["apple", "siri"],
    "Tesla": ["tesla", "optimus"],
    "Stability AI": ["stability ai", "stable diffusion"],
    "Midjourney": ["midjourney"],
    "Hugging Face": ["huggingface", "hugging face", "transformers"],
    "Cohere": ["cohere"],
    "Perplexity": ["perplexity"],
    "Midjourney": ["midjourney"],
    
    # 国内大厂
    "阿里巴巴": ["阿里", "alibaba", "通义千问", "qwen", "达摩院"],
    "字节跳动": ["字节", "bytedance", "豆包", "云雀", "doubao"],
    "百度": ["百度", "baidu", "文心一言", "ernie", "apollo", "飞桨"],
    "腾讯": ["腾讯", "tencent", "混元", "hunyuan"],
    "华为": ["华为", "huawei", "盘古", "mindspore", "昇腾"],
    "智谱 AI": ["智谱", "chatglm", "glm", "zhipu"],
    "月之暗面": ["月之暗面", "kimi"],
    "MiniMax": ["minimax", "abab"],
    "零一万物": ["零一万物", "01.ai", "yi"],
    "百川智能": ["百川", "baichuan"],
    "商汤": ["商汤", "sensetime", "书生"],
    "科大讯飞": ["讯飞", "iflytek", "星火"],
    "理想汽车": ["理想", "li auto"],
    "小鹏": ["小鹏", "xpeng"],
    "蔚来": ["蔚来", "nio"],
    "小米": ["小米", "xiaomi"],
    
    # 研究机构
    "MIT": ["mit", "麻省理工"],
    "Stanford": ["stanford", "斯坦福"],
    "Berkeley": ["berkeley", "伯克利"],
    "CMU": ["cmu", "卡内基梅隆"],
    "清华": ["清华", "tsinghua"],
    "北大": ["北大", "peking university"],
    "中科院": ["中科院", "cas"],
    "UIUC": ["uiuc", "伊利诺伊"],
}

# 分类图标
CATEGORY_ICONS = {
    "releases": "🚀",
    "research": "🔬",
    "business": "💰",
    "products": "📱",
    "community": "💬",
    "general": "📰"
}


def detect_companies(text: str) -> List[str]:
    """识别文本中提到的公司和机构"""
    if not text:
        return []
    
    text_lower = text.lower()
    found_companies = []
    
    for company, keywords in COMPANY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_companies.append(company)
                break
    
    # 去重并保持顺序
    seen = set()
    result = []
    for c in found_companies:
        if c not in seen:
            seen.add(c)
            result.append(c)
    
    return result[:5]  # 最多返回5个


def parse_date(date_str: str) -> Optional[datetime]:
    """解析各种日期格式"""
    if not date_str or date_str == "未知":
        return None
    
    date_formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S",
        "%d %b %Y %H:%M:%S %z",
        "%B %d, %Y",
        "%b %d, %Y",
        "%Y-%m-%d",
    ]
    
    date_str = date_str.strip()
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


class NewsTranslator:
    """翻译新闻内容"""
    
    def __init__(self, translator_engine: str = "bing"):
        self.translator_engine = translator_engine
        self._cache: Dict[str, str] = {}
        
    def translate(self, text: str) -> str:
        if not text or not TRANSLATOR_AVAILABLE:
            return text
            
        if self._is_mostly_chinese(text):
            return text
            
        cache_key = f"{text[:200]}"
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        try:
            result = ts.translate_text(
                text, 
                translator=self.translator_engine,
                from_language='en', 
                to_language='zh'
            )
            self._cache[cache_key] = result
            return result
        except Exception as e:
            return text
    
    def _is_mostly_chinese(self, text: str) -> bool:
        if not text:
            return False
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        return chinese_chars / len(text) > 0.4
    
    def translate_items(self, items: List[Dict], fields: List[str] = None, max_items: int = 10) -> List[Dict]:
        if not TRANSLATOR_AVAILABLE or not items:
            return items
            
        fields = fields or ['title', 'summary']
        items_to_translate = items[:max_items]
        
        print(f"正在翻译 {len(items_to_translate)} 条新闻...")
        for i, item in enumerate(items_to_translate, 1):
            print(f"  [{i}/{len(items_to_translate)}] {item.get('title', '')[:40]}...", end='\r')
            for field in fields:
                if field in item and item[field]:
                    text = item[field][:800] if field == 'summary' else item[field][:200]
                    item[field] = self.translate(text)
        print(f"\n翻译完成！")
        return items


class NewsFetcher:
    """获取和处理 AI 新闻"""
    
    def __init__(self, sources: Optional[List[str]] = None, translator: Optional[NewsTranslator] = None):
        self.sources = sources or list(SOURCES.keys())
        self.news_items: List[Dict] = []
        self.translator = translator
        
    def fetch_rss(self, source_key: str) -> List[Dict]:
        """从 RSS 源获取新闻"""
        if not FEEDPARSER_AVAILABLE:
            print("警告：未安装 feedparser")
            return []
            
        source = SOURCES.get(source_key)
        if not source:
            return []
            
        try:
            print(f"  正在获取: {source['name']}...")
            feed = feedparser.parse(source["url"])
            items = []
            
            for entry in feed.entries[:30]:
                published = entry.get("published", entry.get("updated", "未知"))
                
                item = {
                    "title": entry.get("title", "无标题"),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", entry.get("description", ""))[:400],
                    "published": published,
                    "source": source["name"],
                    "category": source.get("category", "general"),
                    "language": source.get("language", "en")
                }
                
                # 自动识别公司和机构
                full_text = f"{item['title']} {item['summary']}"
                item["companies"] = detect_companies(full_text)
                
                items.append(item)
                
            print(f"    ✓ 获取到 {len(items)} 条")
            return items
        except Exception as e:
            print(f"    ✗ 获取失败：{e}")
            return []
    
    def fetch_all(self, days: int = 1, strict_date_filter: bool = True) -> List[Dict]:
        """从所有来源获取新闻"""
        all_news = []
        
        for source_key in self.sources:
            if source_key in SOURCES:
                items = self.fetch_rss(source_key)
                all_news.extend(items)
        
        # 日期过滤
        if strict_date_filter and days > 0:
            cutoff = datetime.now() - timedelta(days=days)
            cutoff = cutoff.replace(hour=0, minute=0, second=0, microsecond=0)
            
            filtered_news = []
            for item in all_news:
                pub_date = parse_date(item.get("published", ""))
                if pub_date:
                    if pub_date.tzinfo:
                        pub_date = pub_date.replace(tzinfo=None)
                    if pub_date >= cutoff:
                        item["_parsed_date"] = pub_date
                        filtered_news.append(item)
                else:
                    if days > 1:
                        filtered_news.append(item)
            
            all_news = filtered_news
            print(f"\n日期过滤后: {len(all_news)} 条新闻（最近 {days} 天）")
        
        # 按日期排序
        all_news.sort(key=lambda x: x.get("_parsed_date", datetime.min), reverse=True)
        
        self.news_items = all_news
        return all_news
    
    def filter_by_category(self, categories: List[str]) -> List[Dict]:
        """按分类筛选"""
        return [item for item in self.news_items 
                if item.get("category") in categories]
    
    def search(self, keyword: str) -> List[Dict]:
        """关键词搜索"""
        keyword = keyword.lower()
        return [item for item in self.news_items
                if keyword in item.get("title", "").lower() 
                or keyword in item.get("summary", "").lower()]


class NewsFormatter:
    """格式化新闻输出"""
    
    def __init__(self, news_items: List[Dict]):
        self.news_items = news_items
        
    def to_markdown(self, format_type: str = "standard") -> str:
        if format_type == "newsletter":
            return self._to_newsletter_markdown()
        elif format_type == "summary":
            return self._to_summary_markdown()
        else:
            return self._to_standard_markdown()
    
    def _format_companies(self, companies: List[str]) -> str:
        """格式化公司标签"""
        if not companies:
            return ""
        return " · ".join([f"🏢 {c}" for c in companies[:3]])
    
    def _to_newsletter_markdown(self, title: str = "每日 AI 简报", intro: str = "") -> str:
        """简洁美观的新闻通讯格式"""
        today = datetime.now().strftime("%Y年%m月%d日")
        
        lines = [
            f"# {title}",
            "",
            f"📅 **{today}** | 🤖 精选 {len(self.news_items)} 条 AI 圈重要动态",
            "",
            "---",
            ""
        ]
        
        for i, item in enumerate(self.news_items, 1):
            # 来源标签
            source_tag = f"📰 {item['source']}"
            
            # 公司标签
            companies = self._format_companies(item.get("companies", []))
            meta = f"{source_tag}" + (f" | {companies}" if companies else "")
            
            # 摘要处理
            summary = item['summary'][:200] + "..." if len(item['summary']) > 200 else item['summary']
            # 移除 HTML 标签
            summary = re.sub(r'<[^>]+>', '', summary)
            
            lines.extend([
                f"### {i}. {item['title']}",
                "",
                f"{summary}",
                "",
                f"*{meta}*",
                f"[→ 阅读原文]({item['link']})",
                "",
                "---",
                ""
            ])
        
        lines.extend([
            "",
            "💡 *本简报由 AI 自动生成*",
            ""
        ])
        
        return "\n".join(lines)
    
    def _to_standard_markdown(self) -> str:
        """标准分类格式"""
        lines = [
            "# 🤖 AI 新闻日报",
            "",
            f"📅 {datetime.now().strftime('%Y-%m-%d')} | 共 {len(self.news_items)} 条",
            ""
        ]
        
        # 按分类分组
        by_category: Dict[str, List[Dict]] = {}
        for item in self.news_items:
            cat = item.get("category", "general")
            by_category.setdefault(cat, []).append(item)
        
        category_names = {
            "releases": "🚀 新发布",
            "research": "🔬 研究动态",
            "business": "💰 商业资讯",
            "products": "📱 产品更新",
            "community": "💬 社区动态",
            "general": "📰 综合"
        }
        
        for category, items in by_category.items():
            cn_name = category_names.get(category, category)
            lines.extend([f"## {cn_name}", ""])
            
            for item in items:
                companies = self._format_companies(item.get("companies", []))
                meta = f"📰 {item['source']}" + (f" | {companies}" if companies else "")
                
                lines.extend([
                    f"### {item['title']}",
                    "",
                    f"{item['summary'][:250]}...",
                    "",
                    f"*{meta}* | [阅读原文]({item['link']})",
                    ""
                ])
                
        return "\n".join(lines)
    
    def _to_summary_markdown(self) -> str:
        """简洁摘要格式"""
        lines = [
            "# AI 新闻摘要",
            "",
            f"*{datetime.now().strftime('%Y-%m-%d')} - 共 {len(self.news_items)} 条*",
            ""
        ]
        
        for item in self.news_items[:20]:
            companies = self._format_companies(item.get("companies", []))
            source_info = f"📰 {item['source']}"
            if companies:
                source_info += f" | {companies}"
            
            lines.append(f"• **{item['title']}** — *{source_info}*")
            
        return "\n".join(lines)
    
    def to_json(self) -> str:
        return json.dumps({
            "generated_at": datetime.now().isoformat(),
            "count": len(self.news_items),
            "items": self.news_items
        }, indent=2, ensure_ascii=False)
    
    def to_text(self) -> str:
        lines = [
            "AI 每日新闻",
            f"日期：{datetime.now().strftime('%Y-%m-%d')}",
            f"条数：{len(self.news_items)}",
            "=" * 50,
            ""
        ]
        
        for i, item in enumerate(self.news_items[:20], 1):
            companies = ", ".join(item.get("companies", [])) or "未知"
            lines.extend([
                f"{i}. {item['title']}",
                f"   来源：{item['source']} | 公司：{companies}",
                f"   链接：{item['link']}",
                ""
            ])
            
        return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description="AI 每日新闻")
    
    parser.add_argument("--date", choices=["today", "week", "month"], default="today")
    parser.add_argument("--days", type=int, default=1, help="回溯天数")
    parser.add_argument("--categories", help="分类筛选")
    parser.add_argument("--search", help="关键词搜索")
    parser.add_argument("--output", choices=["markdown", "json", "text"], default="markdown")
    parser.add_argument("--format", choices=["standard", "summary", "newsletter"], default="newsletter")
    parser.add_argument("--sources", help="指定新闻源")
    parser.add_argument("--save-to", help="保存路径")
    parser.add_argument("--max-items", type=int, default=15)
    parser.add_argument("--title", default="🤖 AI 每日简报")
    parser.add_argument("--intro", default="")
    parser.add_argument("--translate", action="store_true")
    parser.add_argument("--translate-fields", default="title,summary")
    parser.add_argument("--no-date-filter", action="store_true")
    parser.add_argument("--include-github", action="store_true", help="包含 GitHub 数据源")
    
    return parser.parse_args()


def main():
    args = parse_args()
    
    # 确定新闻源
    if args.sources:
        sources = args.sources.split(",")
    else:
        # 默认使用专业新闻网站（不包含 GitHub）
        sources = [
            "marktechpost",
            "mit-tech-review",
            "venturebeat-ai",
            "synced-review",
            "jiqizhixin",
            "qbitai",
        ]
    
    # 确定天数
    if args.days != 1:
        days = args.days
    else:
        days_map = {"today": 1, "week": 7, "month": 30}
        days = days_map.get(args.date, args.days)
    
    # 初始化翻译器
    translator = None
    if args.translate:
        if not TRANSLATOR_AVAILABLE:
            print("警告：未安装 translators 库，无法翻译")
        else:
            translator = NewsTranslator()
    
    # 获取新闻
    print(f"正在获取 AI 新闻（最近 {days} 天）...")
    print("=" * 50)
    
    fetcher = NewsFetcher(sources=sources, translator=translator)
    news = fetcher.fetch_all(days=days, strict_date_filter=not args.no_date_filter)
    
    # 筛选
    if args.categories:
        news = fetcher.filter_by_category(args.categories.split(","))
    if args.search:
        news = fetcher.search(args.search)
    
    news = news[:args.max_items]
    
    # 翻译
    if args.translate and translator and news:
        news = translator.translate_items(news, fields=args.translate_fields.split(","), max_items=args.max_items)
    
    print(f"\n最终输出: {len(news)} 条新闻")
    
    # 格式化
    formatter = NewsFormatter(news)
    
    if args.output == "json":
        output = formatter.to_json()
    elif args.output == "text":
        output = formatter.to_text()
    else:
        output = formatter.to_markdown(format_type=args.format)
    
    # 保存或输出
    if args.save_to:
        os.makedirs(os.path.dirname(args.save_to) or ".", exist_ok=True)
        with open(args.save_to, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"已保存至：{args.save_to}")
    else:
        print(output)


if __name__ == "__main__":
    main()
