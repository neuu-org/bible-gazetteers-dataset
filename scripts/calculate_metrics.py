#!/usr/bin/env python3
"""
calculate_metrics.py

Calculates boost, priority, and status for entities and symbols
based on structured data from the topics V3 dataset.

Reads gazetteers from data/pt/, uses topics V3 for metric calculation,
updates entries to ACTIVE status with computed metrics.

Usage:
    python scripts/calculate_metrics.py --topics-dir <path_to_topics_v3> --dry-run
    python scripts/calculate_metrics.py --topics-dir <path_to_topics_v3>
    python scripts/calculate_metrics.py --topics-dir <path_to_topics_v3> --entities-only
    python scripts/calculate_metrics.py --topics-dir <path_to_topics_v3> --symbols-only

Example:
    python scripts/calculate_metrics.py \
        --topics-dir ../bible-topics-dataset/data/01_unified
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).parent.parent
ENTITIES_PATH = REPO_ROOT / "data" / "pt" / "entities.json"
SYMBOLS_PATH = REPO_ROOT / "data" / "pt" / "symbols.json"

SKIP_KEYS = {"_metadata", "_common", "_schema"}


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def calculate_entity_metrics(
    entity_name: str, source_topics: List[str], topics_dir: Path
) -> Dict[str, Any]:
    """Calculate importance metrics for an entity using V3 topic data."""
    frequency = len(source_topics)
    books = set()
    centrality = 0
    total_refs = 0
    ref_groups = 0

    for topic_name in source_topics:
        first_letter = topic_name[0].upper() if topic_name else "A"
        topic_file = topics_dir / first_letter / f"{topic_name}.json"
        if not topic_file.exists():
            continue

        try:
            topic = load_json(topic_file)

            for ref in topic.get("biblical_references", []):
                book = ref.get("book")
                if book:
                    books.add(book)

            stats = topic.get("stats", {})
            total_refs += stats.get("ot_refs", 0) + stats.get("nt_refs", 0)
            ref_groups += len(topic.get("reference_groups", []))

            crossrefs = topic.get("cross_reference_network", {})
            if crossrefs:
                centrality += len(crossrefs.get("as_source", []))
                centrality += len(crossrefs.get("as_target", [])) * 0.5

        except Exception:
            continue

    coverage = len(books)
    total_score = (total_refs * 2) + (coverage * 1.5) + ref_groups + (centrality * 0.5)

    return {
        "frequency": frequency,
        "coverage": coverage,
        "centrality": centrality,
        "total_refs": total_refs,
        "ref_group_count": ref_groups,
        "total_score": total_score,
    }


def calculate_symbol_metrics(symbol_data: dict) -> Dict[str, Any]:
    """Calculate importance metrics for a symbol using its own data."""
    examples = symbol_data.get("bible_examples", [])
    meanings = symbol_data.get("symbolic_meaning", [])
    concepts = symbol_data.get("associated_concepts", [])

    books = set()
    for ex in examples:
        if isinstance(ex, dict):
            ref = ex.get("ref", "")
            if ref:
                parts = ref.split()
                book = parts[0] if parts[0] not in ("1", "2", "3") else f"{parts[0]} {parts[1]}" if len(parts) > 1 else parts[0]
                books.add(book)

    frequency = len(examples)
    coverage = len(books)

    return {
        "frequency": frequency,
        "coverage": coverage,
        "meaning_richness": len(meanings),
        "concept_connections": len(concepts),
        "total_score": (frequency * 3) + (coverage * 2) + len(meanings) + (len(concepts) * 0.5),
    }


def process_namespace(
    gazetteer: dict,
    namespace: str,
    topics_dir: Path,
    item_type: str,
    dry_run: bool,
) -> dict:
    """Process all entries in a namespace."""
    items = gazetteer.get(namespace, {})
    if not items:
        return {"processed": 0, "updated": 0}

    real_items = {k: v for k, v in items.items() if k not in SKIP_KEYS}
    if not real_items:
        return {"processed": 0, "updated": 0}

    # Collect metrics
    all_metrics = {}
    for name, data in real_items.items():
        if item_type == "entity":
            m = calculate_entity_metrics(name, data.get("source_topics", []), topics_dir)
        else:
            m = calculate_symbol_metrics(data)
        all_metrics[name] = m

    # Normalize
    max_freq = max((m["frequency"] for m in all_metrics.values()), default=1) or 1
    max_cov = max((m["coverage"] for m in all_metrics.values()), default=1) or 1
    max_score = max((m["total_score"] for m in all_metrics.values()), default=1) or 1

    updated = 0
    for name, metrics in all_metrics.items():
        norm_score = metrics["total_score"] / max_score
        norm_freq = metrics["frequency"] / max_freq
        norm_cov = metrics["coverage"] / max_cov
        combined = (norm_score * 0.5) + (norm_freq * 0.25) + (norm_cov * 0.25)

        boost = round(1.0 + (combined * 3.0), 2)
        priority = min(int(combined * 100), 100)

        if not dry_run:
            entry = items[name]
            entry["boost"] = boost
            entry["priority"] = priority
            entry["status"] = "ACTIVE"
            entry["metrics"] = {
                "frequency": metrics["frequency"],
                "coverage": metrics["coverage"],
                "calculated_at": datetime.now(timezone.utc).isoformat(),
                "total_score": metrics["total_score"],
            }
            if "centrality" in metrics:
                entry["metrics"]["centrality"] = metrics["centrality"]
            if "meaning_richness" in metrics:
                entry["metrics"]["meaning_richness"] = metrics["meaning_richness"]
            entry["last_updated"] = datetime.now(timezone.utc).isoformat()

        updated += 1

    print(f"  {namespace}: {len(real_items)} entries, max_freq={max_freq}, max_cov={max_cov}")

    return {"processed": len(real_items), "updated": updated}


def main():
    parser = argparse.ArgumentParser(description="Calculate gazetteer metrics from topics V3")
    parser.add_argument("--topics-dir", type=Path, required=True, help="Path to topics V3 directory")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--entities-only", action="store_true")
    parser.add_argument("--symbols-only", action="store_true")
    args = parser.parse_args()

    if not args.topics_dir.exists():
        print(f"Topics dir not found: {args.topics_dir}")
        return

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Calculating metrics")
    print(f"Topics: {args.topics_dir}")

    total = {"processed": 0, "updated": 0}

    if not args.symbols_only:
        print(f"\n=== ENTITIES ===")
        entities = load_json(ENTITIES_PATH)
        for ns in sorted(entities.keys()):
            if ns in SKIP_KEYS:
                continue
            stats = process_namespace(entities, ns, args.topics_dir, "entity", args.dry_run)
            total["processed"] += stats["processed"]
            total["updated"] += stats["updated"]

        if not args.dry_run:
            entities["_metadata"]["last_metrics_update"] = datetime.now(timezone.utc).isoformat()
            save_json(ENTITIES_PATH, entities)
            print("  Saved entities.json")

    if not args.entities_only:
        print(f"\n=== SYMBOLS ===")
        symbols = load_json(SYMBOLS_PATH)
        for ns in sorted(symbols.keys()):
            if ns in SKIP_KEYS:
                continue
            stats = process_namespace(symbols, ns, args.topics_dir, "symbol", args.dry_run)
            total["processed"] += stats["processed"]
            total["updated"] += stats["updated"]

        if not args.dry_run:
            symbols["_metadata"]["last_metrics_update"] = datetime.now(timezone.utc).isoformat()
            save_json(SYMBOLS_PATH, symbols)
            print("  Saved symbols.json")

    print(f"\nTotal: {total['processed']} processed, {total['updated']} updated")
    if args.dry_run:
        print("(DRY RUN — nothing saved)")


if __name__ == "__main__":
    main()
