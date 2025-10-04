# comma 3X APN and Roaming Fix - Complete Guide

This repository contains complete troubleshooting resources for comma 3X connectivity issues.

## 📋 Quick Navigation

| Issue | Solution | File to Read |
|-------|----------|--------------|
| **Device won't connect at all** | [Fix APN Config](#fix-apn-configuration) | `QUICK_FIX_SUMMARY.md` |
| **Need to roam in Canada** | [Enable Roaming](#enable-roaming-in-canada) | `ROAMING_IN_CANADA.md` |
| **Want comprehensive info** | [Full Troubleshooting](#full-documentation) | `APN_TROUBLESHOOTING_GUIDE.md` |

---

## 🚨 Quick Answers

### Q: What should the APN be?
**A: EMPTY/BLANK (`""`)** for automatic configuration.

### Q: How do I enable roaming in Canada?
**A: Run `sudo python3 enable_roaming.py`** or use the UI toggle.

### Q: Why isn't it connecting?
**A: Run `sudo python3 fix_apn_python.py`** to reset configuration.

---

## 🔧 Fix APN Configuration

If your device isn't connecting to cellular at all:

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

### What This Does:
- ✅ Clears any manual APN settings
- ✅ Resets modem to auto-config mode
- ✅ Restarts cellular connection
- ✅ Verifies connection status

**Read**: `README_APN_FIX.md` or `QUICK_FIX_SUMMARY.md`

---

## 🇨🇦 Enable Roaming in Canada

If you have a US SIM and need to roam on Canadian networks:

### Option 1: Python Script (Recommended)
```bash
cd /workspace
sudo python3 enable_roaming.py
```

### Option 2: Shell Script
```bash
cd /workspace
sudo bash enable_roaming.sh
```

### Option 3: Via UI
1. Settings → Network → Advanced
2. Toggle "Enable Roaming" to ON
3. Ensure APN is blank

### What This Does:
- ✅ Enables roaming parameter
- ✅ Allows non-home network connections
- ✅ Keeps APN empty for auto-config
- ✅ Restarts cellular connection

**Read**: `ROAMING_IN_CANADA.md` for complete details

### To Disable Roaming Later:
```bash
sudo python3 disable_roaming.py
# or
sudo bash disable_roaming.sh
```

---

## 📁 All Available Scripts

### Diagnostic Scripts (Check Only)
- **`fix_apn_connection.sh`** - Checks current APN and connectivity status

### Fix Scripts (Apply Changes)
- **`fix_apn_python.py`** - Resets APN config (Python)
- **`apply_apn_fix.sh`** - Resets APN config (Bash)
- **`enable_roaming.py`** - Enables Canadian roaming (Python)
- **`enable_roaming.sh`** - Enables Canadian roaming (Bash)
- **`disable_roaming.py`** - Disables roaming (Python)
- **`disable_roaming.sh`** - Disables roaming (Bash)

### Documentation Files
- **`README_MASTER.md`** - This file (overview)
- **`QUICK_FIX_SUMMARY.md`** - Quick reference for APN issues
- **`README_APN_FIX.md`** - Complete APN troubleshooting
- **`APN_TROUBLESHOOTING_GUIDE.md`** - Detailed technical guide
- **`ROAMING_IN_CANADA.md`** - Complete roaming guide

---

## 🔍 Checking Status

### Check Modem Status
```bash
mmcli -m any
```

Look for:
- `state: connected` ✅ Good!
- `state: registered` ⏳ Connecting...
- `state: searching` ⏳ Looking for networks...
- `operator name:` Shows which carrier

### Check Roaming Status
```bash
cat /data/params/d/GsmRoaming
# Output: 1 = enabled, missing = disabled

nmcli -f gsm.home-only connection show lte
# Output: no/false = roaming enabled
```

### Check APN Configuration
```bash
cat /data/params/d/GsmApn
# Should be empty/not exist for auto-config

nmcli -f gsm connection show lte | grep -E "(apn|auto-config)"
# apn should be empty, auto-config should be yes
```

### Check Active Connections
```bash
nmcli connection show --active
```

---

## 🎯 Common Scenarios

### Scenario 1: Device won't connect at home
**Problem**: No cellular connection on home network
**Solution**: Run APN fix script
```bash
sudo python3 fix_apn_python.py
```
**Why**: Manual APN or old config is blocking auto-config

---

### Scenario 2: Device won't roam in Canada
**Problem**: Can't connect to Canadian networks
**Solution**: Enable roaming
```bash
sudo python3 enable_roaming.py
```
**Why**: Roaming is disabled by default

---

### Scenario 3: Was working, stopped working
**Problem**: Worked before but not now
**Solution**: Reset everything
```bash
# 1. Fix APN config
sudo python3 fix_apn_python.py

# 2. Enable roaming (if in Canada)
sudo python3 enable_roaming.py

# 3. Check status
mmcli -m any
```
**Why**: Settings may have been reset or changed

---

### Scenario 4: Roaming enabled but still on US network
**Problem**: Roaming enabled but not using Canadian networks
**Solution**: Force network selection
```bash
# List available networks (takes 60 seconds)
mmcli -m any --3gpp-scan

# Connect to Rogers (example)
mmcli -m any --3gpp-register-in-operator=302720

# Or let it auto-select
mmcli -m any --3gpp-register-in-operator=""
```
**Why**: Auto-selection might be stuck on US tower

---

## ⚙️ Technical Details

### Configuration Summary

**For normal operation (home network):**
```
GsmApn: not set (empty)
GsmRoaming: not set or 0 (false)
gsm.apn: "" (empty)
gsm.auto-config: true
gsm.home-only: true
```

**For roaming in Canada:**
```
GsmApn: not set (empty)
GsmRoaming: 1 (true)
gsm.apn: "" (empty)
gsm.auto-config: true
gsm.home-only: false
```

### Key Files in Codebase

- **`system/hardware/tici/hardware.py`** - Modem configuration (line 438+)
- **`system/hardware/tici/esim.nmconnection`** - NetworkManager GSM config
- **`selfdrive/ui/qt/network/networking.cc`** - UI settings (line 152+)
- **`selfdrive/ui/qt/network/wifi_manager.cc`** - GSM settings management (line 414+)

### Device Information

- **Device**: comma 3X
- **Hardware**: tici or tizi platform
- **Modem**: Qualcomm via ModemManager
- **Network**: NetworkManager with GSM/3GPP support

---

## 🆘 Still Not Working?

### Check Prerequisites
- ✅ SIM card inserted properly
- ✅ SIM card activated with carrier
- ✅ Active data plan
- ✅ In area with cellular coverage
- ✅ For roaming: Carrier allows Canadian roaming

### Try Manual Steps
1. Remove and reinsert SIM card
2. Reboot device
3. Check for hardware damage
4. Test with different SIM (if available)

### Get More Info
```bash
# Detailed modem logs
journalctl -u ModemManager -n 100

# NetworkManager logs
journalctl -u NetworkManager -n 100

# AT commands for debugging
mmcli -m any --command="AT+COPS?"
mmcli -m any --command="AT+CGDCONT?"
```

### Get Help
- comma.ai Discord: https://discord.comma.ai
- comma.ai support: contact through connect.comma.ai
- GitHub issues: commaai/openpilot

---

## 📊 Quick Reference Tables

### Roaming Settings
| Setting | Home Only | Roaming Enabled |
|---------|-----------|-----------------|
| GsmRoaming | 0 or not set | 1 |
| gsm.home-only | true | false |
| Behavior | Home network only | Any network |

### APN Settings
| Setting | Manual APN | Auto-Config |
|---------|------------|-------------|
| GsmApn | has value | not set |
| gsm.apn | has value | empty ("") |
| gsm.auto-config | false | true |
| Behavior | Uses specified APN | Auto-detects APN |

### Network States
| State | Meaning | Action |
|-------|---------|--------|
| disabled | Modem off | Enable modem |
| searching | Looking for networks | Wait 30-60s |
| registered | Found network | Wait for connection |
| connected | Data active | Good! ✅ |
| failed | Error occurred | Check logs, restart |

### Canadian Carriers
| Carrier | Code | APN (if needed) |
|---------|------|-----------------|
| Rogers | 302720 | internet.com |
| Telus | 302220 | isp.telus.com |
| Bell | 302610 | inet.bell.ca |
| Freedom | 302490 | internet.freedommobile.ca |

---

## 🚀 Getting Started

**New to this? Start here:**

1. **Read**: `QUICK_FIX_SUMMARY.md`
2. **Run**: `sudo python3 fix_apn_python.py`
3. **If in Canada**: `sudo python3 enable_roaming.py`
4. **Check**: `mmcli -m any`
5. **Need more help**: `cat ROAMING_IN_CANADA.md`

---

## 📝 Summary

- **APN should be empty** for auto-configuration
- **Roaming must be enabled** for Canadian networks
- **Scripts automate the fix** - just run them
- **Wait 1-2 minutes** after applying changes
- **Check status** with `mmcli -m any`

Good luck! 🚀

---

*Last updated: 2025-10-04*
*Based on: commaai/openpilot codebase analysis*
