# Data Directory

This directory contains MVA data files for the automation tests.

## Files:
- `mva.csv.template` - Template showing the expected format
- `mva.csv` - Your actual MVA data (not tracked in git)

## Setup:
1. Copy `mva.csv.template` to `mva.csv`
2. Replace the example data with your actual MVA numbers
3. The actual `mva.csv` file is ignored by git for security

## Format:
```csv
# Comments start with #
12345678
87654321
```

One MVA number per line, comments allowed with #.