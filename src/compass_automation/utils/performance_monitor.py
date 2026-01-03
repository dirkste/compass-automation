#!/usr/bin/env python3
"""
Performance measurement and benchmarking utilities for Compass automation.

This module provides tools to measure and track performance across different
components of the automation system, including test execution, browser operations,
and system resource usage.
"""

import time
import psutil
import functools
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import json
import statistics


@dataclass
class PerformanceMetric:
    """Single performance measurement."""
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    memory_start: Optional[float] = None
    memory_end: Optional[float] = None
    memory_peak: Optional[float] = None
    cpu_percent: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def finish(self):
        """Mark the metric as finished and calculate duration."""
        if self.end_time is None:
            self.end_time = time.perf_counter()
            self.duration = self.end_time - self.start_time
            self.memory_end = psutil.Process().memory_info().rss / 1024 / 1024  # MB


@dataclass
class PerformanceSummary:
    """Summary of performance metrics."""
    total_duration: float
    average_duration: float
    min_duration: float
    max_duration: float
    memory_usage_mb: float
    memory_peak_mb: float
    cpu_average: float
    operation_count: int
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system.
    
    Features:
    - Function execution timing
    - Memory usage tracking
    - CPU utilization monitoring
    - Resource usage profiling
    - Benchmark comparison
    """
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.active_metrics: Dict[str, PerformanceMetric] = {}
        self._monitoring = False
        self._resource_thread = None
        self._resource_data = []
    
    def start_metric(self, name: str, metadata: Dict[str, Any] = None) -> str:
        """
        Start measuring a performance metric.
        
        Args:
            name: Unique name for this metric
            metadata: Additional context information
            
        Returns:
            str: Metric ID for later reference
        """
        metric_id = f"{name}_{len(self.metrics)}"
        
        metric = PerformanceMetric(
            name=name,
            start_time=time.perf_counter(),
            memory_start=psutil.Process().memory_info().rss / 1024 / 1024,  # MB
            metadata=metadata or {}
        )
        
        self.active_metrics[metric_id] = metric
        return metric_id
    
    def end_metric(self, metric_id: str) -> PerformanceMetric:
        """
        Finish measuring a performance metric.
        
        Args:
            metric_id: ID returned from start_metric
            
        Returns:
            PerformanceMetric: Completed metric with timing data
        """
        if metric_id not in self.active_metrics:
            raise ValueError(f"No active metric found with ID: {metric_id}")
        
        metric = self.active_metrics.pop(metric_id)
        metric.finish()
        
        # Add CPU usage if available
        try:
            metric.cpu_percent = psutil.cpu_percent()
        except:
            pass
        
        self.metrics.append(metric)
        return metric
    
    def measure_function(self, func_name: str = None, metadata: Dict[str, Any] = None):
        """
        Decorator to measure function execution performance.
        
        Args:
            func_name: Override function name for metrics
            metadata: Additional context information
            
        Usage:
            @monitor.measure_function()
            def my_slow_function():
                time.sleep(1)
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                name = func_name or f"{func.__module__}.{func.__name__}"
                metric_id = self.start_metric(name, metadata)
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    # Still record the metric even if function failed
                    metric = self.end_metric(metric_id)
                    metric.metadata['error'] = str(e)
                    raise
                else:
                    self.end_metric(metric_id)
                    return result
            
            return wrapper
        return decorator
    
    def start_resource_monitoring(self, interval: float = 0.1):
        """
        Start continuous resource monitoring in background thread.
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self._monitoring:
            return
        
        self._monitoring = True
        self._resource_data = []
        
        def monitor_resources():
            process = psutil.Process()
            while self._monitoring:
                try:
                    self._resource_data.append({
                        'timestamp': time.time(),
                        'memory_mb': process.memory_info().rss / 1024 / 1024,
                        'cpu_percent': process.cpu_percent(),
                        'threads': process.num_threads()
                    })
                    time.sleep(interval)
                except:
                    break
        
        self._resource_thread = threading.Thread(target=monitor_resources, daemon=True)
        self._resource_thread.start()
    
    def stop_resource_monitoring(self):
        """Stop continuous resource monitoring."""
        self._monitoring = False
        if self._resource_thread:
            self._resource_thread.join(timeout=1.0)
    
    def get_summary(self, name_filter: str = None) -> PerformanceSummary:
        """
        Get performance summary for completed metrics.
        
        Args:
            name_filter: Filter metrics by name (substring match)
            
        Returns:
            PerformanceSummary: Aggregated performance data
        """
        filtered_metrics = self.metrics
        if name_filter:
            filtered_metrics = [m for m in self.metrics if name_filter in m.name]
        
        if not filtered_metrics:
            return PerformanceSummary(
                total_duration=0,
                average_duration=0,
                min_duration=0,
                max_duration=0,
                memory_usage_mb=0,
                memory_peak_mb=0,
                cpu_average=0,
                operation_count=0,
                timestamp=datetime.now().isoformat()
            )
        
        durations = [m.duration for m in filtered_metrics if m.duration is not None]
        memory_usage = [m.memory_end for m in filtered_metrics if m.memory_end is not None]
        cpu_usage = [m.cpu_percent for m in filtered_metrics if m.cpu_percent is not None]
        
        # Resource monitoring peaks
        memory_peak = 0
        if self._resource_data:
            memory_peak = max(d['memory_mb'] for d in self._resource_data)
        
        return PerformanceSummary(
            total_duration=sum(durations),
            average_duration=statistics.mean(durations) if durations else 0,
            min_duration=min(durations) if durations else 0,
            max_duration=max(durations) if durations else 0,
            memory_usage_mb=statistics.mean(memory_usage) if memory_usage else 0,
            memory_peak_mb=memory_peak,
            cpu_average=statistics.mean(cpu_usage) if cpu_usage else 0,
            operation_count=len(filtered_metrics),
            timestamp=datetime.now().isoformat()
        )
    
    def save_benchmark(self, filename: str, description: str = ""):
        """
        Save current performance data as a benchmark.
        
        Args:
            filename: Benchmark file name (will be saved in benchmarks/ dir)
            description: Human-readable description of this benchmark
        """
        benchmark_dir = Path("benchmarks")
        benchmark_dir.mkdir(exist_ok=True)
        
        summary = self.get_summary()
        
        benchmark_data = {
            'timestamp': datetime.now().isoformat(),
            'description': description,
            'summary': {
                'total_duration': summary.total_duration,
                'average_duration': summary.average_duration,
                'min_duration': summary.min_duration,
                'max_duration': summary.max_duration,
                'memory_usage_mb': summary.memory_usage_mb,
                'memory_peak_mb': summary.memory_peak_mb,
                'cpu_average': summary.cpu_average,
                'operation_count': summary.operation_count
            },
            'metrics': [
                {
                    'name': m.name,
                    'duration': m.duration,
                    'memory_start': m.memory_start,
                    'memory_end': m.memory_end,
                    'cpu_percent': m.cpu_percent,
                    'metadata': m.metadata
                }
                for m in self.metrics
            ],
            'resource_data': self._resource_data[-1000:] if self._resource_data else []  # Last 1000 samples
        }
        
        benchmark_file = benchmark_dir / f"{filename}.json"
        with open(benchmark_file, 'w') as f:
            json.dump(benchmark_data, f, indent=2)
        
        print(f"✅ Benchmark saved: {benchmark_file}")
        return benchmark_file
    
    def compare_with_benchmark(self, benchmark_file: str) -> Dict[str, Any]:
        """
        Compare current performance with saved benchmark.
        
        Args:
            benchmark_file: Path to benchmark file
            
        Returns:
            Dict containing comparison results
        """
        benchmark_path = Path("benchmarks") / f"{benchmark_file}.json"
        if not benchmark_path.exists():
            raise FileNotFoundError(f"Benchmark file not found: {benchmark_path}")
        
        with open(benchmark_path) as f:
            benchmark_data = json.load(f)
        
        current_summary = self.get_summary()
        benchmark_summary = benchmark_data['summary']
        
        comparison = {
            'benchmark_date': benchmark_data['timestamp'],
            'current_date': current_summary.timestamp,
            'improvements': {},
            'regressions': {},
            'changes': {}
        }
        
        # Compare key metrics
        metrics_to_compare = [
            'total_duration', 'average_duration', 'memory_usage_mb', 
            'memory_peak_mb', 'cpu_average'
        ]
        
        for metric in metrics_to_compare:
            current_val = getattr(current_summary, metric)
            benchmark_val = benchmark_summary[metric]
            
            if benchmark_val > 0:  # Avoid division by zero
                change_percent = ((current_val - benchmark_val) / benchmark_val) * 100
                
                comparison['changes'][metric] = {
                    'current': current_val,
                    'benchmark': benchmark_val,
                    'change_percent': change_percent,
                    'change_absolute': current_val - benchmark_val
                }
                
                # Classify as improvement or regression
                # Lower is better for duration and resource usage
                if metric in ['total_duration', 'average_duration', 'memory_usage_mb', 'memory_peak_mb']:
                    if change_percent < -5:  # 5% improvement threshold
                        comparison['improvements'][metric] = change_percent
                    elif change_percent > 10:  # 10% regression threshold
                        comparison['regressions'][metric] = change_percent
                
        return comparison
    
    def clear_metrics(self):
        """Clear all collected metrics."""
        self.metrics.clear()
        self.active_metrics.clear()
        self._resource_data.clear()
    
    def print_summary(self, name_filter: str = None):
        """Print a formatted performance summary."""
        summary = self.get_summary(name_filter)
        
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE SUMMARY")
        print("=" * 60)
        print(f"Operations: {summary.operation_count}")
        print(f"Total Duration: {summary.total_duration:.3f}s")
        print(f"Average Duration: {summary.average_duration:.3f}s")
        print(f"Min Duration: {summary.min_duration:.3f}s")
        print(f"Max Duration: {summary.max_duration:.3f}s")
        print(f"Memory Usage: {summary.memory_usage_mb:.1f}MB")
        print(f"Memory Peak: {summary.memory_peak_mb:.1f}MB")
        print(f"CPU Average: {summary.cpu_average:.1f}%")
        print("=" * 60)


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


# Convenience decorators
def measure_performance(name: str = None, metadata: Dict[str, Any] = None):
    """Convenience decorator for measuring function performance."""
    return performance_monitor.measure_function(name, metadata)


def benchmark_test_suite(test_name: str):
    """
    Context manager for benchmarking entire test suites.
    
    Usage:
        with benchmark_test_suite("ai_workflow_tests"):
            # Run tests
            pass
    """
    class TestSuiteBenchmark:
        def __init__(self, name: str):
            self.name = name
            self.metric_id = None
        
        def __enter__(self):
            performance_monitor.start_resource_monitoring()
            self.metric_id = performance_monitor.start_metric(
                f"test_suite_{self.name}",
                {"suite_name": self.name}
            )
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            performance_monitor.end_metric(self.metric_id)
            performance_monitor.stop_resource_monitoring()
            
            if exc_type is None:
                # Tests passed, save benchmark
                performance_monitor.save_benchmark(
                    f"test_suite_{self.name}",
                    f"Benchmark for {self.name} test suite"
                )
    
    return TestSuiteBenchmark(test_name)


if __name__ == "__main__":
    # Example usage and testing
    print("🚀 Performance Monitor Test")
    
    # Test basic measurement
    @measure_performance("example_function")
    def example_function():
        time.sleep(0.1)
        return "done"
    
    # Test suite measurement
    with benchmark_test_suite("example_suite"):
        example_function()
        example_function()
    
    performance_monitor.print_summary()