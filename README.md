# iPool Light (BLE) (poolexa)— Home Assistant (HACS)

Unofficial integration for **RGB pool lights** that speak the **LedBle** protocol (Android package **`com.ledble`**, app names such as **iPool Light**). The same hardware is often sold under **Poolexa** and **other generic / white-label brands**; if your lamp uses that app stack and the usual LedBle GATT services, this integration may work—**verify your MAC and behavior**; we do not claim compatibility with every clone firmware.

Packet layout and GATT UUIDs are taken from **iPool Light 1.0.3** (`Ipoolight_1.0.3_APKPure.apk`, `NetConnectBle` in `classes.dex`). **Not affiliated with any vendor or store brand.** Use at your own risk.

## Share / install via HACS

**Custom repository URL:** [https://github.com/randrcomputers/ha-ipool-light](https://github.com/randrcomputers/ha-ipool-light)

HACS → **Integrations** → **⋮** → **Custom repositories** → category **Integration** → paste the URL → **Add** → install **iPool Light (BLE)** → restart Home Assistant.

## Requirements

- Home Assistant **2024.1+**
- **Bluetooth** integration (adapter or **Bluetooth proxy** near the pool)
- Light **MAC address** (from HA’s Bluetooth device list or nRF Connect)

## Features (v0.2.1)

- **Light** entity: on / off, **RGB** color, **brightness** (mapped to the app’s `setBrightness` 0–100% frame).
- **Select — RGB effect**: **29** presets from the app’s `rgb_mode` array (static colors, tri/seven color jump & gradient, flashes, etc.) — same bytes as `NetConnectBle.setRgbMode`.
- **Select — Warm / cool balance**: **11** presets from `ct_mode` (`setColorWarmModel`).
- **Select — Dimming preset**: **11** levels from `dm_mode` (`setDimModel`).
- **Assumed state** — no BLE notify decode; HA shows the last command you sent.
- Writes try the same **three GATT targets** as the Android app (`ffe9` / `ffe1` / `fff3` under services `ffe5` / `ffe0` / `fff0`).
- One **device** in the registry (light + selects share Bluetooth connection info).

### Scenes and effects

Turn the **light** on, then set an effect on **RGB effect** (firmware runs the animation):

```yaml
# Example scene — seven-color jump
- id: pool_party_jump
  name: Pool party jump
  entities:
    light.ipool_light:
      state: on
      brightness: 255
    select.ipool_light_rgb_effect:
      option: "Seven-color jump"
```

Use **Developer tools → Actions** → `select.select_option` to test (e.g. `Tricolor jump`, `Seven-color gradient`).

## Not in v0.2.1

- **Music / DIY / SPI** and other tabs that use different `NetConnectBle` entry points.
- **State read-back** from the lamp (if the firmware exposes it).

## Troubleshooting

If the light stops responding after an effect, toggle **Power** on the light entity or reload the integration. If problems persist, remove and re-add the device (v0.2.0 previously caused issues on some setups — report your model if effects fail).

## Legal

*iPool Light*, *Poolexa*, *LedBle*, and similar names are trademarks or trade names of their respective owners; this project is independent community software and is not endorsed by them.
