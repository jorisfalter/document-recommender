from flask import Flask, request, jsonify
import requests

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the OpenAI API key
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DATABASE_ID = os.getenv('DATABASE_ID')

app = Flask(__name__)

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

@app.route('/fetch_notion', methods=['GET'])
def fetch_notion():
    query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    response = requests.post(query_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        min_time_to_review = float('inf')
        result_record = None
        # print(data["results[0]"])

        for page in data["results"]:
            properties = page["properties"]
            time_to_review_object = properties["Time To Review"]
            time_to_review_formula= time_to_review_object["formula"]
            time_to_review = time_to_review_formula["number"]
            # print(properties["Title"])
            # input("Press Enter to continue...")
            if time_to_review is not None and time_to_review < min_time_to_review:
                min_time_to_review = time_to_review
                link_rich_text = properties.get("Link",{}).get("rich_text",[{}])
                # link_rich_text_zero = link_rich_text[0]
                # print(link_rich_text)
                result_record = {
                    "title": properties.get("Title", {}).get("title", [{}])[0].get("plain_text", ""),
                    # "link": link_rich_text[0].get("plain_text",""),
                    "last_review_date": properties.get("Last Review", {}).get("date", {}).get("start")
                }

                # {'id': 'title', 'type': 'title', 'title': [{'type': 'text', 'text': {'content': 'Goals long term', 'link': None}, 'annotations': {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False, 'code': False, 'color': 'default'}, 'plain_text': 'Goals long term', 'href': None}]}

        if result_record:
            result_record['min_time_to_review'] = min_time_to_review
            return jsonify(result_record)
 
        else:
            return jsonify({"error": "No valid entries"}), response.status_code
    
    else:
        return jsonify({"error": "Failed to fetch data"}), response.status_code


# fetching data to see what the json looks like
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

def append_blocks_to_page_recommend_first():

    url = f"https://api.notion.com/v1/blocks/026361d8-21fb-4494-9384-a1581eb5f5d0"
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        # "children": [{
        #     "object": "block",
        #     "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": "New Document v2"
                },
                "annotations": {
                    "bold": True,
                    "italic": False,
                    "strikethrough": False,
                    "underline": False,
                    "code": False,
                    "color": "yellow"
                }
            }]
        }
        # }]
    }
    
    response = requests.patch(url, headers=headers, json=data)
    print(response.text)

    # now do the date
    url = f"https://api.notion.com/v1/blocks/1e38be9f-d9b3-4c70-9966-89439260613d"
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        # "children": [{
        #     "object": "block",
        #     "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "mention",
                "mention": {
                    "type": "date",
                    "date": {
                        "start":"2024-05-01"
                    }
                }
            }]
        }
        # }]
    }

    response = requests.patch(url, headers=headers, json=data)

    return response.text

## Call the functions
# update_notion_title()
append_blocks_to_page_recommend_first()
# fetch_data_for_testing()

## run it in the browser
# if __name__ == '__main__':
#     app.run(debug=True)


