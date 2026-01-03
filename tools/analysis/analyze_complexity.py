#!/usr/bin/env python3
"""
Code Complexity Analysis Script

Analyzes Python code complexity using multiple metrics to identify
refactoring opportunities for large, complicated methods.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_radon_analysis():
    """Run comprehensive Radon analysis."""
    print("🔍 CYCLOMATIC COMPLEXITY ANALYSIS (Radon)")
    print("=" * 60)
    
    # Cyclomatic Complexity
    print("\n📊 HIGH COMPLEXITY METHODS (C+ Rating):")
    result = subprocess.run([
        sys.executable, "-m", "radon", "cc", ".", 
        "--min=C", "--show-complexity", "--total-average"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"Error: {result.stderr}")
    
    # Maintainability Index
    print("\n📈 MAINTAINABILITY INDEX:")
    result = subprocess.run([
        sys.executable, "-m", "radon", "mi", ".", 
        "--min=B", "--show"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"Error: {result.stderr}")


def run_xenon_analysis():
    """Run Xenon complexity analysis."""
    print("\n🎯 XENON COMPLEXITY THRESHOLDS")
    print("=" * 60)
    
    # Check for methods above complexity threshold
    result = subprocess.run([
        sys.executable, "-m", "xenon", ".", 
        "--max-absolute=10", "--max-modules=10", "--max-average=5"
    ], capture_output=True, text=True)
    
    print("Methods exceeding complexity thresholds:")
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    print(f"Exit code: {result.returncode} (0=pass, 1=complexity violations found)")


def analyze_specific_files():
    """Analyze specific high-complexity files in detail."""
    print("\n🔬 DETAILED FILE ANALYSIS")
    print("=" * 60)
    
    high_complexity_files = [
        "flows/complaints_flows.py",
        "tests/test_integration_extended.py", 
        "pages/login_page.py",
        "utils/test_validation.py"
    ]
    
    for file_path in high_complexity_files:
        if Path(file_path).exists():
            print(f"\n📄 {file_path}:")
            print("-" * 40)
            
            # Detailed complexity for this file
            result = subprocess.run([
                sys.executable, "-m", "radon", "cc", file_path,
                "--show-complexity", "--min=A"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(result.stdout)


def generate_complexity_report():
    """Generate comprehensive complexity report."""
    print("🏥 COMPASS AUTOMATION - CODE COMPLEXITY ANALYSIS")
    print("=" * 80)
    print("This report identifies refactoring opportunities for large, complex methods.")
    print("Similar to Visual Studio's complexity metrics.\n")
    
    try:
        run_radon_analysis()
        run_xenon_analysis() 
        analyze_specific_files()
        
        print("\n📋 COMPLEXITY RATINGS GUIDE:")
        print("=" * 40)
        print("A: 1-5   (Simple)")
        print("B: 6-10  (More Complex)")  
        print("C: 11-20 (Complex - Consider Refactoring)")
        print("D: 21-30 (Very Complex - Needs Refactoring)")
        print("E: 31+   (Extremely Complex - Urgent Refactoring)")
        
        print("\n🎯 REFACTORING RECOMMENDATIONS:")
        print("=" * 40)
        print("1. Focus on C+ rated methods (Complexity 11+)")
        print("2. Break down large functions into smaller, focused ones")
        print("3. Extract complex conditionals into separate methods")
        print("4. Use strategy pattern for complex branching logic")
        print("5. Consider state machines for complex workflows")
        
        print("\n🛠️ TOOLS USED:")
        print("- Radon: Cyclomatic Complexity & Maintainability Index")
        print("- Xenon: Complexity threshold violations")
        print("- Analysis focused on business logic complexity")
        
    except Exception as e:
        print(f"Error running analysis: {e}")
        print("Ensure 'radon' and 'xenon' are installed: pip install radon xenon")


if __name__ == "__main__":
    generate_complexity_report()