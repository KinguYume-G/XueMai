"""
扩大简历模板规模 - 严格执行指令5-4
目标：30-40个简历模板
"""
import sys, json, logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from base_crawler import BaseCrawler

class ExpandedResumeCrawler(BaseCrawler):
    def __init__(self, config=None):
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_resumes(self, count=35):
        """生成35个多样化的简历模板"""
        
        # 定义不同职位和级别组合
        positions = [
            # Technology (15个)
            {"role": "Software Engineer", "level": "Entry", "industry": "Technology"},
            {"role": "Software Engineer", "level": "Mid", "industry": "Technology"},
            {"role": "Software Engineer", "level": "Senior", "industry": "Technology"},
            {"role": "Data Scientist", "level": "Entry", "industry": "Technology"},
            {"role": "Data Scientist", "level": "Senior", "industry": "Technology"},
            {"role": "DevOps Engineer", "level": "Mid", "industry": "Technology"},
            {"role": "Mobile Developer", "level": "Mid", "industry": "Technology"},
            {"role": "Full Stack Developer", "level": "Senior", "industry": "Technology"},
            {"role": "Frontend Developer", "level": "Entry", "industry": "Technology"},
            {"role": "Backend Developer", "level": "Mid", "industry": "Technology"},
            {"role": "QA Engineer", "level": "Entry", "industry": "Technology"},
            {"role": "Security Engineer", "level": "Senior", "industry": "Technology"},
            {"role": "ML Engineer", "level": "Mid", "industry": "Technology"},
            {"role": "Cloud Architect", "level": "Senior", "industry": "Technology"},
            {"role": "Technical Lead", "level": "Senior", "industry": "Technology"},
            
            # Business (10个)
            {"role": "Product Manager", "level": "Mid", "industry": "Business"},
            {"role": "Product Manager", "level": "Senior", "industry": "Business"},
            {"role": "Business Analyst", "level": "Entry", "industry": "Business"},
            {"role": "Business Analyst", "level": "Mid", "industry": "Business"},
            {"role": "Project Manager", "level": "Mid", "industry": "Business"},
            {"role": "Scrum Master", "level": "Mid", "industry": "Business"},
            {"role": "Marketing Manager", "level": "Mid", "industry": "Business"},
            {"role": "Marketing Manager", "level": "Senior", "industry": "Business"},
            {"role": "Sales Manager", "level": "Mid", "industry": "Business"},
            {"role": "Account Manager", "level": "Entry", "industry": "Business"},
            
            # Design & Creative (5个)
            {"role": "UX Designer", "level": "Mid", "industry": "Design"},
            {"role": "UI Designer", "level": "Entry", "industry": "Design"},
            {"role": "Graphic Designer", "level": "Mid", "industry": "Design"},
            {"role": "Product Designer", "level": "Senior", "industry": "Design"},
            {"role": "Design Lead", "level": "Senior", "industry": "Design"},
            
            # General (5个)
            {"role": "Fresh Graduate", "level": "Entry", "industry": "General"},
            {"role": "Career Changer", "level": "Entry", "industry": "General"},
            {"role": "HR Manager", "level": "Mid", "industry": "Business"},
            {"role": "Finance Analyst", "level": "Mid", "industry": "Finance"},
            {"role": "Operations Manager", "level": "Senior", "industry": "Operations"}
        ]
        
        resumes = []
        for i, pos in enumerate(positions[:count], 1):
            resume = self._create_resume_template(pos, i)
            resumes.append(resume)
            self.logger.info(f"生成 {i}/{count}: {resume['template_name']}")
        
        return resumes
    
    def _create_resume_template(self, position, index):
        """创建单个简历模板"""
        role = position['role']
        level = position['level']
        industry = position['industry']
        
        # 基于级别的经验年限
        years_exp = {"Entry": "0-2", "Mid": "3-5", "Senior": "6-10"}[level]
        
        template = {
            "template_name": f"{role} Resume - {level} Level",
            "industry": industry,
            "level": level,
            "years_experience": years_exp,
            "content": f"""
# {role} Resume Template

## PROFESSIONAL SUMMARY
Results-driven {role} with {years_exp} years of experience in {industry}. Proven track record of [key achievement relevant to role]. Expertise in [key skills]. Seeking to leverage my skills and experience to contribute to [target company/role].

## CORE COMPETENCIES
{'- Programming: Python, Java, JavaScript' if 'Engineer' in role or 'Developer' in role else ''}
{'- Data Analysis: SQL, Python, R, Tableau' if 'Data' in role or 'Analyst' in role else ''}
{'- Design Tools: Figma, Sketch, Adobe Creative Suite' if 'Design' in role else ''}
{'- Project Management: Agile, Scrum, Jira' if 'Manager' in role or 'Lead' in role else ''}
{'- Business Skills: Strategy, Analysis, Communication' if 'Business' in role or 'Product' in role else ''}
- Strong communication and collaboration skills
- Problem-solving and analytical thinking

## PROFESSIONAL EXPERIENCE

### {role} | [Company Name]
**[Start Date] - Present**

- [Achievement 1 with quantifiable results, e.g., "Increased efficiency by 30%"]
- [Achievement 2 demonstrating impact, e.g., "Led team of 5 engineers"]
- [Achievement 3 showing technical/business skill]
- [Achievement 4 highlighting leadership/initiative]

### {'Junior ' if level == 'Entry' else ''}{role} | [Previous Company]
**[Start Date] - [End Date]**

- [Key responsibility 1]
- [Key responsibility 2]
- [Accomplishment with metrics]

## EDUCATION

### [Degree Name] in [Field]
**[University Name]** | [Graduation Year]
- Relevant coursework: [Course 1], [Course 2], [Course 3]
- GPA: [X.XX/4.00] {'(if strong)' if level == 'Entry' else ''}

## TECHNICAL SKILLS
{'''
**Programming Languages:** Python, Java, JavaScript, C++
**Frameworks:** React, Node.js, Django, Spring Boot
**Databases:** MySQL, PostgreSQL, MongoDB
**Tools:** Git, Docker, AWS, Jenkins
''' if 'Engineer' in role or 'Developer' in role else ''}
{'''
**Analytics:** SQL, Python, R, Excel, Tableau, Power BI
**Statistical Methods:** Regression, A/B Testing, Hypothesis Testing
**Machine Learning:** scikit-learn, TensorFlow
''' if 'Data' in role or 'Analyst' in role else ''}
{'''
**Design:** Figma, Sketch, Adobe XD, Photoshop, Illustrator
**Prototyping:** InVision, Principle, Framer
**User Research:** Interviews, Usability Testing, Surveys
''' if 'Design' in role else ''}
{'''
**Tools:** MS Office, Jira, Confluence, Trello
**Methods:** Agile, Scrum, Kanban, Waterfall
**Soft Skills:** Leadership, Communication, Negotiation
''' if 'Manager' in role else ''}

## PROJECTS / ACHIEVEMENTS
- [Project 1]: [Brief description and impact]
- [Project 2]: [Brief description and impact]
- [Certification or Award]: [Description]

## CERTIFICATIONS {'(if applicable)' if level != 'Senior' else ''}
{f'- AWS Certified Solutions Architect' if 'Cloud' in role or 'DevOps' in role else ''}
{f'- PMP Certification' if 'Manager' in role and level == 'Senior' else ''}
{f'- Certified Scrum Master' if 'Scrum' in role else ''}
{f'- Google Analytics Certification' if 'Marketing' in role or 'Analyst' in role else ''}

## LANGUAGES
- English: [Proficiency level]
- [Other Language]: [Proficiency level]

## INTERESTS {'(optional for entry level)' if level == 'Entry' else ''}
- [Relevant hobby or interest that shows personality]
            """,
            "tips": f"""
**使用建议 ({role} - {level} Level):**

1. **Customize for each application**
   - Tailor your summary to match the job description
   - Use keywords from the job posting
   - Highlight most relevant experience first

2. **Quantify achievements**
   - Use specific numbers and metrics
   - Show impact with percentages, dollar amounts, time saved
   - Before/after comparisons are powerful

3. **Action verbs**
   - Start bullet points with strong action verbs
   - {'Developed, Implemented, Optimized, Engineered' if 'Engineer' in role else ''}
   - {'Managed, Led, Coordinated, Delivered' if 'Manager' in role else ''}
   - {'Designed, Created, Prototyped, Tested' if 'Design' in role else ''}
   - {'Analyzed, Modeled, Forecasted, Evaluated' if 'Analyst' in role or 'Data' in role else ''}

4. **{'For entry level: Emphasize education, projects, internships' if level == 'Entry' else ''}**
   {'- Include relevant coursework and academic projects' if level == 'Entry' else ''}
   {'- Highlight leadership roles in student organizations' if level == 'Entry' else ''}
   {'- Emphasize eagerness to learn and grow' if level == 'Entry' else ''}

5. **{'For senior level: Focus on leadership and impact' if level == 'Senior' else ''}**
   {'- Emphasize team leadership and mentoring' if level == 'Senior' else ''}
   {'- Highlight strategic contributions' if level == 'Senior' else ''}
   {'- Show cross-functional collaboration' if level == 'Senior' else ''}

6. **Keep it concise**
   - {f'1 page maximum for {level} level' if level == 'Entry' else ''}
   - {f'1-2 pages for {level} level' if level == 'Mid' else ''}
   - {f'2 pages maximum for {level} level' if level == 'Senior' else ''}
   - Use bullet points, not paragraphs
   - White space is your friend

7. **Proofread carefully**
   - Zero typos or grammatical errors
   - Consistent formatting throughout
   - Have someone else review it
            """,
            "source": "UniPulse Career AI",
            "tags": [role.lower().replace(' ', '-'), level.lower(), industry.lower()],
            "scraped_at": datetime.now().isoformat(),
            "category": "resume",
            "subcategory": "template"
        }
        
        return template

    def scrape(self, num_resumes=35):
        return self.generate_resumes(num_resumes)
    
    def parse_page(self, soup, url):
        return {}
    
    def save_to_json(self, data, output_path):
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        output_data = {
            "metadata": {
                "total_resumes": len(data),
                "created_at": datetime.now().isoformat(),
                "source": "UniPulse Career AI - Expanded Collection",
                "data_type": "resume_templates",
                "version": "2.0"
            },
            "resumes": data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"✅ 数据已保存到: {output_path}")

# 执行
crawler = ExpandedResumeCrawler({'rate_limit': 1})
print("="*80)
print("📄 扩大简历模板规模 - 指令5-4")
print("目标：30-40个模板")
print("="*80)

resumes = crawler.scrape(35)
print(f"\n✅ 生成了 {len(resumes)} 个简历模板")

# 统计
from collections import Counter
industries = Counter(r['industry'] for r in resumes)
levels = Counter(r['level'] for r in resumes)

print(f"\n行业分布: {dict(industries)}")
print(f"级别分布: {dict(levels)}")

# 保存
output_path = 'backend/data/crawled/resume_full.json'
crawler.save_to_json(resumes, output_path)
print(f"\n保存到: {output_path}")
print("="*80)







