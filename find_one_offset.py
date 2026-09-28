
""" find_one_offset.py

Test- und Kalibrierungswerkzeug für einen einzelnen Servomotor
des Lumi Open Duck Mini.

Dieses Skript entstand während der Fehlersuche, da einige Servomotoren
zu stark reagierten, sich in eine unerwartete Richtung bewegten oder
nicht korrekt in ihrer vorgesehenen Ausgangsposition standen.

Mit dem Skript kann ein einzelnes Gelenk ausgewählt werden. Zunächst
werden alle Motoren deaktiviert, sodass das ausgewählte Gelenk von Hand
in seine mechanische Nullposition gebracht werden kann. Anschließend
wird die aktuelle Position ausgelesen. Optional kann diese Position mit
geringer Haltekraft überprüft werden.

Der Test dient insbesondere zur Kontrolle von:

- Servo-ID und Gelenkzuordnung
- mechanischer Nullposition
- gemessener Positionsabweichung
- grundsätzlicher mechanischer Ausrichtung des Servos

Die Gelenknamen und Servo-IDs orientieren sich an der Hardwarestruktur
des Open Duck Mini. Das Skript ist eine eigene, für die Fehlersuche
entwickelte Implementierung und keine Kopie des offiziellen
find_soft_offsets.py-Skripts.

Open Duck Mini Runtime:
https://github.com/apirrone/Open_Duck_Mini_Runtime

Hinweis:
Der ausgegebene Wert wird nicht automatisch gespeichert. Vor der
Übernahme in eine Konfigurationsdatei muss geprüft werden, ob er dem
erwarteten Offset-Format der verwendeten Software entspricht.

Die Tests dürfen nur durchgeführt werden, wenn der Roboter sicher
aufgestellt ist und sich die Gelenke frei bewegen können.
"""

import argparse
import math
import time

import rustypot


JOINTS = {
    "left_hip_yaw": 20,
    "left_hip_roll": 21,
    "left_hip_pitch": 22,
    "left_knee": 23,
    "left_ankle": 24,
    "neck_pitch": 30,
    "head_pitch": 31,
    "head_yaw": 32,
    "head_roll": 33,
    "right_hip_yaw": 10,
    "right_hip_roll": 11,
    "right_hip_pitch": 12,
    "right_knee": 13,
    "right_ankle": 14,
}


parser = argparse.ArgumentParser(
    description="Ermittelt den mechanischen Nullpunkt eines einzelnen Servos."
)

parser.add_argument(
    "--joint",
    required=True,
    choices=sorted(JOINTS.keys()),
    help="Name des zu kalibrierenden Gelenks.",
)

parser.add_argument(
    "--port",
    default="/dev/ttyACM0",
    help="Serieller Anschluss des Servo-Controllers.",
)

args = parser.parse_args()

motor_id = JOINTS[args.joint]
all_ids = list(JOINTS.values())

io = rustypot.feetech(args.port, 1_000_000)


try:
    # Zu Beginn müssen alle Motoren frei sein.
    io.disable_torque(all_ids)

    print()
    print(f"Gelenk: {args.joint}, ID {motor_id}")
    print("Alle Motoren sind ausgeschaltet.")
    print()

    input(
        "Gelenk von Hand in die gewünschte mechanische "
        "Nullstellung bewegen und Enter drücken ..."
    )

    offset = io.read_present_position([motor_id])[0]

    # Mehrumdrehungswerte dürfen nicht zurückgeschrieben werden.
    if abs(offset) > math.pi + 0.05:
        print()
        print(
            f"ABBRUCH: Position {offset:.4f} rad liegt außerhalb "
            "einer einzelnen Umdrehung."
        )
        print(
            "Diesen Wert nicht speichern und nicht an den Servo senden."
        )
        print(
            "Die Servoversorgung vollständig ausschalten, mindestens "
            "zehn Sekunden warten und danach erneut messen."
        )
        raise SystemExit(1)

    print()
    print(f"OFFSET FÜR {args.joint}: {offset:.4f} rad")
    print("Dieser Wert wurde noch nicht gespeichert.")

    answer = input(
        "Position mit geringer Haltekraft prüfen? (j/y/n): "
    ).strip().lower()

    if answer in ("j", "y"):
        print("Aktiviere ausschließlich den gewählten Servo ...")

        io.set_kps([motor_id], [2])
        io.enable_torque([motor_id])
        io.write_goal_position([motor_id], [offset])

        time.sleep(2)

        actual = io.read_present_position([motor_id])[0]
        error = actual - offset

        print(f"Zielposition:            {offset:.4f} rad")
        print(f"Gemessene Halteposition: {actual:.4f} rad")
        print(f"Abweichung:              {error:.4f} rad")

        if abs(error) > 0.1:
            print(
                "WARNUNG: Die Abweichung ist ungewöhnlich groß. "
                "Offset nicht speichern."
            )

        input(
            "Mechanische Position kontrollieren und Enter "
            "zum Abschalten drücken ..."
        )

    else:
        print("Prüfung wurde übersprungen.")


finally:
    try:
        io.disable_torque(all_ids)
        print()
        print("Alle Motoren wurden abgeschaltet.")
    except Exception as error:
        print()
        print(f"Warnung beim Abschalten der Motoren: {error}")
