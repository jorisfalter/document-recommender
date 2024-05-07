# from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the OpenAI API key
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DATABASE_ID = os.getenv('DATABASE_ID')

# app = Flask(__name__)

################################# 
## testing functions
## needs headers from app.py

def append_blocks_to_page_test():
    url = f"https://api.notion.com/v1/blocks/29c5ec3a-b47f-4106-862f-472e7d709ae9/children"
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "children": [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": "You made this page using the Notion API. Pretty cool, huh? We hope you enjoy building with us."
                    }
                }]
            }
        }]
    }
    response = requests.patch(url, headers=headers, json=data)
    # print(response.text)

    return response.text

# fetching data to see what the json looks like - for testing purposes only
def fetch_data_for_testing():
    url = f"https://api.notion.com/v1/blocks/1e38be9f-d9b3-4c70-9966-89439260613d"
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    response = requests.get(url, headers=headers)
    # if response.status_code == 200:
    print(response.json())
            # return jsonify(response)



## update title - not required - for testing purposes only
# @app.route('/update_notion', methods=['PATCH'])
def update_notion_title():
    url = f"https://api.notion.com/v1/pages/29c5ec3a-b47f-4106-862f-472e7d709ae9"

    headers = {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }

    data = {
        "properties": {
            "title": {
                "type": "title",
                "title": [{ "type": "text", "text": { "content": "An update from your pals at Notion" } }]
             }
        }
    }   

    response = requests.patch(url, headers=headers, json=data)
    # print(response.text)