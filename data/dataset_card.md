# Dataset Card: Hindi Citizen Grievance Challenge Set

## Summary

A **synthetic, category-balanced** challenge set of 100 English-Hindi translation pairs
designed to evaluate reference-free QE metric sensitivity to localized administrative
meaning errors in citizen grievance text.

**This dataset is synthetic. It does not represent real citizens or real grievances.**

## Intended Use

- Evaluating QE models for sensitivity to specific semantic error types.
- Benchmarking contrastive pairs in administrative NLP research.

## Out-of-Scope Use

- Real-world administrative decisions.
- Claiming that patterns establish real-world COMETKiwi production reliability.
- Generating misleading translations of real government documents.

## Error Categories

| Category | Description |
|---|---|
| negation_service_status | Inversion of service/repair/inspection status |
| date | Alteration of calendar dates or statutory deadlines |
| duration | Modification of delay or waiting period durations |
| amount | Numerical alteration or role reversal of monetary figures |
| location | Substitution of administrative localities |
| location_detail | Transposition of unit numbers, clinic rooms, pole IDs |
| requested_action | Inversion of citizen-requested actions |
| department_routing_correctness | Swapping civic departments |
| time_reference | Shift in diurnal or chronological timing |
| urgency | Inversion of urgency directives |

## Validation Status

- Structural: COMPLETE (100 pairs, 10x10, no nulls)
- Independent bilingual human validation: NOT PERFORMED

## License

CC-BY-4.0
