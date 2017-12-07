import json
from boto3 import resource
from boto3.dynamodb.conditions import Key
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def my_logging_handler(event, context):
    logger.info('got event{}'.format(event))

def check_access(data, vin_token):
    for element in data:
        if element['vin_token'] == vin_token:
            return True
    return False

def get_imei_for_vin_token(data, vin_token):
    for element in data:
        if element['vin_token'] == vin_token:
            return element['imei']

def lambda_handler(event, context):
    # list all entries from the db
    table_name = "shipitday2017_face_the_performance_data"
    dynamodb_resource = resource('dynamodb')
    table = get_table(dynamodb_resource, table_name)
    logger.info('got event{}'.format(event))
    request_data = json.loads(event['body'])
    vin_token = request_data['vin_token']
    is_open = request_data['is_open']
    # get data from db and filter it
    entries = scan_table(table)['Items']
    entries_data = [entries[0], entries[-1]]
    result_list = []
    for data_group in entries_data:
        entries_filtered = {k: v for k, v in data_group.items() if k in ['vin_token', 'need_to_be_open', 'is_open', 'imei']}
        result_list.append(entries_filtered)

    # look for an element where vin_token == vin_token and token == token
    if check_access(result_list, vin_token) == False:
        return http_response(403, { "success": "false", "message": "Access denied" })

    imei = get_imei_for_vin_token(result_list, vin_token)
    update_opened_status(table, imei, vin_token, is_open)

    return http_response(200, { "success": "true", "message": "Command accepted." })

def get_table(dynamodb_resource, table_name):
    return dynamodb_resource.Table(table_name)

def update_opened_status(table, imei, vin_token, state):
    table.update_item(Key={'imei':imei},
        UpdateExpression="SET is_open = :is_open",
        ConditionExpression="vin_token = :vin_token",
        ExpressionAttributeValues={':vin_token': vin_token, ':is_open': str2bool(state)})

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

def scan_table(table, filter_key=None, filter_value=None):
    """
    Perform a scan operation on table.
    Can specify filter_key (col name) and its value to be filtered.
    """

    if filter_key and filter_value:
        filtering_exp = Key(filter_key).eq(filter_value)
        response = table.scan(FilterExpression=filtering_exp)
    else:
        response = table.scan()

    return response

def http_response(status_code, response):
    """
    return a result in JSON format with the proper HTTP headers
    """

    return {
        'statusCode': status_code,
        'headers': { 'Content-Type': 'application/json' },
        'body': json.dumps(response)
    }
