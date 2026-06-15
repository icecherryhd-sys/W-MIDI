W-MIDI v1.2.0


Wichtige Felder
---------------
MIDI input:
Das MIDI-Geraet oder der virtuelle Port, auf den W-MIDI hoert.

WLED IP:
Die lokale Netzwerkadresse des WLED-Controllers, zum Beispiel 192.168.1.100.

UDP port:
Der WLED-Echtzeit-Port. Normalerweise bleibt er auf 21324.

Total LED count:
Die Anzahl der LEDs fuer die ausgewaehlte Bridge.

Start note:
Die MIDI-Note, die auf LED 0 gelegt wird.

Listen channel:
"All" reagiert auf alle MIDI-Kanaele. Alternativ kannst du einen Kanal waehlen.

LEDs per channel:
Optionaler Bank-Bereich fuer groessere Setups mit mehreren MIDI-Kanaelen.

Palette file:
Die ausgewaehlte Velocity-Palette. Standard ist palettes/Default.


Fehlersuche
-----------
Wenn keine LEDs reagieren:
- Pruefe die WLED-IP.
- Pruefe, ob PC und WLED im gleichen Netzwerk sind.
- Pruefe MIDI-Eingang und Startnote.
- Stelle sicher, dass WLED UDP-Echtzeitdaten akzeptiert.
- Nutze "Reload Ports", nachdem du ein neues MIDI-Geraet angeschlossen hast.

Das Fragezeichen oben rechts oeffnet standardmaessig die englische
README_EN.txt.
