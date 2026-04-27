#!/usr/bin/env python3
"""Standalone test of ExtensionBridge"""
import sys
sys.path.insert(0, '/Users/samuel.kim/dev/my/shop-search')

from models.extension_bridge import ExtensionBridge

print("Creating bridge...")
bridge = ExtensionBridge(port=8765)
print("Starting bridge...")
bridge.start()
print("Bridge started!")

import time
print("Keeping alive for 30 seconds...")
time.sleep(30)
print("Done")
