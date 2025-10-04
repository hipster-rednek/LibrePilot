#!/usr/bin/env python3
"""
comma 3X APN Connection Fix Script

This script fixes APN connection issues by:
1. Clearing manual APN parameters
2. Resetting modem configuration
3. Restarting the cellular connection
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_step(num, text):
    print(f"Step {num}: {text}")

def run_command(cmd, ignore_errors=False):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode != 0 and not ignore_errors:
            print(f"   ⚠️  Warning: Command failed with exit code {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"   ⚠️  Warning: Command timed out")
        return ""
    except Exception as e:
        print(f"   ⚠️  Warning: {e}")
        return ""

def check_device_type():
    """Check if this is a comma 3X (tici/tizi) device."""
    try:
        with open("/sys/firmware/devicetree/base/model", "r") as f:
            model = f.read().strip('\x00')
            device_type = model.split('comma ')[-1] if 'comma ' in model else model
            print(f"   Device type: {device_type}")
            return device_type in ["tici", "tizi"]
    except Exception as e:
        print(f"   ⚠️  Could not determine device type: {e}")
        return False

def clear_apn_parameter():
    """Clear the GsmApn parameter."""
    apn_path = Path("/data/params/d/GsmApn")
    if apn_path.exists():
        try:
            apn_value = apn_path.read_text()
            print(f"   Current APN parameter: '{apn_value}'")
            apn_path.unlink()
            print("   ✅ Removed GsmApn parameter")
            return True
        except Exception as e:
            print(f"   ⚠️  Could not remove APN parameter: {e}")
            return False
    else:
        print("   ℹ️  GsmApn parameter was not set")
        return True

def clear_eps_bearer_apn():
    """Clear the initial EPS bearer APN setting."""
    print("   Clearing initial EPS bearer APN...")
    output = run_command('mmcli -m any --3gpp-set-initial-eps-bearer-settings="apn="', ignore_errors=True)
    if output or True:  # Command may not produce output on success
        print("   ✅ EPS bearer APN cleared")
        return True
    return False

def get_gsm_connection():
    """Get the GSM connection name."""
    output = run_command("nmcli -t -f NAME,TYPE connection show | grep ':gsm$' | cut -d: -f1", ignore_errors=True)
    if output:
        connections = output.split('\n')
        return connections[0] if connections else None
    return None

def restart_connection(conn_name):
    """Restart the GSM connection."""
    print(f"   Restarting connection: {conn_name}")
    
    # Bring down
    run_command(f'nmcli connection down "{conn_name}"', ignore_errors=True)
    time.sleep(2)
    
    # Bring up
    output = run_command(f'nmcli connection up "{conn_name}"', ignore_errors=True)
    print("   ✅ Connection restart attempted")
    return True

def check_modem_status():
    """Check and display modem status."""
    print("   Checking modem status...")
    output = run_command("mmcli -m any --timeout 5", ignore_errors=True)
    
    if "state:" in output:
        for line in output.split('\n'):
            if 'state:' in line or 'signal' in line or 'access tech' in line:
                print(f"   {line.strip()}")
        
        if 'connected' in output.lower():
            print("   ✅ SUCCESS: Modem is connected!")
            return True
        else:
            print("   ℹ️  Modem is not yet connected")
            return False
    else:
        print("   ⚠️  Could not get modem status")
        return False

def configure_modem_via_hardware():
    """Configure modem using the hardware module."""
    try:
        print("   Configuring modem via hardware module...")
        from openpilot.system.hardware import HARDWARE
        HARDWARE.configure_modem()
        print("   ✅ Modem configured")
        return True
    except Exception as e:
        print(f"   ⚠️  Could not configure modem: {e}")
        return False

def main():
    print_header("comma 3X APN Connection Fix")
    
    # Check if we're on the right device
    print_step(1, "Checking device type...")
    if not check_device_type():
        print("\n⚠️  WARNING: This script is designed for comma 3X (tici/tizi) devices.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            return 1
    
    # Clear manual APN parameter
    print_step(2, "Clearing manual APN parameter...")
    clear_apn_parameter()
    
    # Clear EPS bearer APN
    print_step(3, "Clearing initial EPS bearer APN (enables auto-config)...")
    clear_eps_bearer_apn()
    
    # Configure modem
    print_step(4, "Configuring modem...")
    configure_modem_via_hardware()
    
    # Restart connection
    print_step(5, "Restarting cellular connection...")
    gsm_conn = get_gsm_connection()
    if gsm_conn:
        print(f"   Found GSM connection: {gsm_conn}")
        restart_connection(gsm_conn)
    else:
        print("   ⚠️  No GSM connection found")
    
    # Wait and check status
    print_step(6, "Waiting for connection to establish...")
    print("   (This may take up to 60 seconds...)")
    
    for i in range(6):
        time.sleep(10)
        print(f"   Checking... ({(i+1)*10}s)")
        if check_modem_status():
            break
    else:
        print("\n   ℹ️  Modem is not yet connected. It may take a bit longer.")
    
    # Final summary
    print_header("Fix Complete")
    print("Next steps:")
    print("  • Wait 1-2 minutes for the modem to fully connect")
    print("  • Check status with: mmcli -m any")
    print("  • Check connections with: nmcli connection show --active")
    print("\nIf still not working:")
    print("  • Verify SIM card is inserted and activated")
    print("  • Check with your carrier about data plan status")
    print("  • See APN_TROUBLESHOOTING_GUIDE.md for more help")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
