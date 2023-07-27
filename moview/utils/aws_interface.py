import boto3


def getenv(parameter_name):
    client = boto3.client('ssm')
    response = client.get_parameter(Name=parameter_name, WithDecryption=True)
    return response['Parameter']['Value']
