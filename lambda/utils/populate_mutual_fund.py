import time

from utils.dynamo_database import DynamoDBManager
from utils.get_mutual_funds import get_all_mutual_funds_from_API

combined_data, failed_requests = get_all_mutual_funds_from_API()
if not combined_data:
    raise ValueError("Something went wrong, fetching mutual funds from API did not work")

print("Total mutual funds fetched from API", len(combined_data))

dynamodb = DynamoDBManager(partition_key='mutual_fund_id', table_name='mutual_funds')
if dynamodb.table_exists():
    dynamodb.delete_dynamodb_table()
    dynamodb.create_table()

for mf in combined_data:
    for key, value in mf.items():
        if isinstance(value, float) or isinstance(value, int):
            mf[key] = str(value)
    mf['mutual_fund_id'] = mf['search_id']

start_time = time.perf_counter()
dynamodb.insert_data(combined_data)
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"Time taken to insert data: {elapsed_time:.6f} seconds")
