# Northeast Traffic Messages — Home Assistant

Home Assistant custom integration for UTMC Variable Message Signs (VMS) in the North East of England.

Repository: [github.com/06benste/northeasttrafficmessages](https://github.com/06benste/northeasttrafficmessages/)

Data is sourced from [netraveldata.co.uk](https://www.netraveldata.co.uk/?page_id=230) (free account required).

## Requirements

- Home Assistant **2024.1** or newer
- A free **netraveldata.co.uk** account (not needed for the `Demo` sign)
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

1. Enter your UTMC username and password (or choose **Try demo sign** to skip this).
2. Enter the **sign code** from the [supported signs](#supported-signs) table below, for example `VMS_NC_A1058_WB_B1307` or `HE_A1_9570B`.

Lookup is case-insensitive (`vms_nc_a1058_wb_b1307` works the same as `VMS_NC_A1058_WB_B1307`).

## Supported signs

During setup, enter the **Sign code** exactly as shown below. Codes are not case-sensitive. Use `Demo` to preview the integration without a real sign.

<!-- SIGN_TABLE_START -->
| Sign code | Location |
| --- | --- |
| `Demo` | Sample sign with flashing lanterns (no UTMC connection) |
| `VMS_ST_A1018_SB_A1300` | A1018 (SB) / A1300 John Reid Rd |
| `VMS_SL_A1018_SB_B1291` | A1018 (SB) / B1291 Charlton Rd |
| `VMS_NT_A1056_WB_B1318` | A1056 (WB) / B1318 Grt North Rd |
| `VMS_NT_A1056_WB_B1505` | A1056 (WB) / B1505 Station Rd |
| `VMS_NT_A1058_WB_A1108` | A1058 (WB) / A1018 Billy Mill Av |
| `VMS_NC_A1058_WB_B1307` | A1058 (WB) / B1307 Sandyford Rd |
| `VMS_NT_A1058_WB_NHR` | A1058 (WB) / Norham Rd |
| `VMS_SL_A1231_EB_A182` | A1231 (EB) / A182 Washington Hwy |
| `VMS_SL_A1231_EB_A19` | A1231 (EB) / A19 |
| `VMS_SL_A1231_EB_FBL` | A1231 (EB) / Ferryboat Ln |
| `VMS_SL_A1231_EB_PNR` | A1231 (EB)/B1405 Pallion New Rd |
| `VMS_SL_A1231_WB_BCS` | A1231 (WB) / Beach St |
| `VMS_SL_A1231_WB_FBL` | A1231 (WB) / Ferryboat Ln |
| `VMS_GH_A167_NB_A1` | A167 (NB) / A1 J66 |
| `VMS_GH_A167_NB_CBP` | A167 (NB) / Camborne Pl |
| `VMS_NC_A167_SB_A191` | A167 (SB) / A191 Springfield Rd |
| `VMS_GH_A167_SB_EGAT` | A167 (SB) / East Gate |
| `VMS_SL_A183_EB_GWR` | A183 (EB) / Greenwood Rd |
| `VMS_GH_A184_EB_DWR` | A184 (EB) / A1114 Derwentwtr Rd |
| `VMS_GH_A184_EB_A189` | A184 (EB) / A189 Redheugh Brg |
| `VMS_GH_A184_EB_AKR` | A184 (EB) / Askew Rd |
| `VMS_GH_A184_EB_ARW` | A184 (EB) / Askew Rd West |
| `VMS_ST_A184_EB_B1298` | A184 (EB) / B1298 Abingdon Way |
| `VMS_GH_A184_WB_A185` | A184 (WB) / A185 / B1426 Heworth |
| `VMS_GH_A184_WB_ABR` | A184 (WB) / Albany Rd |
| `VMS_GH_A184_WB_OFR` | A184 (WB) / Old Fold Rd |
| `VMS_ST_A184_WB_SNT` | A184 (WB) / St. Nicholas Tce |
| `VMS_ST_A185_EB_B1516` | A185 (EB) / B1516 Park Rd |
| `VMS_GH_A185_WB_PLG` | A185 (WB) / Plantation Gr |
| `VMS_NT_A188_SB_GOA` | A188 (SB) / Goathland Ave |
| `VMS_NC_A189_SB_A167` | A189 (SB) / A167 |
| `VMS_NB_A189_SB_A19` | A189 (SB) / A19 Moor Farm |
| `VMS_NC_A189_SB_CHS` | A189 (SB) / Churchill St |
| `VMS_NC_A189_SB_HOD` | A189 (SB) / Holland Dr |
| `VMS_NC_A189_SB_JDR` | A189 (SB) / Jesmond Dene Rd |
| `VMS_NT_A189_SB_WHF` | A189 (SB) / White House Dr |
| `VMS_NT_A191_WB_B1505` | A191 (WB) / B1505 Grt Lime Rd |
| `VMS_NC_A191_WB_TCL` | A191 (WB) / The Cloisters |
| `VMS_ST_A194_EB_A19` | A194 (EB) / A19 Lindisfarne |
| `VMS_ST_A194_WB_A185` | A194 (WB) / A185 Jarrow Rd |
| `A1M_7338A` | A1M/7338A |
| `A1M_7346A` | A1M/7346A |
| `A1M_7351B` | A1M/7351B |
| `A1M_7361A` | A1M/7361A |
| `A1M_7365B` | A1M/7365B |
| `A1M_7372A` | A1M/7372A |
| `A1M_7377A` | A1M/7377A |
| `A1M_7377B` | A1M/7377B |
| `A1M_7383B` | A1M/7383B |
| `A1M_7388A` | A1M/7388A |
| `VMS_SL_A690_NB_A19` | A690 (NB) / A19 |
| `VMS_SL_A690_NB_BMS` | A690 (NB) / Broadmeadows |
| `VMS_GH_A694_EB_A1114` | A694 (EB) / A1114 Riverside Way |
| `VMS_NC_A695_EB_A189` | A695 (EB) / A189 St. James' Blvd |
| `VMS_GH_A695_EB_B6317` | A695 (EB) / B6317 Bridge St |
| `VMS_NC_A695_SB_SCR` | A695 (SB) / Scotswood Rd |
| `VMS_NC_A695_WB_B1305` | A695 (WB) / B1305 Whitehouse Rd |
| `VMS_GH_ABR_NB_QFR` | Albany Rd (NB) / Quarryfield Rd |
| `VMS_NC_B1318_SB_A189` | B1318 (SB) / A189 Grandstand Rd |
| `VMS_GH_B1426_EB_A184` | B1426 (EB) / A184 |
| `VMS_GH_B1426_WB_FXS` | B1426 (WB) / Fox St |
| `VMS_NC_B1600_WB_A695` | B1600 (WB) / A695 Railway St |
| `VMS_GH_CHS_EB_CNS` | Church St (EB) / Cannon St |
| `VMS1` | Durham - A167 - Northbound - Burn Hall |
| `VMS4` | Durham - A167 - Southbound - Framwellgate Moor |
| `VMS10` | Durham - A167 Plawsworth |
| `VMS9` | Durham - A177 - Northbound - Bell Avenue |
| `VMS8` | Durham - A181 - Westbound - Byers Garth |
| `VMS7` | Durham - A181 - Westbound - Dragon Lane |
| `WIND VMS 4` | Durham - A689 Addison Rd |
| `VMS5` | Durham - A690 - Southbound - Belmont Industrial Estate |
| `VMS6` | Durham - A690 - Southbound - Moor House |
| `CPGS VMS2` | Durham - A690 Castle Chare |
| `CPGS VMS4` | Durham - A690 Leazes Road |
| `VMS14` | Durham - A690 Meadowfield |
| `VMS2` | Durham - A690 Neville's Cross Bank - Northbound - Lowe's Barn Bank |
| `VMS3` | Durham - A691 - Eastbound - Trouts Lane |
| `CPGS VMS1` | Durham - A691 Framwellgate Peth |
| `VMS13` | Durham - B6532 New College |
| `WIND VMS 1` | Durham - Bob Hardisty Drive |
| `VMS11` | Durham - C12 Finchale Road |
| `CPGS VMS3` | Durham - C98 New Elvet |
| `WIND VMS 3` | Durham - Etherley Lane |
| `WIND VMS 2` | Durham - High Bondgate |
| `VMS12` | Durham - Unc Sunderland Road |
| `VMS_GH_GQUAYS_X_QYD` | GH Quays MSCP (Exit) / Quays Bvd |
| `HE_A1_9570B` | Highways England - A1/9570B |
| `HE_A1_9632A` | Highways England - A1/9632A |
| `HE_A19_1450A` | Highways England - A19/1450A |
| `HE_A19_1458A` | Highways England - A19/1458A |
| `HE_A19_1498B` | Highways England - A19/1498B |
| `HE_A194M_9562A` | Highways England - A194M/9562A |
| `HE_A1M_9072A` | Highways England - A1M/9072A |
| `HE_A1M_9072B` | Highways England - A1M/9072B |
| `HE_A1M_9105A` | Highways England - A1M/9105A |
| `HE_A1M_9105B` | Highways England - A1M/9105B |
| `HE_A1M_9125A` | Highways England - A1M/9125A |
| `HE_A1M_9125B` | Highways England - A1M/9125B |
| `HE_A1M_9142A` | Highways England - A1M/9142A |
| `HE_A1M_9142B` | Highways England - A1M/9142B |
| `HE_A1M_9219A` | Highways England - A1M/9219A |
| `HE_A1M_9228B` | Highways England - A1M/9228B |
| `HE_A1M_9394B` | Highways England - A1M/9394B |
| `HE_A1M_9414A` | Highways England - A1M/9414A |
| `HE_A1M_9414B` | Highways England - A1M/9414B |
| `HE_A1M_9461A` | Highways England - A1M/9461A |
| `HE_A1M_9528A3` | Highways England - A1M/9528A3 |
| `HE_A1M_9537A1` | Highways England - A1M/9537A1 |
| `HE_A1M_9537A2` | Highways England - A1M/9537A2 |
| `HE_A1M_9542B` | Highways England - A1M/9542B |
| `HE_A66_0001B` | Highways England - A66/0001B |
| `HE_A66_0003B` | Highways England - A66/0003B |
| `HE_A67_0002B` | Highways England - A67/0002B |
| `VMS_MC_SMW_EB_RED2` | Metrocentre / Red CP Entry |

115 signs are supported (including Demo).
<!-- SIGN_TABLE_END -->
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

## Maintaining the sign list

When UTMC adds or renames signs, regenerate `supported_signs.json` from the development tooling, then run:

```powershell
python build_sign_table.py
```

That refreshes the table in this README. Bump `version` in `manifest.json` and publish a GitHub release for HACS updates.
