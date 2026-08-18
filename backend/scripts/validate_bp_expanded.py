"""验证扩展的BP模板（快速版）"""
import json, sys
from pathlib import Path

file_path = Path(__file__).parent.parent / 'backend' / 'data' / 'crawled' / 'bp_full_expanded.json'
with open(file_path, 'r', encoding='utf-8') as f:
    templates = json.load(f).get('templates', [])

print(f"验证 {len(templates)} 个BP模板...")
score = 10.0

for i, t in enumerate(templates, 1):
    missing = [f for f in ['template_name', 'industry', 'stage', 'content', 'tips'] if not t.get(f)]
    if missing:
        print(f"  ❌ 模板{i}: 缺少{missing}")
        score -= 2
    elif len(t.get('content', '')) < 2000:
        print(f"  ⚠️ 模板{i}: 内容偏短")
        score -= 0.5
    else:
        print(f"  ✅ 模板{i} ({t['template_name'][:40]}...): {len(t['content'])}字符")

print(f"\n总分: {score:.1f}/10")
print("✅ 数据质量优秀！" if score >= 8 else "⚠️ 需改进")







