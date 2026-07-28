import json
import boto3

from decimal import Decimal
from datetime import datetime
from urllib.parse import unquote_plus


s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

table = dynamodb.Table("sensor-data")


def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def process_record(bucket, key):

    print(f"Processing {key}")

    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")

    data = json.loads(content, parse_float=Decimal)

    if "deviceId" not in data:
        raise Exception("deviceId is missing")

    if "temperature" not in data:
        raise Exception("temperature is missing")

    if "humidity" not in data:
        raise Exception("humidity is missing")

    temperature = data["temperature"]
    humidity = data["humidity"]

    if temperature < Decimal("-40") or temperature > Decimal("150"):
        raise Exception("Invalid temperature")

    if humidity < Decimal("0") or humidity > Decimal("100"):
        raise Exception("Invalid humidity")

    if "timestamp" not in data:
        data["timestamp"] = datetime.utcnow().isoformat()

    if temperature < Decimal("30"):
        data["status"] = "NORMAL"
    elif temperature < Decimal("50"):
        data["status"] = "WARNING"
    else:
        data["status"] = "CRITICAL"

    data["processedAt"] = datetime.utcnow().isoformat()

    table.put_item(Item=data)

    processed_key = key.replace("incoming/", "processed/")

    s3.put_object(
        Bucket=bucket,
        Key=processed_key,
        Body=json.dumps(data, default=decimal_to_float),
        ContentType="application/json"
    )

    return data["deviceId"]


def lambda_handler(event, context):

    results = []

    for record in event["Records"]:

        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])

        try:
            device_id = process_record(bucket, key)
            results.append({"deviceId": device_id, "status": "success"})

        except Exception as e:

            print(f"Error processing {key}: {str(e)}")

            failed_key = key.replace("incoming/", "failed/")

            s3.put_object(
                Bucket=bucket,
                Key=failed_key,
                Body=s3.get_object(Bucket=bucket, Key=key)["Body"].read(),
                ContentType="application/json"
            )

            results.append({"key": key, "status": "failed", "error": str(e)})

    return {
        "statusCode": 200,
        "body": json.dumps({"results": results})
    }
