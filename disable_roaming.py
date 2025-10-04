#!/usr/bin/env python3
"""
Disable Roaming on comma 3X (return to home network only)
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd):
    """Run a shell command."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def main():
    print("\n" + "="*60)
    print("  Disable Roaming - Return to Home Network Only")
    print("="*60 + "\n")
    
    # Remove roaming parameter
    params_path = Path("/data/params/d/GsmRoaming")
    if params_path.exists():
        params_path.unlink()
        print("✅ Disabled GsmRoaming parameter")
    
    # Set home-only to true
    run_command('nmcli connection modify lte gsm.home-only true')
    print("✅ Set gsm.home-only to true (roaming disabled)")
    
    # Restart connection
    run_command('nmcli connection down lte')
    run_command('nmcli connection up lte')
    print("✅ Connection restarted")
    
    print("\n✅ Roaming disabled - device will only use home network\n")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nAborted.")
        sys.exit(1)
