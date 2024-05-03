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


# @app.route('/update_notion', methods=['PATCH'])
def update_notion():
    # # Assuming JSON payload in the form of {"page_id": "...", "properties": {...}}
    # data = request.json
    # properties = data['properties']

    # update_url = f"https://api.notion.com/v1/pages/test-ui-29c5ec3ab47f4106862f472e7d709ae9"
    
    # # Prepare the payload based on Notion API requirements
    # payload = {
    #     "properties": properties
    # }

    # response = requests.patch(update_url, headers=headers, json=payload)
    # return response.text

    

    # It should be a 32 character long string. Format this value by inserting hyphens (-) in the following pattern: 8-4-4-4-12 (each number is the length of characters between the hyphens).
    # Example: 1429989fe8ac4effbc8f57f56486db54 becomes 1429989f-e8ac-4eff-bc8f-57f56486db54.

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
                "title": [{ "type": "text", "text": { "content": "A note from your pals at Notion" } }]
             }
        }
    }   

    response = requests.patch(url, headers=headers, json=data)

    print(response.text)

# Call the function
update_notion()

# if __name__ == '__main__':
#     app.run(debug=True)
