#!/usr/bin/env python3
import subprocess
import sys
import os

os.chdir(r'C:\Users\liliwen\OneDrive\Desktop\code\AlphaPulse\scripts')
result = subprocess.run([sys.executable, 'test_improvements.py'], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print("Return code:", result.returncode)
