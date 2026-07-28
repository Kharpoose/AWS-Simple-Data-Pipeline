# Architecture

This document explains the overall design of the pipeline and how the services fit together. For service-specific details, see [S3.md](./S3.md), [DynamoDB.md](./DynamoDB.md), and [Athena.md](./Athena.md).

## Design goals

- **Serverless end-to-end** — no servers to patch or scale; Lambda, DynamoDB, and Athena are all fully managed.
- **Fail-safe by default** — invalid input is never silently dropped; it's preserved in `failed/` for later inspection instead.
- **Two query patterns, two stores** — DynamoDB answers "give me this device's readings, fast" (point lookups by `deviceId`); Athena answers "give me insights across everything" (ad-hoc SQL, aggregates). Rather than stretch one store to do both jobs, the pipeline writes to both.

## Data flow contract

- A single bucket holds all pipeline data, split by prefix rather than separate buckets: `incoming/`, `processed/`, `failed/`, `athena-results/`. At this scale, prefixes keep things simple while still separating concerns.
- `processed/` is the pipeline's source of truth for validated data — both DynamoDB and Athena ultimately reflect what's written there.
- Every record that reaches `processed/` and DynamoDB has already passed the same validation and enrichment step in Lambda, so nothing downstream needs to re-validate.

## Security

Lambda's IAM role should follow least privilege: read/write scoped to the specific S3 prefixes it touches (`incoming/`, `processed/`, `failed/`) and to the `sensor-data` DynamoDB table only — not bucket-wide or account-wide access.

*(Exact policy JSON — to be added.)*

## Service details

| Doc | Covers |
|---|---|
| [S3.md](./S3.md) | Bucket layout, what each prefix contains |
| [DynamoDB.md](./DynamoDB.md) | Table schema, key design, example item |
| [Athena.md](./Athena.md) | Table definition, example query |
