import boto3

class DynamoDBManager:

    def __init__(self, partition_key, table_name) -> None:
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = table_name
        self.partition_key = partition_key
        self.table = self.dynamodb.Table(table_name)
            
    def create_table(self):
        print(f"Creating table {self.table_name}...")
        # create a DynamoDB table
        self.table = self.dynamodb.create_table(
            TableName=self.table_name,
            KeySchema=[
                {'AttributeName': self.partition_key, 'KeyType': 'HASH'} # Partition key
            ],
            AttributeDefinitions = [
                {'AttributeName': self.partition_key, 'AttributeType': 'S'}, 
            ],
            BillingMode='PAY_PER_REQUEST', # On-demand biling mode
            TableClass='STANDARD'
        )

        self.table.meta.client.get_waiter('table_exists').wait(TableName=self.table_name)
        print(f"Table {self.table.table_name} created succesfully")

    def _insert_batch_data(self, items):
        with self.table.batch_writer(overwrite_by_pkeys=[self.partition_key]) as batch:
            for item in items:
                batch.put_item(Item=item)
        print(f"Batch data inserted into table {self.table_name} succesfullly")

    def _insert_single_data(self, data):
        self.table.put_item(Item=data)
        print(f"Data inserted into table {self.table_name} succesfullly")

    def insert_data(self, data):

        if isinstance(data, dict):
            self._insert_single_data(data)
        elif isinstance(data, list):
            self._insert_batch_data(data)
        else:
            raise TypeError("Unsupported data type. Please provide a dictionary or a list of dictionaries.")

    def query_by_partition_key(self, partition_key_value, attributes_to_get=[]):
        query_params = {
            'KeyConditionExpression':boto3.dynamodb.conditions.Key(self.partition_key).eq(partition_key_value)
        }

        if attributes_to_get:
            query_params['projection_expression'] = ", ".join(attributes_to_get)
            query_params['Select'] = 'SPECIFIC_ATTRIBUTES'

        response = self.table.query(**query_params)
        return response
    
    def get_item(self, mutual_fund_id):
        response = self.table.get_item(Key={'mutual_fund_id': mutual_fund_id})
        item = response.get('Item')
        return item
    
    def get_all_mutual_funds(self):
        fund_names = []
        response = self.table.scan(
            ProjectionExpression='fund_name, mutual_fund_id'
        )
        fund_names.extend(response.get('Items', []))
   
        while 'LastEvaluatedKey' in response:
            response = self.table.scan(
                ProjectionExpression='fund_name, mutual_fund_id',
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            print("Count for each request", len(response.get('Items', [])))
            fund_names.extend(response.get('Items', []))
        return fund_names

    def delete_dynamodb_table(self):

        self.table.delete()
        # Wait until the table is deleted
        self.table.meta.client.get_waiter('table_not_exists').wait(TableName=self.table_name)
        print(f"Table {self.table_name} deleted succesfully")

    def table_exists(self):
        try:
            self.dynamodb.meta.client.describe_table(TableName=self.table_name)
            return True
        except self.dynamodb.meta.client.exceptions.ResourceNotFoundException:
            return False
    
    def ensure_table_exists(self):
        if not self.table_exists():
            print(f"Table {self.table_name} does not exists")
            self.create_table()
        else:
            print(f"Table {self.table_name} already exists")