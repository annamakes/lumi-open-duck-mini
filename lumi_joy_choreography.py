#!/usr/bin/env python3

"""
Strombegrenzte Ausdruckschoreografie für Lumi.

Die Choreografie kombiniert kleine Kopf-, Hals-, Hüft- und Kniebewegungen.
Um Stromspitzen zu reduzieren, wird immer nur ein Gelenk gleichzeitig bewegt.
Beide Füße sollen während der gesamten Vorführung am Boden bleiben.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "http://127.0.0.1:8000"

# Etwa 15 bis 20 Sekunden lange Bewegungsfolge.
# Die Wiggle-Funktion bewegt jeweils nur ein Gelenk um ungefähr ±4,6°.
CHOREOGRAPHY = (
    ("head_yaw", "Lumi schaut sich neugierig um"),
    ("head_roll", "Lumi legt den Kopf freundlich schief"),
    ("left_hip_roll", "Kleine Gewichtsverlagerung nach links"),
    ("right_hip_roll", "Kleine Gewichtsverlagerung nach rechts"),
    ("head_pitch", "Lumi nickt"),
    ("left_knee", "Kleine Bewegung des linken Knies"),
    ("right_knee", "Kleine Bewegung des rechten Knies"),
    ("neck_pitch", "Lumi richtet den Kopf auf"),
    ("head_roll", "Lumi neigt den Kopf erneut"),
    ("head_yaw", "Abschließender neugieriger Blick"),
)


def request_json(base_url, path, method="GET", payload=None, timeout=20):
    """Sendet eine Anfrage an den lokalen TNKR-Server."""

    url = f"{base_url.rstrip('/')}{path}"
    headers = {}
    data = None

    if method == "POST":
        if payload is None:
            data = b""
        else:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8").strip()
            return json.loads(body) if body else {}

    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"API-Fehler {error.code} bei {path}: {body}"
        ) from error

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Server unter {url} nicht erreichbar: {error.reason}"
        ) from error


def release_motors(base_url):
    """Schaltet nach der Vorführung das Drehmoment aller Servos ab."""

    print("\nSchalte alle Motoren ab ...")

    try:
        request_json(
            base_url,
            "/api/stance/release",
            method="POST",
            timeout=15,
        )
        print("Alle Motoren wurden freigegeben.")

    except Exception as error:
        print(
            f"WARNUNG: Automatisches Abschalten fehlgeschlagen: {error}",
            file=sys.stderr,
        )
        print(
            "Bitte den Roboter jetzt am Hauptschalter ausschalten.",
            file=sys.stderr,
        )


def check_system(base_url):
    """Kontrolliert Server, Akkuspannung und alle Servos."""

    print("Prüfe TNKR-Server ...")
    health = request_json(base_url, "/api/health")

    if health.get("status") != "ok":
        raise RuntimeError(f"Serverstatus ist nicht OK: {health}")

    if health.get("walking"):
        raise RuntimeError(
            "Die Laufsteuerung ist bereits aktiv. "
            "Die Choreografie wird nicht gestartet."
        )

    print("Prüfe Akkuspannung ...")
    voltage = request_json(base_url, "/api/voltage")

    print(f"Akkuspannung: {voltage.get('volts')} V")
    print(f"Spannungsstatus: {voltage.get('health')}")

    if voltage.get("health") != "ok":
        raise RuntimeError(
            "Die Akkuspannung ist nicht im grünen Bereich. "
            "Roboter ausschalten und zunächst vollständig laden."
        )

    print("Prüfe alle Servos ...")
    motor_check = request_json(
        base_url,
        "/api/motors/check",
        method="POST",
    )

    if not motor_check.get("allResponsive"):
        missing = [
            motor.get("jointName", "unbekannt")
            for motor in motor_check.get("motors", [])
            if not motor.get("responsive")
        ]

        raise RuntimeError(
            "Nicht erreichbare Servos: " + ", ".join(missing)
        )

    print("Alle Servos antworten.")

    return voltage


def run_choreography(base_url):
    """Führt die strombegrenzte Ausdruckschoreografie aus."""

    print("\nAktiviere reduzierte Haltekraft an der aktuellen Position ...")

    request_json(
        base_url,
        "/api/calibration/start",
        method="POST",
    )

    time.sleep(1.5)

    print("Halteposition aktiv.")
    print("Die Choreografie beginnt in drei Sekunden ...")

    for remaining in (3, 2, 1):
        print(remaining)
        time.sleep(1)

    for joint_name, description in CHOREOGRAPHY:
        print(f"\n{description}")
        print(f"Gelenk: {joint_name}")

        request_json(
            base_url,
            "/api/calibration/wiggle",
            method="POST",
            payload={"jointName": joint_name},
        )

        time.sleep(0.3)

    print("\nFreude-Choreografie abgeschlossen.")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Strombegrenzte Freude-Choreografie "
            "mit Kopf- und Beinbewegungen."
        )
    )

    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Adresse des lokalen TNKR-Servers.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Nur System, Spannung und Servos kontrollieren.",
    )

    args = parser.parse_args()

    check_system(args.base_url)

    if args.dry_run:
        print("\nTrockenlauf erfolgreich.")
        print("Es wurde keine Bewegung ausgeführt.")
        return

    print("\nSICHERHEITSHINWEISE:")
    print("- Beide Füße vollständig auf eine rutschfeste Fläche stellen.")
    print("- Knie leicht gebeugt und Füße möglichst parallel ausrichten.")
    print("- Den Oberkörper beim ersten Durchlauf festhalten.")
    print("- Ladekabel vor der Bewegung entfernen.")
    print("- Hauptschalter jederzeit erreichbar halten.")
    print("- Bei Zittern, Blockieren oder ungewöhnlichen Geräuschen abbrechen.")

    input("\nRoboter sicher positionieren und Enter drücken ... ")

    try:
        run_choreography(args.base_url)

    finally:
        release_motors(args.base_url)

    try:
        voltage_after = request_json(args.base_url, "/api/voltage")

        print(
            "\nSpannung nach der Vorführung:",
            voltage_after.get("volts"),
            "V –",
            voltage_after.get("health"),
        )
    except Exception:
        print("Spannung nach der Vorführung konnte nicht gelesen werden.")


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nVorführung wurde mit Ctrl+C abgebrochen.")
        sys.exit(130)

    except Exception as error:
        print(f"\nABBRUCH: {error}", file=sys.stderr)
        sys.exit(1)
