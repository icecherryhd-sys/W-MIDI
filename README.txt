W-MIDI v1.1.0
==============

Kurz gesagt
-----------
W-MIDI verbindet MIDI-Eingaben mit WLED-Echtzeitbeleuchtung per UDP. Die App
unterstuetzt mehrere unabhaengige Bridges, virtuelle MIDI-Ports,
Palettenvorschau und Helligkeitsskalierung, eine Live-LED-Vorschau und eigene
2D-LED-Layouts.


Schnellstart
------------
1. Entpacke die komplette ZIP-Datei.
2. Lasse W-MIDI.exe und den Ordner _internal zusammen im entpackten Ordner.
3. Starte W-MIDI.exe.
4. Waehle einen MIDI-Eingang.
5. Trage die WLED-IP ein oder nutze "Find WLED".
6. Lasse den UDP-Port auf 21324, sofern dein WLED-Setup nichts anderes nutzt.
7. Stelle LED-Anzahl, Startnote und optional LEDs pro Kanal ein.
8. Waehle eine Palette und klicke auf "Start Bridge".

Mit "Test Connection" pruefst du den Controller. Mit "Save Config" speicherst
du deinen Arbeitsstand.


Mehrere Bridges
---------------
Die nummerierten Kreise links stehen fuer einzelne Bridge-Instanzen. Mit "+"
fuegst du eine Instanz hinzu, mit "-" entfernst du die ausgewaehlte Instanz.
Jede Bridge besitzt eigene MIDI-, WLED-, Paletten-, Layout- und
Log-Einstellungen. Laufende Bridges arbeiten beim Wechseln der Tabs
ununterbrochen weiter.


Virtuelle MIDI-Ports
--------------------
Installiere loopMIDI einmalig, damit der virtualMIDI-Treiber vorhanden ist.
Die loopMIDI-Anwendung selbst muss nicht geoeffnet sein. Klicke auf
"Create New Midi Port", trage einen Namen ein und waehle "Add". Von W-MIDI
erzeugte Ports sind temporaer und verschwinden beim Schliessen der App.


Color Engine
------------
Waehle eine Palette aus dem Dropdown. W-MIDI versteht Dateien mit
"velocity:R,G,B"-Eintraegen und Launchpad-Dateien mit Zeilen im Format
"0, R G B;".

Die Vorschau zeigt alle 128 Velocity-Farben. Der Sonnenknopf skaliert
Launchpad-Werte von 0..63 auf 0..255 fuer die ausgewaehlte Bridge. Der
Mondknopf stellt die Originalwerte wieder her. Die Palettendatei selbst wird
dabei niemals veraendert.


LED-Vorschau und Layout-Editor
------------------------------
Der Bereich LED/MIDI Mapping zeigt in Echtzeit exakt die Farben, die an WLED
gesendet werden. Die Anzahl der Quadrate entspricht "Total LED Count".

Mit "POP OUT" oeffnest du eine grosse Live-Vorschau. Mit "EDIT LAYOUT"
platzierst du LEDs frei auf einer 2D-Flaeche. Du kannst einzelne LEDs ziehen,
mehrere LEDs mit einem Auswahlrahmen markieren, Gruppen gemeinsam verschieben
und drehen. "RESET LAYOUT" stellt das automatische Raster wieder her. Layouts
lassen sich als JSON speichern und wieder importieren.


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
