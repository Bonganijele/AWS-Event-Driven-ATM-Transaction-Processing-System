
import json
import boto3
import os

sqs = boto3.client("sqs")

QUEUE_URL = os.environ["QUEUE_URL"]


def lambda_handler(event, context):

    body = json.loads(event["body"])

    transaction = {
        "accountId": body["accountId"],
        "amount": body["amount"],
        "transactionType": body["transactionType"]
    }

    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(transaction)
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Transaction received"
        })
    }
