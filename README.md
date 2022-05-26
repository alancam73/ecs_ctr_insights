# ecs_ctr_insights
AWS Lambda to check if ECS Container Insights are enabled across all clusters in an account

### Description
AWS Lambda function to query all the ECS Clusters in an Account to check if any of them 
do NOT have Container Insights enabled. This feature is very valuable since it provides additional 
cointainer level metrics eg for finding eg num tasks in PENDING, RUNNING states, container
restart failures etc.
This Lambda also outputs the instances that have Container Insights = False to a CloudWatch Log Stream

### Pre-requisites
* python 3.8 or higher
* setup the correct IAM permissions - this is done via the YAML CFT

### Environment variables
* log_group_envvar : the name of the CW Log Group to output the log stream

### Example output


### Triggers
This lambda can be run standalone or via a trigger eg daily via an EventBridge rule eg rate(1 day)

