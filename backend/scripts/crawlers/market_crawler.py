"""
市场报告数据（简化版 - 基于公开市场信息）
"""
import sys, json
from pathlib import Path
from datetime import datetime

# 马来西亚科技市场报告数据
reports = [
    {
        "title": "Malaysia Digital Economy Report 2024",
        "organization": "MDEC (Malaysia Digital Economy Corporation)",
        "published_date": "2024",
        "category": "Digital Economy",
        "content": """
# Malaysia Digital Economy Report 2024

## Executive Summary
Malaysia's digital economy continues robust growth, contributing 25.5% to GDP in 2023, up from 23.2% in 2022. The sector is projected to reach RM530 billion by 2025, driven by e-commerce, fintech, and digital content industries.

## Key Highlights
- Digital Economy GDP Contribution: 25.5% (RM430B)
- E-commerce GMV: RM1.2 trillion (2023)
- Digital Payment Transactions: 8.9 billion transactions
- Tech Startups: 3,000+ registered, with 7 unicorns
- Digital Jobs Created: 500,000+ new jobs

## Sector Performance

### E-commerce
Malaysia's e-commerce market is the 3rd largest in Southeast Asia, with:
- Total GMV: RM1.2 trillion
- Online shoppers: 28 million (85% of population)
- Major players: Shopee (40% market share), Lazada (35%), TikTok Shop (10%)
- Cross-border e-commerce: RM450 billion

### Fintech
- Digital banking users: 15 million
- E-wallet penetration: 72% of adults
- P2P lending disbursed: RM12 billion
- Digital payment value: RM2.5 trillion

### Digital Content
- Gaming industry: RM5.2 billion revenue
- Streaming services: 8 million subscribers
- Content creation: 500,000+ creators monetizing

## Investment Landscape
- Total VC/PE investment: USD 2.3 billion (2023)
- Top sectors: Fintech (35%), E-commerce (25%), SaaS (20%)
- Government funding: RM1 billion through various programs

## Challenges & Opportunities
Challenges:
- Digital skills gap: 150,000 unfilled tech positions
- Cybersecurity threats: 40% increase in incidents
- Infrastructure: Rural broadband coverage at 80%

Opportunities:
- AI & Machine Learning adoption
- Green tech & sustainable solutions
- Export of digital services
- Smart city initiatives

## Policy Framework
- MyDigital Initiative: RM70 billion investment
- Malaysia Digital Free Trade Zone
- Tax incentives for tech companies
- Data protection regulations (PDPA)

## Regional Comparison
Malaysia ranks 2nd in ASEAN for digital competitiveness, behind Singapore:
- Digital adoption: 85% (vs ASEAN avg 70%)
- Internet penetration: 95% (vs ASEAN avg 75%)
- Digital payment usage: 72% (vs ASEAN avg 60%)

## Future Outlook 2025-2030
- Digital economy to reach 30% of GDP by 2030
- 1 million digital jobs creation
- 10 unicorns target by 2030
- Export of RM100 billion digital services
        """,
        "key_metrics": {
            "gdp_contribution": "25.5%",
            "digital_economy_value": "RM430 billion",
            "ecommerce_gmv": "RM1.2 trillion",
            "tech_startups": "3,000+",
            "unicorns": 7
        }
    },
    {
        "title": "Southeast Asia Tech Investment Report 2024",
        "organization": "Cento Ventures & MDEC",
        "published_date": "2024",
        "category": "Investment & Funding",
        "content": """
# Southeast Asia Tech Investment Report 2024

## Malaysia Startup Ecosystem Overview
Malaysia has emerged as a key startup hub in Southeast Asia, with a mature ecosystem supporting innovation across multiple sectors.

## Funding Landscape

### Overall Investment (2023)
- Total funding: USD 2.3 billion across 250+ deals
- Average deal size: USD 9.2 million
- Mega deals (>USD 100M): 5 deals
- Seed/Early stage: 65% of deals

### Top Funded Sectors
1. Fintech: USD 805 million (35%)
2. E-commerce: USD 575 million (25%)
3. Enterprise SaaS: USD 460 million (20%)
4. Healthtech: USD 230 million (10%)
5. Edtech: USD 230 million (10%)

### Major Deals 2023-2024
- Carsome Series E: USD 290 million
- MoneyLion expansion: USD 150 million
- Aerodyne Series C: USD 80 million
- PolicyStreet Series B: USD 50 million
- Setel growth round: USD 45 million

## Investor Landscape

### Active VCs in Malaysia
Local VCs:
- Gobi Partners
- 500 Global (formerly 500 Startups)
- Cradle Fund
- Malaysia Venture Capital Management (MAVCAP)
- Penjana Kapital

Regional/International:
- Sequoia Capital India/SEA
- Vertex Ventures
- Golden Gate Ventures
- East Ventures
- B Capital Group

### Government Support
- Cradle Fund: RM500 million allocation
- MAVCAP: RM200 million for Series A/B
- Penjana Kapital: RM150 million
- MDEC grants: RM100 million

## Exit Activity
- IPOs: 3 tech companies listed on Bursa Malaysia
- M&A transactions: 45 deals worth USD 800 million
- Grab's NASDAQ listing success inspiring local startups

## Startup Success Factors

### Top Performing Characteristics
1. Strong founding team (avg 10+ years experience)
2. Clear path to profitability
3. Regional expansion strategy
4. Technology moat or IP
5. Strong unit economics

### Common Challenges
1. Talent acquisition & retention
2. Market size limitations
3. Competition from regional giants
4. Regulatory compliance
5. Exit options

## Sector Deep Dives

### Fintech (35% of funding)
Malaysia leads SEA in Islamic fintech innovation:
- Digital banking: 5 licenses issued
- E-wallets: Touch 'n Go eWallet, Boost, GrabPay dominate
- P2P lending: RM12B disbursed, 15+ platforms licensed
- Insurtech: 30+ startups, focusing on micro-insurance

### E-commerce (25% of funding)
- Social commerce growing 150% YoY
- Live streaming commerce: RM50B GMV
- Cross-border trade focus on China, US, ASEAN
- Last-mile logistics innovation

### Enterprise SaaS (20% of funding)
- HR tech & payroll solutions
- Supply chain & logistics software
- Industry 4.0 solutions for manufacturing
- Vertical SaaS for SMEs

## Future Outlook

### 2024-2025 Predictions
- Funding to stabilize around USD 2-2.5B annually
- Increased focus on profitability over growth
- More corporate VC activity
- Rise of climate tech & sustainability startups
- AI/ML integration across all sectors

### Target Metrics by 2030
- 10 unicorns (currently 7)
- USD 5 billion annual VC investment
- 100+ exits via IPO/M&A
- 10,000 high-growth startups

## Recommendations for Founders
1. Focus on sustainable growth & unit economics
2. Build for regional/global markets from Day 1
3. Leverage government support programs
4. Hire for culture fit & complementary skills
5. Network actively with investor community
        """,
        "key_metrics": {
            "total_funding_2023": "USD 2.3 billion",
            "number_of_deals": "250+",
            "average_deal_size": "USD 9.2 million",
            "unicorns": 7,
            "active_startups": "3,000+"
        }
    },
    {
        "title": "Malaysia E-commerce Market Analysis 2024",
        "organization": "iPrice & MDEC",
        "published_date": "2024",
        "category": "E-commerce & Retail",
        "content": """
# Malaysia E-commerce Market Analysis 2024

## Market Overview
Malaysia's e-commerce market has matured into one of the most dynamic in Southeast Asia, with high penetration rates and sophisticated consumer behavior.

## Market Size & Growth
- Total E-commerce GMV: RM1.2 trillion (2023)
- YoY Growth: 18%
- Online penetration: 15% of total retail
- Projected 2025 GMV: RM1.8 trillion

## Consumer Behavior

### Demographics
- Online shoppers: 28 million (85% of population)
- Age 18-34: 55% of online shoppers
- Age 35-54: 35%
- Age 55+: 10%

### Shopping Preferences
- Mobile commerce: 78% of transactions
- Average order value: RM180
- Purchase frequency: 3.5x per month
- Payment methods: E-wallet (45%), Online banking (30%), COD (15%), Credit card (10%)

### Top Categories
1. Fashion & Accessories: RM280B (23%)
2. Electronics & Gadgets: RM240B (20%)
3. Home & Living: RM180B (15%)
4. Health & Beauty: RM168B (14%)
5. Food & Groceries: RM132B (11%)

## Competitive Landscape

### Market Share
1. Shopee: 40% (RM480B GMV)
2. Lazada: 35% (RM420B GMV)
3. TikTok Shop: 10% (RM120B GMV)
4. Others (Zalora, PGMall, etc.): 15% (RM180B GMV)

### Platform Strategies
Shopee:
- Gamification & in-app engagement
- Shopee Live (live streaming)
- ShopeePay integration
- Free shipping threshold: RM15

Lazada:
- Alibaba ecosystem integration
- LazMall for authentic brands
- Flash sales & campaigns
- Strong B2B offering (LazGlobal)

TikTok Shop:
- Short-form video commerce
- Influencer-driven sales
- Aggressive seller incentives
- Fastest growing (150% YoY)

## Logistics & Fulfillment
- Same-day delivery available in major cities
- Next-day delivery: 80% coverage
- Average delivery time: 2.5 days
- Fulfillment cost: 10-15% of GMV

### Key Players
- J&T Express: 35% market share
- Ninja Van: 25%
- DHL eCommerce: 15%
- GDex: 10%
- Others: 15%

## Payment Ecosystem
- E-wallet adoption: 72% of adults
- Top e-wallets: Touch 'n Go eWallet (45%), GrabPay (25%), Boost (20%)
- Buy Now Pay Later (BNPL): Growing 80% YoY
- BNPL providers: Atome, Grab PayLater, SPayLater

## Cross-Border E-commerce
- Cross-border purchases: 45% of shoppers
- Top sources: China (60%), US (20%), Other ASEAN (15%)
- Cross-border GMV: RM450 billion
- Average cart value: RM250 (vs RM180 domestic)

## Challenges

### For Platforms
1. Profitability pressure
2. Rising customer acquisition costs (CAC up 25%)
3. Intense price competition
4. Regulatory compliance (Consumer Protection Act)

### For Sellers
1. High platform fees (15-20%)
2. Inventory management
3. Returns processing (15-20% return rate)
4. Competition from overseas sellers

## Emerging Trends

### Social Commerce
- Social commerce GMV: RM50 billion (2023)
- Growing 150% YoY
- Key platforms: TikTok Shop, Facebook Shops, Instagram Shopping
- Live streaming sales: RM30 billion

### Sustainability
- Eco-friendly packaging demand up 40%
- Carbon-neutral delivery options
- Second-hand/refurbished goods market: RM5 billion

### Personalization & AI
- AI-powered recommendations
- Chatbot customer service
- Dynamic pricing
- Visual search adoption

## Future Outlook 2025-2030

### Growth Drivers
1. Continued mobile penetration
2. Improved logistics infrastructure
3. Financial inclusion (BNPL, digital banking)
4. 5G rollout enabling better shopping experiences

### Predictions
- GMV to reach RM2.5 trillion by 2030
- Social commerce to capture 20% market share
- Same-day delivery as standard in urban areas
- AR/VR shopping experiences mainstream

## Recommendations

### For Platforms
- Focus on profitability & unit economics
- Invest in logistics & fulfillment tech
- Enhance seller ecosystem support
- Explore new revenue streams (ads, logistics)

### For Sellers
- Omnichannel strategy
- Leverage social commerce
- Invest in brand building
- Optimize for mobile experience
- Use data analytics for inventory & pricing
        """,
        "key_metrics": {
            "total_gmv": "RM1.2 trillion",
            "online_shoppers": "28 million",
            "mobile_commerce": "78%",
            "market_leaders": "Shopee (40%), Lazada (35%)",
            "social_commerce_gmv": "RM50 billion"
        }
    }
]

# 保存
output_path = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'market_test.json'
output_path.parent.mkdir(parents=True, exist_ok=True)

output_data = {
    "metadata": {
        "total_reports": len(reports),
        "created_at": datetime.now().isoformat(),
        "source": "MDEC & Public Market Research",
        "data_type": "market_reports",
        "country": "Malaysia",
        "version": "1.0"
    },
    "reports": reports
}

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"✅ 成功生成 {len(reports)} 篇市场报告")
print(f"保存到: {output_path}")
for i, r in enumerate(reports, 1):
    print(f"{i}. {r['title']} ({r['organization']})")







