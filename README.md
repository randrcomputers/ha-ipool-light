# iPool Light (BLE) (poolexa)— Home Assistant (HACS)

Unofficial integration for **RGB pool lights** that speak the **LedBle** protocol (Android package **`com.ledble`**, app names such as **iPool Light**). The same hardware is often sold under **Poolexa** and **other generic / white-label brands**; if your lamp uses that app stack and the usual LedBle GATT services, this integration may work—**verify your MAC and behavior**; we do not claim compatibility with every clone firmware.

Packet layout and GATT UUIDs are taken from **iPool Light 1.0.3** (`Ipoolight_1.0.3_APKPure.apk`, `NetConnectBle` in `classes.dex`). **Not affiliated with any vendor or store brand.** Use at your own risk.

## Share / install via HACS

**Custom repository URL:** [https://github.com/randrcomputers/ha-ipool-light](https://github.com/randrcomputers/ha-ipool-light)

HACS → **Integrations** → **⋮** → **Custom repositories** → category **Integration** → paste the URL → **Add** → install **iPool Light (BLE)** → restart Home Assistant.

## Requirements

- Home Assistant **2024.1+**
- **Bluetooth** integration (adapter or **Bluetooth proxy** near the pool)
- Light **MAC address** (confirm in **Settings → Bluetooth**, e.g. `78:9C:E7:08:4C:C2`)

## Features (v0.1.3)

- **Light** entity only: on / off, **RGB** color, **brightness** (stable — no extra `select` entities).
- **Service `ipool_light.set_rgb_effect`** — APK jump / gradient / flash presets (for the **pool light card** or automations).
- **Assumed state** — no BLE notify decode; HA reflects the last command you sent.
- Short BLE sessions: connect, send frame, disconnect.

### Effects (card or Developer tools)

```yaml
action: ipool_light.set_rgb_effect
data:
  entity_id: light.your_ipool_light
  effect: "Tricolor jump"
```

Use the **[pool light card](https://github.com/randrcomputers/ha-pool-light-card)** for a dropdown next to the color swatches. The built-in HA light more-info dialog does not include effects (colors only).

## Legal

*iPool Light*, *Poolexa*, *LedBle*, and similar names are trademarks or trade names of their respective owners; this project is independent community software and is not endorsed by them.
