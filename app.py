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

@app.route('/update_notion', methods=['POST'])
def update_notion():
    # Assuming JSON payload in the form of {"page_id": "...", "properties": {...}}
    data = request.json
    page_id = data['page_id']
    properties = data['properties']

    update_url = f"https://api.notion.com/v1/pages/{page_id}"
    
    # Prepare the payload based on Notion API requirements
    payload = {
        "properties": properties
    }

    response = requests.patch(update_url, headers=headers, json=payload)
    return response.text

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
            print(properties["Title"])
            input("Press Enter to continue...")
            if time_to_review is not None and time_to_review < min_time_to_review:
                min_time_to_review = time_to_review
                result_record = {
                    "title": properties.get("Title", {}).get("title", [{}])[0].get("plain_text", ""),
                    "title - link": properties.get("Title", {}).get("title", [{}])[0].get("plain_text", ""),
                    "last_review_date": properties.get("Last Review", {}).get("date", {}).get("start")
                }

        if result_record:
            result_record['min_time_to_review'] = min_time_to_review
            return jsonify(result_record)
 
        else:
            return jsonify({"error": "No valid entries"}), response.status_code
    
    else:
        return jsonify({"error": "Failed to fetch data"}), response.status_code

## nu ik de de data heb, moet ik de lowest time to review vinden, en de corresponderende column. 



if __name__ == '__main__':
    app.run(debug=True)
