# W-MIDI Web Flasher

Diese kleine Website ist der Browser-Installer fuer die W-MIDI ESP32-S3 Custom-WLED-Firmware. Sie nutzt ESP Web Tools, also denselben Grundmechanismus wie `install.wled.me`: Web Serial, ein Manifest und eine vorbereitete Firmware-Datei.

## Firmware vorbereiten

Baue zuerst die W-MIDI WLED-Firmware und erzeuge daraus eine einzelne gemergte `.bin` Datei. Lege sie danach mit dem Vorbereitungstool in den Web-Flasher:

```powershell
py -3 -m tools.firmware.build_wled_web_flasher
```

Falls du die gemergte `.bin` schon manuell gebaut hast, kannst du sie auch direkt in den Web-Flasher kopieren lassen:

```powershell
py -3 -m tools.firmware.prepare_web_flasher --source "C:\path\to\w-midi-usb-esp32s3-merged.bin"
```

Danach liegt die Datei hier:

```text
web-flasher/firmware/w-midi-usb-esp32s3-merged.bin
```

## Lokal testen

Chrome und Edge erlauben Web Serial auf `localhost`, deshalb reicht lokal:

```powershell
py -3 -m http.server 8008 -d web-flasher
```

Dann `http://localhost:8008` in Chrome oder Edge oeffnen, ESP32-S3 per USB verbinden und installieren.

## Online hosten

Wenn die Seite nicht lokal laeuft, muss sie ueber HTTPS ausgeliefert werden. Manifest und Firmware-Datei muessen vom Browser erreichbar sein.
