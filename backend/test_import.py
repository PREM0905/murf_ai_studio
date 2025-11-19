#!/usr/bin/env python
import sys
import os

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Script location:", os.path.abspath(__file__))
print("\nPython sys.path:")
for i, path in enumerate(sys.path):
    print(f"  [{i}] {path}")

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
print(f"\nBackend path: {backend_path}")

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
    print(f"Added to sys.path: {backend_path}")

# Try importing
print("\n--- Attempting imports ---")
try:
    print("Importing integrations...")
    import integrations
    print("✓ integrations imported")
except ImportError as e:
    print(f"✗ Failed: {e}")

try:
    print("Importing integrations.audio...")
    import integrations.audio
    print("✓ integrations.audio imported")
except ImportError as e:
    print(f"✗ Failed: {e}")

try:
    print("Importing integrations.audio.asr_api...")
    from integrations.audio import asr_api
    print("✓ integrations.audio.asr_api imported")
except ImportError as e:
    print(f"✗ Failed: {e}")
