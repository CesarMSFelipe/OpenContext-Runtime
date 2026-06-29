# Design — authentication API

Add an `oauth2` provider module behind the existing provider gateway, a `sessions`
table migration, and a redaction-aware audit receipt. The schema migration ships with
a reversible down-migration to satisfy the rollback requirement.
