#!/usr/bin/env python3
import re
from pathlib import Path


FLAGSTAT = Path("results/ERR16175435/flagstat.txt")
OUT = Path("results/ERR16175435/mapping_status.txt")
THRESHOLD = 90.0


text = FLAGSTAT.read_text(encoding="utf-8")
match = re.search(r"\bmapped\s+\(([0-9]+(?:\.[0-9]+)?)%\s*:", text)

if not match:
    raise SystemExit("mapped percent not found")

percent = float(match.group(1))
status = "OK" if percent > THRESHOLD else "not OK"

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(
    f"flagstat={FLAGSTAT}\n"
    f"mapped_percent={percent:.2f}\n"
    f"threshold={THRESHOLD:.2f}\n"
    f"status={status}\n",
    encoding="utf-8",
)

print(f"mapped_percent={percent:.2f}")
print(f"status={status}")
