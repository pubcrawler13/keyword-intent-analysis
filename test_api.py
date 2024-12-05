import requests

API_TOKEN = "rKMvQKYP6NdrHqVAgZUoqNPvhy4XaGGM7Fpk5Crh"

def test_ahrefs_api():
    url = "https://api.ahrefs.com/v3/serp-overview/serp-overview"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
    }
    params = {
        "keyword": "macerating toilet",  # Example keyword
        "select": "url",                # Only fetch URLs
        "country": "us"                 # Country code
    }
    
    response = requests.get(url, headers=headers, params=params)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

test_ahrefs_api()
