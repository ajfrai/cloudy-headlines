import requests 

requests.get('https://x8p4l9hrib.execute-api.us-east-1.amazonaws.com/default/grab-headlines',
	headers = {'x-api-key':os.environ['lambda_api_key']}).text