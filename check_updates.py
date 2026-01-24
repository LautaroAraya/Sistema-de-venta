#!/usr/bin/env python
"""Script para forzar chequeo de actualizaciones"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

## from utils.updater import UpdateManager

base_path = os.path.dirname(os.path.abspath(__file__))
## updater = UpdateManager(base_path)

print(f"Versión actual: {updater.current_version}")
## print(f"Versión actual: {updater.current_version}")
print(f"Buscando actualizaciones en GitHub...")

## has_updates, error = updater.check_for_updates(force=True)

print(f"\n¿Hay actualizaciones?: {has_updates}")
if error:
    print(f"Error: {error}")

## config = updater.get_update_config()
print(f"\nConfigración actualizada:")
print(f"  - latest_version: {config.get('latest_version')}")
print(f"  - update_available: {config.get('update_available')}")
print(f"  - download_url: {config.get('download_url')}")
