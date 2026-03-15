#!/usr/bin/env python3
"""
structure.py

Converts raw gazetteers (nested by namespace, with pipeline metadata)
into clean, flat structured files ready for consumption.

Reads from data/pt/ (raw), writes to data/pt/structured/.

Changes:
  - Converts nested {NAMESPACE: {name: {fields}}} to flat list [{fields}]
  - Removes pipeline-internal fields (source_topics, metrics, status, last_updated)
  - Adds 'name' field from the dict key
  - Sorts by boost (descending) for easy consumption

Usage:
    python scripts/structure.py
    python scripts/structure.py --dry-run
"""

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
RAW_DIR = REPO_ROOT / "data" / "pt"
OUT_DIR = REPO_ROOT / "data" / "pt" / "structured"

SKIP_KEYS = {"_metadata", "_common", "_schema"}

# Fields to REMOVE from entities (pipeline internals)
ENTITY_REMOVE = {
    "source_topics",
    "metrics",
    "status",
    "last_updated",
    "lang",
    "reference",
    "references",
    "subtype",
}

# Fields to REMOVE from symbols
SYMBOL_REMOVE = {
    "source_topics",
    "metrics",
    "status",
    "last_updated",
    "lang",
    "source",
}


def structure_entities(raw_path: Path, out_path: Path, dry_run: bool):
    with open(raw_path, encoding="utf-8") as f:
        data = json.load(f)

    entries = []
    for ns in sorted(data.keys()):
        if ns in SKIP_KEYS:
            continue
        items = data[ns]
        if not isinstance(items, dict):
            continue
        for name, fields in sorted(items.items()):
            if name in SKIP_KEYS:
                continue

            entry = {"name": name}
            for k, v in fields.items():
                if k in ENTITY_REMOVE:
                    continue
                # Skip null/empty values
                if v is None or v == [] or v == {} or v == "":
                    continue
                entry[k] = v
            entries.append(entry)

    # Sort by boost descending
    entries.sort(key=lambda x: x.get("boost", 0), reverse=True)

    print(f"  Entities: {len(entries)} entries")

    if not dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)


def structure_symbols(raw_path: Path, out_path: Path, dry_run: bool):
    with open(raw_path, encoding="utf-8") as f:
        data = json.load(f)

    entries = []
    for ns in sorted(data.keys()):
        if ns in SKIP_KEYS:
            continue
        items = data[ns]
        if not isinstance(items, dict):
            continue
        for name, fields in sorted(items.items()):
            if name in SKIP_KEYS:
                continue

            entry = {"name": name}
            for k, v in fields.items():
                if k in SYMBOL_REMOVE:
                    continue
                if v is None or v == [] or v == {} or v == "":
                    continue
                entry[k] = v
            entries.append(entry)

    entries.sort(key=lambda x: x.get("boost", 0), reverse=True)

    print(f"  Symbols: {len(entries)} entries")

    if not dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)


def structure_relationships(raw_path: Path, out_path: Path, dry_run: bool):
    with open(raw_path, encoding="utf-8") as f:
        data = json.load(f)

    rels = data.get("relationships", [])

    # Already a clean list, just copy without _metadata/_schema
    print(f"  Relationships: {len(rels)} entries")

    if not dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(rels, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Structure gazetteers for clean consumption")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Structuring gazetteers -> {OUT_DIR}")

    structure_entities(RAW_DIR / "entities.json", OUT_DIR / "entities.json", args.dry_run)
    structure_symbols(RAW_DIR / "symbols.json", OUT_DIR / "symbols.json", args.dry_run)
    structure_relationships(RAW_DIR / "relationships.json", OUT_DIR / "relationships.json", args.dry_run)

    if args.dry_run:
        print("\n(DRY RUN — nothing saved)")
    else:
        print(f"\nStructured files saved to {OUT_DIR}/")


if __name__ == "__main__":
    main()
