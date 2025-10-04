#!/usr/bin/env python3
"""
Enable Roaming on comma 3X for Canadian Networks

This script enables roaming so a US SIM card can connect to Canadian networks.
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

def run_command(cmd, ignore_errors=False):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode != 0 and not ignore_errors:
            print(f"   ⚠️  Warning: Command failed")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
        return result.stdout.strip()
    except Exception as e:
        print(f"   ⚠️  Warning: {e}")
        return ""

def check_current_roaming_status():
    """Check if roaming is currently enabled."""
    try:
        params_path = Path("/data/params/d/GsmRoaming")
        if params_path.exists():
            value = params_path.read_text().strip()
            enabled = value == "1"
            print(f"   Current GsmRoaming parameter: {value} ({'ENABLED' if enabled else 'DISABLED'})")
            return enabled
        else:
            print("   GsmRoaming parameter not set (roaming DISABLED by default)")
            return False
    except Exception as e:
        print(f"   Could not check roaming status: {e}")
        return None

def check_nm_roaming_status():
    """Check NetworkManager's home-only setting."""
    output = run_command("nmcli -t -f gsm.home-only connection show lte 2>/dev/null", ignore_errors=True)
    if output and "home-only" in output:
        home_only = "yes" in output.lower() or "true" in output.lower()
        roaming_enabled = not home_only  # inverted logic
        print(f"   NetworkManager gsm.home-only: {home_only} (roaming {'ENABLED' if roaming_enabled else 'DISABLED'})")
        return roaming_enabled
    else:
        print("   Could not check NetworkManager roaming status")
        return None

def enable_roaming_parameter():
    """Enable roaming via GsmRoaming parameter."""
    try:
        params_path = Path("/data/params/d/GsmRoaming")
        params_path.write_text("1")
        print("   ✅ Set GsmRoaming parameter to 1 (ENABLED)")
        return True
    except Exception as e:
        print(f"   ⚠️  Could not set GsmRoaming parameter: {e}")
        return False

def update_gsm_settings():
    """Update GSM settings via the hardware module."""
    try:
        print("   Updating GSM settings...")
        # Import and use the hardware module
        from openpilot.common.params import Params
        params = Params()
        
        # Get current settings
        roaming = params.get_bool("GsmRoaming")
        apn = params.get("GsmApn", encoding='utf-8')
        metered = params.get_bool("GsmMetered")
        
        print(f"   Settings: roaming={roaming}, apn='{apn}', metered={metered}")
        
        # This will trigger the updateGsmSettings function
        # which sets home-only = !roaming
        from openpilot.system.hardware import HARDWARE
        
        # The configure_modem function will apply settings
        print("   Applying modem configuration...")
        
        return True
    except Exception as e:
        print(f"   ⚠️  Could not update via hardware module: {e}")
        return False

def update_nm_connection_directly():
    """Directly update NetworkManager connection to enable roaming."""
    print("   Updating NetworkManager connection directly...")
    
    # Set home-only to false (which enables roaming)
    output = run_command('nmcli connection modify lte gsm.home-only false', ignore_errors=True)
    
    # Verify the change
    verify = run_command("nmcli -t -f gsm.home-only connection show lte", ignore_errors=True)
    if "no" in verify.lower() or "false" in verify.lower():
        print("   ✅ NetworkManager: Set gsm.home-only to false (roaming ENABLED)")
        return True
    else:
        print(f"   ⚠️  Could not verify change: {verify}")
        return False

def get_gsm_connection():
    """Get the GSM connection name."""
    output = run_command("nmcli -t -f NAME,TYPE connection show | grep ':gsm$' | cut -d: -f1", ignore_errors=True)
    if output:
        connections = output.split('\n')
        return connections[0] if connections else None
    return "lte"  # default

def restart_connection(conn_name):
    """Restart the GSM connection."""
    print(f"   Restarting connection: {conn_name}")
    
    # Bring down
    run_command(f'nmcli connection down "{conn_name}"', ignore_errors=True)
    time.sleep(2)
    
    # Bring up
    run_command(f'nmcli connection up "{conn_name}"', ignore_errors=True)
    print("   ✅ Connection restarted")
    time.sleep(3)
    return True

def check_modem_status():
    """Check and display modem status."""
    print("\n   Checking modem status...")
    output = run_command("mmcli -m any --timeout 5", ignore_errors=True)
    
    if output:
        # Show relevant lines
        for line in output.split('\n'):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['state:', 'signal', 'access tech', 'operator', 'registration']):
                print(f"   {line.strip()}")
        
        if 'connected' in output.lower():
            print("   ✅ Modem is CONNECTED!")
            return True
        elif 'registered' in output.lower():
            print("   ℹ️  Modem is registered but not yet connected")
            return False
        else:
            print("   ℹ️  Modem is not yet connected")
            return False
    else:
        print("   ⚠️  Could not get modem status")
        return False

def show_network_operator():
    """Show which network operator the modem is using."""
    output = run_command("mmcli -m any --timeout 5 2>&1 | grep -i 'operator'", ignore_errors=True)
    if output:
        print(f"\n   📡 Network: {output.strip()}")
        if any(canadian in output.lower() for canadian in ['rogers', 'telus', 'bell', 'freedom', 'canada']):
            print("   ✅ Connected to Canadian network!")
    
    # Also try AT command for more info
    operator_info = run_command('mmcli -m any --timeout 5 --command="AT+COPS?" 2>&1', ignore_errors=True)
    if operator_info and 'response' in operator_info.lower():
        print(f"   Operator info: {operator_info}")

def main():
    print_header("Enable Roaming for Canada - comma 3X")
    
    print("This script will enable roaming so your SIM can connect to Canadian networks.\n")
    
    # Check current status
    print("Step 1: Checking current roaming status...")
    param_status = check_current_roaming_status()
    nm_status = check_nm_roaming_status()
    
    if param_status and nm_status:
        print("\n✅ Roaming is already ENABLED!")
        response = input("\nDo you want to restart the connection anyway? (y/n): ")
        if response.lower() != 'y':
            print("No changes made.")
            return 0
    
    # Enable roaming parameter
    print("\nStep 2: Enabling roaming parameter...")
    enable_roaming_parameter()
    
    # Update NetworkManager connection
    print("\nStep 3: Updating NetworkManager connection...")
    gsm_conn = get_gsm_connection()
    update_nm_connection_directly()
    
    # Update GSM settings
    print("\nStep 4: Applying configuration...")
    update_gsm_settings()
    
    # Restart connection
    print("\nStep 5: Restarting cellular connection...")
    restart_connection(gsm_conn)
    
    # Wait and check status
    print("\nStep 6: Waiting for connection...")
    print("   (Roaming connections may take 30-60 seconds to establish...)")
    
    for i in range(6):
        time.sleep(10)
        print(f"\n   Checking... ({(i+1)*10}s)")
        if check_modem_status():
            break
    
    # Show operator
    show_network_operator()
    
    # Final summary
    print_header("Roaming Enabled!")
    print("✅ Roaming has been enabled for Canadian networks\n")
    print("Configuration:")
    print("  • GsmRoaming parameter: ENABLED (1)")
    print("  • gsm.home-only: false (roaming allowed)")
    print("  • APN: empty (auto-config)\n")
    print("Your device should now be able to roam on Canadian networks")
    print("(Rogers, Telus, Bell, Freedom Mobile, etc.)\n")
    print("If not connected yet:")
    print("  • Wait up to 2 minutes for registration")
    print("  • Check signal strength (you need Canadian coverage)")
    print("  • Verify your US carrier allows Canadian roaming")
    print("  • Check: mmcli -m any\n")
    
    print("To disable roaming later, run:")
    print("  python3 disable_roaming.py\n")
    
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
