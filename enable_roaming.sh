#!/bin/bash
# Quick script to enable roaming in Canada for comma 3X

set -e

echo ""
echo "=========================================="
echo "  Enable Roaming for Canada - comma 3X"
echo "=========================================="
echo ""

# Enable roaming parameter
echo "Step 1: Enabling roaming parameter..."
echo "1" > /data/params/d/GsmRoaming
echo "   ✅ Set GsmRoaming to 1 (ENABLED)"

# Update NetworkManager connection
echo ""
echo "Step 2: Updating NetworkManager connection..."
nmcli connection modify lte gsm.home-only false
echo "   ✅ Set gsm.home-only to false (roaming allowed)"

# Ensure APN is empty for auto-config
echo ""
echo "Step 3: Ensuring auto-config..."
nmcli connection modify lte gsm.apn "" 2>/dev/null || true
nmcli connection modify lte gsm.auto-config true 2>/dev/null || true
echo "   ✅ APN set to empty (auto-config enabled)"

# Restart connection
echo ""
echo "Step 4: Restarting cellular connection..."
nmcli connection down lte 2>/dev/null || true
sleep 2
nmcli connection up lte || echo "   (Connection will establish shortly)"
echo "   ✅ Connection restart initiated"

echo ""
echo "Step 5: Waiting for connection (30 seconds)..."
sleep 30

# Check status
echo ""
echo "Checking modem status..."
if command -v mmcli &> /dev/null; then
    mmcli -m any --timeout 5 2>&1 | grep -E "(state:|operator|signal)" || echo "   Modem info not available yet"
    
    if mmcli -m any --timeout 5 2>&1 | grep -q "connected"; then
        echo ""
        echo "✅ SUCCESS: Modem is connected!"
    else
        echo ""
        echo "ℹ️  Connection may still be establishing..."
    fi
fi

echo ""
echo "=========================================="
echo "  Roaming Enabled for Canadian Networks"
echo "=========================================="
echo ""
echo "Configuration:"
echo "  • GsmRoaming: ENABLED"
echo "  • gsm.home-only: false (roaming allowed)"
echo "  • APN: empty (auto-config)"
echo ""
echo "Your device can now roam on Canadian networks!"
echo ""
echo "To check status: mmcli -m any"
echo "To disable roaming: bash disable_roaming.sh"
echo ""
