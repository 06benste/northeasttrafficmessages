# Northeast Traffic Messages — Home Assistant

Home Assistant custom integration for UTMC Variable Message Signs (VMS) in the North East of England.

Repository: [github.com/06benste/northeasttrafficmessages](https://github.com/06benste/northeasttrafficmessages/)

Data is sourced from [netraveldata.co.uk](https://www.netraveldata.co.uk/?page_id=230) (free account required).

## Requirements

- Home Assistant **2024.1** or newer
- A free **netraveldata.co.uk** account
- Internet access to `www.netraveldata.co.uk`

## Installation

### Manual install

1. Copy the `custom_components/northeast_traffic_messages` folder into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings → Devices & services → Add integration** and search for **Northeast Traffic Messages**.

### HACS (custom repository)

1. In HACS, open **Integrations → ⋮ → Custom repositories**.
2. Add repository **`https://github.com/06benste/northeasttrafficmessages/`** and category **Integration**.
3. Install **Northeast Traffic Messages** from HACS.
4. Restart Home Assistant and add the integration as above.

## Setup

1. Enter your UTMC username and password.
2. Enter the **sign code** for the VMS you want to monitor, for example `VMS_NC_A1058_WB_B1307` or `HE_A1_9570B`.



See the full [sign list](https://github.com/06benste/northeasttrafficmessages/blob/main/supported_signs.json) on GitHub. 


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

