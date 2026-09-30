#!/usr/bin/env python3

"""
Lumi – expressive Standchoreografie

Die ungefähr 15 bis 20 Sekunden lange Vorführung kombiniert:

1. kleine Bewegungen von Hüfte und Knien,
2. eine kurze Erholungspause,
3. den Übergang in die gespeicherte Grundstellung,
4. einen langen Blick nach links,
5. eine Pause in der Mitte,
6. einen kurzen Blick nach rechts,
7. eine freundliche Kopfneigung,
8. ein kurzes Nicken.

Die Bewegungen erfolgen überwiegend nacheinander, damit nicht zu viele
Servomotoren gleichzeitig beschleunigen und eine große Stromspitze erzeugen.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "http://127.0.0.1:8000"

# Tatsächliche neutrale Kopfposition im Head-Puppet-Koordinatensystem.
#
# pitch=0 und neckPitch=0 entsprechen aufgrund der asymmetrischen
# Bewegungsbereiche nicht der anatomischen Nullstellung des Kopfes.
NEUTRAL_YAW = 0.0
NEUTRAL_ROLL = 0.0
NEUTRAL_PITCH = 0.143
NEUTRAL_NECK_PITCH = -0.5

# Kleine Beinbewegungen über die strombegrenzte Wiggle-Funktion.
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
    """Prüft Server, Akkuspannung und alle 14 Servos."""

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
    """Prüft die Spannung nach der Erholungspause erneut."""

    voltage = request_json(base_url, "/api/voltage")

    print(
        f"Zwischenprüfung: {voltage.get('volts')} V, "
        f"Status {voltage.get('health')}"
    )

    if voltage.get("health") != "ok":
        raise RuntimeError(
            "Die Spannung ist weiterhin zu niedrig. "
            "Der belastendere Kopfabschnitt wird nicht gestartet."
        )


def move_head(base_url, pause=0.0, **axes):
    """
    Bewegt den Kopf über den Head-Puppet-Modus.

    Gültige Achsen:
    yaw, pitch, roll und neckPitch

    Die Achsenwerte liegen zwischen -1.0 und 1.0.
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

    time.sleep(0.8)

    for joint_name, description in LEG_SEQUENCE:
        print(f"- {description}")

        post(
            base_url,
            "/api/calibration/wiggle",
            payload={"jointName": joint_name},
        )

        time.sleep(0.15)

    print("Beinbewegungen abgeschlossen.")


def finish_calibration(base_url):
    """
    Beendet den Kalibrierungs-Haltemodus.

    Dadurch werden die vorübergehend genullten Offsets aus dem
    Arbeitsspeicher verworfen. Beim nächsten Zugriff lädt der Server
    die gespeicherten Offsets erneut aus der Konfiguration.
    """

    result = post(base_url, "/api/calibration/finish")

    failed = result.get("failed", [])

    if failed:
        raise RuntimeError(
            "Folgende Servos konnten beim Beenden nicht aktiviert werden: "
            + ", ".join(failed)
        )


def run_head_sequence(base_url):
    """Führt eine abwechslungsreiche Interaktionsbewegung des Kopfes aus."""

    print("\nAbschnitt 2: interaktive Kopfbewegung")
    print("Der Roboter nimmt jetzt seine gespeicherte Grundstellung ein.")

    # Head-Puppet-Modus aktivieren und dabei die tatsächliche neutrale
    # Kopfposition verwenden.
    move_head(
        base_url,
        pause=1.0,
        yaw=NEUTRAL_YAW,
        pitch=NEUTRAL_PITCH,
        roll=NEUTRAL_ROLL,
        neckPitch=NEUTRAL_NECK_PITCH,
    )

    print("- Lumi schaut langsam und deutlich nach links")

    # Große und etwas länger gehaltene Bewegung nach links.
    move_head(
        base_url,
        pause=1.6,
        yaw=-0.75,
    )

    print("- Lumi schaut wieder geradeaus")

    move_head(
        base_url,
        pause=0.6,
        yaw=NEUTRAL_YAW,
    )

    # Bewusste Denk- beziehungsweise Beobachtungspause.
    print("- Lumi beobachtet kurz die Mitte")
    time.sleep(0.6)

    print("- Lumi schaut kurz nach rechts")

    # Die rechte Bewegung ist kleiner und kürzer als die linke Bewegung.
    move_head(
        base_url,
        pause=0.5,
        yaw=0.45,
    )

    print("- Lumi kehrt zur Mitte zurück")

    move_head(
        base_url,
        pause=0.6,
        yaw=NEUTRAL_YAW,
    )

    print("- Lumi legt den Kopf kurz interessiert zur Seite")

    move_head(
        base_url,
        pause=0.6,
        roll=-0.35,
    )

    move_head(
        base_url,
        pause=0.4,
        roll=NEUTRAL_ROLL,
    )

    print("- Lumi nickt einmal kurz")

    # Kleine Nickbewegung nach unten.
    move_head(
        base_url,
        pause=0.35,
        pitch=-0.05,
    )

    # Kleine Gegenbewegung nach oben.
    move_head(
        base_url,
        pause=0.35,
        pitch=0.28,
    )

    print("- Lumi richtet den Kopf wieder neutral aus")

    move_head(
        base_url,
        pause=0.7,
        yaw=NEUTRAL_YAW,
        pitch=NEUTRAL_PITCH,
        roll=NEUTRAL_ROLL,
        neckPitch=NEUTRAL_NECK_PITCH,
    )

    print("Interaktive Kopfbewegung abgeschlossen.")


def safe_cleanup(base_url, calibration_active, head_active):
    """Beendet die Vorführung und gibt alle Servos sicher frei."""

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

    motors_released = False

    try:
        # Zuerst wird das Drehmoment abgeschaltet. Dadurch kann das
        # nachfolgende Zurücksetzen des Head-Puppet-Modus keine sichtbare
        # Kopfbewegung mehr auslösen.
        post(base_url, "/api/stance/release")
        motors_released = True
        print("Alle Motoren wurden freigegeben.")

    except Exception as error:
        print(
            "WARNUNG: Motoren konnten nicht automatisch freigegeben werden: "
            f"{error}",
            file=sys.stderr,
        )

    if head_active:
        try:
            post(base_url, "/api/head/puppet/stop")

            if motors_released:
                print("Kopfsteuerung wurde ohne weitere Bewegung beendet.")
            else:
                print("Kopfsteuerung wurde beendet.")

        except Exception as error:
            print(
                f"WARNUNG beim Beenden der Kopfsteuerung: {error}",
                file=sys.stderr,
            )

    if not motors_released:
        print(
            "Roboter bitte jetzt am Hauptschalter ausschalten.",
            file=sys.stderr,
        )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Expressive Standchoreografie für Lumi mit kleinen Bein- "
            "und abwechslungsreichen Kopfbewegungen."
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
    print("- Während der Erholungspause wird der Roboter frei.")
    print("- Hauptschalter jederzeit erreichbar halten.")
    print("- Bei Zittern oder Blockieren sofort Ctrl+C drücken.")
    print("- Bei einem Hard Reset sofort den Hauptschalter ausschalten.")

    input("\nRoboter sicher positionieren und Enter drücken ... ")

    calibration_active = False
    head_active = False

    try:
        # Bereits vor dem Aufruf setzen, damit bei einem Fehler innerhalb
        # der Beinfolge trotzdem eine sichere Bereinigung versucht wird.
        calibration_active = True
        run_leg_sequence(args.base_url)

        finish_calibration(args.base_url)
        calibration_active = False

        # Stromversorgung zwischen den beiden Abschnitten entlasten.
        print("\nKurze Erholungspause für Akku und Stromversorgung ...")

        post(args.base_url, "/api/stance/release")

        print("Roboter jetzt unbedingt am Oberkörper festhalten.")
        time.sleep(3.0)

        check_voltage_again(args.base_url)

        print("\nÜbergang zur gespeicherten Grundstellung ...")

        # Vor dem Aufruf setzen, damit auch ein Fehler beim Aktivieren
        # des Head-Puppet-Modus korrekt aufgeräumt wird.
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
