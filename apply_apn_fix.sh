#!/bin/bash
# Script to apply APN connection fixes on comma 3X

set -e

echo "=== Applying comma 3X APN Connection Fix ==="
echo ""
echo "This script will:"
echo "  1. Clear any manually set APN configuration"
echo "  2. Reset the modem's initial EPS bearer settings"
echo "  3. Restart the cellular connection"
echo ""

read -p "Do you want to proceed? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Step 1: Clearing manually set APN parameter..."
if [ -f "/data/params/d/GsmApn" ]; then
    rm -f /data/params/d/GsmApn
    echo "   ✓ Removed GsmApn parameter"
else
    echo "   ℹ GsmApn parameter was not set"
fi

echo ""
echo "Step 2: Clearing initial EPS bearer APN settings (resets to auto-config)..."
if command -v mmcli &> /dev/null; then
    mmcli -m any --3gpp-set-initial-eps-bearer-settings="apn=" || echo "   ⚠️  Warning: Could not clear EPS bearer settings"
    echo "   ✓ EPS bearer APN cleared"
else
    echo "   ⚠️  mmcli not available, skipping this step"
fi

echo ""
echo "Step 3: Ensuring esim connection has auto-config enabled..."
ESIM_CONN="/etc/NetworkManager/system-connections/esim.nmconnection"
if [ -f "$ESIM_CONN" ]; then
    # Check if auto-config is set
    if grep -q "auto-config=true" "$ESIM_CONN"; then
        echo "   ✓ auto-config is already enabled"
    else
        echo "   ⚠️  auto-config may not be enabled, manual intervention may be needed"
    fi
    
    # Check if apn is empty
    if grep -q "^apn=$" "$ESIM_CONN"; then
        echo "   ✓ APN is set to empty (auto-config)"
    else
        echo "   ⚠️  APN may have a value, should be empty for auto-config"
    fi
else
    echo "   ℹ esim.nmconnection not found"
fi

echo ""
echo "Step 4: Restarting cellular connection..."
if command -v nmcli &> /dev/null; then
    # Try to restart the GSM connection
    GSM_CONN=$(nmcli -t -f NAME,TYPE connection show | grep ":gsm$" | cut -d: -f1 | head -1)
    if [ ! -z "$GSM_CONN" ]; then
        echo "   Found GSM connection: $GSM_CONN"
        nmcli connection down "$GSM_CONN" 2>/dev/null || echo "   (connection was already down)"
        sleep 2
        nmcli connection up "$GSM_CONN" || echo "   ⚠️  Warning: Could not bring connection up"
        echo "   ✓ Connection restart attempted"
    else
        echo "   ⚠️  No GSM connection found"
    fi
else
    echo "   ⚠️  nmcli not available"
fi

echo ""
echo "Step 5: Checking connection status..."
sleep 5
if command -v mmcli &> /dev/null; then
    MODEM_STATE=$(mmcli -m any --timeout 5 2>&1 | grep "state:" || echo "unknown")
    echo "   Modem state: $MODEM_STATE"
    
    if echo "$MODEM_STATE" | grep -q "connected"; then
        echo "   ✅ SUCCESS: Modem is connected!"
    else
        echo "   ℹ Modem is not yet connected. It may take a minute to establish connection."
        echo "      Run 'mmcli -m any' to check status."
    fi
fi

echo ""
echo "=== Fix Applied ==="
echo ""
echo "Next steps:"
echo "  - Wait 1-2 minutes for the modem to connect"
echo "  - Check status with: mmcli -m any"
echo "  - Check connection with: nmcli connection show --active"
echo "  - If still not working, you may need to contact your carrier to verify:"
echo "    * SIM card is activated"
echo "    * Data plan is active"
echo "    * APN auto-configuration is supported"
echo ""
