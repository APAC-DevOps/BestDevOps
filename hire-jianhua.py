import os
import boto3
import json
import argparse
import random
import sys
from botocore.client import ClientError

# Jianhua Wu is the intellectual property owner of this script.
# commercial use without Jianhua's written consignment is prohibited

# Run this script with the command:
# python3 hire-jianhua.py --Env Dev --Ref jianhua

parser = argparse.ArgumentParser(
    description='parse option arguments passed to this script',
    epilog='you can write to wujianhua@outlook.jp for help',
    prefix_chars='-'
    )

parser.add_argument('--Env', required = True, choices = [ 'Dev', 'Staging', 'Qa', 'Uat', 'Prod' ], help = 'the type of your application environment')
parser.add_argument('--Ref', nargs = '*', help='a reference string to append to the cfn stackname')
parser.add_argument('--AWSRegion', default='ap-southeast-2', help='The AWS Region in which to deploy your resource')
parser.add_argument('--DomainName', default='hire.jianhua', help='your registered public route53 domain name')
parsed_argu = parser.parse_args(sys.argv[1:])
sys_env = parsed_argu.Env
ref_id = parsed_argu.Ref
ref_id = ''.join(ref_id).lower()
aws_region = parsed_argu.AWSRegion
domain_name = parsed_argu.DomainName

#cf_template_url = 'trimed-cloudfront-s3-static-site.json'
cf_template_url = 'https://jianhua-replication-test.s3-ap-southeast-2.amazonaws.com/trimed-cloudfront-s3-static-site.json'

if ref_id:
    stack_name = "HIRE-JIANHUA-NOW-STACK" + "-" + sys_env.upper()[0:1] + sys_env.lower()[1:] + "-" + ref_id
else:
    stack_name = "HIRE-JIANHUA-NOW-STACK" + "-" + sys_env.upper()[0:1] + sys_env.lower()[1:]




cf_stack_param =  [
            { 'ParameterKey': 'Env', 'ParameterValue': sys_env.lower() },
            { 'ParameterKey': 'AcmCertificateArn', 'ParameterValue': "fakeValue" },
            { 'ParameterKey': 'ExtDomain', 'ParameterValue': domain_name },
            { 'ParameterKey': 'RefId', 'ParameterValue': ref_id },
        ]

def init_client(service, region):
    return boto3.client(service, region_name = region)


def update_stack(cfn_client, stackName=None, templateURL=None, parameters=None):
    stack_response = cfn_client.update_stack(
        StackName = stackName,
        TemplateURL = templateURL,
        Parameters = parameters,
        Capabilities = [
            'CAPABILITY_NAMED_IAM',
        ]
    )


def create_stack(cfn_client, stackName=None, templateURL=None, parameters=None, cfn_timeout=15):
    stack_response = cfn_client.create_stack(
    StackName = stackName,
    TemplateURL = templateURL,
    Parameters = parameters,
    TimeoutInMinutes=cfn_timeout,
    Capabilities=[
        'CAPABILITY_NAMED_IAM'
    ],

    OnFailure='ROLLBACK',
    EnableTerminationProtection = True
    )


def write_output(cfn_client, stackName=None, outputPath=None):
    cloudformation_outputs = cfn_client.describe_stacks(StackName = stackName)['Stacks'][0]['Outputs']
    output_length = len(cloudformation_outputs)
    i=0
    json_output = {}
    while i<output_length:
        json_output[cloudformation_outputs[i]['OutputKey']]  = cloudformation_outputs[i]['OutputValue']
        i = i + 1
    with open(outputPath, 'w+') as outputsfile:
        json.dump(json_output, outputsfile, indent = 4)


def create_update_stack(cfn_client, cfn_timeout=15, stackName=None, templateURL=None, parameters=None, outputPath=None):
    try:
        cfn_client.describe_stacks(StackName = stackName)
        try:
            print("Updating stack: " + stackName)
            update_stack(cfn_client, stackName=stackName, templateURL=templateURL, parameters=parameters)
            stack_waiter = cfn_client.get_waiter('stack_update_complete')
            stack_waiter.wait(StackName = stackName)
            if outputPath:
                print("Config ouput written to: {}".format(outputPath))
                write_output(cfn_client, stackName=stackName, outputPath=outputPath)
            print("Successfully updated stack: " + stackName)
            return 0
        except ClientError as e:
            error_code = int(e.response['ResponseMetadata']['HTTPStatusCode'])
            if error_code == 400:
                print("Nothing to be updated on stack: " + stackName)
                return 0
            print("Error Occured.")
            sys.exit(error_code)
    except ClientError as e:
        error_code = int(e.response['ResponseMetadata']['HTTPStatusCode'])
        if error_code == 403:
            sys.exit("Private Cloudformation stack. Access denied!")
        elif error_code == 400:
            print("Stack does not exist! Creating stack: " + stackName)
            create_stack(cfn_client=cfn_client, stackName=stackName, templateURL=templateURL, parameters=parameters, cfn_timeout=cfn_timeout)
            stack_waiter = cfn_client.get_waiter('stack_create_complete')
            stack_waiter.wait(StackName = stackName)
            if outputPath:
                print("Config ouput written to: {}".format(outputPath))
                write_output(cfn_client, stackName=stackName, outputPath=outputPath)
            print("Created new stack: " + stackName)
            return 0

if __name__ == "__main__":
    # Initialise AWS Clients here, because some scripts need to fetch parameters from aws resources before creating cf_stack_param
    cloudformation_client = init_client(service='cloudformation', region=aws_region)
    create_update_stack(cfn_client=cloudformation_client, cfn_timeout=40, stackName=stack_name, templateURL=cf_template_url, parameters=cf_stack_param)
