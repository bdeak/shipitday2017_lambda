import json
from boto3 import resource
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # list all entries from the db
    table_name = "shipitday2017_face_the_performance_data"
    dynamodb_resource = resource('dynamodb')
    table = get_table(dynamodb_resource, table_name)
    # get all items, while filtering out some columns
    entries = scan_table(table)['Items']
    entries_data = [entries[0], entries[-1]]
    #return entries_data
    masked_fields = [ 'token' ]
    result_list = []
    for data_group in entries_data:
        entries_filtered = {k: v for k, v in data_group.items() if k not in masked_fields}
        result_list.append(entries_filtered)
    return http_response(200, result_list)

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
