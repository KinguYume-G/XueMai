"""
公司信息爬虫
基于公开公司信息生成马来西亚公司数据
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent))
from base_crawler import BaseCrawler


class CompanyCrawler(BaseCrawler):
    """公司信息爬虫"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 马来西亚公司数据（基于公开信息）
        self.companies = self._generate_company_data()
    
    def _generate_company_data(self) -> List[Dict]:
        """
        生成马来西亚公司信息数据
        基于公开的公司信息和市场数据
        """
        companies = [
            # Technology Companies
            {
                "company_name": "Grab Holdings",
                "industry": "Technology/Ride-Hailing",
                "size": "10,000+ employees",
                "location": "Kuala Lumpur, Malaysia (Regional HQ)",
                "description": "Grab is Southeast Asia's leading superapp, providing ride-hailing, food delivery, payment solutions, and financial services. Founded in 2012, Grab operates across 8 countries in the region. The company went public on NASDAQ in 2021 through a SPAC merger valued at $40B. Grab has transformed urban mobility and digital payments in Southeast Asia, serving millions of users daily.",
                "founded": "2012",
                "website": "www.grab.com",
                "specialties": ["Ride-hailing", "Food Delivery", "Digital Payments", "Fintech"],
                "source": "Public Information"
            },
            {
                "company_name": "Carsome",
                "industry": "E-commerce/Automotive",
                "size": "1,000-5,000 employees",
                "location": "Petaling Jaya, Selangor",
                "description": "Carsome is Southeast Asia's largest integrated car e-commerce platform. Founded in 2015, the company provides end-to-end solutions for buying and selling used cars, including inspection, refurbishment, financing, and warranty. Carsome has raised over $450M in funding and operates in Malaysia, Indonesia, Thailand, and Singapore. The platform has facilitated over 300,000 car transactions.",
                "founded": "2015",
                "website": "www.carsome.my",
                "specialties": ["Automotive E-commerce", "Used Cars", "Auto Financing", "Car Inspection"],
                "source": "Public Information"
            },
            {
                "company_name": "Aerodyne Group",
                "industry": "Technology/Drones & AI",
                "size": "500-1,000 employees",
                "location": "Cyberjaya, Selangor",
                "description": "Aerodyne is a global leader in drone-based data services and AI-powered analytics. Founded in 2014, the company provides enterprise drone solutions for industries including oil & gas, utilities, telecommunications, and construction. Aerodyne has conducted over 1 million flights across 50+ countries and has raised over $50M in funding. The company is recognized as a World Economic Forum Technology Pioneer.",
                "founded": "2014",
                "website": "www.aerodyne.group",
                "specialties": ["Drone Services", "AI Analytics", "Industrial Inspections", "Geospatial Data"],
                "source": "Public Information"
            },
            {
                "company_name": "MoneyLion Malaysia",
                "industry": "Fintech/Digital Banking",
                "size": "100-500 employees",
                "location": "Kuala Lumpur, Malaysia",
                "description": "MoneyLion is a digital financial services platform offering mobile banking, lending, and investment products. The company uses AI and machine learning to provide personalized financial recommendations. MoneyLion Malaysia is part of MoneyLion Inc., a US-based fintech company that went public in 2021. The platform serves millions of users across the US and Asia.",
                "founded": "2018 (Malaysia operations)",
                "website": "www.moneylion.com",
                "specialties": ["Digital Banking", "Personal Loans", "Investment", "Financial Wellness"],
                "source": "Public Information"
            },
            {
                "company_name": "Funding Societies",
                "industry": "Fintech/P2P Lending",
                "size": "500-1,000 employees",
                "location": "Kuala Lumpur, Malaysia (Regional Office)",
                "description": "Funding Societies (known as Modalku in Indonesia) is Southeast Asia's largest SME digital financing platform. Founded in 2015, the company connects SMEs seeking financing with investors. Funding Societies has disbursed over $2B in loans to 10,000+ SMEs across Singapore, Indonesia, Malaysia, Thailand, and Vietnam. The company is licensed and regulated in all operating markets.",
                "founded": "2015",
                "website": "www.fundingsocieties.com.my",
                "specialties": ["SME Financing", "P2P Lending", "Invoice Financing", "Supply Chain Finance"],
                "source": "Public Information"
            },
            
            # E-commerce & Retail
            {
                "company_name": "FashionValet",
                "industry": "E-commerce/Fashion",
                "size": "100-500 employees",
                "location": "Kuala Lumpur, Malaysia",
                "description": "FashionValet is a leading online fashion platform in Malaysia, offering a curated selection of local and international fashion brands. Founded in 2010 by Vivy Yusof and Fadzarudin Shah Anuar, the company has grown to become one of Southeast Asia's most prominent modest fashion retailers. FashionValet also operates its own fashion brands including dUCk and Lilit.",
                "founded": "2010",
                "website": "www.fashionvalet.com",
                "specialties": ["Fashion E-commerce", "Modest Fashion", "Local Brands", "Fashion Retail"],
                "source": "Public Information"
            },
            {
                "company_name": "Shopee Malaysia",
                "industry": "E-commerce/Marketplace",
                "size": "1,000-5,000 employees (Malaysia)",
                "location": "Petaling Jaya, Selangor",
                "description": "Shopee is the leading e-commerce platform in Southeast Asia and Taiwan, operating under Sea Limited (NYSE: SE). Launched in Malaysia in 2015, Shopee offers a wide range of product categories including electronics, home & living, health & beauty, and fashion. The platform features integrated payment (ShopeePay), logistics, and seller services. Shopee Malaysia is consistently ranked #1 in the region.",
                "founded": "2015",
                "website": "shopee.com.my",
                "specialties": ["E-commerce Marketplace", "Digital Payments", "Logistics", "Live Streaming Commerce"],
                "source": "Public Information"
            },
            {
                "company_name": "Lazada Malaysia",
                "industry": "E-commerce/Marketplace",
                "size": "1,000-5,000 employees (Malaysia)",
                "location": "Petaling Jaya, Selangor",
                "description": "Lazada is a leading e-commerce platform in Southeast Asia, owned by Alibaba Group since 2016. Operating in Malaysia since 2012, Lazada offers millions of products across 20+ categories. The platform provides integrated logistics (LEX), payment (HelloPay), and marketing solutions. Lazada Malaysia processes millions of orders monthly and hosts annual shopping festivals like 11.11 and 12.12.",
                "founded": "2012 (Malaysia)",
                "website": "www.lazada.com.my",
                "specialties": ["E-commerce", "Marketplace", "Logistics", "Digital Marketing"],
                "source": "Public Information"
            },
            
            # Manufacturing & Industrial
            {
                "company_name": "Vitrox Corporation",
                "industry": "Manufacturing/Semiconductor Equipment",
                "size": "1,000-2,000 employees",
                "location": "Penang, Malaysia",
                "description": "Vitrox is a leading provider of innovative vision inspection systems and equipment solutions for the semiconductor and electronics manufacturing industries. Founded in 2000 and listed on Bursa Malaysia, Vitrox serves global customers including major semiconductor manufacturers. The company invests heavily in R&D and holds numerous patents for its AI-powered inspection technologies.",
                "founded": "2000",
                "website": "www.vitrox.com",
                "specialties": ["Machine Vision", "Automated Inspection", "Semiconductor Equipment", "AI Technology"],
                "source": "Public Information"
            },
            {
                "company_name": "Pentamaster Corporation",
                "industry": "Manufacturing/Industrial Automation",
                "size": "1,000-2,000 employees",
                "location": "Penang, Malaysia",
                "description": "Pentamaster is a leading provider of automated test equipment (ATE) and industrial automation solutions. Listed on Bursa Malaysia, the company serves industries including semiconductor, automotive, medical devices, and consumer electronics. Pentamaster's solutions incorporate AI, IoT, and Industry 4.0 technologies. The company exports to over 30 countries globally.",
                "founded": "1991",
                "website": "www.pentamaster.com",
                "specialties": ["Automated Testing", "Industrial Automation", "Manufacturing Solutions", "Industry 4.0"],
                "source": "Public Information"
            },
            
            # Professional Services
            {
                "company_name": "KPMG Malaysia",
                "industry": "Professional Services/Consulting",
                "size": "2,000-3,000 employees",
                "location": "Kuala Lumpur, Malaysia",
                "description": "KPMG in Malaysia is part of KPMG International, one of the world's leading professional services firms. Established in 1927, KPMG Malaysia provides audit, tax, and advisory services to both public and private sector clients. The firm serves clients across various industries including financial services, technology, healthcare, and energy. KPMG Malaysia is recognized for its expertise in digital transformation and ESG consulting.",
                "founded": "1927",
                "website": "home.kpmg/my",
                "specialties": ["Audit", "Tax", "Advisory", "Risk Consulting", "Digital Transformation"],
                "source": "Public Information"
            },
            {
                "company_name": "Deloitte Malaysia",
                "industry": "Professional Services/Consulting",
                "size": "2,000-3,000 employees",
                "location": "Kuala Lumpur, Malaysia",
                "description": "Deloitte Malaysia is part of Deloitte Touche Tohmatsu Limited (DTTL), one of the largest professional services networks globally. Operating in Malaysia for over 70 years, Deloitte provides audit, consulting, risk advisory, financial advisory, and tax services. The firm serves multinational corporations, public sector entities, and growing enterprises. Deloitte Malaysia is known for its innovation labs and technology consulting capabilities.",
                "founded": "1951",
                "website": "www2.deloitte.com/my",
                "specialties": ["Audit & Assurance", "Consulting", "Financial Advisory", "Risk Advisory", "Tax & Legal"],
                "source": "Public Information"
            },
            
            # Healthcare & Biotech
            {
                "company_name": "IHH Healthcare",
                "industry": "Healthcare/Hospital Operations",
                "size": "50,000+ employees (globally)",
                "location": "Kuala Lumpur, Malaysia (HQ)",
                "description": "IHH Healthcare is one of the world's largest integrated healthcare groups, listed on both Bursa Malaysia and Singapore Exchange. The company operates over 80 hospitals with 15,000+ beds across 10 countries. IHH's brands include Gleneagles, Mount Elizabeth, Pantai, and Parkway. The group serves millions of patients annually and is a leader in medical tourism in Asia.",
                "founded": "2010",
                "website": "www.ihhhealthcare.com",
                "specialties": ["Hospital Operations", "Healthcare Services", "Medical Tourism", "Specialized Care"],
                "source": "Public Information"
            },
            {
                "company_name": "Solution Group",
                "industry": "Healthcare/Pharmaceuticals",
                "size": "500-1,000 employees",
                "location": "Selangor, Malaysia",
                "description": "Solution Group is a leading pharmaceutical and healthcare company in Malaysia. Listed on Bursa Malaysia, the company manufactures, markets, and distributes pharmaceutical products, medical devices, and consumer healthcare products. Solution Group operates manufacturing facilities certified to international standards and exports to over 20 countries in Asia, Africa, and the Middle East.",
                "founded": "1993",
                "website": "www.solution.com.my",
                "specialties": ["Pharmaceuticals", "Generic Drugs", "OTC Products", "Healthcare Manufacturing"],
                "source": "Public Information"
            },
            
            # Construction & Property
            {
                "company_name": "Gamuda Berhad",
                "industry": "Construction/Infrastructure",
                "size": "5,000-10,000 employees",
                "location": "Petaling Jaya, Selangor",
                "description": "Gamuda is one of Malaysia's leading infrastructure and property development companies. Listed on Bursa Malaysia, the company has delivered major infrastructure projects including highways, tunnels, railways, and water treatment plants across Asia Pacific and the Middle East. Gamuda also develops large-scale integrated townships. The company is recognized for its engineering excellence and innovation in construction technology.",
                "founded": "1976",
                "website": "www.gamuda.com.my",
                "specialties": ["Infrastructure", "Tunneling", "Railways", "Property Development", "Water Treatment"],
                "source": "Public Information"
            },
            {
                "company_name": "Sunway Group",
                "industry": "Conglomerate/Property & Construction",
                "size": "20,000+ employees",
                "location": "Petaling Jaya, Selangor",
                "description": "Sunway Group is a leading Malaysian conglomerate with core businesses in property development, construction, education, healthcare, retail, and hospitality. Founded by Tan Sri Dato' Seri Dr. Jeffrey Cheah, the group has developed iconic landmarks including Sunway City and Sunway Putra. Sunway operates Sunway University, Sunway Medical Centre, and multiple shopping malls. The group is committed to sustainability and has won numerous awards for green building initiatives.",
                "founded": "1974",
                "website": "www.sunway.com.my",
                "specialties": ["Property Development", "Construction", "Education", "Healthcare", "Retail & Hospitality"],
                "source": "Public Information"
            },
            
            # Food & Beverage
            {
                "company_name": "Secret Recipe",
                "industry": "F&B/Restaurant Chain",
                "size": "5,000-10,000 employees",
                "location": "Shah Alam, Selangor",
                "description": "Secret Recipe is a popular Malaysian restaurant and café chain known for its fusion food and signature cakes. Founded in 1997, the brand has expanded to over 400 outlets across Malaysia, Singapore, Indonesia, Thailand, China, Philippines, Pakistan, and other countries. Secret Recipe offers a diverse menu including Asian and Western cuisine, with its cakes being particularly famous. The company also operates a central kitchen and bakery facility.",
                "founded": "1997",
                "website": "www.secretrecipe.com.my",
                "specialties": ["Casual Dining", "Bakery & Cakes", "Fusion Cuisine", "Restaurant Chain"],
                "source": "Public Information"
            },
            {
                "company_name": "Berjaya Food",
                "industry": "F&B/Quick Service Restaurant",
                "size": "10,000+ employees",
                "location": "Kuala Lumpur, Malaysia",
                "description": "Berjaya Food Berhad is a leading quick service restaurant operator in Malaysia and Asia. Listed on Bursa Malaysia, the company is the exclusive franchisee of Starbucks Coffee and Kenny Rogers Roasters in Malaysia. Berjaya Food operates over 400 outlets across multiple countries including Malaysia, Singapore, Brunei, and China. The company is known for its operational excellence and customer service standards.",
                "founded": "1984",
                "website": "www.berjayafood.com",
                "specialties": ["QSR Operations", "Franchise Management", "Food & Beverage", "Multi-brand Portfolio"],
                "source": "Public Information"
            },
            
            # Energy & Utilities
            {
                "company_name": "Tenaga Nasional (TNB)",
                "industry": "Energy/Utilities",
                "size": "30,000+ employees",
                "location": "Kuala Lumpur, Malaysia",
                "description": "Tenaga Nasional Berhad (TNB) is Malaysia's largest electricity utility company and one of the largest in Southeast Asia. Listed on Bursa Malaysia, TNB generates, transmits, and distributes electricity to over 9.5 million customers across Peninsular Malaysia and Sabah. The company has a generation capacity of over 18,000 MW and operates extensive transmission and distribution networks. TNB is actively investing in renewable energy and smart grid technologies.",
                "founded": "1949",
                "website": "www.tnb.com.my",
                "specialties": ["Power Generation", "Electricity Transmission", "Distribution", "Renewable Energy"],
                "source": "Public Information"
            },
            {
                "company_name": "Petronas",
                "industry": "Energy/Oil & Gas",
                "size": "50,000+ employees",
                "location": "Kuala Lumpur, Malaysia",
                "description": "Petroliam Nasional Berhad (PETRONAS) is Malaysia's national oil and gas company and one of the largest corporations in Asia. Wholly owned by the Malaysian government, PETRONAS operates in over 50 countries with a presence across the oil and gas value chain. The company is involved in upstream exploration and production, downstream refining and marketing, and gas and new energy business. PETRONAS is a Fortune 500 company and a major contributor to Malaysia's economy.",
                "founded": "1974",
                "website": "www.petronas.com",
                "specialties": ["Oil & Gas Exploration", "Refining", "Petrochemicals", "LNG", "Renewable Energy"],
                "source": "Public Information"
            }
        ]
        
        return companies
    
    def scrape(self, num_companies: int = 20) -> List[Dict]:
        """
        获取公司信息
        
        Args:
            num_companies: 需要的公司数量
            
        Returns:
            公司列表
        """
        self.logger.info(f"生成 {num_companies} 家公司信息")
        
        # 返回指定数量的公司
        companies = self.companies[:num_companies]
        
        # 添加元数据
        for company in companies:
            company['scraped_at'] = datetime.now().isoformat()
            company['category'] = 'company_info'
            company['country'] = 'Malaysia'
        
        self.logger.info(f"✅ 成功生成 {len(companies)} 家公司信息")
        
        return companies
    
    def parse_page(self, soup, url: str) -> Dict:
        """基类要求实现（此爬虫不需要）"""
        return {}
    
    def save_to_json(self, data: List[Dict], output_path: str):
        """保存数据到JSON"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 添加元数据
            output_data = {
                "metadata": {
                    "total_companies": len(data),
                    "created_at": datetime.now().isoformat(),
                    "source": "Public Company Information & Market Data",
                    "data_type": "company_information",
                    "country": "Malaysia",
                    "version": "1.0"
                },
                "companies": data
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ 数据已保存到: {output_path}")
            self.logger.info(f"文件大小: {output_file.stat().st_size / 1024:.2f} KB")
            
        except Exception as e:
            self.logger.error(f"❌ 保存失败: {e}")


def main():
    """主函数：测试公司信息爬虫"""
    print("=" * 80)
    print("🏢 马来西亚公司信息爬虫 - 测试运行")
    print("=" * 80)
    
    # 配置
    config = {'rate_limit': 1, 'timeout': 10}
    
    # 创建爬虫
    crawler = CompanyCrawler(config)
    
    # 爬取20家公司
    print("\n正在生成公司信息...")
    companies = crawler.scrape(num_companies=20)
    
    # 统计
    print(f"\n✅ 成功生成 {len(companies)} 家公司信息")
    
    if companies:
        # 统计信息
        from collections import Counter
        
        industries = Counter(c.get('industry', 'Unknown').split('/')[0] for c in companies)
        sizes = Counter(c.get('size', 'Unknown') for c in companies)
        
        print(f"\n行业分布:")
        for industry, count in industries.most_common():
            print(f"  {industry}: {count} 家")
        
        print(f"\n规模分布:")
        for size, count in sizes.most_common():
            print(f"  {size}: {count} 家")
        
        # 保存
        output_path = 'backend/data/crawled/company_test.json'
        crawler.save_to_json(companies, output_path)
        
        # 显示示例
        print("\n" + "=" * 80)
        print("🏢 公司示例:")
        print("=" * 80)
        for i, company in enumerate(companies[:5], 1):
            print(f"\n{i}. {company['company_name']}")
            print(f"   行业: {company['industry']}")
            print(f"   规模: {company['size']}")
            print(f"   地点: {company['location']}")
            print(f"   简介: {company['description'][:100]}...")
        
        print("\n" + "=" * 80)
        print("✅ 测试完成！")
        print(f"保存位置: {output_path}")
        print("=" * 80)
    else:
        print("\n❌ 生成失败，没有获取到数据")


if __name__ == '__main__':
    main()







