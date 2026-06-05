# Northeast Traffic Messages — Home Assistant

Home Assistant custom integration for UTMC Variable Message Signs (VMS) in the North East of England.

Repository: [github.com/06benste/northeasttrafficmessages](https://github.com/06benste/northeasttrafficmessages)

Data is sourced from [netraveldata.co.uk](https://www.netraveldata.co.uk/?page_id=230) (free account required).

## Installation

1. Copy `custom_components/northeast_traffic_messages` into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Add the integration via **Settings → Devices & services → Add integration** and search for **Northeast Traffic Messages**.

## Setup

1. Enter your UTMC username and password.
2. Enter the **sign code** for the VMS you want to monitor, for example `VMS_NC_A1058_WB_B1307` or `HE_A1_9570B`.

The integration maps sign codes to UTMC `systemCodeNumber` values internally — you never need to type the long hex IDs used by some Highways England signs.

See the full [sign list](https://github.com/06benste/northeasttrafficmessages/blob/main/Homeassistant/supported_signs.json) on GitHub. Each entry has:

| Field | Purpose |
|-------|---------|
| `friendly_id` | Sign code entered during setup |
| `utmc_id` | Actual UTMC API identifier (stored in config) |
| `name` | Human-readable location label |

Lookup is case-insensitive (`vms_nc_a1058_wb_b1307` works the same as `VMS_NC_A1058_WB_B1307`).

## Entities per sign

Each configured sign becomes one device with:

| Entity | Type | Updates |
|--------|------|---------|
| Display | Image (GIF) | Every 5 minutes |
| Message text | Sensor | Every 5 minutes |
| Lanterns flashing | Binary sensor | Every 5 minutes |
| Last updated | Sensor (timestamp) | Every 5 minutes |
| Reason | Sensor (enum) | Every 5 minutes |
| Location | Sensor | Every 24 hours (static feed) |

Device name and map coordinates (when provided by UTMC) are refreshed from the static feed every 24 hours.

## Adding more signs

Run the config flow again for each additional sign. Credentials are shared across all entries.

## Regenerating the sign list

When UTMC adds or renames signs, refresh the catalog from the live API:

```powershell
cd northeasttrafficmessages
python generate_supported_signs.py
```

This updates both `Homeassistant/supported_signs.json` and the copy bundled inside the integration. Commit and release a new integration version.

Sign codes are assigned automatically:

- Signs that already have readable UTMC codes (e.g. `VMS_NC_A1058_WB_B1307`) use that code.
- Opaque hex UTMC IDs get a short code from the sign description (e.g. `HE_A1_9570B`, `A1M_7338A`).
