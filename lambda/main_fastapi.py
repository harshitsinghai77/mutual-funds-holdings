from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# from src.dynamo_database import DynamoDBManager
# from src.compare_mutual_fund_holdings import MutualFundHoldings
from utils.local_database import LocalSQLiteDB
from utils.compare_mutual_fund_holdings_local import MutualFundHoldingsLocal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MutualFundCompare(BaseModel):
    mutual_fund1: str
    mutual_fund2: str

# FastAPI endpoints
@app.get('/mutualfunds')
async def get_mutual_funds():
    try:
        # dynamodb = DynamoDBManager(partition_key='mutual_fund_id', table_name='mutual_funds')
        # dynamodb.ensure_table_exists()
        # mutual_funds = dynamodb.get_all_mutual_funds()
        
        # Working locally
        with LocalSQLiteDB('mutual_funds.db') as db:
            mutual_funds = db.retrieve_mutual_funds()
            
        return mutual_funds
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post('/compare-mutual-funds')
async def compare_mutual_funds(mutual_fund_details: MutualFundCompare):
    try:
        # mf_holdings = MutualFundHoldings()
        # compared_mutual_fund = mf_holdings.compare_mutual_fund_holding(
        #     mutual_fund_details.mutual_fund1,
        #     mutual_fund_details.mutual_fund2
        # )

        mf_holdings = MutualFundHoldingsLocal()
        compared_mutual_fund = mf_holdings.compare_mutual_fund_holding(
            mutual_fund_details.mutual_fund1,
            mutual_fund_details.mutual_fund2
        )
        return JSONResponse(content=compared_mutual_fund)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))