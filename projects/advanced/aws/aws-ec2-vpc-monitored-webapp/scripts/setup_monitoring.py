"""Automate the monitoring stack with Boto3 instead of clicking the Console.

Creates, in one run:
  1. An SNS topic + email subscription for alerts
  2. A CloudWatch alarm on Auto Scaling Group average CPU that notifies SNS
  3. A CloudWatch dashboard showing CPU, memory, and ALB request count

This is the "automation" half of the project: the same thing Steps 07–08 do by
hand in the Console, expressed as repeatable code. Safe to re-run — every call
is idempotent (create-or-update).

Usage:
    pip install boto3
    python setup_monitoring.py \
        --asg-name webapp-asg \
        --alb-arn-suffix app/webapp-alb/0123456789abcdef \
        --email you@example.com
"""
import argparse

import boto3

REGION = "us-east-1"
TOPIC_NAME = "webapp-alerts"
ALARM_NAME = "webapp-high-cpu"
DASHBOARD_NAME = "webapp-monitoring"


def ensure_topic(sns, email):
    # create_topic is idempotent: returns the existing ARN if the topic exists.
    topic_arn = sns.create_topic(Name=TOPIC_NAME)["TopicArn"]
    subs = sns.list_subscriptions_by_topic(TopicArn=topic_arn)["Subscriptions"]
    if not any(s["Endpoint"] == email for s in subs):
        sns.subscribe(TopicArn=topic_arn, Protocol="email", Endpoint=email)
        print(f"Subscription request sent to {email} — confirm it via the email link.")
    print(f"SNS topic ready: {topic_arn}")
    return topic_arn


def ensure_cpu_alarm(cw, asg_name, topic_arn):
    cw.put_metric_alarm(
        AlarmName=ALARM_NAME,
        AlarmDescription="Average CPU across the ASG is above 60% for 2 minutes",
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "AutoScalingGroupName", "Value": asg_name}],
        Statistic="Average",
        Period=60,
        EvaluationPeriods=2,
        Threshold=60.0,
        ComparisonOperator="GreaterThanThreshold",
        TreatMissingData="notBreaching",
        AlarmActions=[topic_arn],
        OKActions=[topic_arn],
    )
    print(f"CloudWatch alarm ready: {ALARM_NAME}")


def ensure_dashboard(cw, asg_name, alb_arn_suffix):
    body = {
        "widgets": [
            {
                "type": "metric", "x": 0, "y": 0, "width": 12, "height": 6,
                "properties": {
                    "title": "ASG Average CPU (%)",
                    "region": REGION,
                    "metrics": [["AWS/EC2", "CPUUtilization",
                                 "AutoScalingGroupName", asg_name]],
                    "stat": "Average", "period": 60,
                },
            },
            {
                "type": "metric", "x": 12, "y": 0, "width": 12, "height": 6,
                "properties": {
                    "title": "Memory Utilization (%) — CloudWatch agent",
                    "region": REGION,
                    "metrics": [["EC2MonitoredWebApp", "MemoryUtilization",
                                 "AutoScalingGroupName", asg_name]],
                    "stat": "Average", "period": 60,
                },
            },
            {
                "type": "metric", "x": 0, "y": 6, "width": 12, "height": 6,
                "properties": {
                    "title": "ALB Request Count",
                    "region": REGION,
                    "metrics": [["AWS/ApplicationELB", "RequestCount",
                                 "LoadBalancer", alb_arn_suffix]],
                    "stat": "Sum", "period": 60,
                },
            },
        ]
    }
    import json
    cw.put_dashboard(DashboardName=DASHBOARD_NAME, DashboardBody=json.dumps(body))
    print(f"CloudWatch dashboard ready: {DASHBOARD_NAME}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asg-name", required=True)
    parser.add_argument("--alb-arn-suffix", required=True,
                        help="e.g. app/webapp-alb/0123456789abcdef (from the ALB ARN)")
    parser.add_argument("--email", required=True)
    parser.add_argument("--region", default=REGION)
    args = parser.parse_args()

    sns = boto3.client("sns", region_name=args.region)
    cw = boto3.client("cloudwatch", region_name=args.region)

    topic_arn = ensure_topic(sns, args.email)
    ensure_cpu_alarm(cw, args.asg_name, topic_arn)
    ensure_dashboard(cw, args.asg_name, args.alb_arn_suffix)
    print("Monitoring stack complete.")


if __name__ == "__main__":
    main()
