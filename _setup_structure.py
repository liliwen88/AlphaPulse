#!/usr/bin/env python3
"""Setup the AlphaPulse skill directory structure programmatically."""
import os
import sys

# Add scripts directory to path
scripts_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scripts_dir)

# Step 1: Create all directories using os.makedirs
dirs_to_create = [
    os.path.join(scripts_dir, "data"),
    os.path.join(scripts_dir, "core"),
    os.path.join(scripts_dir, "analysis"),
    os.path.join(scripts_dir, "reports"),
    os.path.join(scripts_dir, "reports", "templates"),
]

print("Creating directories...")
for directory in dirs_to_create:
    os.makedirs(directory, exist_ok=True)
    print(f"  ✓ {os.path.relpath(directory, scripts_dir)}")

# Step 2: Create __init__.py files
init_files = {
    "data/__init__.py": '"""Data layer: Market data fetching, news, models, and configuration."""\n',
    "core/__init__.py": '"""Core analysis engine: Scoring and strategy generation."""\n',
    "analysis/__init__.py": '"""Analysis layer: Technical indicators and charts."""\n',
    "reports/__init__.py": '"""Reports layer: Report generation and formatting."""\n',
    "reports/templates/__init__.py": '"""Report templates for different output formats."""\n',
}

print("\nCreating __init__.py files...")
for rel_path, content in init_files.items():
    full_path = os.path.join(scripts_dir, rel_path)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ {rel_path}")

print("\n✅ Directory structure created successfully!")
