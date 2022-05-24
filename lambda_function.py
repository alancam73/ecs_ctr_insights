# Lambda to print out all ECS clusters in an account that do NOT have Container Insights enabled
# Also logs results to CloudWatch log stream

import json
import boto3
import os
import botocore
from botocore.exceptions import ClientError
import uuid
import time
from datetime import datetime

ecsClient = boto3.client('ecs')
logsClient = boto3.client('logs')


def lambda_handler(event, context):

    # allow local Python execution testing
    execEnv = str(os.getenv('AWS_EXECUTION_ENV'))
    if execEnv.startswith("AWS_Lambda"):
        logGroupParam = os.getenv('log_group_envvar')
        log_group = str(logGroupParam)
    else:
        log_group = '/aws/lambda/ecsContainerInsightsCheck'

    print("List the status of ECS Container Insights for each ECS cluster")
    print("ClusterName,ClusterStatus,ClusterPerformanceInsightsStatus")
    
    # set up the log groups & log stream so we can push Container Insights False occurrences to CW
    log_stream = 'ECSContainerInsights'
    now = datetime.now()
    date_time_fmt = now.strftime("%m-%d-%Y-%H-%M-%S")
    log_stream_dt = date_time_fmt + '-' + log_stream
#    log_response = logsClient.create_log_group(logGroupName=log_group)
    logsClient.create_log_stream(
        logGroupName=log_group,
        logStreamName=log_stream_dt
    )
    
    response = ecsClient.list_clusters()

    seq_token = None
    for instance in response['clusterArns']:

        clstrInfo = ecsClient.describe_clusters(
            clusters=[instance],
            include=['SETTINGS']
        )
        clstrInfo2 = clstrInfo['clusters']
        clstrSettings = clstrInfo2[0]['settings'][0]['value']
        clstrName = clstrInfo2[0]['clusterName']
        clstrStatus = clstrInfo2[0]['status']
        
        # log which clusters have Container Insights disabled
        if clstrSettings == 'disabled':
            print(clstrName, clstrStatus, clstrSettings, sep=",")
            instList = [clstrName, clstrStatus, clstrSettings]
            instanceData = ",".join(instList)

            log_event = {
                'logGroupName': log_group,
                'logStreamName': log_stream_dt,
                'logEvents': [
                    {
                        'timestamp': int(round(time.time() * 1000)),
                        'message': instanceData
                    },
                ],
            }

            if seq_token:
                log_event['sequenceToken'] = seq_token
            response = logsClient.put_log_events(**log_event)
            seq_token = response['nextSequenceToken']
            
        
    return None


# allow local Python execution testing
if __name__ == '__main__':
    lambda_handler(None,None)
