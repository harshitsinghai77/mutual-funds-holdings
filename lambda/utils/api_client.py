import asyncio
import aiohttp
import requests

class APIClient:
    def __init__(self, urls, process_response_function):
        self.url = urls
        self.isAsync = False
        self.process_response_function = process_response_function
        self.transformed_data = []
        self.failed_requests = []

    async def fetch(self, session, url):
        try:
            async with session.get(url, ssl=False) as response:
                response.raise_for_status()
                
                content_type = response.headers.get('Content-Type', '').lower()
                if 'application/json' in content_type: 
                    return await response.json() 
                if 'text/html' in content_type: 
                    return await response.text
                
                # Default to JSON return
                return response.json()
        except Exception as e:
            print(f"Request to {url} failed: {e}")
            self.failed_requests.append(url)
            return None

    async def async_requests(self):
        print("Using async call to fetch data from external API...")

        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch(session, url) for url in self.url]
            responses = await asyncio.gather(*tasks)
            return responses

    # Getter for transformed data 
    def get_transformed_data(self): 
        return self.transformed_data 
    
    # Getter for failed requests 
    def get_failed_requests(self): 
        return self.failed_requests
    
    def sync_request(self):
        try: 
            print("Using sync call to fetch data from external API...")
            response = requests.get(self.url) 
            response.raise_for_status() 
            
            content_type = response.headers.get('Content-Type', '').lower() 
            if 'application/json' in content_type: 
                return response.json() 
            if 'text/html' in content_type: 
                return response.text
            
            # Default to JSON return
            return response.json()
        except Exception as e:
            print(f"Request to {self.url} failed: {e}")
            self.failed_requests.append(self.url)
            return None

    def run(self):
        if isinstance(self.url, list):
            response = asyncio.run(self.async_requests())
        
        elif isinstance(self.url, str):
            response = self.sync_request()

        self.transformed_data = self.process_response_function(response)
