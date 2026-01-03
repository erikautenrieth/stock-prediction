import requests
import json

url = "https://eu-central-1.aws.data.mongodb-api.com/app/data-ofjll/endpoint/data/v1/action/findOne"
payload = json.dumps({
    "collection": "<COLLECTION_NAME>",
    "database": "<DATABASE_NAME>",
    "dataSource": "Cluster0",
    "projection": {
        "_id": 1
    }
})
headers = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers': '*',
    'api-key': 'DmSdCCzT0KyRFjFAE9cLKpjkjTdv3JHnsRzfYrVfffvqLkLxAjUeDkyo4soobyHV',
}
response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)