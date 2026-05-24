# iPool Light (BLE) (poolexa)— Home Assistant (HACS)

Unofficial integration for **RGB pool lights** that speak the **LedBle** protocol (Android package **`com.ledble`**, app names such as **iPool Light**). The same hardware is often sold under **Poolexa** and **other generic / white-label brands**; if your lamp uses that app stack and the usual LedBle GATT services, this integration may work—**verify your MAC and behavior**; we do not claim compatibility with every clone firmware.

Packet layout and GATT UUIDs are taken from **iPool Light 1.0.3** (`Ipoolight_1.0.3_APKPure.apk`, `NetConnectBle` in `classes.dex`). **Not affiliated with any vendor or store brand.** Use at your own risk.

## Share / install via HACS

**Custom repository URL:** [https://github.com/randrcomputers/ha-ipool-light](https://github.com/randrcomputers/ha-ipool-light)

HACS → **Integrations** → **⋮** → **Custom repositories** → category **Integration** → paste the URL → **Add** → install **iPool Light (BLE)** → restart Home Assistant.

## Requirements

- Home Assistant **2024.1+**
- **Bluetooth** integration (adapter or **Bluetooth proxy** near the pool)
- Light **MAC address** (from HA’s Bluetooth device list or nRF Connect — double-check bytes, e.g. `78:9C:E7:08:4C:C2`)

## Features (v0.2.2)

- **Light** entity: on / off, **RGB** color, **brightness** (always enabled).
- **Optional** (Settings → integration → **Configure**): **RGB effect**, **Warm / cool balance**, **Dimming preset** selects — same APK modes as jump / gradient / flash (off by default so the light keeps working like v0.1.x).
- **Assumed state** — no BLE notify decode; HA reflects the last command you sent.
- Short BLE sessions: connect, send 9-byte frame, disconnect (reduces wedged links).

### Enable animations

1. **Settings → Devices & services → iPool Light (BLE) → Configure**
2. Turn on **Enable RGB / warm-cool / dim preset selects**
3. Integration reloads — three **select** entities appear on the device
4. Turn **light** on, then set **RGB effect** (e.g. **Tricolor jump**)

### Scenes

```yaml
entities:
  light.ipool_light:
    state: on
    brightness: 255
  select.ipool_light_rgb_effect:
    option: "Seven-color jump"
```

(Select entities exist only when the option above is enabled.)

## Legal

*iPool Light*, *Poolexa*, *LedBle*, and similar names are trademarks or trade names of their respective owners; this project is independent community software and is not endorsed by them.
