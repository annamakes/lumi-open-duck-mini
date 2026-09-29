# Lumi – Open Duck Mini

Lumi ist ein sozialer Begleitroboter, der im Rahmen des Semesterprojekts **„Automatisierte Systeme im Design“** entwickelt wird.

Das Projekt untersucht, wie ein kleiner physischer Roboter durch Sprache, Bewegung und eine wiedererkennbare Persönlichkeit als soziale Präsenz im Alltag wahrgenommen werden kann.

Lumi basiert auf dem Open-Source-Projekt [Open Duck Mini V2](https://github.com/apirrone/Open_Duck_Mini/tree/v2). Für den Aufbau und die Einrichtung wird ergänzend die visuell aufbereitete [TNKR-Anleitung](https://tnkr.ai/builds/setup/open-duck-mini) verwendet.

## Projektziel

Ziel ist die Verbindung dreier Bereiche:

1. sprachbasierte Interaktion,
2. körperliche Ausdrucksmöglichkeiten durch Bewegung,
3. eine konsistente Persönlichkeit für Lumi.

Der Roboter soll Sprache erfassen, verarbeiten und beantworten können. Allerdings nicht mit natürlicher Sprache, sondern mithilfe von Tönen. Langfristig sollen Dialog, Bewegung, Sensorik und Ausdruck gemeinsam auf den Gesprächsverlauf reagieren.

## Aktueller Entwicklungsstand

### Mechanik und Elektronik

Der aktuelle Prototyp umfasst:

- vollständig gedruckte und montierte Roboterkomponenten,
- Raspberry Pi Zero 2 W,
- 14 Feetech-ST-Serie-Servomotoren,
- serielles Servo-Steuerungsboard,
- BNO055-IMU,
- Stromversorgung über zwei Lithium-Ionen-Zellen, BMS und 5-V-Regler,
- vorbereitete Komponenten für Mikrofon, Lautsprecher und LEDs.

Die Servo-IDs wurden entsprechend der Open-Duck-Mini-Konfiguration vergeben:

| Bereich | Servo-IDs |
|---|---|
| Rechtes Bein | `10–14` |
| Linkes Bein | `20–24` |
| Hals und Kopf | `30–33` |

Alle 14 Servos wurden bereits gemeinsam über den seriellen Bus erkannt. Die IMU wurde unter der I²C-Adresse `0x28` erkannt und erfolgreich ausgelesen.

Nach der Neuinstallation des Raspberry Pi müssen diese Hardwaretests mit der neuen Runtime erneut bestätigt werden.

### Sprachdialog

Der bisherige Dialogprototyp umfasst:

- Aufnahme deutscher Sprache über ein Mikrofon,
- Umwandlung gesprochener Sprache in Text,
- Übergabe der Texteingabe an ein Sprachmodell,
- einen eigenen System-Prompt für Lumis Persönlichkeit,
- Behandlung ausgewählter Sprach- und Verbindungsfehler,
- Textausgabe der Antworten in der Konsole.

Der Sprachdialog wurde als eigenständiger Softwareprototyp entwickelt. Die vollständige Ausführung auf dem Roboter und die Verbindung mit Bewegung und Audioausgabe befinden sich noch in Arbeit.

### Bewegung

Bereits umgesetzt beziehungsweise getestet wurden:

- Konfiguration aller Servo-IDs,
- Kommunikation mit allen 14 Servos,
- einzelnes Aktivieren und Abschalten der Gelenke,
- Auslesen der Servo-Positionen,
- Messung erster Gelenk-Offsets mit geringer Haltekraft,
- Auslesen der IMU-Daten.

Noch ausstehend sind:

- Kalibrierung der Servos des rechten Beins,
- Übernahme aller Offsets in `duck_config.json`,
- erneuter Motor- und IMU-Test nach der Systeminstallation,
- kontrollierter Test der vollständigen Neutralposition,
- sicherer erster Test der Laufbewegung,
- Verbindung von Dialog und Bewegung.

Die vollständige Laufsteuerung wird erst gestartet, wenn alle Gelenke geprüft und die Stromversorgung unter Last zuverlässig getestet wurden.

## Servo-Kalibrierung

Die Gelenk-Offsets werden einzeln bestimmt. Dadurch wird vermieden, dass alle 14 Servos gleichzeitig aktiviert werden und eine hohe Stromspitze verursachen.

Der bisherige Kalibrierungsstand ist dokumentiert in:

```text
docs/servo_offsets_partial_2026-09-28.md
```

Die dort gespeicherten Werte sind ein Zwischenstand und noch keine vollständig getestete Laufkonfiguration.

## Software-Grundlage

Das Projekt verwendet drei voneinander unterscheidbare Ebenen.

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
- Motor- und Kalibrierungsskripte,
- Roboterkonfiguration,
- Ausführung der trainierten Bewegungs-Policy.

### TNKR-Integration

Für die Installation und Verwaltung auf dem Raspberry Pi wird der Fork [tnkrai/Open_Duck_Mini_Runtime](https://github.com/tnkrai/Open_Duck_Mini_Runtime/tree/v2) verwendet.

Dieser baut auf der ursprünglichen Open-Duck-Runtime auf und ergänzt sie unter anderem um:

- einen automatisierten Installer,
- eine reproduzierbare Python-Umgebung,
- den Systemdienst `tnkr-robot`,
- Diagnose- und Testfunktionen,
- eine Schnittstelle für TNKR Studio,
- optionale anonyme Telemetrie.

Die Mechanik, Servo-IDs und grundlegende Bewegungssteuerung bleiben dabei mit Open Duck Mini kompatibel.

## Installation auf dem Raspberry Pi

Die TNKR-Runtime wird auf dem Raspberry Pi mit folgendem Installer eingerichtet:

```bash
curl -sSL https://raw.githubusercontent.com/tnkrai/Open_Duck_Mini_Runtime/v2/scripts/setup.sh \
  | bash -s -- --clean
```

Während der Installation wird der Servo-Controller vom Raspberry Pi getrennt und eine unabhängige, stabile Stromversorgung verwendet.

Die optionale TNKR-Telemetrie kann während der Installation abgelehnt oder später über folgende Datei deaktiviert werden:

```text
~/.tnkr-telemetry.json
```

## Bewegung und Machine Learning

Die Laufbewegung basiert auf einer bereits trainierten Bewegungs-Policy des Open-Duck-Mini-Projekts.

Das Machine-Learning-Modell wurde nicht im Rahmen dieses Semesterprojekts neu trainiert. Auf dem Raspberry Pi findet kein Training statt. Dort wird lediglich die bereitgestellte ONNX-Policy ausgeführt, um aus Sensor- und Gelenkdaten Zielpositionen für die Servos zu berechnen.

Die Machine-Learning- und grundlegenden Bewegungsfunktionen sind daher keine vollständige Eigenentwicklung. Ihre Herkunft wird in diesem Repository kenntlich gemacht.

## Eigene Erweiterungen

Im Rahmen des Semesterprojekts wurden beziehungsweise werden folgende eigene Bestandteile entwickelt:

- deutscher Sprachdialog,
- Persönlichkeit und System-Prompt für Lumi,
- mikrofonbasierte Eingabe,
- Behandlung von Sprach- und Verbindungsfehlern,
- Konzept für sprachabhängige Reaktionen,
- zusätzliche sichere Motor- und Kalibrierungstests,
- Dokumentation des Druck-, Montage- und Entwicklungsprozesses,
- Konzept für die Verbindung von Dialog, Sensorik, Audio und Bewegung.

## Noch nicht vollständig integriert

Folgende Funktionen befinden sich noch in Entwicklung:

- Audioausgabe über den Lautsprecher,
- vollständige Motor- und Laufsteuerung,
- Verbindung zwischen Dialog und Bewegung,
- Ausdruck über Kopf, LEDs und weitere Aktoren,
- Hindernis- und Umgebungserkennung,
- dauerhaftes Gedächtnis,
- abschließende Absicherung der mobilen Stromversorgung.

## Sicherheit

Der Roboter ist ein Lern- und Forschungsprototyp und nicht für einen unbeaufsichtigten oder produktiven Einsatz vorgesehen.

Vor Motorversuchen muss der Roboter sicher abgestützt werden. Lauf- und Mehrservo-Tests dürfen erst durchgeführt werden, wenn Stromversorgung, Verkabelung, Gelenk-Offsets und Notabschaltung geprüft wurden.

API-Schlüssel, WLAN-Passwörter und andere Zugangsdaten werden nicht im Repository gespeichert. 

## Open-Source-Hinweise

Open Duck Mini wurde von Antoine Pirrone und der Open-Duck-Mini-Community entwickelt. Aus dem Projekt werden technische Konzepte, CAD- und Druckdateien, Runtime-Komponenten sowie Machine-Learning-Policies verwendet.

Die ursprünglichen Projektdateien werden nach Möglichkeit nicht unnötig dupliziert, sondern über ihre jeweiligen Repositories bezogen. Übernommene oder angepasste Dateien behalten ihre bestehenden Lizenz- und Urheberrechtshinweise.

Das ursprüngliche Open-Duck-Mini-Projekt ist unter der [Apache License 2.0](https://github.com/apirrone/Open_Duck_Mini/blob/v2/LICENSE) veröffentlicht.

## Lizenz

Die Lizenzinformationen für die Inhalte dieses Repositories befinden sich in der Datei `LICENSE`.

Für übernommene Bestandteile gelten zusätzlich die Lizenzbedingungen und Urheberrechtshinweise der jeweiligen Ursprungsprojekte.
