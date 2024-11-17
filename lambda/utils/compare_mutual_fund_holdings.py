import json
from bs4 import BeautifulSoup

from utils.api_client import APIClient
from utils.dynamo_database import DynamoDBManager

class MutualFundHoldings:

    def __init__(self) -> None:
        self.dynamo = DynamoDBManager(partition_key='mutual_fund_id', table_name='mutual_fund_holdings')
        # self.dynamo.ensure_table_exists()

    def custom_process_mutual_fund_response_function(self, response):
        soup = BeautifulSoup(response, 'html.parser')
        script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')
        if script_tag:
            json_content = script_tag.string
            data = json.loads(json_content)
            # mutual_fund_search_id = data.get('props').get('pageProps').get('mf').get('search_id')
            holdings = data.get('props').get('pageProps').get('mf').get('holdings')
            return holdings

    def get_holdings_from_db(self, mutual_fund_id):
        retrieve_data = self.dynamo.get_item(mutual_fund_id)
        if retrieve_data and retrieve_data.get('holdings'):
            return retrieve_data, retrieve_data['holdings']
        return {}, {}
    
    def get_mutual_fund_info(self, mutual_fund_search_id):
        mutual_fund_table = DynamoDBManager(partition_key='mutual_fund_id', table_name='mutual_funds')
        mutual_fund_info = mutual_fund_table.get_item(mutual_fund_id=mutual_fund_search_id)
        return mutual_fund_info

    def fetch_mutual_funds_holdings_from_API(self, mutual_fund_name):
        mutual_fund_url = 'https://groww.in/mutual-funds/' + mutual_fund_name
        api_client = APIClient(mutual_fund_url, process_response_function=self.custom_process_mutual_fund_response_function)
        api_client.run()

        return api_client.get_transformed_data()
    
    def get_holdings(self, mutual_fund_search_id):
    
        mutual_fund_info, mutual_fund_holdings = self.get_holdings_from_db(mutual_fund_search_id)
        if not mutual_fund_holdings:
            print(f"holdings for {mutual_fund_search_id} not found in DB")
            mutual_fund_holdings = self.fetch_mutual_funds_holdings_from_API(mutual_fund_search_id)
            mutual_fund_info = self.get_mutual_fund_info(mutual_fund_search_id)
            fund_name = mutual_fund_info.get('fund_name') or "not found"
            logo_url = mutual_fund_info.get('logo_url') or "not found"
            # print(f"==>> mutual_fund_holdings: {mutual_fund_holdings}")

            if not mutual_fund_holdings:      
                raise ValueError(f"No mutual fund holding found from external API for {mutual_fund_search_id}")  
            
            for mf in mutual_fund_holdings:
                for key, value in mf.items():
                    if isinstance(value, float) or isinstance(value, int):
                        mf[key] = str(value)
            
            # Insert holdings back to db
            mutual_fund_data_to_save = {
                'mutual_fund_id': mutual_fund_search_id,
                'fund_name': fund_name,
                'logo_url': logo_url,
                'holdings': mutual_fund_holdings
            }
            self.dynamo.insert_data(mutual_fund_data_to_save)

        return mutual_fund_info, mutual_fund_holdings

    def compare_mutual_fund_holding(self, mutual_fund1_search_id, mutual_fund2_search_id):
        mf1_info, mf1_holdings = self.get_holdings(mutual_fund1_search_id)
        mf2_info, mf2_holdings = self.get_holdings(mutual_fund2_search_id)

        # Step 2: Extract stock_search_ids from both mutual fund holdings
        mf1_stocks = {holding['stock_search_id'] for holding in mf1_holdings}
        mf2_stocks = {holding['stock_search_id'] for holding in mf2_holdings}

        # Step 3: Find common stocks between the two mutual funds
        overlap_mutual_funds = mf1_stocks & mf2_stocks

        # Step 4: Create a dictionary for easier lookup of holdings data by stock_search_id
        mf1_lookup = {holding['stock_search_id']: holding for holding in mf1_holdings}
        mf2_lookup = {holding['stock_search_id']: holding for holding in mf2_holdings}

        # Step 5: Prepare list to store overlap information
        overlap_data = []

        for stock_id in overlap_mutual_funds:
            mf1_data = mf1_lookup.get(stock_id)
            mf2_data = mf2_lookup.get(stock_id)
            
            if mf1_data and mf2_data:
                overlap_entry = {
                    'stock_search_id': stock_id,
                    'company_name': mf1_data['company_name'],
                    'sector_name': mf1_data['sector_name'],
                    'instrument_name': mf1_data['instrument_name'],
                    'corpus_mf1': mf1_data.get('corpus_per'),
                    'corpus_mf2': mf2_data.get('corpus_per')
                }
                overlap_data.append(overlap_entry)

        # Step 6: Count the number of common holdings
        num_common_holdings = len(overlap_data)

        # Step 7: Calculate total unique holdings
        unique_stocks = {holding['stock_search_id'] for holding in mf1_holdings}.union(
            {holding['stock_search_id'] for holding in mf2_holdings}
        )
        num_unique_holdings = len(unique_stocks)

        # Step 8: Calculate overlap percentage
        if num_unique_holdings > 0:
            overlap_percentage = (num_common_holdings / num_unique_holdings) * 100
        else:
            overlap_percentage = 0

        # Stocks in mf1 but not in mf2 
        # diff_mf1_mf2 = mf1_stocks - mf2_stocks 

        # Stocks in mf2 but not in mf1 
        # diff_mf2_mf1 = mf2_stocks - mf1_stocks 

        # Stocks in both mf1 and mf2 
        # overlap_mutual_funds = mf1_stocks & mf2_stocks
        # overlap_mutual_funds = mf1_holdings[mf1_holdings['stock_search_id'].isin(overlap_mutual_funds)]
        # overlap_mutual_funds = (
        #     overlap_mutual_funds.merge(mf2_holdings[['company_name', 'corpus_per']], on='company_name', how='left')
        #     .rename(columns={'corpus_per_x': 'corpus_mf1', 'corpus_per_y': f'corpus_mf2'})
        #     .where(pd.notnull, None)
        #     .drop_duplicates(subset='stock_search_id')
        # )
        # num_common_holdings = len(overlap_mutual_funds)
        
        # # Calculate the total unique holdings
        # unique_holdings = pd.concat([mf1_holdings, mf2_holdings]).drop_duplicates(subset='stock_search_id')
        # num_unique_holdings = len(unique_holdings)
        
        # Calculate the overlap percentage
        # overlap_percentage = (num_common_holdings/num_unique_holdings) * 100

        mutual_fund1 = {
            **mf1_info,
            'holdings': mf1_holdings
        }

        mutual_fund2 = {
            **mf2_info,
            'holdings': mf2_holdings
        }

        return {
            'source': 'Dynamo db',
            f'{mutual_fund1_search_id}': mutual_fund1,
            f'{mutual_fund2_search_id}': mutual_fund2,
            f'intersection_holdings': overlap_data,
            'overlap_percentage': f'{overlap_percentage:.2f}%'
        }
