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

def get_need_to_be_open_status(data, vin_token):
    for element in data:
        if element['vin_token'] == vin_token:
            return element['need_to_be_open']

def lambda_handler(event, context):
    # list all entries from the db
    table_name = "shipitday2017_face_the_performance_data"
    dynamodb_resource = resource('dynamodb')
    table = get_table(dynamodb_resource, table_name)
    logger.info('got event{}'.format(event))
    # here we get the data in queryStringParameters, because it came through a GET
    request_data = event['queryStringParameters']
    vin_token = request_data['vin_token']
    # get data from db and filter it
    entries = scan_table(table)['Items']
    entries_data = [entries[0], entries[-1]]
    result_list = []
    for data_group in entries_data:
        entries_filtered = {k: v for k, v in data_group.items() if k in ['vin_token', 'need_to_be_open', 'is_open']}
        result_list.append(entries_filtered)

    # look for an element where vin_token == vin_token and token == token
    if check_access(result_list, vin_token) == False:
        return http_response(403, { "success": "false", "message": "Access denied" })

    result = get_need_to_be_open_status(result_list, vin_token)

    return http_response(200, { "need_to_be_open": result })

def get_table(dynamodb_resource, table_name):
    return dynamodb_resource.Table(table_name)

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
