# comma 3X APN Connection Fix

## The Answer to Your Question

**Q: What is the APN supposed to be on the comma 3X device?**

**A: The APN should be EMPTY/BLANK (`""`) to enable automatic configuration.**

The comma 3X is designed to automatically detect and configure the correct APN based on your SIM card and carrier. Setting a manual APN actually prevents it from working correctly.

## Why It's Not Connecting

Based on the openpilot codebase analysis, there's a comment in the code that says:

> "clear out old blue prime initial APN"

This indicates that older comma devices may have had a pre-configured APN that needs to be cleared. If your device worked in the past but isn't connecting now, it's likely because:

1. A manual APN is set (it should be empty)
2. The modem has cached old APN settings
3. Auto-configuration is disabled

## Quick Fix - Run This Now

### Option 1: Python Script (Recommended)
```bash
cd /workspace
sudo python3 fix_apn_python.py
```

### Option 2: Shell Script
```bash
cd /workspace
sudo bash apply_apn_fix.sh
```

Both scripts do the same thing:
- ✅ Clear manual APN settings
- ✅ Reset modem to auto-config mode
- ✅ Restart cellular connection
- ✅ Verify connection status

## What These Scripts Do

The fix scripts perform the exact operations that openpilot's `configure_modem()` function does:

1. **Remove manual APN parameter**: Deletes `/data/params/d/GsmApn`
2. **Clear EPS bearer APN**: Runs `mmcli -m any --3gpp-set-initial-eps-bearer-settings="apn="`
3. **Enable auto-config**: Ensures NetworkManager's auto-config is enabled
4. **Restart connection**: Brings down and up the GSM connection
5. **Verify**: Checks modem status to confirm connection

## Files Created

| File | Purpose |
|------|---------|
| `QUICK_FIX_SUMMARY.md` | Quick reference guide (read this first!) |
| `fix_apn_python.py` | Python script to apply fixes |
| `apply_apn_fix.sh` | Bash script to apply fixes |
| `fix_apn_connection.sh` | Diagnostic script (checks status only) |
| `APN_TROUBLESHOOTING_GUIDE.md` | Comprehensive troubleshooting guide |
| `README_APN_FIX.md` | This file |

## How to Use

### Step 1: Run Diagnostics (Optional)
```bash
bash fix_apn_connection.sh
```

This will show you the current state without making changes.

### Step 2: Apply the Fix
```bash
sudo python3 fix_apn_python.py
```

Or:
```bash
sudo bash apply_apn_fix.sh
```

### Step 3: Wait and Verify
Wait 1-2 minutes, then check:
```bash
mmcli -m any
```

Look for `state: connected` in the output.

### Step 4: If Still Not Working
Read the full troubleshooting guide:
```bash
cat APN_TROUBLESHOOTING_GUIDE.md
```

## Technical Details

### Where This is Configured

1. **Code**: `system/hardware/tici/hardware.py` (line 450)
   ```python
   # clear out old blue prime initial APN
   os.system('mmcli -m any --3gpp-set-initial-eps-bearer-settings="apn="')
   ```

2. **Config File**: `system/hardware/tici/esim.nmconnection`
   ```ini
   [gsm]
   apn=
   home-only=false
   auto-config=true
   ```

3. **UI**: Settings → Network → Advanced → APN Setting
   - Should be left blank for auto-configuration

### Device Information

- **Your device**: comma 3X
- **Hardware platform**: tici or tizi
- **Modem**: Qualcomm (configured via ModemManager)
- **Network Manager**: NetworkManager with GSM/3GPP support

### How Auto-Config Works

1. NetworkManager detects SIM card
2. Reads IMSI (International Mobile Subscriber Identity)
3. Looks up carrier in ModemManager's database
4. Automatically configures APN, authentication, and IP settings
5. Establishes cellular data connection

## Common Issues and Solutions

### Issue: "Modem not found"
**Solution**: Check if SIM card is properly inserted

### Issue: "Connection times out"
**Solution**: 
- Wait longer (can take 2-3 minutes)
- Check carrier signal strength
- Verify SIM is activated

### Issue: "Still not connecting after fix"
**Solution**:
1. Check with carrier that SIM is activated and data plan is active
2. Try rebooting the device
3. Test with a different SIM card if available
4. Some carriers may require manual APN (contact carrier)

### Issue: "Modem shows 'registered' but not 'connected'"
**Solution**: Restart the connection:
```bash
nmcli connection down lte && nmcli connection up lte
```

## What NOT to Do

❌ **Don't** set a manual APN unless your carrier specifically requires it
❌ **Don't** modify the esim.nmconnection file directly
❌ **Don't** disable auto-config
❌ **Don't** set an APN in the UI Settings (leave it blank)

## Expected Behavior After Fix

✅ APN parameter is empty/not set
✅ ModemManager auto-config is enabled  
✅ Modem state shows "connected"
✅ IP address is assigned
✅ Data connection works

## Manual APN (Last Resort Only)

If auto-config absolutely doesn't work with your carrier, you can set a manual APN through the UI:

1. Settings → Network → Advanced
2. APN Setting → EDIT
3. Enter carrier's APN

Common APNs:
- AT&T: `phone` or `broadband`
- T-Mobile: `fast.t-mobile.com`
- Verizon: `vzwinternet`
- Google Fi: `h2g2`

**Note**: This should only be needed if your carrier doesn't support auto-config, which is rare.

## Getting Help

If you're still having issues:

1. Check the logs:
   ```bash
   journalctl -u ModemManager -n 100
   journalctl -u NetworkManager -n 100
   ```

2. Post on comma.ai Discord: https://discord.comma.ai

3. Contact comma.ai support

## Summary

**The APN should be blank/empty for automatic configuration.**

The fix clears any manual APN settings and resets the modem to auto-config mode, which is how comma 3X devices are designed to work. Run one of the provided fix scripts and wait 1-2 minutes for the connection to establish.

---

Generated: 2025-10-04  
Based on: openpilot codebase analysis (commaai/openpilot)
