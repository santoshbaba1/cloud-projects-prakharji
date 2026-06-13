"""Automate the serverless monitoring stack with Boto3.

Creates in one idempotent run:
  1. An SNS topic + email subscription for alerts
  2. A CloudWatch alarm on Lambda Errors  -> SNS
  3. A CloudWatch alarm on Lambda Duration (p95) -> SNS
  4. A CloudWatch dashboard: Invocations, Errors, Duration, API 5xx

This is the serverless counterpart to the EC2 project's setup_monitoring.py — note
how the metrics change (no CPU/memory; instead Invocations, Errors, Duration,
Throttles) even though the alerting plumbing is identical.

Usage:
    pip install boto3
    python setup_monitoring.py \
        --function-name serverless-webapp \
        --api-id abc123 \
        --email you@example.com
"""
import argparse
import json

import boto3

REGION = "us-east-1"
TOPIC_NAME = "serverless-webapp-alerts"
DASHBOARD_NAME = "serverless-webapp-monitoring"


def ensure_topic(sns, email):
    topic_arn = sns.create_topic(Name=TOPIC_NAME)["TopicArn"]
    subs = sns.list_subscriptions_by_topic(TopicArn=topic_arn)["Subscriptions"]
    if not any(s["Endpoint"] == email for s in subs):
        sns.subscribe(TopicArn=topic_arn, Protocol="email", Endpoint=email)
        print(f"Subscription request sent to {email} — confirm it via the email link.")
    print(f"SNS topic ready: {topic_arn}")
    return topic_arn


def ensure_error_alarm(cw, fn, topic_arn):
    cw.put_metric_alarm(
        AlarmName=f"{fn}-errors",
        AlarmDescription="Lambda reported >=1 error in a 1-minute window",
        Namespace="AWS/Lambda",
        MetricName="Errors",
        Dimensions=[{"Name": "FunctionName", "Value": fn}],
        Statistic="Sum",
        Period=60,
        EvaluationPeriods=1,
        Threshold=1.0,
        ComparisonOperator="GreaterThanOrEqualToThreshold",
        TreatMissingData="notBreaching",
        AlarmActions=[topic_arn],
        OKActions=[topic_arn],
    )
    print(f"Alarm ready: {fn}-errors")


def ensure_duration_alarm(cw, fn, topic_arn):
    cw.put_metric_alarm(
        AlarmName=f"{fn}-slow",
        AlarmDescription="Lambda p95 duration above 3000 ms for 2 minutes",
        Namespace="AWS/Lambda",
        MetricName="Duration",
        Dimensions=[{"Name": "FunctionName", "Value": fn}],
        ExtendedStatistic="p95",
        Period=60,
        EvaluationPeriods=2,
        Threshold=3000.0,
        ComparisonOperator="GreaterThanThreshold",
        TreatMissingData="notBreaching",
        AlarmActions=[topic_arn],
        OKActions=[topic_arn],
    )
    print(f"Alarm ready: {fn}-slow")


def ensure_dashboard(cw, fn, api_id):
    body = {
        "widgets": [
            {"type": "metric", "x": 0, "y": 0, "width": 12, "height": 6,
             "properties": {"title": "Lambda Invocations & Errors", "region": REGION,
                            "stat": "Sum", "period": 60,
                            "metrics": [
                                ["AWS/Lambda", "Invocations", "FunctionName", fn],
                                ["AWS/Lambda", "Errors", "FunctionName", fn],
                                ["AWS/Lambda", "Throttles", "FunctionName", fn]]}},
            {"type": "metric", "x": 12, "y": 0, "width": 12, "height": 6,
             "properties": {"title": "Lambda Duration (ms)", "region": REGION,
                            "period": 60,
                            "metrics": [
                                ["AWS/Lambda", "Duration", "FunctionName", fn,
                                 {"stat": "p95"}],
                                ["AWS/Lambda", "Duration", "FunctionName", fn,
                                 {"stat": "Average"}]]}},
            {"type": "metric", "x": 0, "y": 6, "width": 12, "height": 6,
             "properties": {"title": "API Gateway 5xx", "region": REGION,
                            "stat": "Sum", "period": 60,
                            "metrics": [["AWS/ApiGateway", "5xx", "ApiId", api_id]]}},
        ]
    }
    cw.put_dashboard(DashboardName=DASHBOARD_NAME, DashboardBody=json.dumps(body))
    print(f"Dashboard ready: {DASHBOARD_NAME}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--function-name", required=True)
    parser.add_argument("--api-id", required=True, help="HTTP API id, e.g. abc123")
    parser.add_argument("--email", required=True)
    parser.add_argument("--region", default=REGION)
    args = parser.parse_args()

    sns = boto3.client("sns", region_name=args.region)
    cw = boto3.client("cloudwatch", region_name=args.region)

    topic_arn = ensure_topic(sns, args.email)
    ensure_error_alarm(cw, args.function_name, topic_arn)
    ensure_duration_alarm(cw, args.function_name, topic_arn)
    ensure_dashboard(cw, args.function_name, args.api_id)
    print("Serverless monitoring stack complete.")


if __name__ == "__main__":
    main()
