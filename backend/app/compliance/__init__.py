"""Compliance modules mapping to Articles 8-15 of Regulation (EU) 2024/1689.

Each module exposes a small, focused surface:
- intended_purpose : Article 8 (binding intended purpose, change-control gate)
- risk_register    : Article 9 (risk-management system)
- data_lineage     : Article 10 (data governance, provenance, bias correction)
- audit_log        : Article 12 (automatic event logging, chained-hash)
- model_card       : Article 13 (transparency to deployers)
- oversight        : Article 14 (human oversight: intervene / override / stop)
- bias_monitor     : Article 15 + Article 72 (accuracy, robustness, monitoring)
- docgen           : Article 11 + Annex IV (technical documentation pack)
"""
