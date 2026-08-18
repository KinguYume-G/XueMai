# 外部数据爬取完整方案
**UniPulse Asia AI工具箱数据补充计划**

**创建日期：** 2025-11-29  
**版本：** v1.0  
**状态：** 设计阶段

---

## 📋 目录
1. [可行性评估矩阵](#1-可行性评估矩阵)
2. [推荐数据源与替代方案](#2-推荐数据源与替代方案)
3. [爬虫架构设计](#3-爬虫架构设计)
4. [技术方案](#4-技术方案)
5. [时间估算](#5-时间估算)
6. [风险评估与缓解](#6-风险评估与缓解)
7. [数据导入RAG方案](#7-数据导入rag方案)
8. [实施路线图](#8-实施路线图)

---

## 1. 可行性评估矩阵

### 1.1 职业发展数据源

| 数据源 | 目标网站 | 合法性 | 技术难度 | API可用性 | 推荐度 | 备注 |
|-------|---------|--------|---------|-----------|--------|------|
| **薪资数据** | JobStreet | ⚠️ 中风险 | 🔴 高 | ❌ 无公开API | 🟡 中 | robots.txt禁止，需登录 |
| | **Glassdoor** | ⚠️ 中风险 | 🔴 高 | ❌ 无公开API | 🟡 中 | 反爬虫强，需登录 |
| | **PayScale** | ⚠️ 中风险 | 🟠 中 | ❌ 无公开API | 🟢 高 | 部分公开数据 |
| | **替代：人工收集** | ✅ 低风险 | 🟢 低 | N/A | 🟢 高 | 最稳妥方案 |
| **公司信息** | LinkedIn | 🔴 高风险 | 🔴 高 | ❌ 官方API需审批 | 🔴 低 | ToS明确禁止爬虫 |
| | Crunchbase | ⚠️ 中风险 | 🟠 中 | ⚠️ 付费API | 🟡 中 | 免费层限制严格 |
| | **替代：公开数据集** | ✅ 低风险 | 🟢 低 | N/A | 🟢 高 | Kaggle/GitHub开源 |
| **简历模板** | Indeed Career Guide | ⚠️ 中风险 | 🟠 中 | ❌ 无API | 🟡 中 | 少量内容可爬 |
| | The Muse | ⚠️ 中风险 | 🟠 中 | ❌ 无API | 🟡 中 | 部分内容公开 |
| | **替代：开源资源** | ✅ 低风险 | 🟢 低 | N/A | 🟢 高 | GitHub模板仓库 |
| **面试问题** | Glassdoor | 🔴 高风险 | 🔴 高 | ❌ 无API | 🔴 低 | 反爬虫机制强 |
| | LeetCode | 🔴 高风险 | 🔴 高 | ⚠️ 非官方API | 🔴 低 | ToS禁止爬虫 |
| | **替代：公开题库** | ✅ 低风险 | 🟢 低 | N/A | 🟢 高 | GitHub开源面试题 |

### 1.2 创业数据源

| 数据源 | 目标网站 | 合法性 | 技术难度 | API可用性 | 推荐度 | 备注 |
|-------|---------|--------|---------|-----------|--------|------|
| **BP模板** | Bplans.com | ⚠️ 中风险 | 🟠 中 | ❌ 无API | 🟡 中 | 版权保护内容 |
| | **替代：开源模板** | ✅ 低风险 | 🟢 低 | N/A | 🟢 高 | GitHub/Notion模板 |
| **市场分析** | Statista | 🔴 高风险 | 🔴 高 | ⚠️ 付费API | 🔴 低 | 付费墙，版权保护 |
| | CB Insights | 🔴 高风险 | 🔴 高 | ⚠️ 企业API | 🔴 低 | 高价格，限制多 |
| | **替代：公开报告** | ✅ 低风险 | 🟢 低 | N/A | 🟢 高 | 政府/学术机构报告 |
| **创业案例** | TechCrunch | ⚠️ 中风险 | 🟠 中 | ⚠️ 有RSS | 🟢 高 | RSS可用，合法 |
| | e27 | ⚠️ 中风险 | 🟠 中 | ⚠️ 可能有API | 🟢 高 | 东南亚焦点 |
| | **Tech in Asia** | ⚠️ 中风险 | 🟠 中 | ❌ 无API | 🟢 高 | 东南亚科技新闻 |

### 1.3 学术写作资源

| 数据源 | 目标网站 | 合法性 | 技术难度 | API可用性 | 推荐度 | 备注 |
|-------|---------|--------|---------|-----------|--------|------|
| **引用格式** | Purdue OWL | ✅ 低风险 | 🟢 低 | ❌ 无API | 🟢 高 | 教育资源，公开 |
| | **Citation Machine** | ✅ 低风险 | 🟢 低 | ❌ 无API | 🟢 高 | 公开引用指南 |
| **学术写作** | Academic Phrasebank | ✅ 低风险 | 🟢 低 | ❌ 无API | 🟢 高 | 学术资源，公开 |
| | Writing Center | ✅ 低风险 | 🟢 低 | ❌ 无API | 🟢 高 | 大学公开资源 |

### 1.4 可行性总结

**风险等级定义：**
- 🟢 **低风险（推荐）：** 公开教育资源、有明确许可、符合robots.txt
- 🟡 **中风险（谨慎）：** 需要登录、部分限制、灰色地带
- 🔴 **高风险（避免）：** ToS明确禁止、强反爬虫、法律风险

**推荐策略：**
1. **优先使用**：开源数据集、公开教育资源、RSS/API
2. **谨慎使用**：少量爬取公开内容（遵守robots.txt）
3. **绝对避免**：LinkedIn、Glassdoor、Statista付费内容

---

## 2. 推荐数据源与替代方案

### 2.1 职业发展数据【推荐方案】

#### 1️⃣ 薪资数据库
**主方案：组合策略**
```
数据来源：
✅ PayScale公开数据（爬取10-20个职位）
✅ Salary.com公开薪资指南（PDF下载）
✅ 马来西亚政府劳工统计（官方数据）
✅ GitHub开源薪资数据集（补充）

预期：150-200条薪资记录
风险：低
合法性：✅ 全部合法
```

**备选方案：**
- 手动收集：从公开的薪资调查报告中提取
- 学生众包：让APU学生匿名提交实习/工作薪资数据

#### 2️⃣ 公司信息库
**主方案：开源数据集**
```
数据来源：
✅ Kaggle - Malaysia Companies Dataset
✅ GitHub - Southeast Asia Startups List
✅ 公开的TechCrunch Crunchbase导出数据
✅ e27公司目录（符合robots.txt的页面）

预期：80-120家公司
风险：低
合法性：✅ 全部开源/公开
```

#### 3️⃣ 简历模板
**主方案：开源资源**
```
数据来源：
✅ GitHub - Awesome Resume Templates (MIT License)
✅ Overleaf - LaTeX Resume Templates (CC License)
✅ Resumake - 开源简历生成器
✅ Indeed Career Guide - 公开文章（少量爬取）

预期：30-40个模板+指南
风险：低
合法性：✅ 开源许可/公开资源
```

#### 4️⃣ 面试问题库
**主方案：开源题库**
```
数据来源：
✅ GitHub - Tech Interview Handbook (100k+ stars)
✅ GitHub - Coding Interview University
✅ GeeksforGeeks - 公开面试题（遵守robots.txt）
✅ 学术论文中的面试问题研究

预期：200-300个问题
风险：低
合法性：✅ 开源/学术资源
```

### 2.2 创业数据【推荐方案】

#### 5️⃣ 商业计划书模板
**主方案：开源模板**
```
数据来源：
✅ GitHub - Business Plan Templates
✅ SCORE.org - 免费BP模板（非营利组织）
✅ SBA.gov - 美国小企业管理局模板
✅ 学术机构的BP指南

预期：15-20个模板
风险：低
合法性：✅ 公开/非营利资源
```

#### 6️⃣ 市场分析报告
**主方案：公开报告**
```
数据来源：
✅ MDEC (Malaysia Digital Economy Corp) - 官方报告
✅ World Bank Open Data - 东南亚市场数据
✅ ASEAN统计局 - 行业数据
✅ 大学研究报告（公开发表的）

预期：25-35篇报告
风险：低
合法性：✅ 官方/学术公开
```

#### 7️⃣ 创业案例库
**主方案：RSS + 公开API**
```
数据来源：
✅ TechCrunch RSS Feed（合法）
✅ e27 RSS Feed（合法）
✅ Tech in Asia - 公开文章（robots.txt允许）
✅ VentureBeat API（如可申请）

预期：80-120篇文章
风险：低
合法性：✅ RSS订阅是合法的
```

### 2.3 学术写作资源【推荐方案】

#### 8️⃣ 引用格式规范
**主方案：教育资源**
```
数据来源：
✅ Purdue OWL - 完整引用指南
✅ APA Style官网 - 公开示例
✅ IEEE Citation Guidelines
✅ Harvard Referencing Guide

预期：完整的引用格式库
风险：极低
合法性：✅ 教育资源，明确允许
```

#### 9️⃣ 学术写作指南
**主方案：大学公开资源**
```
数据来源：
✅ Academic Phrasebank (Manchester Uni)
✅ MIT Writing Center
✅ Stanford Writing Center
✅ 各大学的公开Writing Guide

预期：15-25篇指南
风险：极低
合法性：✅ 教育机构公开资源
```

---

## 3. 爬虫架构设计

### 3.1 系统架构图（文字描述）

```
┌─────────────────────────────────────────────────────────────┐
│                    数据采集调度中心                            │
│                   (Scrapy + Celery)                          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  职业数据     │   │  创业数据     │   │  学术资源     │
│  采集器       │   │  采集器       │   │  采集器       │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
            ┌─────────────────────────────┐
            │    数据清洗与标准化层         │
            │  - 去重                      │
            │  - 格式统一                  │
            │  - 质量验证                  │
            └─────────────────────────────┘
                            ▼
            ┌─────────────────────────────┐
            │      数据存储层               │
            │  - Raw Data (JSON)           │
            │  - Processed Data (JSON)     │
            │  - Metadata (CSV)            │
            └─────────────────────────────┘
                            ▼
            ┌─────────────────────────────┐
            │    RAG向量化导入              │
            │  - Text Chunking             │
            │  - Embedding Generation      │
            │  - Supabase Import           │
            └─────────────────────────────┘
```

### 3.2 模块化设计

#### 模块1：数据采集层
```
scrapers/
├── __init__.py
├── base_scraper.py          # 基础爬虫类
├── career/
│   ├── __init__.py
│   ├── salary_scraper.py    # 薪资数据爬虫
│   ├── company_scraper.py   # 公司信息爬虫
│   ├── resume_scraper.py    # 简历模板爬虫
│   └── interview_scraper.py # 面试题爬虫
├── startup/
│   ├── __init__.py
│   ├── bp_scraper.py        # BP模板爬虫
│   ├── market_scraper.py    # 市场报告爬虫
│   └── news_scraper.py      # 创业新闻爬虫（RSS）
└── academic/
    ├── __init__.py
    ├── citation_scraper.py  # 引用格式爬虫
    └── writing_scraper.py   # 学术写作爬虫
```

#### 模块2：数据处理层
```
processors/
├── __init__.py
├── cleaner.py               # 数据清洗
├── validator.py             # 数据验证
├── normalizer.py            # 格式标准化
└── deduplicator.py          # 去重
```

#### 模块3：存储层
```
storage/
├── __init__.py
├── json_storage.py          # JSON存储管理
├── csv_storage.py           # CSV元数据管理
└── cache_manager.py         # 缓存管理
```

#### 模块4：RAG导入层
```
rag_import/
├── __init__.py
├── chunker.py               # 文本分块
├── embedder.py              # 向量化
└── importer.py              # 导入Supabase
```

### 3.3 并发策略

**可以并行爬取的数据源：**
```python
PARALLEL_GROUP_1 = [
    'career/salary',       # 无依赖
    'career/company',      # 无依赖
    'startup/bp',          # 无依赖
    'academic/citation',   # 无依赖
]

PARALLEL_GROUP_2 = [
    'career/resume',       # 无依赖
    'career/interview',    # 无依赖
    'startup/market',      # 无依赖
    'academic/writing',    # 无依赖
]

SEQUENTIAL_GROUP = [
    'startup/news',        # RSS有请求限制
]
```

**并发配置：**
- Group 1: 4个线程同时运行
- Group 2: 4个线程同时运行  
- Sequential: 1个线程，延迟2秒/请求

### 3.4 反爬虫对策

#### 策略1：请求频率控制
```python
RATE_LIMITS = {
    'low_risk': 1,      # 1秒/请求（教育资源）
    'medium_risk': 3,   # 3秒/请求（公开网站）
    'high_risk': 10,    # 10秒/请求（谨慎爬取）
}
```

#### 策略2：User-Agent轮换
```python
USER_AGENTS = [
    'Mozilla/5.0 (Educational Research Bot)',
    'Mozilla/5.0 (Data Collection for Academic Use)',
    # 10+ 真实浏览器UA
]
```

#### 策略3：代理池（可选）
- 仅用于高风险数据源
- 使用免费代理池（ProxyMesh、ScraperAPI免费层）
- 成本控制：避免付费代理

#### 策略4：失败重试
```python
RETRY_CONFIG = {
    'max_retries': 3,
    'backoff_factor': 2,  # 指数退避
    'status_codes': [429, 500, 502, 503, 504]
}
```

---

## 4. 技术方案

### 4.1 技术栈选择

| 组件 | 技术选择 | 理由 |
|-----|---------|------|
| **Web Scraping** | Scrapy | 成熟、高效、内置中间件 |
| **HTTP Requests** | requests + aiohttp | 简单场景用requests，异步用aiohttp |
| **HTML解析** | BeautifulSoup4 + lxml | 灵活、容易调试 |
| **RSS解析** | feedparser | RSS标准库 |
| **数据清洗** | pandas | 数据处理标准 |
| **任务调度** | Celery (可选) | 如需分布式 |
| **数据存储** | JSON + CSV | 简单、可读性强 |
| **向量化** | Ollama (nomic-embed-text) | 已有基础设施 |
| **错误监控** | Python logging | 内置，无需额外依赖 |

### 4.2 类设计结构

#### BaseScra
per - 基础爬虫类
```python
class BaseScraper(ABC):
    """所有爬虫的基类"""
    
    def __init__(self, config):
        self.config = config
        self.session = self._init_session()
        self.rate_limiter = RateLimiter(config['rate_limit'])
        
    @abstractmethod
    def scrape(self) -> List[Dict]:
        """执行爬取，返回结构化数据"""
        pass
    
    def _init_session(self):
        """初始化requests session，设置UA、重试等"""
        pass
    
    def _save_raw(self, data, filename):
        """保存原始数据"""
        pass
    
    def validate_robots_txt(self, url) -> bool:
        """验证是否允许爬取"""
        pass
```

#### DataCleaner - 数据清洗类
```python
class DataCleaner:
    """统一的数据清洗接口"""
    
    def remove_duplicates(self, data: List[Dict]) -> List[Dict]:
        """去重"""
        pass
    
    def normalize_fields(self, data: List[Dict]) -> List[Dict]:
        """字段标准化"""
        pass
    
    def validate_quality(self, data: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """质量验证，返回(valid, invalid)"""
        pass
```

#### RAGImporter - RAG导入类
```python
class RAGImporter:
    """导入数据到RAG系统"""
    
    def chunk_text(self, text: str) -> List[str]:
        """文本分块"""
        pass
    
    def generate_embeddings(self, chunks: List[str]) -> List[np.array]:
        """生成向量"""
        pass
    
    def import_to_rag(self, documents: List[Dict]) -> int:
        """导入到Supabase，返回导入数量"""
        pass
```

### 4.3 错误处理策略

#### 三层错误处理
```python
# Layer 1: 网络错误
try:
    response = self.session.get(url, timeout=10)
except (requests.Timeout, requests.ConnectionError) as e:
    logger.warning(f"网络错误: {e}, 将重试")
    # 进入重试队列

# Layer 2: HTTP错误
if response.status_code == 429:
    logger.warning("触发限流，延长等待时间")
    time.sleep(60)
    # 重试
elif response.status_code >= 500:
    logger.error("服务器错误，跳过此URL")
    # 记录失败URL

# Layer 3: 解析错误
try:
    data = self.parse(response.content)
except (AttributeError, KeyError) as e:
    logger.error(f"解析失败: {e}")
    # 保存原始HTML用于调试
    self.save_debug_html(response.content)
```

### 4.4 数据存储格式

#### Raw Data（原始数据）
```json
{
  "source": "salary_data",
  "scraped_at": "2025-11-29T10:00:00Z",
  "url": "https://example.com/salary",
  "raw_html": "...",
  "metadata": {
    "scraper_version": "1.0",
    "success": true
  }
}
```

#### Processed Data（处理后数据）
```json
{
  "id": "sal_001",
  "category": "career/salary",
  "title": "Software Engineer Salary in Malaysia",
  "content": {
    "position": "Software Engineer",
    "salary_range": "RM 4,000 - RM 8,000",
    "experience": "2-5 years",
    "location": "Kuala Lumpur",
    "company_size": "50-200 employees"
  },
  "source_url": "https://example.com",
  "processed_at": "2025-11-29T10:05:00Z",
  "quality_score": 0.95
}
```

#### Metadata（元数据）
```csv
id,category,source,status,scraped_at,quality_score,imported_to_rag
sal_001,career/salary,payscale,success,2025-11-29,0.95,true
sal_002,career/salary,salary_com,failed,2025-11-29,0.00,false
```

---

## 5. 时间估算

### 5.1 开发阶段时间

| 阶段 | 任务 | 预计时间 | 前置条件 |
|-----|------|---------|---------|
| **Phase 1** | 基础架构搭建 | 2-3天 | 无 |
| | - BaseScraper类 | 0.5天 | |
| | - 数据清洗模块 | 0.5天 | |
| | - 存储模块 | 0.5天 | |
| | - 配置管理 | 0.5天 | |
| **Phase 2** | 职业数据爬虫 | 4-5天 | Phase 1完成 |
| | - 薪资数据爬虫 | 1天 | |
| | - 公司信息爬虫 | 1天 | |
| | - 简历模板爬虫 | 1天 | |
| | - 面试题爬虫 | 1天 | |
| **Phase 3** | 创业数据爬虫 | 3-4天 | Phase 1完成 |
| | - BP模板爬虫 | 1天 | |
| | - 市场报告爬虫 | 1天 | |
| | - 创业新闻爬虫(RSS) | 1天 | |
| **Phase 4** | 学术资源爬虫 | 2天 | Phase 1完成 |
| | - 引用格式爬虫 | 1天 | |
| | - 学术写作爬虫 | 1天 | |
| **Phase 5** | 数据清洗与质检 | 2-3天 | Phase 2-4完成 |
| **Phase 6** | RAG导入开发 | 2天 | Phase 5完成 |
| **Phase 7** | 测试与调试 | 2-3天 | 所有阶段完成 |
| **总计** | | **17-20天** | |

### 5.2 数据采集时间

| 数据源 | 目标数量 | 爬取速度 | 预计时间 | 备注 |
|-------|---------|---------|---------|------|
| 薪资数据 | 150条 | 20条/小时 | 7-8小时 | 需多次访问 |
| 公司信息 | 100家 | 30家/小时 | 3-4小时 | 开源数据集 |
| 简历模板 | 30个 | 15个/小时 | 2小时 | 下载模板 |
| 面试题 | 200个 | 50个/小时 | 4小时 | 批量抓取 |
| BP模板 | 20个 | 10个/小时 | 2小时 | PDF下载 |
| 市场报告 | 30篇 | 5篇/小时 | 6小时 | PDF处理 |
| 创业新闻 | 100篇 | 30篇/小时 | 3-4小时 | RSS订阅 |
| 引用格式 | 5个标准 | 快速 | 1小时 | 静态页面 |
| 学术写作 | 20篇 | 10篇/小时 | 2小时 | 教育资源 |
| **总计** | | | **30-35小时** | 可并行运行 |

### 5.3 总体时间线

```
Week 1: 基础架构 + 职业数据爬虫开发
  Day 1-3: 基础架构搭建
  Day 4-7: 职业数据爬虫开发

Week 2: 创业数据 + 学术资源爬虫开发
  Day 8-11: 创业数据爬虫开发
  Day 12-13: 学术资源爬虫开发
  Day 14: Buffer（处理意外情况）

Week 3: 数据采集 + 清洗 + RAG导入
  Day 15-16: 执行数据采集（并行）
  Day 17-18: 数据清洗与质检
  Day 19: RAG导入开发
  Day 20: 执行RAG导入

Week 4: 测试 + 优化
  Day 21-22: 全流程测试
  Day 23: 优化与Bug修复
  Day 24-25: 文档编写
```

**总计：25-30天（4-5周）**

---

## 6. 风险评估与缓解

### 6.1 风险矩阵

| 风险 | 概率 | 影响 | 风险等级 | 缓解措施 |
|-----|------|------|---------|---------|
| **被目标网站封IP** | 中 | 高 | 🟠 中 | 降低爬取频率、使用代理池 |
| **数据格式变化** | 中 | 中 | 🟠 中 | 定期监控、版本控制 |
| **法律风险** | 低 | 高 | 🟡 低-中 | 仅爬取公开资源、遵守robots.txt |
| **数据质量不佳** | 中 | 中 | 🟠 中 | 多源验证、人工抽检 |
| **API限额耗尽** | 低 | 中 | 🟢 低 | 使用免费层、备用方案 |
| **依赖库版本冲突** | 低 | 低 | 🟢 低 | 使用虚拟环境、锁定版本 |

### 6.2 数据源失败备选方案

#### Scenario 1: 薪资数据全部失败
**备选方案：**
1. 使用马来西亚政府官方劳工统计数据
2. 手动收集20-30个代表性职位的薪资范围
3. 使用APU校友匿名薪资调查数据

**最小可用数据集：**
- 20个核心职位的薪资范围
- 来源：政府统计 + 公开报告

#### Scenario 2: 公司信息无法获取
**备选方案：**
1. 从TechCrunch文章中提取公司信息
2. 使用LinkedIn公开的公司页面（不登录状态）
3. 手动整理马来西亚科技公司名录

**最小可用数据集：**
- 50家代表性公司基本信息
- 来源：新闻报道 + 公开名录

#### Scenario 3: 简历模板版权问题
**备选方案：**
1. 使用完全开源的LaTeX模板（MIT/CC License）
2. 创建自己的简历模板（基于最佳实践）
3. 使用APU Career Center的模板（获得许可）

**最小可用数据集：**
- 10个基础简历模板
- 来源：开源仓库 + 自创模板

#### Scenario 4: 创业新闻RSS失效
**备选方案：**
1. 使用News API（免费层）
2. 手动收集近期重要创业新闻
3. 使用Google News RSS

**最小可用数据集：**
- 30-50篇代表性创业文章
- 来源：News API + 手动收集

### 6.3 最小可行数据集（MVP）

如果**全部外部数据源失败**，最小可用数据集为：

```
职业发展数据 (MVP):
- 20个职位薪资参考（政府数据）
- 30家马来西亚科技公司（手动整理）
- 10个简历模板（开源）
- 50个面试问题（GitHub开源题库）

创业数据 (MVP):
- 5个BP模板（政府/非营利组织）
- 10篇市场报告（政府/学术）
- 30篇创业文章（手动收集）

学术写作 (MVP):
- 完整引用格式指南（Purdue OWL）
- 10篇学术写作指南（大学公开资源）

总计：~165条高质量数据
```

**MVP标准：**
- 每个AI功能至少有15-30条相关数据
- 数据来源100%合法
- 质量评分>0.8

---

## 7. 数据导入RAG方案

### 7.1 数据转换流程

```
原始数据 (JSON/CSV)
    ↓
统一格式转换
    ↓
内容提取与富化
    ↓
文本分块 (Chunking)
    ↓
向量化 (Embedding)
    ↓
导入数据库 (AIDocument + AIChunk + AIEmbedding)
    ↓
质量验证
```

### 7.2 统一数据格式

#### 标准Document Schema
```python
{
  "doc_id": "career_sal_001",
  "doc_type": "career",  # career/startup/academic
  "category": "salary",  # salary/company/resume/interview/...
  "title": "Software Engineer Salary in KL",
  "content": "Full text content...",
  "metadata": {
    "source": "payscale",
    "url": "https://...",
    "scraped_at": "2025-11-29",
    "tags": ["salary", "software", "malaysia"],
    "quality_score": 0.95
  }
}
```

### 7.3 Chunking策略

#### 按数据类型分块

| 数据类型 | Chunk策略 | Chunk大小 | Overlap |
|---------|----------|----------|---------|
| **薪资数据** | 按职位分块 | 300-400字符 | 50字符 |
| **公司信息** | 按公司分块 | 400-500字符 | 50字符 |
| **简历模板** | 按部分分块 | 500-700字符 | 100字符 |
| **面试题** | 按问题分块 | 200-300字符 | 30字符 |
| **BP模板** | 按章节分块 | 600-800字符 | 100字符 |
| **市场报告** | 按段落分块 | 500-700字符 | 100字符 |
| **创业新闻** | 按文章分块 | 600-800字符 | 100字符 |
| **引用格式** | 按格式分块 | 300-400字符 | 50字符 |
| **学术写作** | 按主题分块 | 500-700字符 | 100字符 |

### 7.4 导入脚本结构

```python
# scripts/import_external_data.py

class ExternalDataImporter:
    """导入外部爬取的数据到RAG系统"""
    
    def __init__(self):
        self.rag_engine = RAGEngine()
        self.chunk_config = self._load_chunk_config()
        
    def import_category(self, category: str):
        """导入特定类别的数据"""
        # 1. 加载处理后的数据
        data = self.load_processed_data(category)
        
        # 2. 转换为统一格式
        documents = self.convert_to_documents(data)
        
        # 3. 分块
        chunked_docs = self.chunk_documents(documents)
        
        # 4. 生成向量
        embeddings = self.generate_embeddings(chunked_docs)
        
        # 5. 导入数据库
        self.import_to_db(documents, chunked_docs, embeddings)
        
        # 6. 验证
        self.validate_import(category)
        
    def validate_import(self, category: str):
        """验证导入质量"""
        # 检查点1: 数量一致性
        # 检查点2: 向量质量
        # 检查点3: 检索测试
        pass
```

### 7.5 质量验证

#### 验证检查清单
```python
VALIDATION_CHECKS = {
    'count_consistency': {
        'check': 'AIChunk.count() == AIEmbedding.count()',
        'critical': True
    },
    'vector_quality': {
        'check': 'All embeddings have valid 768-dim vectors',
        'critical': True
    },
    'retrieval_test': {
        'check': 'Test queries return relevant results',
        'critical': True
    },
    'metadata_completeness': {
        'check': 'All required metadata fields present',
        'critical': False
    },
    'content_length': {
        'check': 'Chunk lengths within acceptable range',
        'critical': False
    }
}
```

#### 测试查询
```python
TEST_QUERIES = {
    'career': [
        "Software Engineer薪资in Malaysia",
        "如何写一份好简历",
        "常见的技术面试问题"
    ],
    'startup': [
        "如何写商业计划书",
        "东南亚市场规模",
        "成功的创业案例"
    ],
    'academic': [
        "APA引用格式怎么写",
        "学术论文写作技巧"
    ]
}
```

### 7.6 导入流程时间估算

| 步骤 | 数据量 | 预计时间 | 说明 |
|-----|-------|---------|------|
| 数据转换 | ~1000条 | 30分钟 | Python脚本处理 |
| 文本分块 | ~1000条 | 15分钟 | RecursiveCharacterTextSplitter |
| 向量化 | ~3000 chunks | 2-3小时 | Ollama生成，约1秒/chunk |
| 数据库导入 | ~3000条 | 30分钟 | Django ORM批量插入 |
| 质量验证 | 全部 | 15分钟 | 自动化测试 |
| **总计** | | **4-5小时** | |

---

## 8. 实施路线图

### 8.1 Phase 1: 准备与架构（Week 1-2）

#### Week 1: 基础设施
- [ ] Day 1-2: 环境搭建、依赖安装
  ```bash
  pip install scrapy beautifulsoup4 feedparser pandas aiohttp
  ```
- [ ] Day 3-4: BaseScraper类开发
- [ ] Day 5-6: 数据清洗模块开发
- [ ] Day 7: 存储模块与配置管理

#### Week 2: 第一批爬虫
- [ ] Day 8: 学术资源爬虫（最简单，先完成）
  - Purdue OWL引用格式
  - Academic Phrasebank
- [ ] Day 9-10: 简历模板爬虫
  - GitHub开源模板
  - Overleaf模板
- [ ] Day 11-12: 面试题爬虫
  - Tech Interview Handbook
  - GeeksforGeeks（遵守robots.txt）
- [ ] Day 13-14: 测试与调试第一批爬虫

### 8.2 Phase 2: 核心数据采集（Week 3-4）

#### Week 3: 职业数据
- [ ] Day 15-16: 薪资数据爬虫
  - PayScale公开数据
  - 政府劳工统计
- [ ] Day 17-18: 公司信息爬虫
  - Kaggle数据集下载
  - GitHub开源列表
- [ ] Day 19: 数据清洗与验证
- [ ] Day 20-21: 创业新闻爬虫（RSS）
  - TechCrunch RSS
  - e27 RSS
  - Tech in Asia

#### Week 4: 创业资源
- [ ] Day 22: BP模板爬虫
  - SCORE.org
  - GitHub开源模板
- [ ] Day 23-24: 市场报告爬虫
  - MDEC官方报告
  - World Bank数据
- [ ] Day 25: 数据整合与质检
- [ ] Day 26-27: 全部数据清洗与标准化
- [ ] Day 28: Buffer（处理问题）

### 8.3 Phase 3: RAG导入与验证（Week 5）

- [ ] Day 29: RAG导入脚本开发
- [ ] Day 30: 执行批量导入
- [ ] Day 31: 质量验证
  - 数量一致性检查
  - 向量质量检查
  - 检索功能测试
- [ ] Day 32: 优化与修复
- [ ] Day 33: 最终测试
- [ ] Day 34-35: 文档编写与交付

### 8.4 里程碑检查点

| 里程碑 | 日期 | 交付物 | 验收标准 |
|-------|------|--------|---------|
| **M1: 基础完成** | Week 1结束 | 基础架构 | 代码可运行、有单元测试 |
| **M2: 学术数据完成** | Week 2结束 | 学术资源数据 | 20+篇指南已采集 |
| **M3: 职业数据完成** | Week 3结束 | 职业发展数据 | 200+条数据已清洗 |
| **M4: 创业数据完成** | Week 4结束 | 创业资源数据 | 100+条数据已验证 |
| **M5: RAG导入完成** | Week 5中 | 全部数据入库 | 检索测试通过 |
| **M6: 项目交付** | Week 5结束 | 完整系统 | 所有功能可用 |

---

## 9. 成本估算

### 9.1 时间成本
- **开发时间：** 17-20天（约140-160小时）
- **数据采集：** 30-35小时
- **测试与优化：** 20-25小时
- **总计：** ~200小时

### 9.2 技术成本
| 项目 | 成本 | 说明 |
|-----|------|------|
| 服务器/VPS | $0 | 使用本地机器 |
| 代理服务 | $0-10 | 仅在必要时使用免费层 |
| API费用 | $0 | 仅使用免费API |
| 存储 | $0 | 本地存储足够 |
| **总计** | **$0-10** | 几乎零成本 |

---

## 10. 成功指标

### 10.1 数量指标
- ✅ 职业数据：≥400条（薪资150+公司100+简历30+面试200）
- ✅ 创业数据：≥150条（BP20+报告30+新闻100）
- ✅ 学术资源：≥35篇（引用5+写作30）
- ✅ **总计：≥585条高质量数据**

### 10.2 质量指标
- ✅ 数据来源合法率：100%
- ✅ 数据完整性：>95%（所有必填字段完整）
- ✅ 去重率：<5%（重复数据<5%）
- ✅ RAG检索相关性：>0.75（测试查询平均相似度）

### 10.3 功能指标
- ✅ Career AI：支持4/4功能（薪资查询、公司推荐、简历优化、面试准备）
- ✅ Startup AI：支持4/4功能（BP写作、市场分析、案例学习、融资建议）
- ✅ Academic Writing AI：支持4/4功能（引用格式、写作指导、查重、改进建议）

---

## 11. 附录

### 11.1 推荐的Python包
```txt
# requirements_scraping.txt
scrapy==2.11.0
beautifulsoup4==4.12.2
lxml==4.9.3
requests==2.31.0
aiohttp==3.9.1
feedparser==6.0.10
pandas==2.1.4
selenium==4.15.2  # 仅在需要JS渲染时
fake-useragent==1.4.0
python-dotenv==1.0.0
tqdm==4.66.1  # 进度条
```

### 11.2 配置文件示例
```yaml
# config/scraper_config.yaml
scrapers:
  career:
    salary:
      enabled: true
      sources:
        - payscale
        - salary_com
      rate_limit: 3  # seconds
      max_pages: 10
    
  startup:
    news:
      enabled: true
      rss_feeds:
        - https://techcrunch.com/feed/
        - https://e27.co/feed/
      update_frequency: daily
      
  academic:
    citation:
      enabled: true
      sources:
        - purdue_owl
        - apa_style
      rate_limit: 1
```

### 11.3 robots.txt检查脚本
```python
# utils/robots_checker.py
from urllib.robotparser import RobotFileParser

def check_robots_txt(url, user_agent="*"):
    """检查URL是否允许爬取"""
    rp = RobotFileParser()
    rp.set_url(f"{url}/robots.txt")
    rp.read()
    return rp.can_fetch(user_agent, url)
```

---

## 12. 总结与建议

### 12.1 核心策略
1. **合法优先**：100%使用合法数据源，避免任何法律风险
2. **开源优先**：优先使用开源数据集和公开教育资源
3. **质量优先**：宁愿数据少但质量高，不要大量低质量数据
4. **渐进式**：先完成MVP（最小可用数据集），再逐步扩充

### 12.2 推荐执行顺序
```
1️⃣ Week 1-2: 学术资源 + 简历模板（最简单、最合法）
   → 验证整个流程可行

2️⃣ Week 3: 面试题 + 创业新闻（开源+RSS，风险低）
   → 积累经验

3️⃣ Week 4: 薪资数据 + 公司信息（稍有难度）
   → 核心价值数据

4️⃣ Week 5: RAG导入 + 测试（整合所有数据）
   → 完成闭环
```

### 12.3 关键成功因素
- ✅ 严格遵守robots.txt和ToS
- ✅ 合理的请求频率（避免被封）
- ✅ 完善的错误处理（确保稳定性）
- ✅ 数据质量验证（确保可用性）
- ✅ 详细的日志记录（便于调试）

### 12.4 风险提示
⚠️ **不要做的事：**
- ❌ 不要爬取LinkedIn、Glassdoor等明确禁止的网站
- ❌ 不要使用他人的付费API key
- ❌ 不要绕过登录墙或付费墙
- ❌ 不要爬取版权保护的内容（如付费报告）

✅ **要做的事：**
- ✅ 使用开源数据集
- ✅ 使用RSS/Atom订阅
- ✅ 使用公开教育资源
- ✅ 尊重网站的robots.txt

---

**文档版本：** 1.0  
**最后更新：** 2025-11-29  
**作者：** AI Assistant  
**审核状态：** 待审核

