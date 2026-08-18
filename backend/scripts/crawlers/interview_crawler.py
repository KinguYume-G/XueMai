"""
面试题爬虫
提供灵活的面试题数据采集和管理功能
"""

import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from bs4 import BeautifulSoup

import sys
sys.path.insert(0, str(Path(__file__).parent))
from base_crawler import BaseCrawler


class InterviewCrawler(BaseCrawler):
    """面试题爬虫"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def create_sample_questions(self) -> List[Dict]:
        """
        创建示例面试题
        这些是我们自己编写的题目，用于测试系统
        """
        sample_questions = [
            {
                "question": "什么是二叉树的三种遍历方法？请解释前序、中序、后序遍历的区别。",
                "category": "算法",
                "difficulty": "简单",
                "answer": "二叉树有三种基本遍历方法：\n1. 前序遍历(Pre-order)：根节点 -> 左子树 -> 右子树\n2. 中序遍历(In-order)：左子树 -> 根节点 -> 右子树\n3. 后序遍历(Post-order)：左子树 -> 右子树 -> 根节点\n\n区别主要在于访问根节点的顺序。前序遍历先访问根节点，中序遍历在左子树之后访问根节点，后序遍历最后访问根节点。",
                "source": "UniPulse Asia - 自编题库",
                "tags": ["数据结构", "树", "遍历", "算法基础"]
            },
            {
                "question": "解释什么是快速排序(Quick Sort)，并说明其时间复杂度。",
                "category": "算法",
                "difficulty": "中等",
                "answer": "快速排序是一种分治算法：\n1. 选择一个基准元素(pivot)\n2. 将数组分为两部分：小于基准的元素和大于基准的元素\n3. 递归地对两部分进行快速排序\n\n时间复杂度：\n- 平均情况：O(n log n)\n- 最坏情况：O(n²) (当数组已排序时)\n- 最好情况：O(n log n)\n空间复杂度：O(log n) (递归栈空间)",
                "source": "UniPulse Asia - 自编题库",
                "tags": ["排序算法", "分治", "快速排序"]
            },
            {
                "question": "什么是哈希表(Hash Table)？解释哈希冲突及其解决方法。",
                "category": "算法",
                "difficulty": "简单",
                "answer": "哈希表是一种使用哈希函数将键映射到值的数据结构，提供O(1)的平均查找时间。\n\n哈希冲突：当两个不同的键映射到同一个索引时发生。\n\n解决方法：\n1. 链地址法(Chaining)：在冲突位置使用链表存储多个元素\n2. 开放寻址法(Open Addressing)：寻找下一个空闲位置\n   - 线性探测\n   - 二次探测\n   - 双重哈希",
                "source": "UniPulse Asia - 自编题库",
                "tags": ["数据结构", "哈希表", "冲突解决"]
            },
            {
                "question": "如何检测链表中是否存在环？",
                "category": "算法",
                "difficulty": "中等",
                "answer": "使用快慢指针法(Floyd's Cycle Detection)：\n1. 设置两个指针：slow(慢指针)和fast(快指针)\n2. slow每次移动一步，fast每次移动两步\n3. 如果链表有环，fast最终会追上slow\n4. 如果fast到达null，说明无环\n\n时间复杂度：O(n)\n空间复杂度：O(1)",
                "source": "UniPulse Asia - 自编题库",
                "tags": ["链表", "双指针", "环检测"]
            },
            {
                "question": "解释动态规划(Dynamic Programming)的核心思想。",
                "category": "算法",
                "difficulty": "中等",
                "answer": "动态规划的核心思想：\n1. 将问题分解为子问题\n2. 存储子问题的解(避免重复计算)\n3. 使用子问题的解构建原问题的解\n\n关键要素：\n- 最优子结构：问题的最优解包含子问题的最优解\n- 重叠子问题：同一子问题会被多次求解\n- 状态转移方程：描述子问题之间的关系\n\n常见应用：斐波那契数列、背包问题、最长公共子序列",
                "source": "UniPulse Asia - 自编题库",
                "tags": ["动态规划", "算法设计", "优化"]
            },
            {
                "question": "设计一个URL缩短服务(like bit.ly)，考虑系统设计的关键要素。",
                "category": "系统设计",
                "difficulty": "困难",
                "answer": "关键设计要素：\n\n1. 功能需求：\n   - 生成短URL\n   - 重定向到原URL\n   - 自定义短链(可选)\n   - 统计访问次数\n\n2. 非功能需求：\n   - 高可用性\n   - 低延迟\n   - 可扩展性\n\n3. 技术方案：\n   - 哈希算法生成唯一ID\n   - Base62编码(a-z, A-Z, 0-9)\n   - 数据库：键值存储(Redis, DynamoDB)\n   - 缓存：热门链接缓存\n   - 负载均衡：分布式架构\n\n4. 容量估算：\n   - 假设每天100M新URL\n   - 7年 = 2.5B URLs\n   - 使用6字符Base62 = 62^6 ≈ 56B 可能性",
                "source": "UniPulse Asia - 自编题库",
                "tags": ["系统设计", "分布式系统", "缩短服务"]
            },
            {
                "question": "如何设计一个分布式缓存系统？",
                "category": "系统设计",
                "difficulty": "困难",
                "answer": "分布式缓存系统设计：\n\n1. 核心组件：\n   - 缓存节点：存储数据\n   - 一致性哈希：数据分片\n   - 复制：数据冗余\n\n2. 关键特性：\n   - 数据分片(Sharding)\n   - 数据复制(Replication)\n   - 失效策略(LRU, LFU)\n   - 一致性保证\n\n3. 技术选型：\n   - Redis Cluster\n   - Memcached\n   - 自建方案\n\n4. 挑战：\n   - 热点数据\n   - 缓存雪崩\n   - 缓存穿透\n   - 数据一致性",
                "source": "UniPulse Asia - 自编题库",
                "tags": ["系统设计", "缓存", "分布式"]
            },
            {
                "question": "介绍一下你过去做过的最有挑战性的项目。",
                "category": "行为",
                "difficulty": "中等",
                "answer": "回答技巧(STAR方法)：\n\nSituation(情境)：\n- 描述项目背景和挑战\n\nTask(任务)：\n- 说明你的角色和责任\n\nAction(行动)：\n- 详细说明你采取的具体行动\n- 遇到的困难和如何克服\n\nResult(结果)：\n- 项目成果和影响\n- 学到的经验教训\n\n示例要点：\n- 技术难点的解决方案\n- 团队协作经验\n- 时间管理能力\n- 创新和主动性",
                "source": "UniPulse Asia - 自编题库",
                "tags": ["行为面试", "STAR方法", "项目经验"]
            },
            {
                "question": "你如何处理工作中的冲突和分歧？",
                "category": "行为",
                "difficulty": "简单",
                "answer": "处理冲突的建议方法：\n\n1. 保持冷静和专业\n   - 避免情绪化反应\n   - 倾听对方观点\n\n2. 寻找共同目标\n   - 关注问题本身，而非个人\n   - 明确团队目标\n\n3. 数据驱动决策\n   - 提供客观数据支持\n   - 做技术对比和分析\n\n4. 寻求妥协和双赢\n   - 考虑多种解决方案\n   - 必要时寻求上级或第三方意见\n\n5. 从经验中学习\n   - 反思冲突原因\n   - 改进沟通方式",
                "source": "UniPulse Asia - 自编题库",
                "tags": ["行为面试", "冲突管理", "团队协作"]
            },
            {
                "question": "你的职业规划是什么？为什么想加入我们公司？",
                "category": "行为",
                "difficulty": "简单",
                "answer": "回答建议：\n\n职业规划部分：\n1. 短期目标(1-2年)：\n   - 具体技能提升\n   - 项目经验积累\n\n2. 中期目标(3-5年)：\n   - 技术深度或领导力发展\n   - 行业影响力\n\n3. 长期愿景：\n   - 职业发展方向\n   - 个人价值实现\n\n为什么加入公司：\n1. 公司价值观认同\n2. 技术栈匹配\n3. 成长机会\n4. 团队文化\n5. 产品/业务兴趣\n\n关键：展示对公司的研究和真诚的兴趣",
                "source": "UniPulse Asia - 自编题库",
                "tags": ["行为面试", "职业规划", "动机"]
            }
        ]
        
        return sample_questions
    
    def scrape(self, source: str = "sample") -> List[Dict]:
        """
        爬取面试题
        
        Args:
            source: 数据源类型 ("sample", "github", "leetcode", etc.)
        
        Returns:
            面试题列表
        """
        if source == "sample":
            return self.create_sample_questions()
        else:
            self.logger.warning(f"暂不支持数据源: {source}")
            return []
    
    def parse_page(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        解析页面（基类要求实现）
        对于面试题，我们主要使用结构化数据
        """
        return {}
    
    def save_to_json(self, data: List[Dict], output_path: str):
        """保存数据到JSON"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 添加元数据
            output_data = {
                "metadata": {
                    "total_questions": len(data),
                    "created_at": datetime.now().isoformat(),
                    "source": "UniPulse Asia Interview Question Bank",
                    "license": "Proprietary - For educational use",
                    "version": "1.0"
                },
                "questions": data
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"✅ 数据已保存到: {output_path}")
            self.logger.info(f"文件大小: {output_file.stat().st_size / 1024:.2f} KB")
            
        except Exception as e:
            self.logger.error(f"❌ 保存失败: {e}")


def main():
    """主函数：创建测试面试题"""
    print("=" * 80)
    print("🎯 面试题爬虫 - 测试运行")
    print("=" * 80)
    
    # 创建爬虫
    crawler = InterviewCrawler()
    
    # 生成示例题目
    print("\n正在生成示例面试题...")
    questions = crawler.scrape(source="sample")
    
    # 统计
    print(f"\n✅ 成功生成 {len(questions)} 道面试题")
    
    # 按分类统计
    categories = {}
    difficulties = {}
    
    for q in questions:
        cat = q['category']
        diff = q['difficulty']
        categories[cat] = categories.get(cat, 0) + 1
        difficulties[diff] = difficulties.get(diff, 0) + 1
    
    print("\n按类别统计:")
    for cat, count in categories.items():
        print(f"  {cat}: {count} 道")
    
    print("\n按难度统计:")
    for diff, count in difficulties.items():
        print(f"  {diff}: {count} 道")
    
    # 保存
    output_path = 'backend/data/crawled/interview_test.json'
    crawler.save_to_json(questions, output_path)
    
    # 显示示例
    print("\n" + "=" * 80)
    print("📝 题目示例:")
    print("=" * 80)
    for i, q in enumerate(questions[:3], 1):
        print(f"\n{i}. [{q['category']} - {q['difficulty']}] {q['question'][:60]}...")
        print(f"   标签: {', '.join(q['tags'][:3])}")
    
    print("\n" + "=" * 80)
    print("✅ 测试完成！")
    print(f"保存位置: {output_path}")
    print("=" * 80)


if __name__ == '__main__':
    main()

