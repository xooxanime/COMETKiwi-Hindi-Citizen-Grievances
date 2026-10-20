# Data Directory

## challenge_set.csv

**Rows:** 100 pairs (SYN001_hi to SYN100_hi)
**SHA-256:** ae04ccf209516e531a8cd2badd31e7dece3d2f59ce137053b69edb51ba6538d5
**Encoding:** UTF-8 with BOM (utf-8-sig)

### Columns

| Column | Description |
|---|---|
| `pair_id` | Unique identifier (e.g., SYN001_hi) |
| `scenario_id` | Base scenario |
| `error_category` | One of 10 administrative error categories |
| `source_english` | Original English grievance text |
| `faithful_translation` | Semantically faithful Hindi translation |
| `corrupted_translation` | Hindi translation with an intended meaning error |
| `intended_change` | Description of the error introduced |

See `dataset_card.md` for full documentation.
