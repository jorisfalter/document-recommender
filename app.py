import requests
import json
from datetime import datetime
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the OpenAI API key
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
DATABASE_ID = os.getenv('DATABASE_ID')


## first URLs
# last review
url_reco1_last = f"https://api.notion.com/v1/blocks/d2b57791-2bce-4b60-bd3d-82cf11f2f4ce"
# new last review date
# dit is wel een datum in Notion maar hier in Python pakken we de plain text
url_reco1_new = f"https://api.notion.com/v1/blocks/466cdb80-63a6-4d05-b04f-ddb6d0672c14"
url_reco1_title = f"https://api.notion.com/v1/blocks/026361d8-21fb-4494-9384-a1581eb5f5d0"
url_reco2_last = f"https://api.notion.com/v1/blocks/32040b5a-b45c-471b-8ef3-b075853612cd"
url_reco2_new = f"https://api.notion.com/v1/blocks/8505ec27-d3ef-401b-af9f-666458925c77"
url_reco2_title = f"https://api.notion.com/v1/blocks/2dc01f9a-d57c-4dcd-9fc2-348f4685bf1a"


# 1 first we check if any of the dates have been updated recently on the UI
# 2 if they have been, we have to update the table
def check_if_new_date(url_reco_last,url_reco_new,url_reco_title):
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # !! dit is text geen datum maar een string
    response = requests.get(url_reco_last, headers=headers)
    # print(response.json())
    getParagraph = response.json()["paragraph"]
    getRichText = getParagraph["rich_text"][0]
    getText = getRichText["text"]
    last = getText["content"]
    # print(type(getContent))



    response = requests.get(url_reco_new, headers=headers)
    getParagraph = response.json()["paragraph"]
    getRichText = getParagraph["rich_text"][0]
    newLast = getRichText["plain_text"]

    ## nu datums vergelijken
    if last == newLast:
        print("no changes to db")
    else:
        ### Stap 2: de tabel updaten
        # convert both dates to string
        # The format of the date string
        date_format = "%Y-%m-%d"
        lastReview = datetime.strptime(last, date_format)
        newLastReviewDate = datetime.strptime(newLast, date_format)
        if newLastReviewDate > lastReview:
            # eerst juist rij vinden
            # dan datum cell vinden
            # dan datum cell updaten
            response = requests.get(url_reco_title, headers=headers)
            getParagraph = response.json()["paragraph"]
            getRichText = getParagraph["rich_text"][0]
            getText = getRichText["text"]
            docTitle = getText["content"]
            # print(docTitle)
           
            # find the row in the table
            db_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
            data = {
                    "filter":{
                        "and":[{
                            "property": "Title",
                            "rich_text": {
                                "equals": docTitle
                            }
                        }]
                    }
            }
            response = requests.post(db_url, headers=headers, json=data)

            # after filtering, find the date in the db
            if response.status_code == 200:
                results = response.json().get("results", [])
                cell_page_id = results[0]["id"]
                # print(cell_page_id)

                if results:
                    # "Last Review" is a date property, but I think it's stored in the variable as a string
                    last_review_date = results[0]["properties"]["Last Review"]["date"]["start"]
                    # hence why we have to convert to a date
                    last_review_date_db = datetime.strptime(last_review_date, date_format)

                    if newLastReviewDate > last_review_date_db:

                        # print("db date is lower than entered date - ok")
                        # print(newLastReviewDate.strftime('%Y-%m-%d'))

                        # hier moeten we de datum in de db updaten 
                        cell_url = f"https://api.notion.com/v1/pages/{cell_page_id}"
                        data = {
                            "properties": {
                                "Last Review": {  # This should match the exact name of the date property in Notion
                                    "date": {
                                        "start": newLastReviewDate.strftime('%Y-%m-%d'),
                                        "end": None  # You can set an end date if applicable
                                    }
                                }
                            }
                        }

                        response = requests.patch(cell_url, headers=headers, json=data)
                        if response.status_code == 200:
                            print("Date updated successfully.")
                            return response.json()  # Returns the updated page object
                        else:
                            print("Failed to update date:", response.status_code)
                            print(response.text)
                            return None

                    else:
                        print("db date is higher than entered date - error") 
                else:
                    return "No matching records found."
                    print("error")
            else:
                return "Failed to fetch data: " + response.text
                print("error")

            print("date changed")

        else: 
            print("something wrong")

    ## dan ook voor de 2e recommendation

# supporting function to update the Notion UI
def patch_endpoint(field, url, data):
    headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
            print(field + " updated successfully.")
    else:
        print("Failed to update " + field, response.status_code)
        print(response.text)

# 3 find the minimum time to review in the database and update the ui
def fetch_db_entries():
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
        second_min_time_to_review = float('inf')  # Second smallest
        result_record = None
        result_record_second = None


        for page in data["results"]:
            properties = page["properties"]
            time_to_review_object = properties["Time To Review"]
            time_to_review_formula= time_to_review_object["formula"]
            time_to_review = time_to_review_formula["number"]

            if time_to_review is not None:
                if time_to_review < min_time_to_review:
                    # Update second min to the old min
                    second_min_time_to_review = min_time_to_review
                    result_record_second = result_record

                    # Update the min to the new lowest value
                    min_time_to_review = time_to_review
                    result_record = {
                        "title": properties.get("Title", {}).get("title", [{}])[0].get("plain_text", ""),
                        "last_review_date": properties.get("Last Review", {}).get("date", {}).get("start")
                    }
                elif time_to_review < second_min_time_to_review:
                    # Update the second lowest value if this value is less than the second min but greater than min
                    second_min_time_to_review = time_to_review
                    result_record_second = {
                        "title": properties.get("Title", {}).get("title", [{}])[0].get("plain_text", ""),
                        "last_review_date": properties.get("Last Review", {}).get("date", {}).get("start")
                    }

        if result_record:
            
            # print(result_record)
            url_reco1_date = f"https://api.notion.com/v1/blocks/d2b57791-2bce-4b60-bd3d-82cf11f2f4ce"
            url_reco1_date_last = f"https://api.notion.com/v1/blocks/466cdb80-63a6-4d05-b04f-ddb6d0672c14" # need this because it's not event based but cron based

            # print(result_record_second)
            url_reco2_date = f"https://api.notion.com/v1/blocks/32040b5a-b45c-471b-8ef3-b075853612cd"
            url_reco2_date_last = f"https://api.notion.com/v1/blocks/8505ec27-d3ef-401b-af9f-666458925c77" # need this because it's not event based but cron based
                 
            ### update title
            data = {
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": result_record["title"]
                            }
                        }]
                }
            }
            patch_endpoint("first title", url_reco1_title, data)

            ### update Last Review date
            data = {
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": result_record["last_review_date"]
                            }
                        }]
                }
            }
            patch_endpoint("first last review date", url_reco1_date, data)

            ### also update the New Last Review Date so these stay in sync 
            data = {
                "paragraph": {
                    "rich_text": [{
                        "mention": {
                            "date": {
                                "start": result_record["last_review_date"]
                            }
                        }
                    }]
                }
            }
            patch_endpoint("first new last review date", url_reco1_date_last, data)

            ### update second title
            data = {
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": result_record_second["title"]
                            }
                        }]
                }
            }
            patch_endpoint("second title", url_reco2_title, data)

            ### update second Last Review date
            data = {
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": result_record_second["last_review_date"]
                            }
                        }]
                }
            }
            patch_endpoint("second last review date", url_reco2_date, data)

            ### also update second New Last Review Date so these stay in sync 
            data = {
                "paragraph": {
                    "rich_text": [{
                        "mention": {
                            "date": {
                                "start": result_record_second["last_review_date"]
                            }
                        }
                    }]
                }
            }
            patch_endpoint("second new last review date", url_reco2_date_last, data)

            return json.dumps(result_record)  
 
        else:
            print("no valid entries")
            return json.dumps({"error": "No valid entries"}), 404  # Error handling

    else:
        print("Failed to fetch data")
        return json.dumps({"error": "Failed to fetch data"}), response.status_code


##################################
## Call the functions


while True:
    print("updating DB for first reco")
    check_if_new_date(url_reco1_last,url_reco1_new,url_reco1_title)
    print("updating DB for second reco")
    check_if_new_date(url_reco2_last,url_reco2_new,url_reco2_title)
    print("updating UI")
    fetch_db_entries()
    print("sleeping")
time.sleep(10)  # Sleep for 15 seconds







