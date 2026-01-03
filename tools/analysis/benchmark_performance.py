#!/usr/bin/env python3
"""
Performance benchmarking script for Compass automation.

This script runs various components of the system to establish performance
baselines and identify optimization opportunities.
"""

import sys
import time
import subprocess
from pathlib import Path
from compass_automation.utils.performance_monitor import performance_monitor, benchmark_test_suite
from compass_automation.utils.logger import log


def run_test_suite_benchmark(suite_name: str, test_path: str, description: str):
    """
    Run a test suite and capture performance metrics.
    
    Args:
        suite_name: Name for the benchmark
        test_path: Path to test file or pattern
        description: Human-readable description
    """
    print(f"\n🔄 Benchmarking: {suite_name}")
    print(f"📋 Description: {description}")
    print(f"📁 Test Path: {test_path}")
    
    start_time = time.time()
    
    try:
        # Run pytest with timing information
        cmd = [
            sys.executable, "-m", "pytest", 
            test_path, "-v", "--tb=short", 
            "--durations=10"  # Show 10 slowest tests
        ]
        
        with benchmark_test_suite(suite_name):
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minute timeout
            )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {suite_name}: PASSED in {duration:.2f}s")
        else:
            print(f"❌ {suite_name}: FAILED in {duration:.2f}s")
            print("STDOUT:", result.stdout[-500:])  # Last 500 chars
            print("STDERR:", result.stderr[-500:])
        
        return {
            'suite_name': suite_name,
            'duration': duration,
            'success': result.returncode == 0,
            'test_count': result.stdout.count('PASSED') + result.stdout.count('FAILED'),
            'output_size': len(result.stdout) + len(result.stderr)
        }
        
    except subprocess.TimeoutExpired:
        print(f"⏱️ {suite_name}: TIMEOUT after 5 minutes")
        return {
            'suite_name': suite_name,
            'duration': 300,
            'success': False,
            'test_count': 0,
            'output_size': 0,
            'timeout': True
        }
    except Exception as e:
        print(f"💥 {suite_name}: ERROR - {e}")
        return {
            'suite_name': suite_name,
            'duration': 0,
            'success': False,
            'test_count': 0,
            'output_size': 0,
            'error': str(e)
        }


def benchmark_data_operations():
    """Benchmark data loading and processing operations."""
    print("\n🔄 Benchmarking: Data Operations")
    
    performance_monitor.start_resource_monitoring()
    
    # Test MVA data loading
    metric_id = performance_monitor.start_metric(
        "mva_data_loading",
        {"operation": "load_mvas_from_csv"}
    )
    
    try:
        from compass_automation.utils.data_loader import load_mvas
        
        # Load MVA data multiple times to test caching impact
        for i in range(10):
            mvas = load_mvas("data/mva.csv")
        
        performance_monitor.end_metric(metric_id)
        print(f"✅ MVA Data Loading: {len(mvas)} MVAs loaded 10 times")
        
    except Exception as e:
        performance_monitor.end_metric(metric_id)
        print(f"❌ MVA Data Loading: ERROR - {e}")
    
    # Test log processing
    metric_id = performance_monitor.start_metric(
        "log_processing",
        {"operation": "validation_report_generation"}
    )
    
    try:
        from compass_automation.utils.test_validation import create_validation_report
        
        # Generate validation report multiple times
        for i in range(5):
            report = create_validation_report()
        
        performance_monitor.end_metric(metric_id)
        print("✅ Log Processing: Validation reports generated 5 times")
        
    except Exception as e:
        performance_monitor.end_metric(metric_id)
        print(f"❌ Log Processing: ERROR - {e}")
    
    performance_monitor.stop_resource_monitoring()


def benchmark_import_performance():
    """Benchmark module import times."""
    print("\n🔄 Benchmarking: Import Performance")
    
    imports_to_test = [
        ("utils.logger", "from utils.logger import log"),
        ("config.config_loader", "from config.config_loader import get_config"),
        ("utils.data_loader", "from utils.data_loader import load_mvas"),
        ("pages.login_page", "from pages.login_page import LoginPage"),
        ("ai_workflow_executor", "from ai_workflow_executor import AIWorkflowExecutor"),
        ("ai_context_detector", "from ai_context_detector import AIContextDetector"),
    ]
    
    for module_name, import_statement in imports_to_test:
        metric_id = performance_monitor.start_metric(
            f"import_{module_name}",
            {"module": module_name, "statement": import_statement}
        )
        
        try:
            exec(import_statement)
            performance_monitor.end_metric(metric_id)
            print(f"✅ Import {module_name}: Success")
        except Exception as e:
            performance_monitor.end_metric(metric_id)
            print(f"❌ Import {module_name}: ERROR - {e}")


def run_comprehensive_benchmark():
    """Run comprehensive performance benchmark suite."""
    print("🚀 Starting Comprehensive Performance Benchmark")
    print("=" * 60)
    
    # Clear any previous metrics
    performance_monitor.clear_metrics()
    
    # Benchmark import performance
    benchmark_import_performance()
    
    # Benchmark data operations
    benchmark_data_operations()
    
    # Benchmark test suites
    test_suites = [
        ("smoke_tests", "tests/test_smoke.py", "Basic smoke tests for core functionality"),
        ("unit_tests", "tests/test_unit_fast.py", "Fast unit tests for individual components"),
        ("integration_tests", "tests/test_integration.py", "Integration tests for system components"),
        ("ai_workflow_tests", "tests/test_ai_workflow_executor.py", "AI workflow execution tests"),
        ("ai_context_tests", "tests/test_ai_context_detector.py", "AI context detection tests"),
    ]
    
    suite_results = []
    
    for suite_name, test_path, description in test_suites:
        result = run_test_suite_benchmark(suite_name, test_path, description)
        suite_results.append(result)
    
    # Generate comprehensive summary
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE BENCHMARK RESULTS")
    print("=" * 60)
    
    # Test suite summary
    total_tests = sum(r.get('test_count', 0) for r in suite_results)
    total_duration = sum(r.get('duration', 0) for r in suite_results)
    successful_suites = sum(1 for r in suite_results if r.get('success', False))
    
    print(f"Test Suites: {successful_suites}/{len(suite_results)} passed")
    print(f"Total Tests: {total_tests}")
    print(f"Total Duration: {total_duration:.2f}s")
    print(f"Average per Test: {total_duration/total_tests:.3f}s" if total_tests > 0 else "N/A")
    
    # Performance monitor summary
    performance_monitor.print_summary()
    
    # Save baseline benchmark
    benchmark_file = performance_monitor.save_benchmark(
        "baseline_comprehensive",
        f"Comprehensive baseline benchmark - {total_tests} tests in {total_duration:.2f}s"
    )
    
    print(f"\n💾 Baseline benchmark saved: {benchmark_file}")
    print("🎯 Use this benchmark to measure future performance improvements!")
    
    return {
        'suite_results': suite_results,
        'total_tests': total_tests,
        'total_duration': total_duration,
        'performance_summary': performance_monitor.get_summary(),
        'benchmark_file': str(benchmark_file)
    }


def quick_benchmark():
    """Run a quick performance benchmark for development."""
    print("⚡ Running Quick Performance Benchmark")
    print("-" * 40)
    
    performance_monitor.clear_metrics()
    
    # Quick import test
    benchmark_import_performance()
    
    # Quick data operation test
    benchmark_data_operations()
    
    # Quick smoke test
    result = run_test_suite_benchmark(
        "quick_smoke", 
        "tests/test_smoke.py", 
        "Quick smoke test benchmark"
    )
    
    performance_monitor.print_summary()
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Performance benchmarking for Compass automation')
    parser.add_argument('--quick', action='store_true', help='Run quick benchmark only')
    parser.add_argument('--suite', help='Run specific test suite benchmark')
    
    args = parser.parse_args()
    
    if args.quick:
        quick_benchmark()
    elif args.suite:
        run_test_suite_benchmark(args.suite, f"tests/test_{args.suite}.py", f"Benchmark for {args.suite}")
    else:
        run_comprehensive_benchmark()