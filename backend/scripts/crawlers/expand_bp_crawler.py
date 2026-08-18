"""
扩大BP模板规模 - 严格执行指令6-4
目标：10-15个BP模板（生成12个）
"""
import sys, json, logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from base_crawler import BaseCrawler

class ExpandedBPCrawler(BaseCrawler):
    def __init__(self, config=None):
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_bp_templates(self, count=12):
        """生成12个多样化的BP模板"""
        
        templates = [
            # 已有的3个
            {"type": "Tech Startup - SaaS", "industry": "Technology/SaaS", "stage": "Seed/Series A"},
            {"type": "E-commerce", "industry": "E-commerce/Retail", "stage": "Startup/Early Growth"},
            {"type": "Social Impact", "industry": "Social Impact/Non-Profit", "stage": "Startup/Foundation"},
            
            # 新增9个
            {"type": "Mobile App Startup", "industry": "Technology/Mobile", "stage": "Seed"},
            {"type": "AI/ML Startup", "industry": "Technology/AI", "stage": "Series A"},
            {"type": "Fintech Startup", "industry": "Fintech/Payments", "stage": "Seed/Series A"},
            {"type": "Healthtech Startup", "industry": "Healthcare/Technology", "stage": "Early Stage"},
            {"type": "Edtech Platform", "industry": "Education/Technology", "stage": "Growth"},
            {"type": "Food & Beverage", "industry": "F&B/Restaurant", "stage": "Startup"},
            {"type": "Marketplace Platform", "industry": "E-commerce/Marketplace", "stage": "Series A"},
            {"type": "B2B SaaS", "industry": "Enterprise Software", "stage": "Series A/B"},
            {"type": "Sustainable Business", "industry": "Green Tech/Sustainability", "stage": "Startup"}
        ]
        
        bp_list = []
        for i, t in enumerate(templates[:count], 1):
            bp = self._create_bp_template(t, i)
            bp_list.append(bp)
            self.logger.info(f"生成 {i}/{count}: {bp['template_name']}")
        
        return bp_list
    
    def _create_bp_template(self, template_type, index):
        """创建单个BP模板（简化版但完整）"""
        bp_type = template_type['type']
        industry = template_type['industry']
        stage = template_type['stage']
        
        template = {
            "template_name": f"{bp_type} Business Plan",
            "industry": industry,
            "stage": stage,
            "content": f"""
# BUSINESS PLAN: {bp_type}

## EXECUTIVE SUMMARY
[Company Name] is a {industry.lower()} company focused on [problem solution]. We are at the {stage} stage, seeking [funding amount] to achieve [key milestones].

**Key Highlights:**
- Market Size: $[X]B TAM
- Revenue Model: [Primary revenue streams]
- Current Stage: {stage}
- Funding Ask: $[Amount]
- Target: [Key metric] by [timeframe]

## PROBLEM STATEMENT
The {industry.split('/')[0]} industry faces significant challenges:
1. [Problem 1 with market data]
2. [Problem 2 with impact statistics]
3. [Problem 3 with customer pain points]

**Market Opportunity:** $[X]B market growing at [Y]% CAGR.

## SOLUTION
Our {bp_type.lower()} platform provides:

**Core Features:**
1. [Feature 1]: [Description and benefit]
2. [Feature 2]: [Description and benefit]
3. [Feature 3]: [Description and benefit]

**Competitive Advantages:**
- [Unique value proposition 1]
- [Proprietary technology/approach 2]
- [Market positioning advantage 3]

## MARKET ANALYSIS

### Target Market
**Primary Customer Segment:**
- Demographics: [Target audience details]
- Market Size: [Serviceable market size]
- Pain Points: [Specific problems we solve]

### Competition
| Competitor | Strengths | Weaknesses | Our Edge |
|-----------|-----------|------------|----------|
| Competitor A | [strength] | [weakness] | [our advantage] |
| Competitor B | [strength] | [weakness] | [our advantage] |

## BUSINESS MODEL

### Revenue Streams
1. **Primary Revenue ({{'80%' if 'SaaS' in bp_type else '70%'}})**
   - {'Subscription: $X/month per user' if 'SaaS' in bp_type or 'Platform' in bp_type else 'Product Sales: $X per unit'}
   - {'Professional Services: $X per project' if 'B2B' in bp_type else 'Premium Features: $X/month'}

2. **Secondary Revenue ({{20 if 'SaaS' in bp_type else 30}}%)**
   - [Additional revenue stream]
   - [Monetization strategy]

### Unit Economics
- Customer Acquisition Cost (CAC): $[X]
- Lifetime Value (LTV): $[Y]
- LTV:CAC Ratio: [Z]:1
- Gross Margin: [%]
- Payback Period: [X] months

### Go-to-Market Strategy
**Phase 1 (Months 0-6):** {{'Product-Led Growth' if 'SaaS' in bp_type else 'Market Entry'}}
- [Strategy 1]
- [Channel 1]
- [Tactic 1]

**Phase 2 (Months 6-18):** Scale
- [Growth strategy]
- [New channels]
- [Team expansion]

## FINANCIAL PROJECTIONS

### 3-Year Forecast
| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Revenue | $[X]K | $[Y]M | $[Z]M |
| Customers | [A] | [B] | [C] |
| Gross Profit | [%] | [%] | [%] |
| EBITDA | ($[X]K) | $[Y]K | $[Z]M |

### Funding Requirements
**{stage} Round: $[Amount]**
- Product Development: [%]
- Sales & Marketing: [%]
- Operations: [%]
- Working Capital: [%]

**Use of Funds:**
1. Engineering team (hiring [X] engineers): $[amount]
2. Marketing and customer acquisition: $[amount]
3. Operations and infrastructure: $[amount]
4. Reserve/contingency: $[amount]

## TEAM

### Founding Team
**[Founder 1] - CEO**
- Background: [Experience in industry]
- Expertise: [Key skills]

**[Founder 2] - {"CTO" if "Tech" in industry else "COO"}**
- Background: [Technical/operational experience]
- Expertise: [Core competencies]

### Advisors & Board
- [Advisor 1]: [Industry expert, credentials]
- [Advisor 2]: [Technical advisor, background]

### Hiring Plan
- Year 1: Hire [X] people (Engineering, Sales, Ops)
- Year 2: Expand to [Y] team members
- Year 3: Scale to [Z] employees

## RISKS & MITIGATION

### Key Risks
1. **Market Risk:** [Competitive pressure]
   - Mitigation: [Strategy to address]

2. **Execution Risk:** [Team/product challenges]
   - Mitigation: [Approach to manage]

3. **Financial Risk:** [Cash flow/funding]
   - Mitigation: [Contingency plan]

## MILESTONES & EXIT STRATEGY

### Key Milestones
- **Month 3:** [Early traction milestone]
- **Month 6:** [Product-market fit indicator]
- **Month 12:** [Revenue/growth target]
- **Month 18:** [Scale milestone]
- **Month 24:** [Series [Next] ready]

### Exit Strategy
- **Primary:** Acquisition by [Type of strategic buyer]
- **Secondary:** {"IPO (7-10 years)" if "Series" in stage else "Growth equity/strategic investment"}
- **Potential Acquirers:** [List 3-5 companies]

## APPENDIX
- Financial model (detailed)
- Market research data
- Customer testimonials/LOIs
- Technical specifications
- Team bios
            """,
            "tips": f"""
**使用建议 ({bp_type} BP):**

1. **Tailor to your audience**
   - VC version: Focus on growth potential and returns
   - Bank version: Emphasize stability and cash flow
   - Strategic partner version: Highlight synergies

2. **Data-driven approach**
   - Support all claims with data
   - Use credible sources for market research
   - Show clear path to profitability

3. **Clear differentiation**
   - Explain why you're different (not just better)
   - Demonstrate sustainable competitive advantage
   - Show defensibility of your position

4. **Realistic financials**
   - Conservative, base, optimistic scenarios
   - Clearly state assumptions
   - Show unit economics that make sense

5. **Strong team section**
   - Highlight relevant experience
   - Show complementary skills
   - Demonstrate ability to execute

6. **Risk awareness**
   - Proactively address potential concerns
   - Show you've thought through challenges
   - Demonstrate risk mitigation strategies

7. **Professional presentation**
   - Clean, consistent formatting
   - Visual aids (charts, graphs)
   - Error-free content

8. **Compelling narrative**
   - Tell a story, not just facts
   - Make it memorable
   - Show passion and vision

9. **Specific to {industry}**
   {'- Focus on recurring revenue and SaaS metrics' if 'SaaS' in bp_type else ''}
   {'- Highlight marketplace network effects' if 'Marketplace' in bp_type or 'Platform' in bp_type else ''}
   {'- Emphasize social impact alongside financial returns' if 'Social' in bp_type or 'Sustainable' in bp_type else ''}
   {'- Show regulatory compliance and data security' if 'Fintech' in bp_type or 'Health' in bp_type else ''}

10. **Action-oriented**
    - Clear ask (funding amount, partnership type)
    - Next steps outlined
    - Contact information prominent
            """,
            "source": "UniPulse Startup AI - Expanded Collection",
            "tags": [bp_type.lower().replace(' ', '-'), industry.lower().split('/')[0], stage.lower().replace('/', '-')],
            "scraped_at": datetime.now().isoformat(),
            "category": "business_plan",
            "subcategory": "template"
        }
        
        return template
    
    def scrape(self, num_templates=12):
        return self.generate_bp_templates(num_templates)
    
    def parse_page(self, soup, url):
        return {}
    
    def save_to_json(self, data, output_path):
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        output_data = {
            "metadata": {
                "total_templates": len(data),
                "created_at": datetime.now().isoformat(),
                "source": "UniPulse Startup AI - Expanded BP Collection",
                "data_type": "business_plan_templates",
                "version": "2.0"
            },
            "templates": data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"✅ 数据已保存到: {output_path}")

# 执行
crawler = ExpandedBPCrawler({'rate_limit': 1})
print("="*80)
print("📄 扩大BP模板规模 - 指令6-4")
print("目标：10-15个模板")
print("="*80)

bp_templates = crawler.scrape(12)
print(f"\n✅ 生成了 {len(bp_templates)} 个BP模板")

# 统计
from collections import Counter
industries = Counter(t['industry'].split('/')[0] for t in bp_templates)
stages = Counter(t['stage'] for t in bp_templates)

print(f"\n行业分布: {dict(industries)}")
print(f"阶段分布: {dict(stages)}")

# 保存
output_path = 'backend/data/crawled/bp_full_expanded.json'
crawler.save_to_json(bp_templates, output_path)
print(f"\n保存到: {output_path}")
print("="*80)







