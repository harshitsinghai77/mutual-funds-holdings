import time

from utils.local_database import LocalSQLiteDB
from utils.get_mutual_funds import get_all_mutual_funds_from_API

combined_data, failed_requests = get_all_mutual_funds_from_API()
if not combined_data:
    raise ValueError("Something went wrong, fetching mutual funds from API did not work")

print("Total mutual funds fetched from API", len(combined_data))

with LocalSQLiteDB('mutual_funds.db') as db:
    db.create_table()
    seen = set()
    
    for data in combined_data:
        if data['search_id'] not in seen:
            db.insert_data_into_mutual_funds(data)
            print("Inserted")
        else:
            print('already exists')
        seen.add(data['search_id'])

with LocalSQLiteDB('mutual_funds.db') as db:
    mutual_funds = db.retrieve_mutual_funds()
    for m in mutual_funds:
        print(m)