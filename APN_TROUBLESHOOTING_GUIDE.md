# comma 3X APN Connection Troubleshooting Guide

## Summary

Your **comma 3X** device is designed to use **automatic APN configuration**. The APN should be **blank/empty** to enable auto-config mode.

## The Correct APN Configuration

### What the APN Should Be:
- **APN value**: Empty/blank (`""`)
- **Auto-config**: Enabled (`true`)

### Why Empty?

The openpilot code in `system/hardware/tici/hardware.py` (lines 449-451) explicitly clears any manual APN settings:

```python
if self.get_device_type() in ("tici", "tizi"):
    # clear out old blue prime initial APN
    os.system('mmcli -m any --3gpp-set-initial-eps-bearer-settings="apn="')
```

This allows the modem to automatically negotiate the correct APN with your carrier.

## Why It's Not Connecting

Based on the code comment "clear out old blue prime initial APN", there was likely a legacy APN configuration that interferes with modern auto-configuration. If your device worked in the past but doesn't now, possible causes:

1. **Manual APN Override**: The `GsmApn` parameter might be set, overriding auto-config
2. **Stale Modem Configuration**: Old APN settings cached in the modem
3. **NetworkManager Connection Issues**: The GSM connection profile may be misconfigured
4. **Carrier Changes**: Your carrier may have changed their network requirements

## Diagnostic Steps

### 1. Check Current Configuration

Run the diagnostic script:
```bash
bash fix_apn_connection.sh
```

This will check:
- Device type
- Current APN parameter value
- Modem status
- NetworkManager connections
- SIM card status

### 2. Manual Diagnostics

Check the modem status:
```bash
mmcli -m any
```

Check for GSM connections:
```bash
nmcli connection show
```

Check if APN parameter is set:
```bash
cat /data/params/d/GsmApn 2>/dev/null
```

Check current 3GPP EPS bearer settings:
```bash
mmcli -m any --3gpp-show-initial-eps-bearer-settings
```

## Fix Instructions

### Quick Fix (Recommended)

Run the automated fix script:
```bash
sudo bash apply_apn_fix.sh
```

This script will:
1. Clear any manually set APN parameter
2. Reset the modem's initial EPS bearer settings to empty
3. Restart the cellular connection
4. Verify the connection status

### Manual Fix

If you prefer to apply fixes manually:

#### Step 1: Clear Manual APN Setting
```bash
rm -f /data/params/d/GsmApn
```

#### Step 2: Clear Initial EPS Bearer APN
```bash
mmcli -m any --3gpp-set-initial-eps-bearer-settings="apn="
```

#### Step 3: Restart GSM Connection
```bash
# Find the GSM connection name
nmcli connection show | grep gsm

# Restart it (replace 'lte' with your connection name if different)
nmcli connection down lte
nmcli connection up lte
```

#### Step 4: Reconfigure Modem (if still not working)
```python
python3 << EOF
from openpilot.system.hardware import HARDWARE
HARDWARE.configure_modem()
EOF
```

#### Step 5: Wait and Check
Wait 1-2 minutes, then check status:
```bash
mmcli -m any
```

Look for `state: connected` in the output.

## Expected Configuration Files

### /etc/NetworkManager/system-connections/esim.nmconnection

Should contain:
```ini
[gsm]
apn=
home-only=false
auto-config=true
```

If this file exists and matches the above, auto-config is properly enabled.

## Device Type Information

The comma 3X runs on the "tici" or "tizi" hardware platform. You can check your device type:

```bash
cat /sys/firmware/devicetree/base/model
```

## Still Not Working?

If the connection still fails after trying these fixes:

### 1. Check SIM Card and Carrier
- Ensure your SIM card is properly inserted
- Verify the SIM is activated with your carrier
- Confirm you have an active data plan
- Some carriers require explicit APN configuration (see below)

### 2. Try Manual APN (Last Resort)

If auto-config doesn't work with your carrier, you may need to manually set the APN. You can do this through the openpilot UI:

1. Go to Settings → Network → Advanced
2. Tap "APN Setting" → "EDIT"  
3. Enter your carrier's APN (contact your carrier for this)

Common carrier APNs:
- **AT&T**: `phone` or `broadband`
- **T-Mobile**: `fast.t-mobile.com`
- **Verizon**: `vzwinternet`
- **Google Fi**: `h2g2`

### 3. Check for ModemManager Issues

Check ModemManager logs:
```bash
journalctl -u ModemManager -n 100
```

Restart ModemManager:
```bash
sudo systemctl restart ModemManager
```

### 4. Hardware Issues

If nothing works:
- Try removing and reinserting the SIM card
- Reboot the device
- Check for physical damage to the SIM slot
- Test with a different SIM card if available

## Technical Details

### How Auto-Config Works

1. When APN is empty and `auto-config=true`, NetworkManager uses ModemManager's automatic provisioning
2. ModemManager reads the SIM's IMSI (International Mobile Subscriber Identity)
3. It looks up the carrier in its internal database
4. It automatically configures the appropriate APN, authentication, and IP settings

### The configure_modem() Function

The `configure_modem()` function in `system/hardware/tici/hardware.py` does several things:

For "tici" and "tizi" devices (which includes the comma 3X):
- Clears the initial EPS bearer APN setting
- Configures the modem for data-centric operation
- Disables IMS (IP Multimedia Subsystem)
- Sets the UE usage setting for data

## References

- Code: `system/hardware/tici/hardware.py` (configure_modem function, line 438)
- Config: `system/hardware/tici/esim.nmconnection`
- UI: `selfdrive/ui/qt/network/networking.cc` (APN settings UI)
- Network Manager: `selfdrive/ui/qt/network/wifi_manager.cc` (updateGsmSettings function, line 414)

## Additional Resources

- NetworkManager GSM documentation: https://networkmanager.dev/docs/api/latest/settings-gsm.html
- ModemManager documentation: https://www.freedesktop.org/wiki/Software/ModemManager/
- comma.ai Discord: https://discord.comma.ai (for community support)

---

**Note**: The "3X" in "comma 3X" refers to the device model name, not a carrier designation or APN suffix.
