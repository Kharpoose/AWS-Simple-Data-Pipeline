# DynamoDB

A single table, `sensor-data`, storing every valid sensor reading as its own item. Nothing is ever overwritten, so the table works as an append-only log of readings.

## Key schema

| Key | Attribute | Type |
|---|---|---|
| Partition key | `deviceId` | String |
| Sort key | `timestamp` | String |

This is a natural fit for time-series device data: every reading from the same device shares a partition, ordered by `timestamp`. That means you can efficiently pull "everything sensor004 has reported, most recent first" without scanning the whole table — and since the sort key is the timestamp, two readings from the same device essentially never collide (they'd need the exact same timestamp to overwrite one another).

## Attributes

| Attribute | Type | Notes |
|---|---|---|
| `deviceId` | String | Partition key |
| `timestamp` | String | Sort key; ISO 8601 |
| `temperature` | Number | |
| `humidity` | Number | |
| `status` | String | `NORMAL` / `WARNING` / `CRITICAL`, computed by Lambda |
| `processedAt` | String | ISO 8601, when Lambda wrote the item |

## Example item

Raw DynamoDB format (as returned by the low-level API):

```json
{
  "deviceId": {"S": "sensor004"},
  "timestamp": {"S": "2026-07-28T07:53:26.751073"},
  "humidity": {"N": "25"},
  "processedAt": {"S": "2026-07-28T07:53:26.751087"},
  "status": {"S": "WARNING"},
  "temperature": {"N": "45"}
}
```

`S` and `N` are DynamoDB's own type markers (String, Number). The console's item view shows the same data without these wrappers — they only show up in the raw JSON / low-level SDK format.
