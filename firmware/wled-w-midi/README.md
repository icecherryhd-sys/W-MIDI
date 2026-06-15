# W-MIDI USB WLED Firmware

This folder is an overlay for a custom WLED build on ESP32-S3 with native
USB-MIDI input.

## What It Does

- Keeps normal WLED WiFi, web UI, OTA, effects, and UDP realtime available.
- Adds a `W_MIDI_USB` usermod for the ESP32-S3 native USB/OTG port.
- Receives class-compliant USB-MIDI Note On and Note Off messages.
- Treats Note On with velocity `0` as Note Off.
- Maps MIDI note `36` to LED `0` by default.
- Controls 32 LEDs by default.
- Uses the same W-MIDI `palettes/Default` colors, scaled from Launchpad
  `0..63` RGB to full `0..255` RGB.
- Uses WLED's existing `strip` buffer. It does not create a second FastLED or
  NeoPixel driver.

## Files

```text
firmware/wled-w-midi/
|-- platformio_override.ini
|-- README.md
`-- usermods/
    `-- W_MIDI_USB/
        |-- library.json
        |-- usermod_w_midi_usb.h
        |-- w_midi_usb.cpp
        `-- w_midi_palette.h
```

## Build

1. Download current WLED source `0.16+` or WLED `main`.
2. Copy this folder's `platformio_override.ini` into the WLED root folder.
3. Copy `usermods/W_MIDI_USB` into WLED's `usermods/` folder.
4. Open the WLED root folder in VS Code with PlatformIO.
5. Build environment `w_midi_esp32s3_usb`.

Command-line build from the WLED root:

```powershell
pio run -e w_midi_esp32s3_usb
```

The firmware binary will be under WLED's `.pio/build/w_midi_esp32s3_usb/`
folder.

## Regenerate Palette

Run this from the W-MIDI repository:

```powershell
py -3 -m tools.firmware.generate_wled_palette
```

That regenerates `usermods/W_MIDI_USB/w_midi_palette.h` from
`palettes/Default`.

## Hardware

- Controller: ESP32-S3 with native USB/OTG port.
- LED count: 32 by default.
- LED type: WS2811/WS2812-compatible 5 V addressable pixels.
- Data pin: GPIO 7 by default through `DATA_PINS=7`.
- ESP32 and LEDs need common ground.
- Do not run all 32 LEDs at maximum white from a weak PC USB port.
- The usermod includes a software current limit default of `850 mA`.
- For more LED power, feed 5 V directly from a suitable supply or the protected
  USB 5 V rail, but avoid backfeeding the PC USB port.

## Source Priority

USB-MIDI has visual priority while USB MIDI events are arriving:

1. Every USB-MIDI Note On/Off refreshes the USB activity timeout.
2. Changed pixels are batched and flushed once per WLED loop.
3. After `usbTimeoutMs`, the usermod stops writing pixels.
4. WLED effects and UDP realtime can take over again.

Default timeout is `600 ms`.

## WLED Usermod Settings

Stored under `W_MIDI_USB` in WLED config:

- `enabled`
- `ledCount`
- `firstNote`
- `midiChannel`, where `0` means omni and `1..16` select one channel
- `usbTimeoutMs`
- `currentLimitMa`
- `usbPriority`

## Native USB Port

Use the board connector wired to the ESP32-S3 native USB D+/D- pins. Some dev
boards have a separate USB-UART connector; that connector is only for serial
and flashing and will not expose USB-MIDI.

## Test Plan

1. Flash WLED with the usermod.
2. Connect the native ESP32-S3 USB port to the PC.
3. Confirm a class-compliant MIDI device named `W-MIDI Underlight` appears.
4. Send MIDI note `36` with velocity > `0`; LED `0` should light.
5. Send Note Off for note `36`; LED `0` should turn off.
6. Send Note On velocity `0`; it should behave like Note Off.
7. Send UDP realtime from the desktop W-MIDI app; it should still work when
   USB-MIDI is idle.
8. While repeatedly sending USB-MIDI, confirm USB-MIDI takes visual priority.
9. Stop USB-MIDI and wait longer than `usbTimeoutMs`; WLED effects or UDP
   realtime should be usable again.

## Troubleshooting

- No MIDI device appears: make sure you are using the native USB/OTG port.
- Build cannot find `USBMIDI.h`: use current WLED `0.16+`/`main` with an
  ESP32-S3 Arduino core that includes TinyUSB MIDI.
- LEDs flicker: raise `usbTimeoutMs` slightly or lower MIDI event rate.
- LEDs are too dim: raise `currentLimitMa` only if your power path is safe.
- Wrong LED responds: adjust `firstNote` or `ledCount` in WLED config.
