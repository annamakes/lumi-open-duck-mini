# Lumi – Open Duck Mini

Lumi ist ein sozialer Begleitroboter, der im Rahmen des Semesterprojekts **„Automatisierte Systeme im Design“** entwickelt wurde. Das Projekt untersucht, wie ein kleiner physischer Roboter durch Bewegung, Töne, sprachbasierte Verarbeitung und eine wiedererkennbare Persönlichkeit als soziale Präsenz im Alltag wahrgenommen werden kann.

Die mechanische und technische Grundlage bildet das Open-Source-Projekt [Open Duck Mini V2](https://github.com/apirrone/Open_Duck_Mini/tree/v2). Für Installation, Konfiguration und Diagnose auf dem Raspberry Pi wird ergänzend die visuell aufbereitete [TNKR-Anleitung](https://tnkr.ai/builds/setup/open-duck-mini) sowie der zugehörige [TNKR-Runtime-Fork](https://github.com/tnkrai/Open_Duck_Mini_Runtime/tree/v2) verwendet.

## Projektziel

Das Projekt verbindet drei Bereiche:

1. sprachbasierte Interaktion,
2. körperlichen Ausdruck durch Bewegung,
3. eine konsistente Persönlichkeit für Lumi.

Der Roboter soll gesprochene deutsche Sprache erfassen und inhaltlich verarbeiten können. Seine Reaktionen sollen langfristig nicht ausschließlich über synthetische Sprache, sondern vor allem über Töne, Kopf- und Körperbewegungen sowie visuelle Ausdruckselemente erfolgen. Dadurch soll Lumi weniger wie ein klassischer Sprachassistent und stärker wie ein kleines interaktives Wesen wirken.

## Aktueller Entwicklungsstand

Der aktuelle Prototyp ist mechanisch vollständig montiert. Alle 14 Servomotoren, die IMU und die lokale TNKR-Steuerung wurden erkannt und getestet. Der Roboter kann sich in einer vorbereiteten Standposition selbst halten und kurze strombegrenzte Ausdruckschoreografien ausführen.

Bereits umgesetzt und getestet wurden:

- Druck und Montage der mechanischen Komponenten,
- Vergabe und Prüfung aller 14 Servo-IDs,
- gemeinsame Kommunikation mit allen Servos über den seriellen Bus,
- Auslesen von Position, Spannung und Temperatur der Servos,
- Ermittlung und Speicherung der Gelenk-Offsets,
- Prüfung der Zielpositionen gegen den erlaubten Servobereich,
- Erkennung und Auslesen der BNO055-IMU,
- lokale Steuerung über den Dienst `tnkr-robot`,
- kontrolliertes Halten einer Standposition,
- kleine Kopf-, Hals-, Hüft- und Kniebewegungen,
- mehrere abgesicherte Demonstrationsskripte,
- Aufnahme und Verarbeitung deutscher Sprache in einem separaten Dialogprototyp,
- Anbindung eines Sprachmodells und Entwicklung eines System-Prompts für Lumis Persönlichkeit.

Noch nicht vollständig integriert beziehungsweise abschließend getestet sind:

- die vollständige Laufbewegung,
- die Verbindung zwischen Dialog und Bewegung,
- die Audioausgabe am Roboter,
- die Einbindung von LEDs und weiterer Sensorik,
- Hindernis- und Umgebungserkennung,
- dauerhaftes Gedächtnis,
- ein abschließend belastbarer mobiler Energieaufbau für längere Bewegungsabläufe.

## Hardware

Der aktuelle Aufbau umfasst:

- Raspberry Pi Zero 2 W,
- Raspberry Pi OS 64-Bit,
- 14 Feetech-STS3215-Servomotoren,
- serielles Servo-Steuerungsboard,
- BNO055-IMU,
- zwei Lithium-Ionen-Zellen in Serienschaltung,
- 2S-BMS,
- 5-V-Spannungsregler für den Raspberry Pi,
- USB-Verbindung zwischen Raspberry Pi und Servo-Steuerungsboard,
- vorbereitete Komponenten für Mikrofon, Lautsprecher und LEDs.

### Servo-IDs

| Bereich | Gelenk | ID |
|---|---|---:|
| Rechtes Bein | `right_hip_yaw` | 10 |
| Rechtes Bein | `right_hip_roll` | 11 |
| Rechtes Bein | `right_hip_pitch` | 12 |
| Rechtes Bein | `right_knee` | 13 |
| Rechtes Bein | `right_ankle` | 14 |
| Linkes Bein | `left_hip_yaw` | 20 |
| Linkes Bein | `left_hip_roll` | 21 |
| Linkes Bein | `left_hip_pitch` | 22 |
| Linkes Bein | `left_knee` | 23 |
| Linkes Bein | `left_ankle` | 24 |
| Hals/Kopf | `neck_pitch` | 30 |
| Hals/Kopf | `head_pitch` | 31 |
| Hals/Kopf | `head_yaw` | 32 |
| Hals/Kopf | `head_roll` | 33 |

Die IMU wurde am I²C-Bus unter der Adresse `0x28` erkannt.

## Softwarearchitektur

Das Projekt nutzt mehrere voneinander getrennte Ebenen.

### Open Duck Mini

[apirrone/Open_Duck_Mini](https://github.com/apirrone/Open_Duck_Mini/tree/v2) ist die ursprüngliche Grundlage für:

- Robotermechanik,
- CAD- und Druckdateien,
- Gelenkstruktur,
- Elektronikaufbau,
- Machine-Learning- und Sim2Real-Konzept.

### Open Duck Mini Runtime

[apirrone/Open_Duck_Mini_Runtime](https://github.com/apirrone/Open_Duck_Mini_Runtime/tree/v2) stellt unter anderem bereit:

- Kommunikation mit den Servomotoren,
- IMU-Anbindung,
- Roboterkonfiguration,
- Kalibrierungs- und Testfunktionen,
- Ausführung der trainierten Bewegungs-Policy.

### TNKR-Integration

Auf dem Raspberry Pi wird der Fork [tnkrai/Open_Duck_Mini_Runtime](https://github.com/tnkrai/Open_Duck_Mini_Runtime/tree/v2) verwendet. Dieser ergänzt die ursprüngliche Runtime unter anderem um:

- einen automatisierten Installer,
- eine reproduzierbare Python-Umgebung,
- den Systemdienst `tnkr-robot`,
- Diagnose- und Testfunktionen,
- eine lokale HTTP-API,
- eine interaktive OpenAPI-Dokumentation,
- eine Schnittstelle für TNKR Studio,
- optionale anonyme Telemetrie.

Die lokale API-Dokumentation ist bei laufendem Roboter im selben Netzwerk erreichbar:

- [http://lumipi.local:8000/docs](http://lumipi.local:8000/docs)

### Eigene Anwendungsschicht

Die eigene Anwendungsschicht enthält den Sprachdialog, Lumis Persönlichkeit, Fehlerbehandlung sowie zusätzliche abgesicherte Bewegungs- und Diagnoseskripte. Sie greift auf die vorhandene Runtime zurück, ersetzt diese aber nicht.

## Installation

### Betriebssystem

Getestete Umgebung:

- Raspberry Pi Zero 2 W,
- Raspberry Pi OS 64-Bit,
- Debian 13 (Trixie),
- Python 3.13,
- Hostname `lumipi`.

SSH kann im Raspberry Pi Imager aktiviert werden. Nach dem Start ist der Pi im lokalen Netzwerk beispielsweise so erreichbar:

```bash
ssh anna@lumipi.local
```

### TNKR-Runtime installieren

Die TNKR-Runtime kann auf einem frisch eingerichteten Raspberry Pi mit folgendem Installer installiert werden:

```bash
curl -sSL https://raw.githubusercontent.com/tnkrai/Open_Duck_Mini_Runtime/v2/scripts/setup.sh \
  | bash -s -- --clean
```

`--clean` führt eine saubere Neuinstallation der Runtime durch. Vorher müssen eigene Konfigurationsdateien und Skripte gesichert werden.

Während der Installation sollte der Servo-Controller vom Raspberry Pi getrennt und der Pi über eine stabile Stromquelle versorgt werden.

### Systembibliotheken für Audio

Für Mikrofonaufnahme und Audioverarbeitung werden zusätzliche Systembibliotheken benötigt:

```bash
sudo apt update
sudo apt install -y \
  python3-venv \
  python3-dev \
  build-essential \
  portaudio19-dev \
  libportaudio2 \
  libasound2-dev
```

Diese Pakete werden durch das Betriebssystem verwaltet und gehören deshalb nicht in `requirements.txt`.

### Virtuelle Python-Umgebung

Die TNKR-Installation erstellt normalerweise bereits eine virtuelle Umgebung im Runtime-Verzeichnis. Sie wird mit folgenden Befehlen aktiviert:

```bash
cd ~/Open_Duck_Mini_Runtime
source .venv/bin/activate
```

Eine aktive Umgebung ist am Präfix `(.venv)` vor der Eingabeaufforderung erkennbar.

Falls noch keine virtuelle Umgebung existiert, kann sie erstellt werden:

```bash
cd ~/Open_Duck_Mini_Runtime
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

Nach einem Neustart oder einer neuen SSH-Verbindung muss die Umgebung erneut aktiviert werden.

### Python-Abhängigkeiten

Die direkten Abhängigkeiten des eigenen Sprach- und Audiocodes werden in `requirements.txt` dokumentiert:

```text
openai
numpy
sounddevice
SpeechRecognition
PyAudio
```

Installation:

```bash
python -m pip install -r requirements.txt
python -m pip check
```

Die Abhängigkeiten der Motorsteuerung und Machine-Learning-Runtime werden durch die Open-Duck-Mini-/TNKR-Installation eingerichtet und deshalb nicht vollständig in der `requirements.txt` dieses Projekts dupliziert.

## Systemdienst und Diagnose

Status des TNKR-Dienstes prüfen:

```bash
systemctl is-active tnkr-robot
sudo systemctl status tnkr-robot --no-pager
```

Dienst steuern:

```bash
sudo systemctl start tnkr-robot
sudo systemctl stop tnkr-robot
sudo systemctl restart tnkr-robot
```

Live-Protokoll anzeigen:

```bash
sudo journalctl -u tnkr-robot -f
```

API-Zustand kontrollieren:

```bash
curl -s http://127.0.0.1:8000/api/health | python3 -m json.tool
```

Akkuspannung und Servotemperaturen kontrollieren:

```bash
curl -s http://127.0.0.1:8000/api/voltage | python3 -m json.tool
```

Alle Servos prüfen:

```bash
curl -s -X POST http://127.0.0.1:8000/api/motors/check \
  | python3 -m json.tool
```

## Konfiguration und Kalibrierung

Die aktuelle Roboterkonfiguration befindet sich auf dem Raspberry Pi in:

```text
~/duck_config.json
```

Sie enthält unter anderem:

- Gelenk-Offsets,
- Gelenkrichtungen,
- Funktionsschalter für optionale Hardware,
- Start- und IMU-Einstellungen.

Die Offsets sind spezifisch für den mechanischen Aufbau dieses Roboters und dürfen nicht ungeprüft auf einen anderen Open Duck Mini übertragen werden.

### Aktuell dokumentierte Offsets

| Gelenk | Offset in rad |
|---|---:|
| `left_hip_yaw` | `-2.6875` |
| `left_hip_roll` | `-0.8007` |
| `left_hip_pitch` | `2.8624` |
| `left_knee` | `-1.1459` |
| `left_ankle` | `-1.2134` |
| `neck_pitch` | `0.6627` |
| `head_pitch` | `-0.4510` |
| `head_yaw` | `-1.0032` |
| `head_roll` | `-0.1304` |
| `right_hip_yaw` | `0.0000` |
| `right_hip_roll` | `0.2240` |
| `right_hip_pitch` | `-1.0354` |
| `right_knee` | `0.0000` |
| `right_ankle` | `-1.1229` |

`right_hip_yaw` und `right_knee` wurden im Servo selbst neu referenziert. Ihre Software-Offsets stehen deshalb auf `0.0`.

Vor jeder automatischen Bewegung müssen Konfiguration, Servo-Zuordnung, Bewegungsrichtung und mechanische Nullposition erneut kontrolliert werden.

## Demonstrationsskripte

Für die sichere schrittweise Inbetriebnahme wurden mehrere eigene Skripte entwickelt.

### `lumi_safe_demo.py`

Erste strombegrenzte Demonstration mit kleinen Kopf- und Halsbewegungen. Das Skript prüft vor der Bewegung Serverstatus, Akkuspannung und Servo-Erreichbarkeit.

### `lumi_joy_choreography.py`

Kurze Ausdruckssequenz mit Kopf-, Hüft- und Kniebewegungen. Die Gelenke werden nacheinander bewegt, um Stromspitzen zu reduzieren.

### `lumi_expressive_choreography.py`

Erweiterte Standchoreografie mit:

- kleinen Beinbewegungen,
- bewussten Pausen,
- einem längeren Blick nach links,
- einer kürzeren Reaktion nach rechts,
- einer seitlichen Kopfneigung,
- einem abschließenden Nicken,
- Sicherheits- und Spannungsprüfungen.

Vor dem ersten echten Durchlauf sollte jeweils der Trockenlauf ausgeführt werden:

```bash
cd ~/Open_Duck_Mini_Runtime
source .venv/bin/activate
python -u scripts/lumi_expressive_choreography.py --dry-run
```

Echter Start:

```bash
python -u scripts/lumi_expressive_choreography.py
```

## Sprachdialog

Der bisherige Dialogprototyp umfasst:

- Aufnahme deutscher Sprache über ein Mikrofon,
- Umwandlung gesprochener Sprache in Text,
- Übergabe der Texteingabe an ein Sprachmodell,
- einen eigenen System-Prompt für Lumis Persönlichkeit,
- Behandlung ausgewählter Sprach- und Verbindungsfehler,
- Textausgabe der Antwort in der Konsole.

Der Sprachdialog wurde als eigenständiger Softwareprototyp entwickelt. Die vollständige Ausführung auf dem Roboter und die Verbindung mit Bewegung, Tönen und visuellen Ausdrucksmitteln befinden sich noch in Entwicklung.

## Bewegung und Machine Learning

Die Laufbewegung basiert auf einer bereits trainierten Bewegungs-Policy des Open-Duck-Mini-Projekts. Das Machine-Learning-Modell wurde nicht im Rahmen dieses Semesterprojekts neu trainiert.

Auf dem Raspberry Pi findet kein Training statt. Dort wird lediglich die bereitgestellte ONNX-Policy ausgeführt, um aus Sensor-, Zustands- und Gelenkdaten Zielpositionen für die Servos zu berechnen.

Die Machine-Learning-Policy und die grundlegenden Laufalgorithmen sind daher keine Eigenentwicklung dieses Projekts. Ihre Herkunft wird im Repository kenntlich gemacht.

## Eigenleistung

Im Rahmen des Semesterprojekts wurden insbesondere folgende Bestandteile selbst entwickelt beziehungsweise projektspezifisch angepasst:

- Konzeption der sozialen Roboterfigur Lumi,
- Persönlichkeit und System-Prompt,
- deutscher Sprachdialog,
- mikrofonbasierte Eingabe,
- Behandlung von Sprach- und Verbindungsfehlern,
- Konzept für tonbasierte Reaktionen,
- Montage, Verkabelung und Inbetriebnahme des physischen Prototyps,
- Zuordnung und Prüfung der 14 Servos,
- Ermittlung und Dokumentation der individuellen Gelenk-Offsets,
- zusätzliche Sicherheits- und Diagnoseskripte,
- strombegrenzte Ausdruckschoreografien,
- Dokumentation des Druck-, Montage- und Entwicklungsprozesses,
- Konzept zur Verbindung von Dialog, Sensorik, Audio und Bewegung.

Bei der Entwicklung, Fehlersuche und Dokumentation wurde KI-gestützte Assistenz eingesetzt. Generierter oder vorgeschlagener Code wurde in das Projekt eingeordnet, angepasst und am realen Prototyp getestet.

## Sicherheit

Lumi ist ein Lern- und Forschungsprototyp und nicht für unbeaufsichtigten oder produktiven Einsatz vorgesehen.

Vor jedem Motorversuch gilt:

- Roboter mechanisch sichern oder am Oberkörper festhalten,
- beide Füße auf eine rutschfeste Fläche stellen,
- Verkabelung und Polarität kontrollieren,
- Ladekabel vor Motorbewegungen entfernen,
- Akkuspannung kontrollieren,
- Erreichbarkeit aller Servos prüfen,
- Hauptschalter jederzeit erreichbar halten,
- Bewegungsbereich von Personen und Gegenständen freihalten.

Bei Zittern, Blockieren, ungewöhnlichen Geräuschen, starker Erwärmung, Verbindungsabbruch oder Hard Reset muss der Roboter sofort am Hauptschalter ausgeschaltet werden.

Ein als `low` oder `critical` bewerteter Spannungsstatus darf nicht durch das Entfernen von Sicherheitsprüfungen umgangen werden.

## Bekannte Einschränkungen

- Der Raspberry Pi Zero 2 W besitzt begrenzte Rechen- und Speicherressourcen.
- Hohe gleichzeitige Servolast kann Spannungseinbrüche verursachen.
- Die mobile Stromversorgung ist für längere oder dynamische Laufbewegungen noch nicht abschließend validiert.
- Die Ausdruckschoreografien sind Demonstrationen und ersetzen keine dynamisch stabilisierte Laufsteuerung.
- Die Audioausgabe und die Verknüpfung von Dialog und Bewegung sind noch nicht vollständig integriert.
- Kalibrierungswerte sind individuell und nicht ohne Prüfung auf andere Roboter übertragbar.

## Datenschutz und Zugangsdaten

API-Schlüssel, WLAN-Passwörter, Tokens und andere Zugangsdaten werden nicht im Repository gespeichert.

Lokale Dateien mit Geheimnissen müssen über `.gitignore` ausgeschlossen werden, beispielsweise:

```gitignore
.venv/
__pycache__/
*.pyc
.env
api_key_folder.json
duck_config.local.json
```

Die optionale TNKR-Telemetrie kann bei der Installation abgelehnt oder über die lokale TNKR-Konfiguration verwaltet werden.

## Repository-Struktur

Eine mögliche Struktur des Projekt-Repositories ist:

```text
.
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── docs/
│   ├── servo_offsets_partial_2026-09-28.md
│   └── development_notes.md
└── scripts/
    ├── lumi_safe_demo.py
    ├── lumi_joy_choreography.py
    └── lumi_expressive_choreography.py
```

Die Originaldateien der Open-Duck-Mini-Runtime werden nach Möglichkeit nicht unnötig kopiert. Eigene Skripte und Dokumente werden getrennt und mit ihrer Herkunft beziehungsweise Funktion beschrieben.

## Open-Source-Hinweise

Open Duck Mini wurde von Antoine Pirrone und der Open-Duck-Mini-Community entwickelt. Aus dem Projekt werden technische Konzepte, CAD- und Druckdateien, Runtime-Komponenten sowie Machine-Learning-Policies verwendet.

Die ursprünglichen Projektdateien werden nach Möglichkeit über ihre jeweiligen Repositories bezogen. Übernommene oder angepasste Dateien behalten ihre bestehenden Lizenz- und Urheberrechtshinweise.

Das ursprüngliche Open-Duck-Mini-Projekt ist unter der [Apache License 2.0](https://github.com/apirrone/Open_Duck_Mini/blob/v2/LICENSE) veröffentlicht.

## Lizenz

Die Lizenzinformationen für die eigenen Inhalte dieses Repositories befinden sich in `LICENSE`. Für übernommene Bestandteile gelten zusätzlich die Lizenzbedingungen und Urheberrechtshinweise der jeweiligen Ursprungsprojekte.

