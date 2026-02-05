#!/usr/bin/env python3
"""
自动飞行记录仪 - 变更日志记录脚本
用于追踪代码变更并维护 AI_CHANGELOG.md
"""

import os
import sys
from datetime import datetime
from pathlib import Path

def log_change(change_type, summary, risk_analysis):
    """
    记录变更到 AI_CHANGELOG.md
    
    Args:
        change_type: 变更类型 [Feature | Bugfix | Refactor | Critical-Fix]
        summary: 变更的技术摘要
        risk_analysis: 风险分析
    """
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    changelog_path = project_root / "docs" / "AI_CHANGELOG.md"
    
    # 确保 docs 目录存在
    changelog_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 生成变更记录条目
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"""
## {timestamp} - {change_type}

**摘要:** {summary}

**风险分析:** {risk_analysis}

---

"""
    
    # 如果文件不存在，创建文件并添加头部
    if not changelog_path.exists():
        header = """# AI 变更日志

本文档由 Auto-Flight Recorder 自动维护，记录所有代码变更。

---
"""
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(header)
    
    # 追加新的变更记录
    with open(changelog_path, 'a', encoding='utf-8') as f:
        f.write(entry)
    
    print(f"✅ 变更已记录到 {changelog_path}")
    print(f"   类型: {change_type}")
    print(f"   摘要: {summary}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python log_change.py <change_type> <summary> <risk_analysis>")
        print("change_type: Feature | Bugfix | Refactor | Critical-Fix")
        sys.exit(1)
    
    change_type = sys.argv[1]
    summary = sys.argv[2]
    risk_analysis = sys.argv[3]
    
    log_change(change_type, summary, risk_analysis)
