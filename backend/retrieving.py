import requests

# Getting data from free api
'''
def fetching_data():
    url = "https://newsdata.io/api/1/latest" # URL of the NewsData.io.
    api_key = "pub_62108a7e5227904699c28d0b0d322ef7c5631" # API key

    params = {
        "apikey": api_key,
        "language": "en"  # Language filter
        #"category": "business",  # Category filter
        #"country": "bd",  # Country filter
        #"page": 1  # Pagination
    }

    response = requests.get(url, params=params)
   
    if response.status_code == 200:  # Check for successful HTTP response
        data = response.json()  # Parse JSON

        # Debugging
        #print("API Response:", data)
        
        # Ensure the expected data exists
        if "results" in data and data["results"]:
            articles = []
            for article in data["results"]:
                # Extract fields, with default values if not present
                date = article.get("pubDate")
                description = article.get("description")
                #category = article.get("category")
                #country = article.get("country")
                category = ", ".join(article.get("category", [])) if isinstance(article.get("category"), list) else article.get("category", "")
                country = ", ".join(article.get("country", [])) if isinstance(article.get("country"), list) else article.get("country", "")

                title = article.get("title", "")
                link = article.get("link", "")
                # Append articles in array
                articles.append({
                    'date': date,
                    'description': description,
                    'category': category,
                    'country': country,
                    'title': title,
                    'link': link
                })
            return articles
        else:
            raise Exception("No results found in the response.")
    else:
        print(f"HTTP Error {response.status_code}: {response.text}")
        raise Exception(f"Failed to fetch data. HTTP Status Code: {response.status_code}")

    
try:
    articles = fetching_data()
    for article in articles:
        print(f"Date: {article['date']}\nCategory: {article['category']}\nCountry: {article['country']}\nTitle: {article['title']}\nDescription: {article['description']}\nLink: {article['link']}")
except Exception as e:
    print(f"Error: {e}")
'''

import requests

# Getting data from free API
def fetching_data():
    url = "https://newsdata.io/api/1/latest"  # URL of the NewsData.io
    api_key = "pub_62108dce5cd6981efd750ebc06be71d34dd46"  

    params = {
        "apikey": api_key,
        "language": "en"  # Language filter
    }

    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()  # Parse JSON response

        # Debugging: Print the API response to inspect structure
        print("API Response:", data)

        # Ensure the 'results' field exists and is not empty
        if "results" in data and data["results"]:
            articles = []
            for article in data["results"]:
                # Extract fields with defaults to handle missing data
                date = article.get("pubDate", "Unknown Date")  # Use "Unknown Date" if missing
                description = article.get("description", "No description available.")
                category = ", ".join(article.get("category", [])) if isinstance(article.get("category"), list) else article.get("category", "")
                country = ", ".join(article.get("country", [])) if isinstance(article.get("country"), list) else article.get("country", "")
                title = article.get("title", "Untitled")
                link = article.get("link", "No link available.")

                # Append formatted data into the articles list
                articles.append({
                    'date': date,
                    'description': description,
                    'category': category,
                    'country': country,
                    'title': title,
                    'link': link
                })
            return articles
        else:
            print("No results found in the response.")
            return None
    elif response.status_code == 401:
        print("Error: Invalid API key. Please verify your API key and try again.")
        return None
    else:
        print(f"HTTP Error {response.status_code}: {response.text}")
        return None


# Fetch and display articles
try:
    articles = fetching_data()
    if articles:
        for article in articles:
            print(f"Date: {article['date']}\nCategory: {article['category']}\nCountry: {article['country']}\nTitle: {article['title']}\nDescription: {article['description']}\nLink: {article['link']}\n")
    else:
        print("No articles available.")
except Exception as e:
    print(f"Error: {e}")
