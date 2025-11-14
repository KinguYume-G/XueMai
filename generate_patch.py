# -*- coding: utf-8 -*-
from pathlib import Path
content = Path('header_head.tsx').read_text(encoding='utf-8')
content = content.replace("import { useNavigate } from 'react-router-dom'", "import { Link, useNavigate } from 'react-router-dom'")
old_block = """        <div className=\"flex items-center gap-2\">\n          <div className=\"flex h-8 w-8 items-center justify-center rounded-lg bg-primary\">\n            <span className=\"text-lg font-bold text-white\">瀛?/span>\n          </div>\n          <span className=\"text-lg font-semibold\">瀛﹁剦 | UniPulse Asia</span>\n        </div>"""
new_block = """        <div className=\"flex items-center gap-2\">\n          <Link to=\"/\" className=\"inline-flex items-center\">\n            <img src=\"/logo.png\" alt=\"UniPulse Asia\" className=\"h-7 md:h-8 w-auto\" />\n          </Link>\n        </div>"""
if old_block not in content:
    raise SystemExit('Old block not found in header_head.tsx')
content = content.replace(old_block, new_block)
Path('header_patch.tsx').write_text(content, encoding='utf-8')
