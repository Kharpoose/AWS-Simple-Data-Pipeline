# Athena

Athena runs SQL queries directly against the JSON files in `processed/` — no database server, no copying data anywhere. It works through a table definition (created manually here, via `CREATE EXTERNAL TABLE`) that maps SQL columns onto the JSON fields and points at the `processed/` S3 location.

The table is named `sensor_data` (underscore), not `sensor-data` — Athena's SQL doesn't allow hyphens in unquoted table names (it would read as subtraction), so the underscore is a naming requirement, not a different table or a different dataset.

## Example query

```sql
SELECT * FROM sensor_data;
```

| deviceid | humidity | processedat | status | temperature | timestamp |
|---|---|---|---|---|---|
| sensor004 | 25.00 | 2026-07-28T07:53:26.751087 | WARNING | 45.00 | 2026-07-28T07:53:26.751073 |
| sensor002 | 75.00 | 2026-07-28T07:49:17.190777 | WARNING | 44.80 | 2026-07-28T07:38:13.565302 |

A couple of things worth noting in this result:
- Column names come back lowercase (`deviceid`, not `deviceId`) — Athena lowercases unquoted identifiers by default.
- `humidity` and `temperature` show two decimal places even for whole numbers like `25` — the column type for these is a decimal/double in the table definition, so Athena displays them consistently regardless of how the original JSON wrote them.

## Query results

Every query run through the console writes its output to `athena-results/` automatically — one file per execution. That's an Athena setting (the query result location), not something the pipeline itself writes to.
