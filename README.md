## Software und Dokumentation

Dieser Roboter basiert auf dem ursprünglichen **Open Duck Mini V2** von [apirrone](https://github.com/apirrone/Open_Duck_Mini).

Für den mechanischen Aufbau, die Verkabelung und die strukturierte Schritt-für-Schritt-Anleitung wurde die visuell aufbereitete [TNKR-Anleitung für den Open Duck Mini](https://tnkr.ai/builds/setup/open-duck-mini) verwendet.

### Runtime

Für die Softwareinstallation wird der TNKR-Fork der Open-Duck-Runtime verwendet:

- [TNKR Open Duck Mini Runtime](https://github.com/tnkrai/Open_Duck_Mini_Runtime/tree/v2)
- Upstream: [apirrone/Open_Duck_Mini_Runtime](https://github.com/apirrone/Open_Duck_Mini_Runtime/tree/v2)

Der TNKR-Fork verwendet weiterhin die ursprüngliche Open-Duck-Runtime, die Servo-IDs, Motorskripte und das ONNX-Laufmodell. Zusätzlich stellt er eine automatisierte Installation, Systemdienste, Tests und eine Schnittstelle für TNKR Studio bereit.

Installation auf dem Raspberry Pi:

```bash
curl -sSL https://raw.githubusercontent.com/tnkrai/Open_Duck_Mini_Runtime/v2/scripts/setup.sh \
  | bash -s -- --clean
```

### System

- Raspberry Pi Zero 2 W
- 64-Bit-Betriebssystem
- Hostname: `lumipi`
- Benutzer: `anna`
- Runtime-Verzeichnis: `~/Open_Duck_Mini_Runtime`
- Servo-Controller: `/dev/ttyACM0`
- IMU: BNO055, I²C-Adresse `0x28`
- Servos: 14 × Feetech STS3215

### Machine Learning

Das Training der Laufbewegung findet nicht auf dem Raspberry Pi statt. Auf dem Pi wird lediglich die bereits trainierte ONNX-Policy durch die Open-Duck-Runtime ausgeführt.

### Kalibrierungsstatus

Die Servo-IDs wurden erfolgreich konfiguriert und erkannt. Die Gelenk-Offsets werden einzeln und mit geringer Haltekraft bestimmt, um hohe gleichzeitige Stromspitzen zu vermeiden.

Die bisher bestätigten Werte befinden sich in:

```text
docs/servo_offsets_partial_2026-09-28.md
```

Die Werte des rechten Beins sind noch nicht vollständig kalibriert. Der Roboter darf deshalb noch nicht mit dem vollständigen Laufprogramm gestartet werden.

### Hinweis zu TNKR

Der TNKR-Fork ergänzt die ursprüngliche Runtime um Installations- und Verwaltungsfunktionen. Die Mechanik, Gelenkstruktur und grundlegende Motorsteuerung stammen weiterhin aus dem Open-Duck-Mini-Projekt.

Die optionale anonyme TNKR-Telemetrie kann über `~/.tnkr-telemetry.json` deaktiviert werden.
