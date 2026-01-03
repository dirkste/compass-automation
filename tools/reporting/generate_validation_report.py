#!/usr/bin/env python3
"""
Generate and save E2E validation report.

Usage:
    python generate_validation_report.py
    python generate_validation_report.py --include-historical
    python generate_validation_report.py --output validation_report.md
"""
import argparse
from datetime import datetime
from pathlib import Path
from compass_automation.utils.test_validation import create_validation_report


def main():
    parser = argparse.ArgumentParser(description='Generate E2E validation report')
    parser.add_argument('--include-historical', action='store_true', 
                       help='Include all historical test data (default: latest session only)')
    parser.add_argument('--output', '-o', default='validation_report.md',
                       help='Output file name (default: validation_report.md)')
    
    args = parser.parse_args()
    
    # Generate report
    latest_session_only = not args.include_historical
    report = create_validation_report(latest_session_only=latest_session_only)
    
    # Add metadata header
    scope = "Latest Session Only" if latest_session_only else "All Historical Data"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    full_report = f"""<!-- 
Generated: {timestamp}
Scope: {scope}
-->

{report}

---
*Generated on {timestamp} | Scope: {scope}*
"""
    
    # Save to file
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_report)
    
    print(f"✅ Validation report saved to: {output_path.absolute()}")
    print(f"📊 Scope: {scope}")
    
    # Also display summary
    print("\n" + "="*50)
    print("SUMMARY:")
    lines = report.split('\n')
    for line in lines:
        if line.startswith('- **') and any(x in line for x in ['Expected', 'Processed', 'Success Rate']):
            print(line)
        elif 'PASS:' in line or 'FAIL:' in line:
            print(line)
    print("="*50)


if __name__ == "__main__":
    main()