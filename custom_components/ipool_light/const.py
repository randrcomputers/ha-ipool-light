"""Constants for iPool Light (LedBle / com.ledble) BLE control."""

DOMAIN = "ipool_light"

CONF_ADDRESS = "address"
CONF_NAME = "name"

DEFAULT_NAME = "iPool Light"

# From iPool Light 1.0.3 ``NetConnectBle.sendCharacteristic`` (``classes.dex``).
# The app tries these service/characteristic pairs in order for the same payload.
GATT_WRITE_TARGETS: list[tuple[str, str]] = [
    ("0000ffe5-0000-1000-8000-00805f9b34fb", "0000ffe9-0000-1000-8000-00805f9b34fb"),
    ("0000ffe0-0000-1000-8000-00805f9b34fb", "0000ffe1-0000-1000-8000-00805f9b34fb"),
    ("0000fff0-0000-1000-8000-00805f9b34fb", "0000fff3-0000-1000-8000-00805f9b34fb"),
]

# Prefer matching devices that expose the primary LED service in advertisements.
SERVICE_UUID_FILTER = "0000ffe0-0000-1000-8000-00805f9b34fb"

# After HA restarts or a bad session, the first command may need extra scan time.
BLE_ADVERTISEMENT_WAIT_SECONDS = 60

DATA_CONNECTION = "connection"
DATA_LIGHT_ENTITY = "light_entity"
