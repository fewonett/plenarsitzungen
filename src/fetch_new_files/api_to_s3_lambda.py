""" The code in this file:
    1. Identifies the date of the newest Plenarsitzung in the S3 bucket
    2. Fetches all newer xml files from the Bundestag API/ website 
    3. Uploads them to the S3 bucket
"""

import boto3
import os
import re
import requests
import time

def lambda_handler(event, context):
    s3 = boto3.client(
        's3'
    )
    bucket_name = os.environ["S3_BUCKET_NAME"]
    
    filenames = fetch_s3_filenames(s3, bucket_name)
    newest_date = get_newest_date(filenames)
    result = fetch_and_upload_new_xml(newest_date, s3, bucket_name)
    if result != 0:
        return(result)
    print("\n################################")
    print("Upload of all files successful!")
    print("################################\n")
    return {
        "statusCode": 200,
        "body": "Upload of all files successful!"
    }


def fetch_s3_filenames(s3, bucket_name):
    """Fetches all filenames in the S3 Bucket and returns them as a list"""
    response = s3.list_objects_v2(Bucket=bucket_name)
    filenames = [res["Key"] for res in response["Contents"]]
    return filenames
    
    
def extract_date(filename):
    match = re.search(r"\d{4}-\d{2}-\d{2}", filename)
    return match.group(0) if match else None


def get_newest_date(filenames):
    dates = sorted([extract_date(filename) for filename in filenames])
    newest_date = dates[-1]
    return(newest_date)


def save_to_s3(filename,
               text,
               s3,
               bucket_name):
    """ This function takes in a filename and text and saves the file as an xml in the s3""" 
    try:
        s3.put_object(
            Bucket = bucket_name,
            Key = filename,
            Body = text,
            ContentType = 'application/xml'
        )
    except Exception as e:
        raise Exception(f"Something went wrong uploading to S3: {e}")
    
    print(f"Saved file {filename} succesfully\n")
    return 0

def fetch_and_upload_new_xml(newest_date,
                             s3,
                             bucket_name):
    """This function fetches all Plenarsitzungen from the Bundestag API, which are newer than the newest date and then saves them to S3"""
    
    BUNDESTAG_KEY = os.environ["BUNDESTAG_KEY"]
    URL = f"https://search.dip.bundestag.de/api/v1/plenarprotokoll?f.zuordnung=BT&f.datum.start={newest_date}"
    
    headers = {
    "Authorization": f"ApiKey {BUNDESTAG_KEY}"
    }
    
    params = {
    "size": 100, # api max request size
    }
    
    response = requests.get(URL, headers=headers, params=params)
    if response.status_code != 200:
            raise Exception(f"Something went wrong with the Bundestag API. Response Code: {response.status_code}")
        
    res = response.json()
    if res["numFound"] > 100:
        raise Exception("More than 100 new documents - cursor logic implementation necessary: See Bundestag API docs")
    
    docs = res["documents"]   
    docs = [doc for doc in docs if doc["fundstelle"]["datum"] != newest_date]
    if not len(docs):
        print("No new files were found.")
        return {
        "statusCode": 200,
        "body": "No new files. Lambda completed without changes."
        }
    
    documents_ls = [
        {'xml_url':doc['fundstelle']['xml_url'],
        'date':doc['fundstelle']['datum'],
        'doc_nr':doc['fundstelle']['dokumentnummer']}
            for doc in docs
            ]
    
    for doc in documents_ls:
        doc_nr = doc['doc_nr'].replace('/', '_')
        date = doc['date']
        response = requests.get(doc['xml_url'])
        if response.status_code != 200:
            raise Exception(f"Could not fetch XML file: Status code: {response.status_code}")
        
        text = response.content
        filename = f"plenarsitzung_{doc_nr}_{date}.xml"
        save_to_s3(filename, text, s3, bucket_name)
        time.sleep(0.5)
    return 0

