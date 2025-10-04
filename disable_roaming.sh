#!/bin/bash
# Disable roaming - return to home network only

echo ""
echo "=========================================="
echo "  Disable Roaming - Home Network Only"
echo "=========================================="
echo ""

# Remove roaming parameter
if [ -f "/data/params/d/GsmRoaming" ]; then
    rm -f /data/params/d/GsmRoaming
    echo "✅ Disabled GsmRoaming parameter"
else
    echo "ℹ️  GsmRoaming was not set"
fi

# Set home-only to true
nmcli connection modify lte gsm.home-only true
echo "✅ Set gsm.home-only to true (roaming disabled)"

# Restart connection
nmcli connection down lte 2>/dev/null
sleep 2
nmcli connection up lte
echo "✅ Connection restarted"

echo ""
echo "✅ Roaming disabled - device will only use home network"
echo ""
