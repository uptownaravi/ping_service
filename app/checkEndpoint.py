import json
import boto3
import urllib3

cloudwatch = boto3.client('cloudwatch')


def lambda_handler(event, context):
    print(event)
    status_code = 0

    try:
        http = urllib3.PoolManager()
        response = http.request('GET', event['ping_url'])
        status_code = response.status
    except:
        print("issue in fetching the url status")
        status_code = 500

    http = urllib3.PoolManager()
    response = http.request('GET', event['ping_url'])
    print(response.status)

    addMetric = cloudwatch.put_metric_data(
        Namespace=event['ping_name'],
        MetricData=[

            {
                'MetricName': 'Status_Code',
                'Value': status_code,
                'Unit': 'None',
            },
        ]
    )

    print(addMetric)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
