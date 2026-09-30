#!/usr/bin/env python3
"""Prüft alle Zielpositionen vor dem Aktivieren der Servos.

Das Skript liest die Ausgangspositionen und die aktuelle Konfiguration
vom lokalen TNKR-Server. Es bewegt keine Motoren.
"""

import json
import sys
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8000"


def request_json(path, method="GET"):
    request = urllib.request.Request(
        BASE_URL + path,
        method=method,
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def main():
    try:
        stance = request_json("/api/stance/start", method="POST")
        config = request_json("/api/config")
    except urllib.error.URLError as error:
        print(f"TNKR-Server nicht erreichbar: {error}", file=sys.stderr)
        return 1

    limit = float(stance["servoRange"])
    offsets = config["joints_offsets"]
    signs = config["joints_signs"]

    unsafe = False

    print(f"Erlaubter Bereich: ±{limit:.2f} rad\n")

    for name in stance["joints"]:
        initial_position = float(stance["initPos"][name])
        offset = float(offsets[name])
        sign = float(signs[name])

        target = sign * initial_position + offset
        margin = limit - abs(target)

        status = "OK" if margin >= 0 else "AUSSERHALB"
        unsafe |= margin < 0

        print(
            f"{name:20s} "
            f"Ziel={target: .4f}  "
            f"Reserve={margin: .4f}  "
            f"{status}"
        )

    if unsafe:
        print("\nErgebnis: NICHT AKTIVIEREN")
        return 1

    print("\nErgebnis: Alle Zielpositionen liegen im erlaubten Bereich.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
