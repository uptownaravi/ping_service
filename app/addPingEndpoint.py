import json
import boto3

event_bridge_scheduler = boto3.client('scheduler')
cloudwatch = boto3.client('cloudwatch')


def lambda_handler(event, context):

    print(event)
    print(context)
    ping_json = json.loads(event["body"])

    ping_data = {
        "ping_name": ping_json["service_name"],
        "ping_url": ping_json["service_url"],
        "ping_cron": ping_json["service_cron"],
        "ping_details": ping_json["service_details"]
    }

    # create the event bridge schedule to check the endpoint
    print(eventBridge(json.dumps(ping_data), str(
        ping_data["ping_name"]), str(ping_data["ping_cron"])))

    # add alarm for the metric
    addAlarm(str(ping_data["ping_name"]))

    return {
        'statusCode': 200,
        'body': json.dumps('Schedule Added')
    }


def eventBridge(data, ping_name, ping_cron):

    print(data)
    cron = "cron(" + ping_cron + ")"
    response = event_bridge_scheduler.create_schedule(
        Description='string',
        FlexibleTimeWindow={
            'Mode': 'OFF'
        },

        Name=ping_name,
        ScheduleExpression=cron,
        ScheduleExpressionTimezone='UTC',
        State='ENABLED',
        Target={
            # add the function arn of the checkendpoint, this will be the target of the eventbrdige schedule
            'Arn': 'arn:aws:lambda:<region>:<accountnumber>:function:<checkEndpoint function name>',
            'Input': str(data),
            'RetryPolicy': {
                'MaximumEventAgeInSeconds': 120,
                'MaximumRetryAttempts': 5
            },
            'RoleArn': 'arn:aws:iam::<account number>:role/<role name of addPingEndpointPolicy>',
        }
    )
    return response


def addAlarm(ping_name):
    response = cloudwatch.put_metric_alarm(
        AlarmName='Uptime Alarm for %s' % ping_name,
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName="Status_Code",
        Namespace=ping_name,
        Period=60,
        Statistic='Average',
        Threshold=200.0,
        ActionsEnabled=False,
        AlarmDescription='Alarm when uptime for http return code of %s endpoint is above 200' % ping_name,
        Unit='None'
    )
    return response
