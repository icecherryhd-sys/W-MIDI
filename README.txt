W-MIDI
======

Kurz gesagt
-----------
W-MIDI verbindet ein MIDI-Eingabegeraet mit einem WLED-Controller.
Eingehende MIDI-Noten und Controller-Nachrichten werden in UDP-Lichtdaten
uebersetzt, damit LEDs in WLED direkt auf dein MIDI-Spiel reagieren.


Starten
-------
1. Starte die Anwendung ueber W-MIDI.exe.
2. Waehle dein MIDI-Eingabegeraet aus.
3. Trage die IP-Adresse deines WLED-Controllers ein.
4. Pruefe, ob der UDP-Port auf 21324 steht. Das ist der WLED-Standard.
5. Stelle LED-Anzahl und Startnote passend zu deinem Setup ein.
6. Klicke auf "Start Bridge".

Mit "Stop Bridge" beendest du die laufende Verbindung wieder.


Wichtige Felder
---------------
MIDI input device:
Das MIDI-Geraet oder der virtuelle MIDI-Port, von dem die Software Noten
empfangen soll.

WLED controller IP:
Die lokale Netzwerkadresse deines WLED-Controllers, zum Beispiel
192.168.1.100.

UDP port:
Der Echtzeit-Port von WLED. In der Regel bleibt dieser Wert auf 21324.

Total LED count:
Die Anzahl der LEDs, die von der Software angesprochen werden sollen.

Start note (base):
Die MIDI-Note, die auf LED 0 gelegt wird. Jede hoehere Note wandert weiter
nach rechts durch den LED-Streifen.

Listen channel:
"All" reagiert auf alle MIDI-Kanaele. Alternativ kannst du einen einzelnen
Kanal von 1 bis 16 auswaehlen.

LEDs per channel:
Optional fuer groessere Setups. Damit kann jeder MIDI-Kanal einen eigenen
LED-Bereich bekommen.

Mapping mode:
Legt fest, wie die Farben erzeugt werden. Fuer den Einstieg ist
"velocity_palette" sinnvoll, weil die Anschlagstaerke die Farbe bestimmt.

Velocity palette file:
Die Palette fuer den Modus "velocity_palette". Standard ist
palettes/velocity_palette.txt.

Frame interval (ms):
Begrenzt, wie schnell neue Lichtdaten gesendet werden. 5 ms ist schnell,
10 ms kann bei instabilen Netzwerken ruhiger laufen.

MIDI read burst:
Bestimmt, wie viele MIDI-Nachrichten pro Durchlauf verarbeitet werden.
Der Standardwert ist fuer normale Nutzung passend.

Verbose output in log:
Schreibt mehr Details in das Log. Fuer Fehlersuche hilfreich, fuer Live-Betrieb
meist ausgeschaltet lassen.


Typischer Ablauf
----------------
1. WLED-Controller einschalten und sicherstellen, dass er im gleichen Netzwerk
   wie der PC ist.
2. MIDI-Geraet verbinden oder virtuellen MIDI-Port starten.
3. W-MIDI.exe oeffnen.
4. WLED-IP und MIDI-Geraet einstellen.
5. Mit "Test Connection" pruefen, ob der Controller erreichbar ist.
6. Mit "Start Bridge" starten.
7. MIDI-Noten spielen und die LEDs beobachten.
8. Einstellungen bei Bedarf mit "Save Config" speichern.


Log und Fehlersuche
-------------------
Unten im Fenster befindet sich das Bridge Log. Dort siehst du Statusmeldungen
und Hinweise, wenn etwas nicht stimmt.

"Pop Out" oeffnet das Log in einem eigenen Fenster.
"Clear Log" leert die Anzeige.

Wenn keine LEDs reagieren:
- Pruefe die WLED-IP.
- Pruefe, ob PC und WLED im gleichen Netzwerk sind.
- Pruefe, ob das richtige MIDI-Geraet ausgewaehlt ist.
- Pruefe, ob die Startnote zu deinen gespielten Noten passt.
- Stelle sicher, dass WLED UDP-Realtime-Daten akzeptiert.


Einstellungen speichern
-----------------------
Mit "Save Config" werden deine aktuellen Einstellungen in config.json
gespeichert. Beim naechsten Start werden sie automatisch geladen.


Hilfe oeffnen
-------------
Das Fragezeichen oben rechts in der Anwendung oeffnet standardmaessig die
englische README_EN.txt.
