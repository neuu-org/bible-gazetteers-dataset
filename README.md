# Bible Gazetteers Dataset

Structured gazetteers of biblical entities, symbols, and relationships for NLP, semantic search, and computational theology.

Part of the [NEUU](https://github.com/neuu-org) biblical scholarship ecosystem.

## Overview

| Gazetteer | Entries | Namespaces | Description |
|-----------|---------|------------|-------------|
| **Entities** | 2,474 | 9 | People, places, concepts, objects, events |
| **Symbols** | 347 | 7 | Natural elements, objects, actions, colors |
| **Relationships** | 436 | 53 types | Connections between entities |

All entries are **100% curated** (ACTIVE status) with computed boost and priority metrics.

## Quick Start

For direct consumption, use the **structured** files — clean flat lists sorted by importance:

```python
import json

with open("data/pt/structured/entities.json") as f:
    entities = json.load(f)

# Top 5 most important entities
for e in entities[:5]:
    print(f"{e['name']:20s} boost={e['boost']}  type={e['type']}")

# Output:
# Satanás              boost=4.0   type=ANGEL
# Jerusalém            boost=4.0   type=PLACE
# Cristo               boost=3.96  type=DEITY
# Ezequiel             boost=3.89  type=PERSON
# Isaías               boost=3.8   type=PERSON
```

## Structure

```
bible-gazetteers-dataset/
├── data/
│   └── pt/
│       ├── entities.json              # Raw (pipeline format, nested by namespace)
│       ├── symbols.json               # Raw (pipeline format, nested by namespace)
│       ├── relationships.json         # Raw (with _metadata, by_type index)
│       └── structured/                # Clean flat format for consumption
│           ├── entities.json          # 2,474 entries as flat list (-51% size)
│           ├── symbols.json           # 347 entries as flat list
│           └── relationships.json     # 436 entries as flat list
│   └── (future: en/, es/, etc.)
│
├── scripts/
│   ├── calculate_metrics.py           # Compute boost/priority from topics V3
│   └── structure.py                   # Raw → structured (clean flat format)
│
├── docs/
│   ├── figures/                       # Pipeline and formula diagrams
│   ├── metrics-pipeline.mmd           # Mermaid source
│   └── score-formula.mmd             # Mermaid source
│
├── METHODOLOGY.md                     # Full metrics methodology with diagrams
├── CHANGELOG.md
└── LICENSE
```

### Raw vs Structured

| Aspect | Raw (`data/pt/*.json`) | Structured (`data/pt/structured/*.json`) |
|--------|----------------------|----------------------------------------|
| Format | Nested by namespace `{PERSON: {name: {...}}}` | Flat list `[{name, ...}]` |
| Pipeline fields | Includes source_topics, metrics, status, last_updated | Removed |
| Null values | Present | Removed |
| Size | 2,249 KB | 1,105 KB (-51%) |
| Sort order | By namespace, then alphabetical | By boost (most important first) |
| Use case | Pipeline development, debugging | Direct consumption, NLP, search |

## Entities

2,474 entities organized by namespace:

| Namespace | Count | Examples |
|-----------|-------|----------|
| PERSON | 1,112 | Abraao, Davi, Moises, Paulo, Jesus |
| PLACE | 578 | Jerusalem, Egito, Sinai, Babilonia |
| CONCEPT | 360 | Graca, Fe, Salvacao, Alianca |
| OBJECT | 229 | Arca, Altar, Espada, Coroa |
| EVENT | 122 | Exodo, Pascoa, Pentecostes |
| LITERARY_FORM | 27 | Salmo, Parabola, Profecia |
| DEITY | 16 | Deus, Espirito Santo |
| ANGEL | 15 | Miguel, Gabriel |
| LITERARY_WORK | 15 | Torah, Evangelho |

**Structured schema** (clean):
```json
{
  "name": "Jerusalém",
  "canonical_id": "LOC:jerusalem",
  "type": "PLACE",
  "aliases": ["Cidade de Davi", "Cidade Santa", "Monte Sião", "Nova Jerusalém", "Sião"],
  "description": "Local da crucificação",
  "categories": ["Cidade Santa", "Escatologia", "Lugar"],
  "boost": 4.0,
  "priority": 100
}
```

## Symbols

347 symbols with literal and symbolic meanings:

| Namespace | Count | Examples |
|-----------|-------|----------|
| OBJECT | 208 | Espada, Lampada, Coroa, Vaso |
| NATURAL | 101 | Agua, Fogo, Vento, Luz, Trevas |
| ACTION | 17 | Lavagem, Uncao, Sacrificio |
| PERSON_TYPE | 9 | Pastor, Noiva, Rei, Servo |
| COLOR | 8 | Branco, Vermelho, Purpura |
| NUMBER | 2 | 7, 12, 40 |
| PLACE | 2 | Deserto, Montanha |

**Structured schema** (clean):
```json
{
  "name": "Água",
  "canonical_id": "NAT:agua",
  "type": "NATURAL",
  "aliases": ["chuva", "fontes", "mar", "rio", "água"],
  "literal_meaning": "H2O, elemento essencial para a vida",
  "symbolic_meaning": ["Purificação", "Juízo", "Espírito Santo", "Novo nascimento"],
  "bible_examples": [{"ref": "Mt 4:2", "context": "..."}],
  "boost": 3.85,
  "priority": 95
}
```

## Relationships

436 relationships between entities across 53 types:

| Type | Count |
|------|-------|
| PARENT_OF | 67 |
| LEADER_OF | 50 |
| ENEMY_OF | 41 |
| MEMBER_OF | 37 |
| CONTEMPORARY_OF | 36 |
| ALLY_OF | 28 |
| SPOUSE_OF | 25 |

**Schema:**
```json
{
  "source": "Aarat",
  "target": "Noé",
  "target_type": "PERSON",
  "type": "PART_OF",
  "description": "Aarat é o local onde a arca de Noé repousou após o dilúvio.",
  "source_topic": "aarat"
}
```

## Pipeline

```
bible-topics-dataset (7,873 topics)
        ↓ Phase 0 (AI extraction)
Raw gazetteers (entities + symbols + relationships)
        ↓ calculate_metrics.py
Curated gazetteers (100% ACTIVE with boost/priority)
        ↓ structure.py
Structured gazetteers (clean flat format, -51% size)
```

### Dependencies

| Dependency | Repository | Used for |
|-----------|-----------|----------|
| **Topics V3** | [bible-topics-dataset](https://github.com/neuu-org/bible-topics-dataset) | Source data + metrics calculation |
| **Cross-references** | [bible-crossrefs-dataset](https://github.com/neuu-org/bible-crossrefs-dataset) | Centrality metrics |
| **Bible text** | [bible-text-dataset](https://github.com/neuu-org/bible-text-dataset) | Coverage calculation |

> Full methodology: [METHODOLOGY.md](METHODOLOGY.md)

## Scripts

```bash
# Recalculate boost/priority from topics V3
python scripts/calculate_metrics.py --topics-dir ../bible-topics-dataset/data/01_unified

# Regenerate structured files from raw
python scripts/structure.py
```

## Language

Current data is in **Portuguese (pt)**. The `data/pt/` structure supports future multilingual expansion.

## License

CC BY 4.0

## Citation

```bibtex
@misc{neuu_bible_gazetteers_2026,
  title={Bible Gazetteers Dataset: Entities, Symbols, and Relationships},
  author={NEUU},
  year={2026},
  publisher={GitHub},
  url={https://github.com/neuu-org/bible-gazetteers-dataset}
}
```

## Related Datasets

- [bible-topics-dataset](https://github.com/neuu-org/bible-topics-dataset) — Source: 7,873 topics
- [bible-commentaries-dataset](https://github.com/neuu-org/bible-commentaries-dataset) — 31,218 commentaries
- [bible-crossrefs-dataset](https://github.com/neuu-org/bible-crossrefs-dataset) — 1.1M+ cross-references
- [bible-text-dataset](https://github.com/neuu-org/bible-text-dataset) — 17 Bible translations
- [bible-hybrid-search](https://github.com/neuu-org/bible-hybrid-search) — Hybrid retrieval research
