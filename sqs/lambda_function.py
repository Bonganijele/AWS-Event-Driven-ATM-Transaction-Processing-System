import json
import boto3
import os

sns = boto3.client("sns")

TOPIC_ARN = os.environ["TOPIC_ARN"]


def lambda_handler(event, context):

    for record in event["Records"]:

        transaction = json.loads(record["body"])

        print("Processing:", transaction)

        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps({
                "status":"COMPLETED",
                "transaction":transaction
            })
        )

    return {
        "statusCode":200
    }
