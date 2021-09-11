import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import os


def create_item(body: str):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    if not get_item_by_id(body['id']):
        try:
            table.put_item(Item=body)
        except ClientError:
            raise
        return ('item successfully added')
    else:
        return ('Item already exist')


def get_item_by_id(item_id: str):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    try:
        item_info = table.get_item(Key={'id': item_id})
    except ClientError:
        raise
    if 'Item' in item_info:
        return item_info['Item']
    else:
        return False


def get_all_item(price):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    try:
        all_items = table.scan(FilterExpression=Key(
            'price').eq(price))
    except ClientError:
        raise
    if 'Items' not in all_items['Items'] == 0:
        return ('Nothing find')
    return all_items['Items']


def order_item(item_id):
    item_info = get_item_by_id(item_id)
    if int(item_info['stock']) == 0:
        return ('Out of stock')
    item_info['stock'] = str(int(item_info['stock']) - 1)
    place_order_dict = {
        'id': "order#1",
        'name': item_info['name'],
        'price': item_info['price']
    }
    create_item(place_order_dict)
    update_item(item_info)
    return ('successfully ordered')


def update_item(item_info):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    try:
        table.update_item(Key={'id':
                               item_info['id']
                               },
                          UpdateExpression='SET #stock=:stock',
                          ExpressionAttributeValues={
            ':stock': item_info['stock']},
            ExpressionAttributeNames={
            '#stock': 'stock'},
            ReturnValues="UPDATED_NEW"
        )
    except ClientError:
        raise
