#!/usr/bin/env python3
"""
Performance comparison and analysis tool.

Compare current performance against saved benchmarks and identify
performance changes, improvements, and regressions.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from compass_automation.utils.performance_monitor import performance_monitor


def list_benchmarks() -> List[str]:
    """List all available benchmark files."""
    benchmark_dir = Path("benchmarks")
    if not benchmark_dir.exists():
        return []
    
    benchmarks = []
    for file_path in benchmark_dir.glob("*.json"):
        benchmarks.append(file_path.stem)
    
    return sorted(benchmarks)


def load_benchmark(name: str) -> Dict[str, Any]:
    """Load benchmark data from file."""
    benchmark_path = Path("benchmarks") / f"{name}.json"
    
    if not benchmark_path.exists():
        raise FileNotFoundError(f"Benchmark '{name}' not found at {benchmark_path}")
    
    with open(benchmark_path) as f:
        return json.load(f)


def format_performance_change(current: float, baseline: float, metric_name: str) -> str:
    """Format performance change with appropriate indicators."""
    if baseline == 0:
        return "N/A (baseline was 0)"
    
    change_percent = ((current - baseline) / baseline) * 100
    change_absolute = current - baseline
    
    # For time/memory metrics, lower is better
    is_time_metric = 'duration' in metric_name.lower() or 'time' in metric_name.lower()
    is_memory_metric = 'memory' in metric_name.lower()
    
    if is_time_metric or is_memory_metric:
        if change_percent < -5:  # 5%+ improvement
            indicator = "🟢 IMPROVED"
        elif change_percent > 10:  # 10%+ regression
            indicator = "🔴 REGRESSION"
        else:
            indicator = "🟡 UNCHANGED"
    else:
        # For other metrics, neutral formatting
        indicator = "📊"
    
    return f"{indicator} {change_percent:+.1f}% ({change_absolute:+.3f})"


def compare_benchmarks(current_name: str, baseline_name: str):
    """Compare two benchmark files."""
    print(f"\n📊 Comparing Performance: {current_name} vs {baseline_name}")
    print("=" * 70)
    
    try:
        current = load_benchmark(current_name)
        baseline = load_benchmark(baseline_name)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return
    
    # Compare summaries
    current_summary = current['summary']
    baseline_summary = baseline['summary']
    
    print(f"📅 Current:  {current['timestamp']} - {current.get('description', 'No description')}")
    print(f"📅 Baseline: {baseline['timestamp']} - {baseline.get('description', 'No description')}")
    print()
    
    # Key metrics comparison
    metrics_to_compare = [
        ('total_duration', 'Total Duration (s)'),
        ('average_duration', 'Average Duration (s)'),
        ('memory_usage_mb', 'Memory Usage (MB)'),
        ('memory_peak_mb', 'Memory Peak (MB)'),
        ('cpu_average', 'CPU Average (%)'),
        ('operation_count', 'Operation Count')
    ]
    
    print("📈 Performance Changes:")
    print("-" * 50)
    
    for metric_key, metric_name in metrics_to_compare:
        current_val = current_summary.get(metric_key, 0)
        baseline_val = baseline_summary.get(metric_key, 0)
        
        change_str = format_performance_change(current_val, baseline_val, metric_key)
        
        print(f"{metric_name:20}: {current_val:8.3f} | {baseline_val:8.3f} | {change_str}")
    
    # Detailed test comparison if available
    if 'metrics' in current and 'metrics' in baseline:
        print(f"\n🔍 Detailed Test Analysis:")
        print("-" * 50)
        
        current_tests = {m['name']: m for m in current['metrics']}
        baseline_tests = {m['name']: m for m in baseline['metrics']}
        
        # Find tests that exist in both benchmarks
        common_tests = set(current_tests.keys()) & set(baseline_tests.keys())
        
        if common_tests:
            # Show biggest improvements and regressions
            changes = []
            
            for test_name in common_tests:
                curr = current_tests[test_name]
                base = baseline_tests[test_name]
                
                if curr.get('duration') and base.get('duration'):
                    change_percent = ((curr['duration'] - base['duration']) / base['duration']) * 100
                    changes.append((test_name, change_percent, curr['duration'], base['duration']))
            
            # Sort by change percentage
            changes.sort(key=lambda x: x[1])
            
            # Show top improvements (most negative percentage)
            print("🟢 Top Improvements:")
            for name, change, curr_dur, base_dur in changes[:3]:
                if change < -5:  # Only show significant improvements
                    print(f"   {name}: {change:+.1f}% ({curr_dur:.3f}s vs {base_dur:.3f}s)")
            
            print("\n🔴 Top Regressions:")
            # Show top regressions (most positive percentage)  
            for name, change, curr_dur, base_dur in changes[-3:]:
                if change > 10:  # Only show significant regressions
                    print(f"   {name}: {change:+.1f}% ({curr_dur:.3f}s vs {base_dur:.3f}s)")
        
        # Tests only in current
        new_tests = set(current_tests.keys()) - set(baseline_tests.keys())
        if new_tests:
            print(f"\n🆕 New Tests ({len(new_tests)}):")
            for test_name in sorted(new_tests):
                duration = current_tests[test_name].get('duration', 0)
                print(f"   {test_name}: {duration:.3f}s")
        
        # Tests only in baseline (removed)
        removed_tests = set(baseline_tests.keys()) - set(current_tests.keys())
        if removed_tests:
            print(f"\n🗑️ Removed Tests ({len(removed_tests)}):")
            for test_name in sorted(removed_tests):
                print(f"   {test_name}")


def show_benchmark_details(name: str):
    """Show detailed information about a benchmark."""
    print(f"\n📋 Benchmark Details: {name}")
    print("=" * 50)
    
    try:
        data = load_benchmark(name)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return
    
    # Basic information
    print(f"📅 Timestamp: {data['timestamp']}")
    print(f"📝 Description: {data.get('description', 'No description')}")
    print()
    
    # Summary statistics
    summary = data['summary']
    print("📊 Summary Statistics:")
    print(f"   Operations: {summary['operation_count']}")
    print(f"   Total Duration: {summary['total_duration']:.3f}s")
    print(f"   Average Duration: {summary['average_duration']:.3f}s")
    print(f"   Min Duration: {summary['min_duration']:.3f}s")
    print(f"   Max Duration: {summary['max_duration']:.3f}s")
    print(f"   Memory Usage: {summary['memory_usage_mb']:.1f}MB")
    print(f"   Memory Peak: {summary['memory_peak_mb']:.1f}MB")
    print(f"   CPU Average: {summary['cpu_average']:.1f}%")
    
    # Slowest operations
    if 'metrics' in data:
        metrics = data['metrics']
        # Sort by duration
        sorted_metrics = sorted(
            [m for m in metrics if m.get('duration')], 
            key=lambda x: x['duration'], 
            reverse=True
        )
        
        print(f"\n🐌 Slowest Operations (Top 10):")
        for i, metric in enumerate(sorted_metrics[:10], 1):
            print(f"   {i:2d}. {metric['name']}: {metric['duration']:.3f}s")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description='Performance comparison and analysis')
    parser.add_argument('--list', action='store_true', help='List available benchmarks')
    parser.add_argument('--details', metavar='NAME', help='Show details for a benchmark')
    parser.add_argument('--compare', nargs=2, metavar=('CURRENT', 'BASELINE'), 
                       help='Compare two benchmarks')
    parser.add_argument('--latest', action='store_true', 
                       help='Compare latest benchmark with baseline_comprehensive')
    
    args = parser.parse_args()
    
    if args.list:
        benchmarks = list_benchmarks()
        if not benchmarks:
            print("📁 No benchmarks found. Run benchmark_performance.py to create some!")
        else:
            print("📁 Available Benchmarks:")
            for name in benchmarks:
                try:
                    data = load_benchmark(name)
                    desc = data.get('description', 'No description')[:50]
                    timestamp = data['timestamp'][:19]  # Just date and time
                    print(f"   {name:25} - {timestamp} - {desc}")
                except Exception as e:
                    print(f"   {name:25} - ERROR: {e}")
    
    elif args.details:
        show_benchmark_details(args.details)
    
    elif args.compare:
        current, baseline = args.compare
        compare_benchmarks(current, baseline)
    
    elif args.latest:
        compare_benchmarks("latest_test_session", "baseline_comprehensive")
    
    else:
        # Default: show available benchmarks
        benchmarks = list_benchmarks()
        if len(benchmarks) >= 2:
            print("💡 Tip: Use --compare to compare benchmarks")
            print("💡 Example: python compare_performance.py --compare latest_test_session baseline_comprehensive")
        
        print("\n📁 Available benchmarks:")
        for name in benchmarks:
            print(f"   - {name}")
        
        if not benchmarks:
            print("📁 No benchmarks found.")
            print("💡 Run: python benchmark_performance.py")


if __name__ == "__main__":
    main()