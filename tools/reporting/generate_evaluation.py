#!/usr/bin/env python3
"""
Generate a new code evaluation checklist for branch integration assessment.

Usage:
    python generate_evaluation.py <branch-name> [target-branch]
    
Example:
    python generate_evaluation.py feature/next-development main
"""

import sys
import os
from datetime import datetime
from pathlib import Path

def generate_evaluation_checklist(branch_name, target_branch="main"):
    """Generate a new evaluation checklist from template."""
    
    # Read the template
    template_path = Path("markdown/EVALUATION_CHECKLIST_TEMPLATE.md")
    if not template_path.exists():
        print("❌ Template file not found: markdown/EVALUATION_CHECKLIST_TEMPLATE.md")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_branch = branch_name.replace('/', '_').replace('\\', '_')
    filename = f"evaluation_{safe_branch}_{timestamp}.md"
    
    # Replace template placeholders
    evaluation_content = template_content.replace('[branch-name]', branch_name)
    evaluation_content = evaluation_content.replace('[target-branch]', target_branch)
    evaluation_content = evaluation_content.replace('[YYYY-MM-DD]', datetime.now().strftime("%Y-%m-%d"))
    evaluation_content = evaluation_content.replace('[name/identifier]', os.getenv('USERNAME', 'evaluator'))
    
    # Get commit range info
    try:
        import subprocess
        result = subprocess.run(['git', 'log', '--oneline', '-5', branch_name], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            recent_commits = result.stdout.strip()
            evaluation_content = evaluation_content.replace('[start-hash..end-hash]', 
                                                          f"Recent commits:\n{recent_commits}")
        else:
            evaluation_content = evaluation_content.replace('[start-hash..end-hash]', 
                                                          f"Unable to get commit range: {result.stderr}")
    except Exception as e:
        evaluation_content = evaluation_content.replace('[start-hash..end-hash]', 
                                                      f"Manual review required - git not available: {str(e)}")
    
    # Write the evaluation file
    eval_path = Path("evaluations")
    eval_path.mkdir(exist_ok=True)
    
    eval_file = eval_path / filename
    with open(eval_file, 'w', encoding='utf-8') as f:
        f.write(evaluation_content)
    
    print(f"✅ Evaluation checklist generated: {eval_file}")
    print(f"📋 Please complete all sections before making integration recommendations")
    print(f"📖 Reference: markdown/CODE_EVALUATION_STANDARDS.md for detailed criteria")
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_evaluation.py <branch-name> [target-branch]")
        print("Example: python generate_evaluation.py feature/next-development main")
        sys.exit(1)
    
    branch_name = sys.argv[1]
    target_branch = sys.argv[2] if len(sys.argv) > 2 else "main"
    
    print(f"🔍 Generating evaluation checklist for: {branch_name} → {target_branch}")
    
    success = generate_evaluation_checklist(branch_name, target_branch)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()