import requests

def get_city_images(city_name, count=6):
    api_key = "MrPT0hTXtqkcQU55t2DOipyFKfXE2wcuhnwro1AgdG0mpMSCPCmG1kgU"
    headers = {
        "Authorization": api_key
    }

    # Search for the city with clearer intent
    query = f"{city_name} city skyline"  # or use "city view", "cityscape", etc.

    params = {
        "query": query,
        "per_page": count
    }

    response = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return [photo["src"]["landscape"] for photo in data["photos"]]

    return []
