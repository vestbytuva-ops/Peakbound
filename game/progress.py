"""Local player profile, mountain records and replay history."""

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from game.replay import validate_frames


SAVE_VERSION = 1
RECENT_RUNS = 5
UPGRADE_KINDS = ("engine", "tank", "grip")
UPGRADE_COSTS = (40, 80, 145, 230, 350)
POST_MODES = ("post", "fjellpost", "delivery", "mail")


@dataclass(frozen=True)
class RunRecord:
    id: str
    world: str
    mode: str
    vehicle: str
    distance: float
    coins: int
    deliveries: int
    seconds: float
    reason: str
    frames: list
    created: str

    @property
    def score(self):
        return int(self.distance) + self.coins * 5


def _valid_text(value, limit):
    return isinstance(value, str) and 0 < len(value) <= limit and value.isprintable()


def _valid_integer(value, limit):
    return type(value) is int and 0 <= value <= limit


def _valid_number(value):
    return type(value) in (int, float) and 0 <= value <= 100_000_000


def _read_record(raw):
    if not isinstance(raw, dict):
        return None
    for field, limit in (("id", 64), ("world", 64), ("mode", 64), ("vehicle", 64),
                         ("reason", 100), ("created", 32)):
        if not _valid_text(raw.get(field), limit):
            return None
    if not _valid_number(raw.get("distance")) or not _valid_number(raw.get("seconds")):
        return None
    if not _valid_integer(raw.get("coins"), 1_000_000_000):
        return None
    if not _valid_integer(raw.get("deliveries"), 1_000_000):
        return None
    frames = validate_frames(raw.get("frames"))
    if frames is None:
        return None
    if frames and frames[-1][0] > raw["seconds"] + 0.001:
        return None
    return RunRecord(
        raw["id"], raw["world"], raw["mode"], raw["vehicle"], raw["distance"],
        raw["coins"], raw["deliveries"], raw["seconds"], raw["reason"],
        frames, raw["created"],
    )


def _ranking(record):
    if record.mode.casefold() in POST_MODES:
        return (record.deliveries, record.distance, record.score)
    return (record.distance, record.score)


def _retain_runs(records):
    """Keep the newest runs and the record holder for each world and mode."""
    groups = {}
    for record in records:
        groups.setdefault((record.world, record.mode), []).append(record)
    kept_ids = set()
    for group in groups.values():
        kept_ids.update(record.id for record in group[:RECENT_RUNS])
        kept_ids.add(max(group, key=_ranking).id)
    return [record for record in records if record.id in kept_ids]


class ProgressStore:
    def __init__(self, path=None):
        default_path = Path(__file__).resolve().parents[1] / "saves" / "saves.json"
        self.path = Path(path) if path is not None else default_path
        self.name = "Spiller"
        self.balance = 0
        self.upgrades = dict.fromkeys(UPGRADE_KINDS, 0)
        self.error = None
        self._runs = []
        self._revision = None
        self._needs_backup = False
        self._blocked = None
        self._load()

    def _read_bytes(self):
        try:
            return self.path.read_bytes()
        except FileNotFoundError:
            return None

    @staticmethod
    def _digest(raw):
        return None if raw is None else hashlib.sha256(raw).digest()

    def _load(self):
        try:
            raw = self._read_bytes()
        except OSError:
            self._blocked = self.error = "Kunne ikke åpne lagringsfilen."
            return
        self._revision = self._digest(raw)
        if raw is None or not raw.strip():
            return
        try:
            data = json.loads(raw)
        except (ValueError, RecursionError):
            self._needs_backup = True
            self.error = "Lagringsfilen er skadet. En kopi beholdes ved neste lagring."
            return
        if not isinstance(data, dict):
            self._needs_backup = True
            self.error = "Lagringsfilen har et ukjent format. En kopi beholdes ved neste lagring."
            return
        version = data.get("version", SAVE_VERSION)
        if type(version) is not int or version != SAVE_VERSION:
            self._blocked = self.error = "Denne lagringsfilen bruker en annen spillversjon."
            return

        name = data.get("name", self.name)
        if _valid_text(name, 24):
            self.name = name
        else:
            self._needs_backup = True
        balance = data.get("balance", self.balance)
        if _valid_integer(balance, 1_000_000_000):
            self.balance = balance
        else:
            self._needs_backup = True
        upgrades = data.get("upgrades", {})
        if isinstance(upgrades, dict):
            for kind in UPGRADE_KINDS:
                level = upgrades.get(kind, 0)
                if _valid_integer(level, len(UPGRADE_COSTS)):
                    self.upgrades[kind] = level
                else:
                    self._needs_backup = True
        else:
            self._needs_backup = True
        records = data.get("runs", [])
        if isinstance(records, list):
            seen = set()
            for entry in records:
                record = _read_record(entry)
                if record is None or record.id in seen:
                    self._needs_backup = True
                    continue
                self._runs.append(record)
                seen.add(record.id)
            self._runs = _retain_runs(self._runs)
        else:
            self._needs_backup = True
        if self._needs_backup:
            self.error = "Ugyldige lagringsdata ble hoppet over. En kopi beholdes ved neste lagring."

    def records(self, world, mode):
        return [record for record in self._runs if record.world == world and record.mode == mode]

    def best(self, world, mode):
        return max(self.records(world, mode), key=_ranking, default=None)

    def upgrade_cost(self, kind):
        level = self.upgrades.get(kind)
        if level is None or level >= len(UPGRADE_COSTS):
            return None
        return UPGRADE_COSTS[level]

    def set_name(self, name):
        if isinstance(name, str):
            name = " ".join(name.split())
        if not _valid_text(name, 24):
            self.error = "Skriv et navn med 1–24 tegn."
            return False
        return self._commit(name, self.balance, self.upgrades, self._runs)

    def buy_upgrade(self, kind):
        cost = self.upgrade_cost(kind)
        if cost is None:
            self.error = "Oppgraderingen er allerede på maks nivå."
            return False
        if self.balance < cost:
            self.error = "Du trenger flere mynter til denne oppgraderingen."
            return False
        upgrades = self.upgrades.copy()
        upgrades[kind] += 1
        return self._commit(self.name, self.balance - cost, upgrades, self._runs)

    def save_run(self, world, mode, vehicle, distance, coins, deliveries, seconds, reason, frames):
        record = _read_record({
            "id": uuid4().hex,
            "world": world, "mode": mode, "vehicle": vehicle,
            "distance": distance, "coins": coins, "deliveries": deliveries,
            "seconds": seconds, "reason": reason, "frames": frames,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        if record is None:
            self.error = "Kunne ikke lagre forsøket. Turdataene er ugyldige."
            return None
        runs = _retain_runs([record, *self._runs])
        balance = min(1_000_000_000, self.balance + record.coins)
        if self._commit(self.name, balance, self.upgrades, runs):
            return record
        return None

    def _commit(self, name, balance, upgrades, records):
        if self._blocked:
            self.error = self._blocked
            return False

        data = {
            "version": SAVE_VERSION,
            "name": name,
            "balance": balance,
            "upgrades": upgrades,
            "runs": [vars(record) for record in records],
        }
        serialized = json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        payload = (serialized + "\n").encode("utf-8")
        temporary = None
        try:
            current = self._read_bytes()
            if self._digest(current) != self._revision:
                self.error = "Lagringsfilen har endret seg. Åpne spillet på nytt før du lagrer."
                return False
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self._needs_backup and current is not None:
                backup = self.path.with_name(f"{self.path.name}.{uuid4().hex[:8]}.bak")
                with backup.open("xb") as file:
                    file.write(current)
                self._needs_backup = False
            with tempfile.NamedTemporaryFile(dir=self.path.parent, prefix=self.path.name + ".",
                                             suffix=".tmp", delete=False) as file:
                temporary = Path(file.name)
                file.write(payload)
                file.flush()
                os.fsync(file.fileno())
            if self._digest(self._read_bytes()) != self._revision:
                self.error = "Lagringsfilen har endret seg. Åpne spillet på nytt før du lagrer."
                return False
            os.replace(temporary, self.path)
        except OSError:
            self.error = "Kunne ikke skrive lagringsfilen."
            return False
        finally:
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass

        self._revision = self._digest(payload)
        self.name = name
        self.balance = balance
        self.upgrades = upgrades
        self._runs = records
        self.error = None
        return True
