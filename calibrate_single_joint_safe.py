sudo systemctl stop tnkr-robot

python - <<'PY'
import json
import shutil
from pathlib import Path

config_path = Path.home() / "duck_config.json"
offsets_path = Path.home() / "duck_offsets.txt"
backup_path = Path.home() / "duck_config.before_offsets.json"

if not backup_path.exists():
    shutil.copy2(config_path, backup_path)

offsets = {}
for line in offsets_path.read_text().splitlines():
    if not line.strip():
        continue
    name, value = line.split(":", 1)
    offsets[name.strip()] = float(value.strip())

config = json.loads(config_path.read_text())
expected = set(config["joints_offsets"])
received = set(offsets)

if expected != received:
    raise SystemExit(
        f"ABBRUCH\nFehlend: {sorted(expected - received)}\n"
        f"Unbekannt: {sorted(received - expected)}"
    )

config["joints_offsets"] = {
    name: offsets[name] for name in config["joints_offsets"]
}
config["start_paused"] = True

temporary_path = config_path.with_suffix(".json.tmp")
temporary_path.write_text(json.dumps(config, indent=4) + "\n")
temporary_path.replace(config_path)

print("Alle 14 Offsets wurden übernommen.")
print("start_paused wurde auf true gesetzt.")
print("Sicherung:", backup_path)
PY
