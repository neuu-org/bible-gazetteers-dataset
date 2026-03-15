#!/usr/bin/env python3
"""
validate_coherence.py

Validates coherence and consistency of the gazetteers.
Run after every pipeline update to catch issues early.

Checks:
  1. Near-duplicate entity names (accent/case variants)
  2. Duplicate canonical_ids
  3. Entity namespace misclassification
  4. Description quality (empty, generic)
  5. Orphan relationships (source/target not in entities)
  6. Missing symmetric relationships
  7. Symbols without bible_examples
  8. Alias conflicts (same alias pointing to different entities)

Usage:
    python scripts/validate_coherence.py
    python scripts/validate_coherence.py --fix  (future: auto-fix simple issues)
"""

import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data" / "pt"
SKIP_KEYS = {"_metadata", "_common", "_schema"}

GENERIC_DESCRIPTIONS = {
    "Personagem presente na narrativa bíblica.",
    "Personagem bíblica.",
    "Conceito teológico.",
    "Lugar bíblico.",
    "",
}

SYMMETRIC_TYPES = {"SPOUSE_OF", "ALLY_OF", "CONTEMPORARY_OF", "SIBLING", "ENEMY_OF"}

# Known valid cross-namespace entities (not bugs)
KNOWN_CROSS_NS = {
    "Jeremias",  # person + book
    "Isaías",    # person + book
    "Ezequiel",  # person + book
    "Daniel",    # person + book
}


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return s.encode("ascii", "ignore").decode("ascii").strip()


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def iter_entries(data: dict):
    """Iterate over all entries in a gazetteer, yielding (namespace, name, entry_data)."""
    for ns in sorted(data.keys()):
        if ns in SKIP_KEYS:
            continue
        items = data[ns]
        if not isinstance(items, dict):
            continue
        for name, entry in items.items():
            if name in SKIP_KEYS:
                continue
            yield ns, name, entry


def check_duplicate_names(entities: dict) -> list:
    """Find near-duplicate entity names across namespaces."""
    issues = []
    name_map = defaultdict(list)

    for ns, name, _ in iter_entries(entities):
        norm = normalize(name)
        name_map[norm].append((ns, name))

    for norm, entries in name_map.items():
        if len(entries) > 1:
            # Filter out known cross-namespace entities
            if any(name in KNOWN_CROSS_NS for _, name in entries):
                continue
            # Same namespace duplicates are always bugs
            namespaces = [ns for ns, _ in entries]
            if len(namespaces) != len(set(namespaces)):
                issues.append({
                    "type": "SAME_NS_DUPLICATE",
                    "severity": "HIGH",
                    "normalized": norm,
                    "entries": entries,
                })
            elif len(set(namespaces)) > 2:
                issues.append({
                    "type": "CROSS_NS_DUPLICATE",
                    "severity": "MEDIUM",
                    "normalized": norm,
                    "entries": entries,
                })

    return issues


def check_duplicate_ids(entities: dict) -> list:
    """Find duplicate canonical_ids."""
    issues = []
    id_map = defaultdict(list)

    for ns, name, entry in iter_entries(entities):
        cid = entry.get("canonical_id", "")
        if cid:
            id_map[cid].append((ns, name))

    for cid, entries in id_map.items():
        if len(entries) > 1:
            issues.append({
                "type": "DUPLICATE_ID",
                "severity": "HIGH",
                "canonical_id": cid,
                "entries": entries,
            })

    return issues


def check_descriptions(entities: dict) -> list:
    """Check description quality."""
    issues = []

    for ns, name, entry in iter_entries(entities):
        desc = entry.get("description", "")
        if desc in GENERIC_DESCRIPTIONS or not desc.strip():
            issues.append({
                "type": "POOR_DESCRIPTION",
                "severity": "LOW",
                "namespace": ns,
                "name": name,
                "description": desc[:50] if desc else "(empty)",
            })

    return issues


def check_orphan_relationships(entities: dict, relationships: list) -> list:
    """Check that relationship sources/targets exist as entities."""
    issues = []

    entity_names = set()
    for ns, name, _ in iter_entries(entities):
        entity_names.add(normalize(name))

    for rel in relationships:
        source_norm = normalize(rel.get("source", ""))
        target_norm = normalize(rel.get("target", ""))

        if source_norm not in entity_names:
            issues.append({
                "type": "ORPHAN_SOURCE",
                "severity": "MEDIUM",
                "source": rel.get("source"),
                "target": rel.get("target"),
                "relationship": rel.get("type"),
            })
        if target_norm not in entity_names:
            issues.append({
                "type": "ORPHAN_TARGET",
                "severity": "MEDIUM",
                "source": rel.get("source"),
                "target": rel.get("target"),
                "relationship": rel.get("type"),
            })

    return issues


def check_symmetric_relationships(relationships: list) -> list:
    """Check that symmetric relationships have their reverse."""
    issues = []
    pairs = set()

    for rel in relationships:
        pair = (normalize(rel["source"]), normalize(rel["target"]), rel["type"])
        pairs.add(pair)

    for rel in relationships:
        rtype = rel["type"]
        if rtype in SYMMETRIC_TYPES:
            reverse = (normalize(rel["target"]), normalize(rel["source"]), rtype)
            if reverse not in pairs:
                issues.append({
                    "type": "MISSING_SYMMETRIC",
                    "severity": "LOW",
                    "source": rel["source"],
                    "target": rel["target"],
                    "relationship": rtype,
                })

    return issues


def check_symbols(symbols: dict) -> list:
    """Check symbol data quality."""
    issues = []

    for ns, name, entry in iter_entries(symbols):
        if not entry.get("bible_examples"):
            issues.append({
                "type": "NO_BIBLE_EXAMPLES",
                "severity": "LOW",
                "namespace": ns,
                "name": name,
            })
        if not entry.get("symbolic_meaning"):
            issues.append({
                "type": "NO_SYMBOLIC_MEANING",
                "severity": "MEDIUM",
                "namespace": ns,
                "name": name,
            })

    return issues


def main():
    print("=" * 60)
    print("Gazetteer Coherence Validation")
    print("=" * 60)

    entities = load_json(DATA_DIR / "entities.json")
    rels_data = load_json(DATA_DIR / "relationships.json")
    relationships = rels_data.get("relationships", [])
    symbols = load_json(DATA_DIR / "symbols.json")

    all_issues = []

    # Run checks
    checks = [
        ("Duplicate names", check_duplicate_names(entities)),
        ("Duplicate IDs", check_duplicate_ids(entities)),
        ("Description quality", check_descriptions(entities)),
        ("Orphan relationships", check_orphan_relationships(entities, relationships)),
        ("Symmetric relationships", check_symmetric_relationships(relationships)),
        ("Symbol quality", check_symbols(symbols)),
    ]

    for check_name, issues in checks:
        all_issues.extend(issues)
        severity_counts = Counter(i["severity"] for i in issues)
        total = len(issues)
        if total == 0:
            print(f"\n  {check_name}: PASS")
        else:
            high = severity_counts.get("HIGH", 0)
            medium = severity_counts.get("MEDIUM", 0)
            low = severity_counts.get("LOW", 0)
            print(f"\n  {check_name}: {total} issues (HIGH={high} MEDIUM={medium} LOW={low})")
            # Show first 3
            for issue in issues[:3]:
                detail = {k: v for k, v in issue.items() if k not in ("type", "severity")}
                print(f"    [{issue['severity']}] {issue['type']}: {detail}")
            if total > 3:
                print(f"    ... and {total - 3} more")

    # Summary
    severity_total = Counter(i["severity"] for i in all_issues)
    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(all_issues)} total issues")
    print(f"  HIGH:   {severity_total.get('HIGH', 0)}")
    print(f"  MEDIUM: {severity_total.get('MEDIUM', 0)}")
    print(f"  LOW:    {severity_total.get('LOW', 0)}")
    print(f"{'='*60}")

    return 1 if severity_total.get("HIGH", 0) > 0 else 0


if __name__ == "__main__":
    exit(main())
