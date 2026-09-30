#!/usr/bin/env python3
# Kopfbewegung 
# Code erstellt mit KI

import argparse
import json
import sys
import time
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "http://127.0.0.1:8000"

# Kleine Bewegungsfolge. Es werden keine Beinservos bewegt.
DEMO_SEQUENCE = (
    "head_yaw",
    "head_pitch",
    "neck_pitch",
    "head_roll",
    "head_yaw",
)


def request_json(base_url, path, method="GET", payload=None, timeout=20):
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
    print("\nSchalte alle Motoren ab ...")

    try:
        request_json(
            base_url,
            "/api/stance/release",
            method="POST",
            timeout=15,
        )
        print("Motoren wurden freigegeben.")
    except Exception as error:
        print(
            f"WARNUNG: Automatisches Abschalten fehlgeschlagen: {error}",
            file=sys.stderr,
        )
        print(
            "Bitte den Roboter jetzt am Hauptschalter ausschalten.",
            file=sys.stderr,
        )


def main():
    parser = argparse.ArgumentParser(
        description="Stromsparende Kopfbewegungs-Demo für Lumi."
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Adresse des lokalen TNKR-Servers.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Nur System, Spannung und Motoren prüfen.",
    )
    args = parser.parse_args()

    print("Prüfe TNKR-Server ...")
    health = request_json(args.base_url, "/api/health")

    if health.get("status") != "ok":
        raise RuntimeError(f"Serverstatus ist nicht OK: {health}")

    if health.get("walking"):
        raise RuntimeError("Die Laufsteuerung ist bereits aktiv.")

    voltage = request_json(args.base_url, "/api/voltage")
    volts = voltage.get("volts")
    voltage_health = voltage.get("health")

    print(f"Akkuspannung: {volts} V")
    print(f"Spannungsstatus: {voltage_health}")

    if voltage_health != "ok":
        raise RuntimeError(
            "Die Akkuspannung ist nicht im grünen Bereich. "
            "Roboter zuerst ausschalten und laden."
        )

    print("Prüfe alle Servos ...")
    motor_check = request_json(
        args.base_url,
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

    if args.dry_run:
        print("Trockenlauf erfolgreich. Es wurde keine Bewegung ausgeführt.")
        return

    print()
    print("SICHERHEIT:")
    print("- Beide Füße müssen vollständig auf einer rutschfesten Fläche stehen.")
    print("- Den Oberkörper zunächst mit der Hand oder einer Halterung sichern.")
    print("- Den Hauptschalter jederzeit erreichbar halten.")
    print("- Das Ladekabel darf während des Tests nicht angeschlossen sein.")
    print("- Bei Zittern, Geräuschen oder Spannungsausfall sofort ausschalten.")
    print()

    input("Roboter sicher positionieren und Enter drücken ... ")

    try:
        print("Aktiviere reduzierte Haltekraft an der aktuellen Position ...")
        request_json(
            args.base_url,
            "/api/calibration/start",
            method="POST",
        )

        time.sleep(1.0)

        print("Der Roboter hält jetzt seine aktuelle Position.")
        print("Stütze nur vorsichtig lockern; noch nicht vollständig loslassen.")
        time.sleep(2.0)

        for joint_name in DEMO_SEQUENCE:
            print(f"Kleine Bewegung: {joint_name}")

            request_json(
                args.base_url,
                "/api/calibration/wiggle",
                method="POST",
                payload={"jointName": joint_name},
            )

            time.sleep(0.4)

        print("Bewegungsfolge abgeschlossen.")

    finally:
        release_motors(args.base_url)

    try:
        voltage_after = request_json(args.base_url, "/api/voltage")
        print(
            "Spannung nach dem Test:",
            voltage_after.get("volts"),
            "V –",
            voltage_after.get("health"),
        )
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAbbruch durch Benutzer.")
        sys.exit(130)
    except Exception as error:
        print(f"\nABBRUCH: {error}", file=sys.stderr)
        sys.exit(1)
