# Bible Gazetteers Dataset

Structured gazetteers of biblical entities, symbols, and relationships for NLP, semantic search, and computational theology.

Part of the [NEUU](https://github.com/neuu-org) biblical scholarship ecosystem.

## Overview

| Gazetteer | Entries | Namespaces | Description |
|-----------|---------|------------|-------------|
| **Entities** | 2,474 | 9 | People, places, concepts, objects, events |
| **Symbols** | 347 | 7 | Natural elements, objects, actions, colors |
| **Relationships** | 436 | 53 types | Connections between entities |

## Structure

```
bible-gazetteers-dataset/
├── data/
│   └── pt/                         # Portuguese (primary language)
│       ├── entities.json           # 2,474 biblical entities
│       ├── symbols.json            # 347 biblical symbols
│       └── relationships.json      # 436 entity relationships
│   └── (future: en/, es/, etc.)
```

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

Schema per entity:
```json
{
  "canonical_id": "PER:aarao",
  "type": "PERSON",
  "aliases": ["Aarao"],
  "description": "Personagem presente na narrativa biblica.",
  "categories": ["Pessoa"],
  "lang": "pt",
  "status": "ACTIVE",
  "boost": null,
  "priority": null,
  "source_topics": [],
  "metrics": {}
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

Schema per symbol:
```json
{
  "canonical_id": "NAT:agua",
  "type": "NATURAL",
  "aliases": ["chuva", "fontes", "mar", "rio", "agua"],
  "literal_meaning": "H2O, elemento essencial para a vida",
  "symbolic_meaning": ["Purificacao", "Juizo", "Espirito Santo", "Novo nascimento"],
  "associated_concepts": ["batismo", "vida eterna"],
  "bible_examples": [],
  "boost": null,
  "priority": null,
  "status": "PENDING_REVIEW"
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
| EXEMPLIFIED_BY | 25 |
| CHILD_OF | 19 |

Schema per relationship:
```json
{
  "source": "Aarat",
  "target": "Noe",
  "target_type": "PERSON",
  "type": "PART_OF",
  "description": "Aarat e o local onde a arca de Noe repousou apos o diluvio.",
  "source_topic": "aarat"
}
```

## Language

Current data is in **Portuguese (pt)**. The `data/pt/` structure supports future multilingual expansion (`data/en/`, `data/es/`, etc.).

## Provenance

Generated from the [bible-topics-dataset](https://github.com/neuu-org/bible-topics-dataset) via the topical enrichment pipeline (Phase 0 + Phase 3). Entities and symbols were extracted from AI-enriched topic analysis.

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
