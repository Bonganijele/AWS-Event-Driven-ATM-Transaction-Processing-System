# Technical Report: AWS Event-Driven ATM Transaction Processing System

## 1. Project Overview

This project implements a simplified banking transaction processing system using AWS serverless and messaging services.

The objective was to design an event-driven architecture where an ATM transaction request is received, processed asynchronously, and distributed to downstream systems using AWS managed services.

The architecture demonstrates common patterns used in financial systems:

* API-based transaction submission
* Asynchronous processing
* Message queuing
* Event publishing
* Identity and access management

---

# 2. System Architecture

The implemented architecture:

```
ATM Client
    |
    |
    v
API Gateway
    |
    |
    v
Lambda Producer
    |
    |
    v
Amazon SQS Queue
    |
    |
    v
Lambda Worker
    |
    |
    v
Amazon SNS Topic
    |
    |
    v
Notification Subscribers
```

---

# 3. AWS Services Used

## 3.1 Amazon API Gateway

Purpose:

API Gateway acts as the entry point for ATM transaction requests.

Responsibilities:

* Receives HTTP requests
* Provides an API endpoint
* Invokes the Lambda producer function

Created endpoint:

```
POST /withdraw
```

Example request:

```json
{
  "accountId": "100000001",
  "amount": 500,
  "transactionType": "WITHDRAWAL"
}
```

---

## 3.2 AWS Lambda Producer

Function:

```
ATMTransactionProducer
```

Purpose:

The producer Lambda receives transaction requests from API Gateway and places them into an SQS queue.

Responsibilities:

* Parse incoming JSON request
* Validate transaction information
* Create transaction message
* Send message to SQS

Example message:

```json
{
  "accountId": "100000001",
  "amount": 500,
  "transactionType": "WITHDRAWAL"
}
```

Response:

```json
{
  "message": "Transaction received"
}
```

---

## 3.3 Amazon SQS Queue

Queue:

```
ATMTransactionQueue
```

Purpose:

SQS provides asynchronous communication between transaction submission and transaction processing.

Benefits:

* Prevents system overload
* Allows independent scaling
* Provides reliable message delivery
* Decouples services

The producer does not wait for transaction completion. It only confirms that the transaction was successfully queued.

---

## 3.4 AWS Lambda Worker

Function:

```
ATMTransactionWorker
```

Purpose:

The worker consumes messages from SQS and processes completed transactions.

Responsibilities:

* Receive messages from SQS
* Process transaction events
* Publish transaction completion events to SNS

Processing example:

```
Transaction received
        |
        |
Validation
        |
        |
Completed Event
```

---

## 3.5 Amazon SNS

Topic:

```
ATMTransactionTopic
```

Purpose:

SNS provides a publish/subscribe communication model.

The worker publishes completed transaction events to SNS.

Subscribers can include:

* Email notifications
* SMS systems
* Audit systems
* Other banking services

Example event:

```json
{
  "status": "COMPLETED",
  "transaction": {
    "accountId": "100000001",
    "amount": 500,
    "transactionType": "WITHDRAWAL"
  }
}
```

---

# 4. IAM Security Configuration

AWS Identity and Access Management (IAM) was used to control service permissions.

## Producer Lambda Role

The producer Lambda required permission:

```
sqs:SendMessage
```

Purpose:

Allows Lambda to send transaction messages to the SQS queue.

Permission flow:

```
Lambda
 |
IAM Role
 |
IAM Policy
 |
SQS SendMessage
```

---

## Worker Lambda Role

The worker Lambda requires:

```
sqs:ReceiveMessage
sqs:DeleteMessage
sqs:GetQueueAttributes
sns:Publish
```

Purpose:

Allows the worker to:

* Read transactions from SQS
* Remove processed messages
* Publish transaction events to SNS

---

# 5. Testing Process

## API Gateway Testing

The API endpoint was tested using an HTTP request.

Example:

```
POST /withdraw
```

Payload:

```json
{
 "accountId":"100000001",
 "amount":500,
 "transactionType":"WITHDRAWAL"
}
```

Successful response:

```json
{
 "message":"Transaction received"
}
```

---

## SQS Validation

The transaction message was verified inside:

```
Amazon SQS
 |
ATMTransactionQueue
```

The queue successfully stored the transaction event.

---

## Lambda Execution Testing

CloudWatch Logs were used to verify:

* Lambda execution
* Permission errors
* Message processing

---

# 6. Challenges Encountered

## IAM Permission Error

Initial issue:

```
AccessDenied:
not authorized to perform sqs:SendMessage
```

Cause:

The Lambda execution role did not have permission to send messages to SQS.

Solution:

Added IAM permission:

```
sqs:SendMessage
```

---

## SQS Trigger Permission Error

Initial issue:

```
Lambda does not have permissions to call ReceiveMessage
```

Cause:

Worker Lambda role lacked SQS consumer permissions.

Solution:

Added:

```
sqs:ReceiveMessage
sqs:DeleteMessage
sqs:GetQueueAttributes
```

---

# 7. Architecture Benefits

## Scalability

The architecture can handle increasing traffic because:

* API Gateway scales automatically
* Lambda scales automatically
* SQS buffers high traffic periods

---

## Reliability

SQS provides:

* Message durability
* Retry handling
* Decoupled processing

---

## Security

IAM provides:

* Least privilege access
* Controlled service communication
* No hardcoded credentials

---

# 8. Current Limitations

The current system is a simplified transaction pipeline.

It does not yet include:

* Customer database
* Account balance validation
* Transaction history
* Fraud detection
* Authentication
* Private networking

---

# 9. Future Improvements

## Phase 2: Enterprise Backend

Replace Worker Lambda:

```
SQS
 |
Go Transaction Service
 |
Aurora PostgreSQL
```

The Go service will:

* Validate accounts
* Update balances
* Store transactions
* Apply business rules

---

## Phase 3: Production Architecture

Add:

* Amazon VPC
* Private subnets
* Security Groups
* Aurora Multi-AZ
* AWS KMS encryption
* AWS Secrets Manager
* CloudFormation deployment
* CloudWatch monitoring
* CloudTrail auditing

Final target architecture:

```
API Gateway
      |
 Lambda
      |
 SQS
      |
 ECS Fargate (Go Service)
      |
 Aurora PostgreSQL
      |
 SNS
```

---

# 10. Conclusion

This project successfully implemented an AWS event-driven architecture for processing ATM transactions.

The project demonstrated practical usage of:

* API Gateway for API exposure
* Lambda for serverless compute
* SQS for asynchronous messaging
* SNS for event notifications
* IAM for secure service communication

The design follows patterns commonly used in enterprise systems where reliability, scalability, and loose coupling are required.
