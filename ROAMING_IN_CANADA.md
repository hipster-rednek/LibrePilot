# Enable Roaming in Canada - comma 3X

## 🇨🇦 Quick Answer

To roam in Canada with your US SIM card, you need to:

1. **Enable roaming** (`GsmRoaming` = true)
2. **Keep APN empty** (auto-config)
3. **Ensure carrier allows Canadian roaming**

## 🚀 Quick Fix - Run This:

```bash
cd /workspace
sudo python3 enable_roaming.py
```

This will:
- ✅ Enable the GsmRoaming parameter
- ✅ Set NetworkManager's `home-only` to false (allows roaming)
- ✅ Keep APN empty for auto-config
- ✅ Restart the cellular connection
- ✅ Check connection status

## How Roaming Works

### The Settings

There are two related settings (they're inverses):

1. **GsmRoaming** (openpilot parameter)
   - `true` = roaming ENABLED
   - `false` or not set = roaming DISABLED

2. **home-only** (NetworkManager GSM setting)
   - `false` = roaming ENABLED (can use non-home networks)
   - `true` = roaming DISABLED (home network only)

The relationship: `home-only = !GsmRoaming`

### Configuration Files

**Default** (`/system/hardware/tici/esim.nmconnection`):
```ini
[gsm]
apn=
home-only=false    # allows roaming
auto-config=true
```

When you enable roaming:
```
GsmRoaming parameter: 1 (true)
gsm.home-only: false
APN: empty (auto-config)
```

## Manual Method

If you prefer to do it manually:

### Method 1: Via UI (Easiest)
1. Go to **Settings** → **Network** → **Advanced**
2. Toggle **"Enable Roaming"** to ON
3. Ensure **"APN Setting"** is blank/empty
4. Wait 1-2 minutes for connection

### Method 2: Via Command Line

```bash
# 1. Enable roaming parameter
echo "1" > /data/params/d/GsmRoaming

# 2. Update NetworkManager connection
nmcli connection modify lte gsm.home-only false

# 3. Keep APN empty (auto-config)
nmcli connection modify lte gsm.apn ""
nmcli connection modify lte gsm.auto-config true

# 4. Restart connection
nmcli connection down lte
nmcli connection up lte

# 5. Check status (wait 30-60 seconds)
mmcli -m any
```

### Method 3: Via Parameters API

```python
from openpilot.common.params import Params

params = Params()
params.put_bool("GsmRoaming", True)  # Enable roaming
params.remove("GsmApn")  # Keep APN empty

# Then restart the connection via nmcli or UI
```

## What Happens When Roaming

1. **Modem scans** for available networks
2. **Registers** on strongest Canadian network (Rogers, Telus, Bell, etc.)
3. **Negotiates** roaming agreement with your US carrier
4. **Connects** using auto-configured APN
5. **Data flows** through Canadian network → your US carrier

## Checking Status

### Check if roaming is enabled:
```bash
# Check parameter
cat /data/params/d/GsmRoaming
# Output: 1 = enabled, 0 or missing = disabled

# Check NetworkManager
nmcli -f gsm.home-only connection show lte
# Output: false = roaming enabled, true = roaming disabled
```

### Check what network you're on:
```bash
# Detailed modem info
mmcli -m any

# Look for these lines:
#   operator name: 'Rogers' or 'TELUS' or 'Bell' etc.
#   state: 'registered' or 'connected'
#   access tech: 'lte' or 'umts'
```

### Check if roaming is active:
```bash
# AT command to check operator
mmcli -m any --command="AT+COPS?"

# Should show Canadian carrier code
# Rogers: 302720
# Telus: 302220
# Bell: 302610
```

## Troubleshooting

### Not Connecting in Canada?

**1. Check Roaming Status**
```bash
python3 enable_roaming.py
```

**2. Verify Carrier Allows Roaming**
- Contact your US carrier
- Confirm Canadian roaming is included in your plan
- Some carriers require roaming activation

**3. Check Signal Strength**
```bash
mmcli -m any | grep signal
```
- Need at least 25% signal
- Try moving to different location
- Canadian networks may have different coverage

**4. Manual Network Selection**
Sometimes auto-selection doesn't work. Force a network:

```bash
# List available networks (takes 30-60 seconds)
mmcli -m any --3gpp-scan

# Connect to specific network (example: Rogers)
mmcli -m any --3gpp-register-in-operator=302720

# Or let it auto-select
mmcli -m any --3gpp-register-in-operator=""
```

**5. Check Modem State**
```bash
mmcli -m any | grep state
```

Possible states:
- `searching` - Looking for networks (normal, wait)
- `registered` - Found network, not connected yet (wait)
- `connected` - Data connection active (good!)
- `disabled` - Modem off (check if SIM is inserted)

**6. Restart Modem**
```bash
# Disable modem
mmcli -m any --disable
sleep 3

# Enable modem
mmcli -m any --enable
sleep 10

# Check status
mmcli -m any
```

### Common Issues

**Issue: "Roaming enabled but still on US network"**
- You may not be in Canada yet, or
- You're near border with US signal stronger, or
- Manual network selection needed (see above)

**Issue: "Registered but not connected"**
```bash
# Restart the data connection
nmcli connection down lte && nmcli connection up lte
```

**Issue: "No signal"**
- Check antenna connections
- Verify SIM card is properly inserted
- Try different location (buildings block signal)

**Issue: "Carrier doesn't allow roaming"**
- Some prepaid plans don't include roaming
- Contact carrier to enable international/Canadian roaming
- May need to add roaming package

**Issue: "APN error even with empty APN"**
Some Canadian networks need specific APN:
```bash
# Try Rogers APN
nmcli connection modify lte gsm.apn "internet.com"

# Or try Telus
nmcli connection modify lte gsm.apn "isp.telus.com"

# Or try Bell
nmcli connection modify lte gsm.apn "inet.bell.ca"

# Then restart
nmcli connection down lte && nmcli connection up lte
```

But **try auto-config first** (empty APN)!

## Canadian Carriers

Major networks your device might connect to:

| Carrier | Network Code | Technology | Coverage |
|---------|--------------|------------|----------|
| Rogers | 302720 | LTE/5G | Nationwide |
| Telus | 302220 | LTE/5G | Nationwide |
| Bell | 302610 | LTE/5G | Nationwide |
| Freedom Mobile | 302490 | LTE | Urban areas |

Your US carrier likely has agreements with Rogers, Telus, and Bell.

## Cost Considerations

⚠️ **Important**: Roaming can be expensive!

- Check your US carrier's roaming rates
- Many carriers offer Canadian roaming plans
- Some unlimited plans include Canada
- Monitor data usage to avoid surprise bills

Popular carriers with Canadian roaming:
- **T-Mobile**: Often includes Canada in plans
- **AT&T**: Offers North America plans
- **Verizon**: TravelPass or North America plan
- **Google Fi**: Included in standard plan

## Disable Roaming (Return Home)

When you're back in the US or want to disable roaming:

```bash
sudo python3 disable_roaming.py
```

Or manually:
```bash
rm -f /data/params/d/GsmRoaming
nmcli connection modify lte gsm.home-only true
nmcli connection down lte && nmcli connection up lte
```

Or via UI:
Settings → Network → Advanced → "Enable Roaming" toggle OFF

## Complete Configuration

For roaming in Canada with auto-config:

```bash
# Enable roaming
echo "1" > /data/params/d/GsmRoaming

# Set NetworkManager (home-only = false allows roaming)
nmcli connection modify lte gsm.home-only false
nmcli connection modify lte gsm.apn ""
nmcli connection modify lte gsm.auto-config true

# Restart
nmcli connection down lte
sleep 2
nmcli connection up lte

# Wait and check (30-60 seconds)
sleep 30
mmcli -m any
```

## Testing After Configuration

```bash
# 1. Check roaming is enabled
cat /data/params/d/GsmRoaming  # Should output: 1

# 2. Check NetworkManager config
nmcli -f gsm connection show lte | grep -E "(home-only|apn|auto-config)"

# Expected output:
#   gsm.auto-config: yes
#   gsm.home-only: no
#   gsm.apn: --

# 3. Check modem status
mmcli -m any | grep -E "(state|operator|signal)"

# Expected when connected:
#   state: connected
#   operator name: Rogers (or Telus, Bell, etc.)
#   signal quality: XX%

# 4. Test data connection
ping -c 3 8.8.8.8
```

## Summary

✅ **To roam in Canada:**
1. Enable roaming: `sudo python3 enable_roaming.py`
2. Keep APN empty (auto-config)
3. Wait 30-60 seconds for registration
4. Verify with `mmcli -m any`

✅ **Key settings:**
- `GsmRoaming` = `1` (true)
- `gsm.home-only` = `false`
- `gsm.apn` = empty
- `gsm.auto-config` = `true`

✅ **Works with US carriers that support Canadian roaming:**
- T-Mobile ✓
- AT&T ✓
- Verizon ✓
- Google Fi ✓
- Others (check with carrier)

🇨🇦 **Canadian networks:**
- Rogers (most common)
- Telus
- Bell
- Freedom Mobile (urban areas)

---

**Note**: You mentioned it worked before - if it stopped working, the roaming parameter may have been reset or the connection config changed. Running the enable script should restore it.
