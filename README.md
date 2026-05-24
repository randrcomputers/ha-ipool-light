# iPool Light (BLE) (poolexa)— Home Assistant (HACS)

Unofficial integration for **RGB pool lights** that speak the **LedBle** protocol (Android package **`com.ledble`**, app names such as **iPool Light**). The same hardware is often sold under **Poolexa** and **other generic / white-label brands**; if your lamp uses that app stack and the usual LedBle GATT services, this integration may work—**verify your MAC and behavior**; i do not claim compatibility with every clone firmware.

Packet layout and GATT UUIDs are taken from **iPool Light 1.0.3** (`Ipoolight_1.0.3_APKPure.apk`, `NetConnectBle` in `classes.dex`). **Not affiliated with any vendor or store brand.** Use at your own risk.

## Share / install via HACS

**Custom repository URL:** [https://github.com/randrcomputers/ha-ipool-light](https://github.com/randrcomputers/ha-ipool-light)

HACS → **Integrations** → **⋮** → **Custom repositories** → category **Integration** → paste the URL → **Add** → install **iPool Light (BLE)** → restart Home Assistant.

## Requirements

- Home Assistant **2024.1+**
- **Bluetooth** integration (adapter or **Bluetooth proxy** near the pool)
- Light **MAC address** (from HA’s Bluetooth device list or nRF Connect)

## Features (v0.1.x)

- **Light** entity: on / off, **RGB** color, **brightness** (mapped to the app’s `setBrightness` 0–100% frame).
- **Assumed state** — this version does not decode BLE notifies; HA reflects the last command you sent.
- Writes try the same **three GATT targets** as the Android app (`ffe9` / `ffe1` / `fff3` under services `ffe5` / `ffe0` / `fff0`).

## Not in v0.1.0

- **Dynamic / music / DIY / SPI** modes from the app (`setDynamicModel`, `setMusic`, …) — can be added later as `select` or `button` entities once mapped.
- **State read-back** from the lamp (if the firmware exposes it).

## Development

**v0.2.0 experiment** (RGB / warm-cool / dim preset `select` entities from APK tables) is preserved on branch [`save/v0.2-effect-selects`](https://github.com/randrcomputers/ha-ipool-light/tree/save/v0.2-effect-selects). **Stable HACS default is `main` (v0.1.x)** — v0.2.0 was rolled back after reports that it broke setups.

## Legal

*iPool Light*, *Poolexa*, *LedBle*, and similar names are trademarks or trade names of their respective owners; this project is independent community software and is not endorsed by them.
