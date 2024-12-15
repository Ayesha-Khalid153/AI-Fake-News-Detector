import requests
import os
import spacy
import schedule
import time
import pandas as pd
from urllib.parse import urlparse
from textblob import TextBlob
from dateutil import parser
from datetime import datetime
def retrieving_data():
    url = "https://newsdata.io/api/1/latest" # URL of the NewsData.io.
    api_key = "pub_62108dce5cd6981efd750ebc06be71d34dd46" # API key

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

    
#try:
#    articles = fetching_data()
    #for article in articles:
        #print(f"Date: {article['date']}\nCategory: {article['category']}\nCountry: {article['country']}\nTitle: {article['title']}\nDescription: {article['description']}\nLink: {article['link']}")
#except Exception as e:
#    print(f"Error: {e}")
nlp = spacy.load("en_core_web_md")

def preprocess_articles(articles):
    

    processed_articles = []
    for article in articles:
        # Skip articles with missing critical data
        if not article.get("title"):
            article["title"] = "N/A"
        elif not article.get("link"):
            article["link"] = "N/A"
        
        # Standardize and enrich data
        #date_str = article.get("pubDate", "")
        #try:
            # Attempt to parse date using dateutil.parser for flexibility
            #date = parser.parse(date_str).strftime("%Y-%m-%d") if date_str else "N/A"
        #except (ValueError, parser.ParserError):
            #date = "Invalid date"

        #date_str = article.get("pubDate")
        #try:
            #if date_str:
                #date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")  
        #    else: 
        #        date = "N/A"
        #except ValueError:
        #    date = "Invalid date"
        '''
        date_str = article.get("pubDate")
        print(f"Raw pubDate: {date_str}")
        if date_str:
            date_formats = [
            "%Y-%m-%dT%H:%M:%SZ",  # ISO 8601
            "%Y-%m-%d %H:%M:%S",   # Space-separated datetime
            "%Y/%m/%d",            # Slash-separated date
            ]
            for fmt in date_formats:
                try:
                    date = datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
                    break  # Stop if a format works
                except ValueError:
                    continue
            else:
            # If no format matches
                print(f"Unable to parse date: {date_str}")
                date = "Invalid date"
        else:
            # Handle missing or empty date
            date = "N/A"
        print(f"Parsed date: {date}")
        '''
        '''
        date_str = article.get("pubDate", "")
        try:
            date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d") if date_str else "N/A"
        except ValueError:
            date = "Invalid date"
        
        description = article.get("description", "N/A")
        description = (description[:150] + "...") if len(description) > 150 else description
        '''
        date = article.get("pubDate")
        # Handle None for description
        description = article.get("description", "")
        description = (description[:150] + "...") if description else "N/A"
        
        #category = ", ".join([cat.strip().title() for cat in article.get("category", []) if isinstance(cat, str)]) else "N/A"
        #country = ", ".join([c.strip().upper() for c in article.get("country", []) if isinstance(c, str)]) else "N/A"
        
        # Ensure category and country are processed correctly
        category = ", ".join([cat.strip().title() for cat in article.get("category", []) if isinstance(cat, str)]) if article.get("category") else "N/A"
        country = ", ".join([c.strip().upper() for c in article.get("country", []) if isinstance(c, str)]) if article.get("country") else "N/A"
        
        domain = urlparse(article['link']).netloc
        sentiment = TextBlob(description).sentiment.polarity

        doc = nlp(description)
        semantic_vector = doc.vector
        
        processed_articles.append({
            'date': date,
            'domain': domain,
            'category': category,
            'country': country,
            'title': article.get("title", "N/A"),
            'description': description,
            'link': article['link'],
            'sentiment': sentiment,
            'semantic_vector': semantic_vector
        })
    
    # Sort articles by date (most recent first)
    processed_articles.sort(key=lambda x: x['date'] or "0000-01-01", reverse=True)
    return processed_articles

def storing_data(articles, file_name = "newdata.xlsx"):
    if os.path.exists(file_name):
        with pd.ExcelWriter(file_name, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                df_new = pd.DataFrame(articles)
                # Write new data at the end of the existing file
                df_new.to_excel(writer, index=False, header=False, sheet_name='Sheet1', startrow=writer.sheets['Sheet1'].max_row)
                print(f"Data has been appended to {file_name}.")
    else:
        df = pd.DataFrame(articles)
        df.to_excel(file_name, index = False)
        print(f"Data saved to {file_name}")

def fetching_data():
    try:
        raw_articles = retrieving_data()
        articles = preprocess_articles(raw_articles)
        storing_data(articles) # Save processed articles to Excel

        for article in articles:
            print(f"Date: {article['date']}\nDomain: {article['domain']}\nCategory: {article['category']}\nCountry: {article['country']}\nTitle: {article['title']}\nDescription: {article['description']}\nLink: {article['link']}\nSentiment: {article['sentiment']:.2f}\n")
    except Exception as e:
        print(f"Error: {e}")

schedule.every(2).minutes.do(fetching_data)

while(True):
    schedule.run_pending()
    time.sleep(60)



