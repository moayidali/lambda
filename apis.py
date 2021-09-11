from operations import create_item, get_all_item, order_item
from botocore.exceptions import ClientError


def response_object(statusCode, body):
    return {"statusCode": statusCode,
            "body": body
            }


def lambda_handler(event, context):
    if event["httpMethod"] == "GET":
        return lambda_get(event, context)
    elif event["httpMethod"] == "POST":
        if event['path'] == '/order/':
            return lambda_post_order(event, context)
        else:
            return lambda_post_item(event, context)
    else:
        response = response_object(400, "http method not supported")
        return response


def lambda_get(event, context):
    try:
        sort_by = event['headers']['queryParameter']
        all_items = get_all_item(sort_by)
        response = response_object(200, all_items)
    except ClientError as e:
        error = response_object(500, "Database error")
        return error
    return response


def lambda_post_item(event, context):
    try:
        message = create_item(event['body'])
    except ClientError as e:
        error = response_object(500, "Database error")
        return error
    response = response_object(200, message)
    return response


def lambda_post_order(event, context):
    try:
        item_id = event['headers']['queryParameter']
        message = order_item(item_id)
    except ClientError as e:
        error = response_object(500, "Database error")
        return error
    response = response_object(200, message)
    return response
