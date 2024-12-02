---
categories: "AWS"
tag: ["sqs", "aws", "sns"]
teaser: "2023-12-15-aws-lambda"
title: "[AWS] SNS 로 인한 람다 동시성 문제 해결"
description: "aws 서버리스 이벤트 기반 아키텍처 활용을 위해 SNS, SQS 을 알아보고 프로젝트 문제점을 해결했습니다."
---

이전에는 **SNS**에서 발생한 이벤트가 **Lambda**를 직접 트리거하는 방식으로 구성되었습니다. 하지만 이 방식은 트래픽 급증이나 Lambda 동시 실행 제한으로 인해 이벤트가 처리되지 않거나 누락되는 문제가 발생할 수 있었습니다. 이를 해결하기 위해 SNS가 SQS 대기열을 통해 Lambda를 호출하도록 변경하면서 안정성과 확장성을 모두 확보할 수 있습니다.

------

## **1. 기존 구조: SNS -> Lambda**

![image-20241202151001679](../../images/2024-11-27-[AWS]snsproblem/image-20241202151001679.png)

### **동작 방식**

- SNS는 이벤트가 발생하면 메시지를 Lambda에 즉시 전달(푸시)합니다.
- Lambda는 메시지를 받아 처리하며, 처리 결과를 반환합니다.

### **문제점**

1. **동시 실행 제한**
   - Lambda 함수에는 AWS 계정당 기본 동시 실행 제한(1,000)이 있습니다.
   - SNS가 이를 초과하는 메시지를 발행하면 초과된 메시지는 처리되지 않고 누락됩니다.
2. **메시지 재처리 부족**
   - Lambda가 실패하면 SNS는 최대 4번의 재시도를 시도하지만, 여전히 처리되지 않으면 메시지가 손실됩니다.
3. **트래픽 급증 처리 불가**
   - 트래픽이 급증하는 환경에서는 SNS가 Lambda의 처리 능력을 초과하는 메시지를 보내도 대기하거나 저장할 공간이 없습니다.

------

## **2. 개선된 구조: SNS -> SQS -> Lambda**

![image-20241202151101397](../../images/2024-11-27-[AWS]snsproblem/image-20241202151101397.png)

### **변경 내용**

SNS가 Lambda를 직접 호출하지 않고, 먼저 **SQS 대기열**에 메시지를 저장한 뒤 Lambda가 대기열에서 메시지를 하나씩 처리하도록 변경합니다.

### **동작 방식**

1. **SNS -> SQS**
   - SNS는 이벤트가 발생하면 메시지를 SQS 대기열로 보냅니다.
   - SQS는 메시지를 보존하며, 처리 가능할 때까지 저장합니다.
2. **SQS -> Lambda**
   - Lambda는 SQS 대기열에서 메시지를 하나씩 가져와 처리합니다.
   - SQS의 메시지 보존 및 재시도 메커니즘 덕분에 Lambda의 동시성 제한 문제를 피할 수 있습니다.

------

## **3. 개선된 구조의 장점**

### **3.1. 동시성 문제 해결**

- SQS는 메시지를 큐에 저장하므로 Lambda의 동시성 제한(1,000)을 초과하는 메시지가 발생해도 안전하게 보존됩니다.
- Lambda는 제한된 수의 메시지만 처리하며, 나머지 메시지는 대기열에서 차례로 처리됩니다.

### **3.2. 메시지 보존 및 재처리**

- SQS는 메시지를 최대 14일까지 저장할 수 있으며, Lambda가 메시지를 처리하지 못하면 재시도가 가능합니다.
- 메시지가 소비되지 않으면 Dead Letter Queue(DLQ)로 이동해 손실을 방지할 수 있습니다.

### **33. 확장성 및 안정성**

- SQS는 트래픽 급증 상황에서도 무제한으로 메시지를 저장할 수 있으므로, 시스템이 높은 트래픽을 안정적으로 처리할 수 있습니다.
- Lambda와 SQS 간의 느슨한 결합 구조로 서비스 확장성이 높아집니다.

------

## **4. 구현 방법**

### **CloudFormation을 활용한 구성**

```
...
Resources:
  UpdateKeywordSNSTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: UpdateKeywordSNSTopic

  UpdateKeywordSQSQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: UpdateKeywordQueue
      
  UpdateKeywordSubscription:
    Type: AWS::SNS::Subscription
    Properties:
      TopicArn: !Ref UpdateKeywordSNSTopic
      Protocol: sqs
      Endpoint: !GetAtt UpdateKeywordSQSQueue.Arn

  UpdateKeywordSQSQueuePolicy:
    Type: AWS::SQS::QueuePolicy
    Properties:
      Queues:
        - !Ref UpdateKeywordSQSQueue
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal: "*"
            Action: "sqs:SendMessage"
            Resource: !GetAtt UpdateKeywordSQSQueue.Arn
            Condition:
              ArnEquals:
                aws:SourceArn: !Ref UpdateKeywordSNSTopic

  UpdateTbProductFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: updatetbproduct/
      Handler: app.lambda_handler
      Runtime: python3.11
      MemorySize: 4096
      Events:
        SQSTrigger:
          Type: SQS
          Properties:
            Queue: !Ref UpdateKeywordSQSQueue
```

------

## **5. 주요 설정**

1. **SNS와 SQS 연결**:
   - SNS 주제(`UpdateKeywordSNSTopic`)가 SQS 대기열(`UpdateKeywordSQSQueue`)에 메시지를 게시할 수 있도록 SQS 정책(`UpdateKeywordSQSQueuePolicy`)을 설정.
2. **Lambda와 SQS 연결**:
   - Lambda 함수(`UpdateTbProductFunction`)가 SQS 대기열을 폴링하여 메시지를 처리하도록 설정.
3. **Dead Letter Queue 설정(옵션)**:
   - 메시지가 처리되지 못할 경우를 대비하여 SQS에 DLQ를 추가로 설정할 수 있습니다.

------

## **6. 결과**

### **변경 전**

- SNS가 Lambda를 직접 호출하던 구조는 동시 실행 제한 초과, 메시지 손실, 트래픽 급증 시 안정성 부족 등의 문제가 있었습니다.

### **변경 후**

- SNS가 SQS 대기열에 메시지를 저장하고, Lambda가 이를 처리함으로써 동시성 제한 문제를 해결하고 안정성을 확보했습니다.
- 메시지는 SQS에 안전하게 보관되며, 필요하면 재처리하거나 DLQ를 활용해 손실을 방지할 수 있습니다.

------

## **결론**

SNS에서 Lambda를 직접 호출하는 구조는 간단하지만, 대규모 트래픽 처리나 안정성이 요구되는 경우 한계가 명확합니다. SQS를 중간에 추가하는 간단한 변경으로 메시지 보존, 동시성 제한 극복, 트래픽 급증에 대한 대응 등 다양한 문제를 해결할 수 있습니다.

