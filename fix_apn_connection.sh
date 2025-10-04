#!/bin/bash
# Script to troubleshoot and fix APN connection issues on comma 3X

echo "=== comma 3X APN Connection Troubleshooter ==="
echo ""

# Check device type
echo "1. Checking device type..."
if [ -f "/sys/firmware/devicetree/base/model" ]; then
    DEVICE_TYPE=$(cat /sys/firmware/devicetree/base/model | tr -d '\0' | sed 's/comma //')
    echo "   Device: $DEVICE_TYPE"
else
    echo "   ERROR: Cannot determine device type"
fi
echo ""

# Check current GsmApn parameter
echo "2. Checking current APN configuration..."
if command -v /data/params 2>&1 >/dev/null; then
    CURRENT_APN=$(cat /data/params/d/GsmApn 2>/dev/null || echo "NOT SET")
    echo "   Current GsmApn parameter: '$CURRENT_APN'"
    if [ "$CURRENT_APN" != "NOT SET" ] && [ ! -z "$CURRENT_APN" ]; then
        echo "   ⚠️  WARNING: APN is manually set. For auto-config, it should be empty."
    fi
else
    echo "   Params not accessible, skipping..."
fi
echo ""

# Check modem status
echo "3. Checking modem status..."
if command -v mmcli &> /dev/null; then
    echo "   Modem information:"
    mmcli -m any --timeout 5 2>&1 | grep -E "(manufacturer|model|state|signal|access tech)" || echo "   Could not get modem info"
    
    echo ""
    echo "   Current 3GPP settings:"
    mmcli -m any --3gpp-show-initial-eps-bearer-settings 2>&1 || echo "   Could not get 3GPP settings"
else
    echo "   mmcli not available"
fi
echo ""

# Check NetworkManager connections
echo "4. Checking NetworkManager GSM connections..."
if command -v nmcli &> /dev/null; then
    echo "   GSM connections:"
    nmcli connection show | grep gsm || echo "   No GSM connections found"
    
    echo ""
    echo "   Active connections:"
    nmcli connection show --active || echo "   No active connections"
else
    echo "   nmcli not available"
fi
echo ""

# Check SIM status
echo "5. Checking SIM card status..."
if command -v mmcli &> /dev/null; then
    SIM_INFO=$(mmcli -m any --timeout 5 2>&1 | grep -i "sim")
    if [ ! -z "$SIM_INFO" ]; then
        echo "$SIM_INFO"
    else
        echo "   No SIM information available"
    fi
fi
echo ""

echo "=== Recommended Actions ==="
echo ""

if [ "$CURRENT_APN" != "NOT SET" ] && [ ! -z "$CURRENT_APN" ]; then
    echo "ACTION 1: Clear the manually set APN to enable auto-configuration"
    echo "   Run: rm -f /data/params/d/GsmApn"
    echo ""
fi

echo "ACTION 2: Reset the initial EPS bearer settings (clears old APN)"
echo "   Run: mmcli -m any --3gpp-set-initial-eps-bearer-settings=\"apn=\""
echo ""

echo "ACTION 3: Restart the modem connection"
echo "   Run: nmcli connection down lte && nmcli connection up lte"
echo ""

echo "ACTION 4: If still not working, try reconfiguring the modem"
echo "   Run: python3 -c 'from openpilot.system.hardware import HARDWARE; HARDWARE.configure_modem()'"
echo ""

echo "=== End of Diagnostics ==="
