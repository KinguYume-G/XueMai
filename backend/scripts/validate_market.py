"""市场报告数据验证（快速版）"""
import json, sys
from pathlib import Path

file_path = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'market_test.json'
with open(file_path, 'r', encoding='utf-8') as f:
    reports = json.load(f).get('reports', [])

print(f"验证 {len(reports)} 篇市场报告...")
score = 10.0

for i, r in enumerate(reports, 1):
    missing = [f for f in ['title', 'organization', 'category', 'content'] if not r.get(f)]
    if missing:
        print(f"  ❌ 报告{i}: 缺少{missing}")
        score -= 2
    elif len(r.get('content', '')) < 1000:
        print(f"  ⚠️ 报告{i}: 内容过短")
        score -= 1
    else:
        print(f"  ✅ 报告{i} ({r['title'][:40]}...): {len(r['content'])}字符")

print(f"\n总分: {score}/10")
print("✅ 数据质量优秀！" if score >= 8 else "⚠️ 需改进")
sys.exit(0 if score >= 6 else 1)







