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
        return jsonify(data)
    else:
        return jsonify({"error": "Failed to fetch data"}), response.status_code


if __name__ == '__main__':
    app.run(debug=True)
