#!/usr/bin/env python3
"""Create directory structure for AlphaPulse skill reorganization."""

from pathlib import Path

BASE = Path(__file__).parent

dirs = [
    "data",
    "core",
    "analysis",
    "reports",
    "reports/templates",
]

for dir_name in dirs:
    dir_path = BASE / dir_name
    dir_path.mkdir(parents=True, exist_ok=True)
    print(f"Created: {dir_path}")

print("All directories created successfully!")
