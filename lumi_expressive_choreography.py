#!/usr/bin/env python3

"""
Lumi – expressive Standchoreografie

Ungefähr 15 bis 20 Sekunden lange Vorführung mit:

1. kleinen Bewegungen von Hüfte und Knien,
2. Übergang in die gespeicherte Grundstellung,
3. deutlichem Blick nach links,
4. Rückkehr zur Mitte,
5. freundlicher Kopfneigung,
6. kurzer Rechts-links-Bewegung,
7. abschließendem Nicken.

Die Bewegungen werden bewusst nacheinander ausgeführt, um gleichzeitige
Stromspitzen mehrerer Servomotoren möglichst zu vermeiden.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "http://127.0.0.1:8000"

# Kleine Beinbewegungen mit der strombegrenzten Wiggle-Funktion.
LEG_SEQUENCE = (
    ("left_hip_roll", "Gewichtsverlagerung nach links"),
    ("right_hip_roll", "Gewichtsverlagerung nach rechts"),
    ("left_knee", "Kleine Bewegung des linken Knies"),
    ("right_knee", "Kleine Bewegung des rechten Knies"),
)


def request_json(base_url, path, method="GET", payload=None, timeout=25):
    """Sendet eine JSON-Anfrage an den lokalen TNKR-Server."""

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


def post(base_url, path, payload=None, timeout=25):
    """Abkürzung für eine POST-Anfrage."""

    return request_json(
        base_url,
        path,
        method="POST",
        payload=payload,
        timeout=timeout,
    )


def check_system(base_url):
    """Prüft Server, Akkuspannung und Erreichbarkeit aller Servos."""

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
            "Roboter zuerst ausschalten und vollständig laden."
        )

    print("Prüfe alle 14 Servos ...")
    motor_check = post(base_url, "/api/motors/check")

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


def check_voltage_again(base_url):
    """Kontrolliert die Spannung vor dem belastenderen zweiten Abschnitt."""

    voltage = request_json(base_url, "/api/voltage")

    print(
        f"Zwischenprüfung: {voltage.get('volts')} V, "
        f"Status {voltage.get('health')}"
    )

    if voltage.get("health") != "ok":
        raise RuntimeError(
            "Die Spannung ist während der Vorführung abgesunken. "
            "Der Kopfabschnitt wird nicht gestartet."
        )


def move_head(base_url, pause=0.0, **axes):
    """
    Bewegt den Kopf über den Head-Puppet-Modus.

    Gültige Achsen:
    yaw, pitch, roll, neckPitch

    Die Werte liegen zwischen -1.0 und 1.0.
    """

    post(
        base_url,
        "/api/head/puppet",
        payload=axes,
    )

    if pause > 0:
        time.sleep(pause)


def run_leg_sequence(base_url):
    """Führt kleine Beinbewegungen mit reduzierter Haltekraft aus."""

    print("\nAbschnitt 1: kleine Beinbewegungen")
    print("Aktiviere reduzierte Haltekraft an der aktuellen Position ...")

    result = post(base_url, "/api/calibration/start")

    if result.get("mode") != "hold":
        raise RuntimeError(
            "Der Server hat den sicheren Haltemodus nicht bestätigt."
        )

    time.sleep(1.0)

    for joint_name, description in LEG_SEQUENCE:
        print(f"- {description}")

        post(
            base_url,
            "/api/calibration/wiggle",
            payload={"jointName": joint_name},
        )

        time.sleep(0.25)

    print("Beinbewegungen abgeschlossen.")


def finish_calibration(base_url):
    """
    Beendet den Kalibrierungs-Haltemodus.

    Dadurch verwirft der Server die vorübergehend genullten Offsets im
    Arbeitsspeicher. Beim nächsten Zugriff werden die gespeicherten
    Roboter-Offsets wieder aus der Konfiguration geladen.
    """

    result = post(base_url, "/api/calibration/finish")

    failed = result.get("failed", [])

    if failed:
        raise RuntimeError(
            "Folgende Servos konnten beim Beenden nicht aktiviert werden: "
            + ", ".join(failed)
        )


def run_head_sequence(base_url):
    """Führt unterschiedliche und gezielte Kopfbewegungen aus."""

    print("\nAbschnitt 2: Ausdrucksbewegungen des Kopfes")
    print("Der Roboter nimmt jetzt seine gespeicherte Grundstellung ein.")

    # Der erste Aufruf aktiviert den Head-Puppet-Modus und richtet
    # Kopf und Beine anhand der gespeicherten Konfiguration aus.
    move_head(
        base_url,
        pause=1.5,
        yaw=0.0,
        pitch=0.0,
        roll=0.0,
        neckPitch=0.0,
    )

    print("- Lumi schaut deutlich nach links")
    move_head(
        base_url,
        pause=1.5,
        yaw=-0.75,
    )

    print("- Lumi richtet den Kopf wieder zur Mitte")
    move_head(
        base_url,
        pause=1.0,
        yaw=0.0,
    )

    print("- Lumi legt den Kopf freundlich zur Seite")
    move_head(
        base_url,
        pause=1.2,
        roll=-0.5,
    )

    print("- Kopfneigung zurück zur Mitte")
    move_head(
        base_url,
        pause=0.8,
        roll=0.0,
    )

    print("- Kurzer Blick nach rechts")
    move_head(
        base_url,
        pause=0.55,
        yaw=0.4,
    )

    print("- Kurzer Blick nach links")
    move_head(
        base_url,
        pause=0.55,
        yaw=-0.4,
    )

    print("- Noch einmal kurz nach rechts")
    move_head(
        base_url,
        pause=0.45,
        yaw=0.3,
    )

    print("- Kopf wieder gerade")
    move_head(
        base_url,
        pause=0.7,
        yaw=0.0,
    )

    print("- Lumi nickt")
    move_head(
        base_url,
        pause=0.65,
        pitch=-0.2,
    )

    move_head(
        base_url,
        pause=0.65,
        pitch=0.2,
    )

    print("- Abschließende neutrale Kopfposition")
    move_head(
        base_url,
        pause=1.0,
        yaw=0.0,
        pitch=0.0,
        roll=0.0,
        neckPitch=0.0,
    )

    print("Kopfbewegungen abgeschlossen.")


def safe_cleanup(base_url, calibration_active, head_active):
    """Versucht unabhängig von Fehlern, den Roboter sicher freizugeben."""

    print("\nBeende die Vorführung ...")

    if calibration_active:
        try:
            post(base_url, "/api/calibration/finish")
            print("Kalibrierungs-Haltemodus beendet.")
        except Exception as error:
            print(
                f"WARNUNG beim Beenden des Haltemodus: {error}",
                file=sys.stderr,
            )

    if head_active:
        try:
            post(base_url, "/api/head/puppet/stop")
            print("Kopfsteuerung beendet.")
        except Exception as error:
            print(
                f"WARNUNG beim Beenden der Kopfsteuerung: {error}",
                file=sys.stderr,
            )

    try:
        post(base_url, "/api/stance/release")
        print("Alle Motoren wurden freigegeben.")
    except Exception as error:
        print(
            f"WARNUNG: Motoren konnten nicht automatisch freigegeben werden: "
            f"{error}",
            file=sys.stderr,
        )
        print(
            "Roboter bitte jetzt am Hauptschalter ausschalten.",
            file=sys.stderr,
        )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Expressive Standchoreografie für Lumi "
            "mit Bein- und abwechslungsreichen Kopfbewegungen."
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
        help="Nur Server, Spannung und Servos prüfen.",
    )

    args = parser.parse_args()

    check_system(args.base_url)

    if args.dry_run:
        print("\nTrockenlauf erfolgreich.")
        print("Es wurde keine Bewegung ausgeführt.")
        return

    print("\nSICHERHEITSHINWEISE:")
    print("- Akku muss vollständig geladen sein.")
    print("- Ladekabel vor der Bewegung entfernen.")
    print("- Beide Füße auf eine rutschfeste Fläche stellen.")
    print("- Roboter beim ersten Durchlauf am Oberkörper sichern.")
    print("- Hauptschalter jederzeit erreichbar halten.")
    print("- Bei Zittern, Blockieren oder Geräuschen sofort Ctrl+C drücken.")
    print("- Bei einem Hard Reset sofort den Hauptschalter ausschalten.")

    input("\nRoboter sicher positionieren und Enter drücken ... ")

    calibration_active = False
    head_active = False

    try:
        run_leg_sequence(args.base_url)
        calibration_active = True

        finish_calibration(args.base_url)
        calibration_active = False

        check_voltage_again(args.base_url)

        print("\nÜbergang zur gespeicherten Grundstellung ...")

        # run_head_sequence aktiviert den Head-Puppet-Modus mit seinem
        # ersten API-Aufruf.
        head_active = True
        run_head_sequence(args.base_url)

        print("\nExpressive Choreografie erfolgreich abgeschlossen.")

    finally:
        safe_cleanup(
            args.base_url,
            calibration_active=calibration_active,
            head_active=head_active,
        )

    try:
        voltage_after = request_json(args.base_url, "/api/voltage")

        print(
            "\nSpannung nach der Vorführung:",
            voltage_after.get("volts"),
            "V –",
            voltage_after.get("health"),
        )

    except Exception:
        print(
            "Die Spannung nach der Vorführung konnte nicht gelesen werden."
        )


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("\nVorführung wurde mit Ctrl+C abgebrochen.")
        sys.exit(130)

    except Exception as error:
        print(f"\nABBRUCH: {error}", file=sys.stderr)
        sys.exit(1)
