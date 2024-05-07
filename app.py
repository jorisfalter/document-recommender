from flask import Flask, request, jsonify
import requests
import json


import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the OpenAI API key
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DATABASE_ID = os.getenv('DATABASE_ID')

app = Flask(__name__)


# first we check if any of the dates have been updated recently
def check_if_new_date():
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    url_reco1_last = f"https://api.notion.com/v1/blocks/d2b57791-2bce-4b60-bd3d-82cf11f2f4ce"
    
    # !! dit is text geen datum maar een string
    response = requests.get(url_reco1_last, headers=headers)
    # print(response.json())
    getParagraph = response.json()["paragraph"]
    getRichText = getParagraph["rich_text"][0]
    getText = getRichText["text"]
    getContent = getText["content"]
    print(getContent)

    # dit is wel een datum 
    url_reco1_new = f"https://api.notion.com/v1/blocks/466cdb80-63a6-4d05-b04f-ddb6d0672c14"

    response = requests.get(url_reco1_new, headers=headers)
    getParagraph = response.json()["paragraph"]
    getRichText = getParagraph["rich_text"][0]
    getPlainText = getRichText["plain_text"]
    print(getPlainText)



    ## nu datums vergelijken, als ze gelijk zijn gelijk naar stap 3: eerste en tweede uit de tabel halen, anders eerst naar stap 2: de tabel updaten
    ## dan ook voor de 2e recommendation
    ## idealiter zouden we de "last review" in een meer leesbaar formaat houden



# @app.route('/fetch_notion', methods=['GET'])
def fetch_notion():
    query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    response = requests.post(query_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        min_time_to_review = float('inf')
        result_record = None
        # print(data)
        # print(data["results"])

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
                result_record = {
                    "title": properties.get("Title", {}).get("title", [{}])[0].get("plain_text", ""),
                    # "link": link_rich_text[0].get("plain_text",""),
                    "last_review_date": properties.get("Last Review", {}).get("date", {}).get("start")
                }
                print(result_record)


                # {'id': 'title', 'type': 'title', 'title': [{'type': 'text', 'text': {'content': 'Goals long term', 'link': None}, 'annotations': {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False, 'code': False, 'color': 'default'}, 'plain_text': 'Goals long term', 'href': None}]}

        if result_record:
            result_record['min_time_to_review'] = min_time_to_review
            return json.dumps(result_record)  # Using json.dumps instead of jsonify
            print(result_record)
 
        else:
            return json.dumps({"error": "No valid entries"}), 404  # Error handling
            print("no valid entries")
    
    else:
        return json.dumps({"error": "Failed to fetch data"}), response.status_code
        print("Failed to fetch data")


def append_blocks_to_page_recommend_first():

    url = f"https://api.notion.com/v1/blocks/026361d8-21fb-4494-9384-a1581eb5f5d0"
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # update the project title
    data = {
        # "children": [{
        #     "object": "block",
        #     "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": "Project Ideas"
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

    # update the date
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
                        "start":"2024-03-01"
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
# append_blocks_to_page_recommend_first()
# fetch_data_for_testing()
# fetch_notion()
check_if_new_date()

## run it in the browser
# if __name__ == '__main__':
#     app.run(debug=True)




################################# testing functions

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