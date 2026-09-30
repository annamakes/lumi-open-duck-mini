#!/usr/bin/env python3
"""Kontrolliert die zentrale Python-Umgebung des Lumi-Roboters.

Das Skript prüft, ob die für die Open-Duck-Mini-Runtime benötigten
Python-Module importiert werden können. Es greift nicht auf Motoren
oder andere Hardware zu.
"""

import importlib
import importlib.metadata
import os
import sys


DEPENDENCIES = {
    "mini_bdx_runtime": "mini-bdx-runtime",
    "rustypot": "rustypot",
    "onnxruntime": "onnxruntime",
    "numpy": "numpy",
    "scipy": "scipy",
}


def get_version(distribution_name):
    try:
        return importlib.metadata.version(distribution_name)
    except importlib.metadata.PackageNotFoundError:
        return "keine Paketversion gefunden"


def main():
    print("Python-Umgebungsprüfung für Lumi")
    print("=" * 40)
    print(f"Python-Version: {sys.version.split()[0]}")
    print(f"Python-Pfad:    {sys.executable}")
    print(f"Virtuelle Umgebung: {os.environ.get('VIRTUAL_ENV', 'nicht aktiv')}")
    print()

    failed = False

    for module_name, distribution_name in DEPENDENCIES.items():
        try:
            importlib.import_module(module_name)
            version = get_version(distribution_name)
            print(f"OK       {module_name}: {version}")
        except Exception as error:
            failed = True
            print(f"FEHLER   {module_name}: {error}")

    print()

    if failed:
        print("Ergebnis: Die Python-Umgebung ist unvollständig.")
        return 1

    print("Ergebnis: Alle zentralen Module sind verfügbar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
