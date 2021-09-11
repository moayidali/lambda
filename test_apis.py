from moto import mock_dynamodb2
import boto3
import pytest
import os
os.environ['TABLE_NAME'] = "unit_test"


@pytest.fixture(scope="session", autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'


@pytest.fixture(autouse=True)
def moto_boto():
    mock_dynamodb = mock_dynamodb2()
    mock_dynamodb.start()
    yield
    mock_dynamodb.stop()


@pytest.fixture
# Factory
def make_event():
    def _make_event(type="GET", body=None, path=None, parameter=None):
        event = {
            "resource": "/",
            "path": path,
            "httpMethod": type,
            "body": body,
            "isBase64Encoded": False
        }
        event['headers'] = {}
        event['headers']['queryParameter'] = parameter
        return event

    return _make_event


@pytest.fixture(scope="function")
def add_item_to_table():
    dynamodb = boto3.resource('dynamodb', 'eu-west-1')
    dynamodb.create_table(
        TableName=os.environ["TABLE_NAME"],
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    def _add_item_to_table(item):
        table = dynamodb.Table(os.environ["TABLE_NAME"])

        return table.put_item(Item=item)

    return _add_item_to_table


def test_post_method_add_item_return_200(aws_credentials, add_item_to_table, make_event):
    # Arrange
    from apis import lambda_handler

    body = {'id': 'P001', 'name': 'computer books',
            'price': '100 noks', 'stock': '20'}

    # Act
    path = '/items'
    response = lambda_handler(event=make_event(
        "POST", body), context={})

    # Assert
    assert response['statusCode'] == 200
    assert response['body']


def test_get_method_return_200(aws_credentials, add_item_to_table, make_event):
    # Arrange
    from apis import lambda_handler

    item1 = {'id': 'P001', 'name': 'computer books',
             'price': '100', 'stock': '20'}
    item2 = {'id': 'P002', 'name': 'science books',
             'price': '200', 'stock': '10'}
    item3 = {'id': 'P003', 'name': 'language books',
             'price': '200', 'stock': '10'}
    add_item_to_table(item1)
    add_item_to_table(item2)
    add_item_to_table(item3)
    price = '200'
    path = f"/items?sortBy={price}"
    # Act
    response = lambda_handler(event=make_event(
        "GET", False, path=path, parameter=price), context={})

    # Assert
    assert response['statusCode'] == 200
    assert response['body']


def test_post_method_order_item_return_200(aws_credentials, add_item_to_table, make_event):
    # Arrange
    from apis import lambda_handler

    item1 = {'id': 'P001', 'name': 'computer books',
             'price': '100', 'stock': '10'}
    item2 = {'id': 'P002', 'name': 'science books',
             'price': '200', 'stock': '10'}
    item3 = {'id': 'P003', 'name': 'language books',
             'price': '200', 'stock': '20'}
    add_item_to_table(item1)
    add_item_to_table(item2)
    add_item_to_table(item3)
    item_id = 'P001'
    path = f"/order/"

    # Act
    response = lambda_handler(event=make_event(
        "POST",  False, path=path, parameter=item_id), context={})

    # Assert
    assert response['statusCode'] == 200
    assert response['body']
