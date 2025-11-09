#!/usr/bin/env python3
"""
Quick test runner for compass-automation project.
Run fast unit tests without browser dependencies.
"""
import subprocess
import sys
import time
from pathlib import Path


def main():
    """Run fast unit tests and display results."""
    # Check for quiet mode
    quiet_mode = "--quiet" in sys.argv
    
    if not quiet_mode:
        print("[TEST] Running Compass Automation Unit Tests...")
        print("=" * 50)
    
    # Change to tests directory (relative to this script)
    script_dir = Path(__file__).parent
    tests_dir = script_dir / "tests"
    
    start_time = time.time()
    
    # Build pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        "test_unit_fast.py",
        "test_edge_cases.py", 
        "test_smoke.py",
        "test_integration.py",
        "test_integration_extended.py"
    ]
    
    if quiet_mode:
        cmd.extend(["-q", "--tb=no"])
    else:
        cmd.extend(["-v", "--tb=short", "--no-header"])
    
    try:
        result = subprocess.run(cmd, cwd=tests_dir, capture_output=True, text=True)
        elapsed = time.time() - start_time
        
        # Display results based on mode
        if not quiet_mode:
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
        
        # Summary
        if result.returncode == 0:
            if quiet_mode:
                print(f"[PASS] Tests passed ({elapsed:.2f}s)")
            else:
                print(f"[PASS] All tests passed in {elapsed:.2f} seconds!")
        else:
            if quiet_mode:
                print("[FAIL] Tests failed")
                print(result.stdout)  # Show failures even in quiet mode
            else:
                print(f"[FAIL] Some tests failed (exit code: {result.returncode})")
                print("Run with pytest directly for more details.")
        
        return result.returncode
        
    except Exception as e:
        print(f"[ERROR] Failed to run tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())