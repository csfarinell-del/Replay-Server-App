# Configuration Keys Reference

This document explains all configuration keys used in the Assetto Corsa Server Configuration Manager. Configuration files are located in `server_root/cfg/`.

---

## server_cfg.ini

Core server configuration file (standard Assetto Corsa format).

### [SERVER] Section

| Key | Type | Range | Notes |
|-----|------|-------|-------|
| **NAME** | String | - | Server display name (required) |
| **TRACK** | String | - | Track identifier (lowercase with underscores, e.g., 'monza', 'silverstone') |
| **UDP_PORT** | Integer | 1024-65535 | Network port for game clients |
| **TCP_PORT** | Integer | 1024-65535 | TCP port (typically UDP_PORT + 1) |
| **HTTP_PORT** | Integer | 1024-65535 | HTTP port for web interface |
| **TIME_OF_DAY_MULT** | Integer | 0/1 | Multiplier for time progression (0=fixed, 1=multiplied) |
| **SUN_ANGLE** | Float | -180 to 180 | Sun angle in degrees (derived from TIME_OF_DAY) |
| **MAX_CLIENTS** | Integer | 1+ | Maximum players (should match entry_list.ini car count) |
| **ALLOWED_TYRES_OUT** | String | - | Allowed tire compound names (space-separated) |
| **CLIENT_SEND_INTERVAL_HZ** | Integer | 10-120 | Network update frequency in Hz (default: 33) |

### [WEATHER_0] Section

| Key | Type | Notes |
|-----|------|-------|
| **GRAPHICS** | String | Weather preset name (e.g., 'clear', 'rain', 'storm') |

---

## entry_list.ini

Player and bot car list (standard Assetto Corsa format).

### [CARS] Section

Each entry follows the pattern `[CAR_0]`, `[CAR_1]`, etc.

| Key | Type | Notes |
|-----|------|-------|
| **MODEL** | String | Car model name (must exist in AC content/cars/) |
| **SKIN** | String | Car livery/skin name; for bots, must end with `/VS` |
| **DRIVERNAME** | String | Driver name for this entry |
| **TEAM** | String | Team name (optional) |
| **SPECTATOR_MODE** | 0/1 | 1 = spectator, 0 = normal player |
| **GUID** | String | Unique identifier; **bots use 8888880 + index** (e.g., 8888880, 8888881, ...) |
| **BALLAST** | Integer | Weight penalty in kg (for balance) |
| **RESTRICTOR** | Integer | Power restriction percentage (0-100) |

### Virtual Steward Specific

- **First N entries** (where N = num_bots) are treated as bots
- **Bot entries require:**
  - GUID = `"8888880 + index"` (8888880 for first bot, 8888881 for second, etc.)
  - Skin suffix `/VS` (e.g., `porsche_2k19_rsr/VS`)
- **Player entries must have:**
  - GUID = `""` (empty string)
  - Skin WITHOUT `/VS` suffix

---

## extra_cfg.yml

Extended server configuration (YAML format).

| Key | Type | Notes |
|-----|------|-------|
| **ServerDescription** | String | Long-form server description/motd |
| **ForceLights** | Boolean | Force headlights on (true/false) |
| **EnablePlugins** | List | List of plugin names to enable (e.g., `['VSReplayPlugin']`) |

---

## plugin_vs_replay_cfg.yml

Virtual Steward replay plugin configuration (YAML format).

| Key | Type | Range | Notes |
|-----|------|-------|-------|
| **AutoStart** | Integer | 0+ | Number of bots to automatically start (auto-spawned) |
| **AutoStartOffset** | Integer | 0-100 or 0 | **Critical Key:** Controls bot train feature<br>0 = bot trains disabled<br>1-100 = bot trains enabled, value is gap between bots in grid |
| **AutoStartStagger** | Float | - | Stagger between bot formations |
| **LoopLap** | Integer | 1+ | Number of laps to repeat for replay/practice |
| **StartingMeters** | Integer | - | Starting position offset in meters |

### AutoStartOffset Explanation

The `AutoStartOffset` key has a special dual purpose:

1. **Disabled State (value = 0)**
   - Bot trains are disabled
   - Each bot is independent

2. **Enabled State (value != 0)**
   - Bot trains are enabled
   - The numeric value becomes the gap between bots (in grid positions)
   - Valid range: typically 5-100 (UI clamps to this range)
   - Example: AutoStartOffset=15 means 15-position gap between bots in the train

### Why This Design?

Using a single key for both the enabled state and the value reduces configuration complexity. The checkbox UI reads this key and derives:
- Is checked if value != 0
- Slider value = the numeric value itself

---

## plugin_virtual_steward_cfg.yml

Virtual Steward plugin general configuration (YAML format).

| Key | Type | Notes |
|-----|------|-------|
| **EnableVirtualSteward** | Boolean | Whether to run Virtual Steward integration |
| **ReplayFolder** | String | Path to replay storage (relative to server root) |
| **BotBrainType** | String | AI difficulty/behavior type (e.g., 'aggressive', 'defensive') |

---

## Key Mapping Examples

### Example 1: 3 Bot Server with Bot Trains

```ini
[entry_list.ini - [CAR_0], [CAR_1], [CAR_2] are bots]
MODEL=porsche_911_2k16
SKIN=porsche_2k16_rsr/VS
GUID=8888880

MODEL=porsche_911_2k16
SKIN=porsche_2k16_rsr/VS
GUID=8888881

MODEL=porsche_911_2k16
SKIN=porsche_2k16_rsr/VS
GUID=8888882

[entry_list.ini - [CAR_3]+ are regular players]
MODEL=ferrari_488
SKIN=ferrari_488_red
GUID=
```

```yaml
# plugin_vs_replay_cfg.yml
AutoStart: 3
AutoStartOffset: 20  # Bot trains enabled with 20-position gap
LoopLap: 10
```

### Example 2: Server Without Bot Trains

```yaml
# plugin_vs_replay_cfg.yml
AutoStart: 2
AutoStartOffset: 0  # Bot trains disabled
LoopLap: 0
```

---

## Configuration State Flow

### Loading (disk → memory)
1. `config_manager.load_configs()` reads INI/YAML files
2. Parsers store raw data in `self.configs` dict
3. UI population methods read from this dict

### Editing (memory)
- User modifies UI fields
- `mark_as_modified()` sets `has_unsaved_changes = True`
- Changes remain only in memory until saved

### Saving (memory → disk)
1. `save_config()` validates all user inputs
2. Updates `self.configs` in-memory structures
3. Calls `config_manager.save_ini_targeted()` or `write_entry_list_ini()` for each file
4. Immediately reloads configs to sync UI with disk state

### Virtual Steward Specific
- When VS is enabled: `_apply_vs_skins_to_entry_list()` modifies entry skins and GUIDs
- When VS is disabled: Removes `/VS` suffixes and clears bot GUIDs
- Changes apply immediately to entry_list_table display
- Persisted to disk on save

---

## Data Type Notes

- **Integer**: Whole numbers (no decimals)
- **Float**: Decimal numbers allowed
- **Boolean**: YAML uses `true`/`false` (not Python's `True`/`False`)
- **String**: Text values; no quotes needed in INI, but may be needed in YAML
- **List**: YAML format only, uses dash notation (e.g., `['VSReplayPlugin']`)

---

## Common Configuration Mistakes

1. **BOT GUID Mismatch**: Using non-bot GUIDs for bots (must be 8888880+index)
2. **Missing /VS Suffix**: Bot skins must end with `/VS` when VS is enabled
3. **PORT CONFLICTS**: Multiple servers on same machine need different ports
4. **TRACK NAME**: Must use correct internal name, not display name
5. **MaxClients Mismatch**: MAX_CLIENTS in server_cfg.ini should match car count in entry_list.ini

---

## Performance Considerations

- **Large Player Lists**: >60 cars can cause performance issues; recommend max 40-50
- **Bot Count**: More bots = more network traffic; recommend <8 bots
- **Network Updates**: CLIENT_SEND_INTERVAL_HZ=33 is safe default; lower values = higher bandwidth
- **Plugin Load**: VSReplayPlugin adds minimal overhead; safe to enable always

---

## References

- AC Server Documentation: `server/docs/` (if available)
- Assetto Corsa Competizione: Uses extended YAML configs vs original AC
- Virtual Steward Repo: GitHub repository for latest plugin schema
