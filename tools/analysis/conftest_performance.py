# Performance measurement pytest plugin

# Add this to pytest.ini to enable:
# [tool:pytest]
# addopts = -p performance_plugin

"""
Pytest plugin for automatic performance measurement during test runs.
"""

import pytest
import time
import psutil
from typing import Dict, List
from compass_automation.utils.performance_monitor import performance_monitor


class PerformancePlugin:
    """Pytest plugin to automatically measure test performance."""
    
    def __init__(self):
        self.test_metrics: Dict[str, Dict] = {}
        self.session_start_time = None
        self.session_start_memory = None
    
    def pytest_sessionstart(self, session):
        """Called at start of test session."""
        self.session_start_time = time.perf_counter()
        self.session_start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        performance_monitor.clear_metrics()
        performance_monitor.start_resource_monitoring()
        print(f"\n🚀 Performance monitoring started for test session")
    
    def pytest_sessionfinish(self, session, exitstatus):
        """Called at end of test session."""
        performance_monitor.stop_resource_monitoring()
        
        session_duration = time.perf_counter() - self.session_start_time
        session_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        print(f"\n📊 Test Session Performance Summary:")
        print(f"   Total Duration: {session_duration:.3f}s")
        print(f"   Memory Start: {self.session_start_memory:.1f}MB")
        print(f"   Memory End: {session_memory:.1f}MB")
        print(f"   Memory Change: {session_memory - self.session_start_memory:+.1f}MB")
        
        # Save session benchmark if tests passed
        if exitstatus == 0:
            performance_monitor.save_benchmark(
                "latest_test_session",
                f"Latest test session - {len(self.test_metrics)} tests"
            )
            print(f"✅ Performance benchmark saved for successful test run")
        
        performance_monitor.print_summary()
    
    def pytest_runtest_setup(self, item):
        """Called before each test."""
        test_id = item.nodeid
        self.test_metrics[test_id] = {
            'start_time': time.perf_counter(),
            'start_memory': psutil.Process().memory_info().rss / 1024 / 1024,
            'metric_id': performance_monitor.start_metric(
                f"test_{item.name}",
                {
                    'test_file': str(item.fspath),
                    'test_name': item.name,
                    'test_id': test_id,
                    'markers': [m.name for m in item.iter_markers()]
                }
            )
        }
    
    def pytest_runtest_teardown(self, item):
        """Called after each test."""
        test_id = item.nodeid
        if test_id in self.test_metrics:
            test_data = self.test_metrics[test_id]
            
            # Finish the performance metric
            metric = performance_monitor.end_metric(test_data['metric_id'])
            
            # Update test data
            test_data.update({
                'end_time': time.perf_counter(),
                'end_memory': psutil.Process().memory_info().rss / 1024 / 1024,
                'duration': metric.duration,
                'memory_change': metric.memory_end - metric.memory_start if metric.memory_start else 0
            })
    
    def pytest_runtest_logreport(self, report):
        """Called when test report is available."""
        if report.when == "call":  # Only for the actual test call, not setup/teardown
            test_id = report.nodeid
            if test_id in self.test_metrics:
                self.test_metrics[test_id]['outcome'] = report.outcome
                self.test_metrics[test_id]['failed'] = report.failed
                
                # Print performance info for slow tests (>1s)
                duration = self.test_metrics[test_id].get('duration', 0)
                if duration > 1.0:
                    print(f"\n⏱️  SLOW TEST: {report.nodeid} took {duration:.3f}s")


def pytest_configure(config):
    """Register the performance plugin."""
    if not hasattr(config, 'performance_plugin'):
        config.performance_plugin = PerformancePlugin()
        config.pluginmanager.register(config.performance_plugin, 'performance_plugin')