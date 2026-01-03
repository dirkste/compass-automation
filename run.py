import sys
import os
from pathlib import Path

# Add src directory to sys.path to allow importing the compass_automation package
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from compass_automation.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAutomation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred during execution: {e}")
        sys.exit(1)
