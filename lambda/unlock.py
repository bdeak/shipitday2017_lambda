import json
from boto3 import resource
from boto3.dynamodb.conditions import Key
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def my_logging_handler(event, context):
    logger.info('got event{}'.format(event))

def check_access(data, imei, phone_token):
    for element in data:
        if element['imei'] == imei and element['phone_token'] == phone_token:
            return True
    return False


def lambda_handler(event, context):
    # list all entries from the db
    table_name = "shipitday2017_face_the_performance_data"
    dynamodb_resource = resource('dynamodb')
    table = get_table(dynamodb_resource, table_name)
    logger.info('got event{}'.format(event))
    request_data = json.loads(event['body'])
    imei = request_data['imei']
    phone_token = request_data['phone_token']
    # get data from db and filter it
    entries = scan_table(table)['Items']
    entries_data = [entries[0], entries[-1]]
    result_list = []
    for data_group in entries_data:
        entries_filtered = {k: v for k, v in data_group.items() if k in ['imei', 'phone_token']}
        result_list.append(entries_filtered)

    # look for an element where imei == imei and token == token
    if check_access(result_list, imei, phone_token) == False:
        return http_response(403, { "success": "false", "message": "Access denied" })


    # update need_to_be_open
    update_opened_status(table, imei, True)

    return http_response(200, { "success": "true", "message": "Command accepted." })

def update_opened_status(table, imei, state):
        table.update_item(Key={'imei':imei},
            UpdateExpression="SET need_to_be_open = :need_to_be_open",
            ExpressionAttributeValues={':need_to_be_open': state})

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
