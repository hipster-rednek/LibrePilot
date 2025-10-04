# What the APN Should Be on Your comma 3X Device

## Quick Answer

**The APN should be EMPTY (blank).** 

Your comma 3X is designed to use **automatic APN configuration**.

## Details

Based on the openpilot source code analysis:

1. **APN Value**: Empty string `""`
2. **Auto-config**: Enabled
3. **Location in code**: `system/hardware/tici/hardware.py` line 450-451

The code explicitly clears any manual APN settings:
```python
# clear out old blue prime initial APN
os.system('mmcli -m any --3gpp-set-initial-eps-bearer-settings="apn="')
```

## Why It's Not Connecting

The comment in the code mentions "clear out old blue prime initial APN" - this suggests there was a legacy configuration that needs to be removed. Your device might have:

1. A manually set APN stored in the `GsmApn` parameter
2. Stale modem configuration from a previous setup
3. A misconfigured NetworkManager GSM connection

## How to Fix It

### Option 1: Run the Fix Script (Easiest)
```bash
sudo bash apply_apn_fix.sh
```

### Option 2: Run the Diagnostic First
```bash
bash fix_apn_connection.sh
```

### Option 3: Manual Fix
```bash
# Clear manual APN
rm -f /data/params/d/GsmApn

# Clear modem APN
mmcli -m any --3gpp-set-initial-eps-bearer-settings="apn="

# Restart connection
nmcli connection down lte
nmcli connection up lte
```

## Files Created for You

1. **APN_TROUBLESHOOTING_GUIDE.md** - Complete troubleshooting documentation
2. **fix_apn_connection.sh** - Diagnostic script (read-only, checks status)
3. **apply_apn_fix.sh** - Automated fix script (applies the fixes)

## Still Need Help?

If auto-config doesn't work with your carrier, you may need to manually set your carrier's APN through the openpilot UI (Settings → Network → Advanced → APN Setting).

Common carrier APNs (only if auto-config fails):
- AT&T: `phone` or `broadband`
- T-Mobile: `fast.t-mobile.com`
- Verizon: `vzwinternet`
- Google Fi: `h2g2`

But **try auto-config (empty APN) first** - it should work for most carriers!
