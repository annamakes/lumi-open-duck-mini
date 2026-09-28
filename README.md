# Lumi Open Duck Mini

Lumi ist ein sozialer Begleitroboter, der im Rahmen des Semesterprojekts „Automatisierte Systeme im Design“ entwickelt wurde. Das Projekt basiert auf dem Open-Source-Projekt [Open Duck Mini v2](https://github.com/apirrone/Open_Duck_Mini).

Ziel des Projekts ist es, zu untersuchen, wie ein kleiner Roboter durch Sprache, Bewegung und eine wiedererkennbare Persönlichkeit als soziale Präsenz im Alltag wahrgenommen werden kann.

## Aktueller Entwicklungsstand

Der aktuelle Prototyp umfasst:

- gedruckte mechanische Komponenten
- Aufnahme deutscher Sprache über ein Mikrofon
- Umwandlung der Sprache in Text
- Dialog mit einem Sprachmodell
- einen eigenen System-Prompt für Lumis Persönlichkeit
- Textausgabe der Antworten in der Konsole

Noch nicht vollständig integriert sind:

- Audioausgabe am Roboter
- Motorsteuerung und Laufbewegungen
- Sensorik und Hinderniserkennung
- dauerhaftes Gedächtnis
- Verbindung zwischen Dialog und Bewegung

Das Repository dokumentiert einen frühen Lern- und Forschungsprototyp. Der Code ist nicht für einen produktiven Einsatz vorgesehen.

## Eigene Erweiterungen

Für dieses Semesterprojekt wurden folgende Bestandteile entwickelt:

- deutscher Sprachdialog
- Persönlichkeit und System-Prompt für Lumi
- mikrofonbasierte Eingabe
- Behandlung von Sprach- und Verbindungsfehlern
- Dokumentation des Druck- und Entwicklungsprozesses
- Konzept für die Verbindung von Dialog, Sensorik und Bewegung

## Open-Source-Grundlage

Open Duck Mini wurde von Antoine Pirrone und der Open-Duck-Mini-Community entwickelt. Aus dem Ausgangsprojekt wurden technische Konzepte, CAD- und Druckdateien sowie Ansätze für die Bewegungssteuerung und Machine-Learning-Policies verwendet.

Die Machine-Learning- und Bewegungsfunktionen sind keine vollständige Eigenentwicklung. Die Herkunft übernommener Bestandteile wird in diesem Repository kenntlich gemacht.

Open Duck Mini ist unter der Apache License 2.0 veröffentlicht.

## Sicherheit

API-Schlüssel und andere Zugangsdaten werden nicht im Repository gespeichert. Die Datei `api_key_folder.json` muss lokal bleiben und ist von der Versionsverwaltung ausgeschlossen.

## Lizenz

Die Lizenzinformationen befinden sich in der Datei `LICENSE`. Die Lizenz- und Urheberrechtshinweise übernommener Bestandteile bleiben erhalten.
