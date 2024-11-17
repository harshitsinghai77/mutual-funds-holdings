from utils.api_client import APIClient

# url = 'https://groww.in/v1/api/search/v1/derived/scheme?available_for_investment=true&doc_type=scheme&max_aum=&page=0&plan_type=Direct&q=&size=15&sort_by=3'
# https://groww.in/v1/api/search/v1/derived/scheme?available_for_investment=true&doc_type=scheme&max_aum=&page=105&plan_type=Direct&q=&size=15&sort_by=3

def get_all_mutual_funds_from_API():

    # Define your list of URLs
    urls = [
            f'https://groww.in/v1/api/search/v1/derived/scheme?available_for_investment=true&doc_type=scheme&max_aum=&page={i}&plan_type=Direct&q=&size=15&sort_by=3'
            for i in range(0, 106)
    ]

    # User-defined function to process responses
    def custom_process_response_function(responses):
        keys_to_keep = ['fund_name', 'search_id', 'category', 'sub_category', 'scheme_name', 'scheme_type', 'fund_house', 'risk', 'direct_fund', 'amc', 'aum', 'direct_search_id', 'logo_url']
        transformed_data = []
        for response in responses:
            for item in response.get('content', []):
                filtered_item = {key: item.get(key) for key in keys_to_keep}
                transformed_data.append(filtered_item)
        return transformed_data

    # Initialize and run the API client with the user-defined function
    api_client = APIClient(urls, process_response_function=custom_process_response_function)
    api_client.run()

    combined_data = api_client.get_transformed_data()
    failed_requests = api_client.get_failed_requests()

    return combined_data, failed_requests
