import boto3

def get_parameter(param_name):
  param_name = 'balance-indexer-{}'.format(param_name)
  ssm = boto3.client('ssm', region_name='us-east-2')
  response = ssm.get_parameters(Names=[param_name], WithDecryption=True)
  return response['Parameters'][0]['Value']

