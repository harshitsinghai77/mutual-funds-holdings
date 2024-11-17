import json

from utils.dynamo_database import DynamoDBManager
from utils.compare_mutual_fund_holdings import MutualFundHoldings
# from src.local_database import LocalSQLiteDB
# from src.compare_mutual_fund_holdings_local import MutualFundHoldingsLocal


def handler(event, context):

    http_method = event['requestContext']['http']['method'].upper() # method could be GET POST DELETE
    http_path = event['requestContext']['http']['path'].lower() # path could be /mutual-funds

    if http_method == 'GET' and http_path == '/mutualfunds':
        try:
            dynamodb = DynamoDBManager(partition_key='mutual_fund_id', table_name='mutual_funds')
            # dynamodb.ensure_table_exists()
            mutual_funds = dynamodb.get_all_mutual_funds()
            
            # Working locally
            # with LocalSQLiteDB('mutual_funds.db') as db:
            #     mutual_funds = db.retrieve_mutual_funds()
                
            return {
                "statusCode": 200,
                "body": json.dumps(mutual_funds)
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }
    
    elif http_method == 'POST' and http_path == '/compare-mutual-funds':
        try:
            body = json.loads(event.get('body', '{}'))

            required_keys = ['mutual_fund1', 'mutual_fund2']
            # Check if the required keys are in the parsed data
            missing_keys = [key for key in required_keys if key not in body]
            if missing_keys:
                return {
                    "statusCode": 400,
                    "body": json.dumps({
                        "message": "Missing required keys",
                        "missing_keys": missing_keys
                    })
                }
            
            mutual_fund1 = body['mutual_fund1']
            mutual_fund2 = body['mutual_fund2']

            mf_holdings = MutualFundHoldings()
            compared_mutual_fund = mf_holdings.compare_mutual_fund_holding(
                mutual_fund1, mutual_fund2
            )

            # Working locally
            # mf_holdings = MutualFundHoldingsLocal()
            # compared_mutual_fund = mf_holdings.compare_mutual_fund_holding(
            #     mutual_fund_details.mutual_fund1,
            #     mutual_fund_details.mutual_fund2
            # )

            return {
                "statusCode": 200,
                "body": json.dumps(compared_mutual_fund)
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }
    
    return {
        "statusCode": 404,
        "body": json.dumps({"message": "Path not found"})
    }