import requests
import os
import json
import pandas as pd
from tqdm import tqdm

import time

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = "AAAAAAAAAAAAAAAAAAAAAD%2FZWwEAAAAAJgG8hY2XJfmsYbbs%2Bp5BruRr8aM%3DtRxrtqs0eEhHQ9ZFE9U7tRlNnqm7oPUXeQEijSnj3RgxWgvN5l"


# curl "https://api.twitter.com/2/tweets?ids=1000018438184734720,999992400725585920" \
#   -H "Authorization: Bearer AAAAAAAAAAAAAAAAAAAAAD%2FZWwEAAAAAJgG8hY2XJfmsYbbs%2Bp5BruRr8aM%3DtRxrtqs0eEhHQ9ZFE9U7tRlNnqm7oPUXeQEijSnj3RgxWgvN5l"




search_url = "https://api.twitter.com/2/tweets?"

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()



def main():
    data = pd.read_csv("snopes_clean.csv")

    all_ids = data.id.tolist()
    info = {"missing":[], "ok":[], "auth":[], "other":[]}
    for i in tqdm(range(0, len(all_ids), 100)):
        
        str_ugly = str(all_ids[i:i+100]).replace("[", "").replace("]", "").replace(" ", "")

        query_params = {'ids': str_ugly}

        json_response = connect_to_endpoint(search_url, query_params)

        tweets = [tweet['id'] for tweet in json_response["data"]]
        deleted_errors = [i["value"] for i in json_response["errors"] if i["title"] == "Not Found Error"]

        auth_errors = [i["value"] for i in json_response["errors"] if i["title"] == "Authorization Error"]
        
        two_errors = deleted_errors + auth_errors
        other_errors = [i for i in json_response["errors"] if i["value"] not in two_errors]
        
        info["missing"]+=deleted_errors
        info["ok"]+=tweets
        info["auth"]+=auth_errors
        info["other"]+=other_errors
        # time.sleep(3)
    
    # data = data.set_index("id")
    # for key, value in info.items():
    #     data.loc[value, "available"] = key

    # data["tweet"] = data.id.map(info)

    print(data)
    data.to_csv("tweet_info.csv", index=False)
    with open("json_data.json","w") as wfile:
        import json
        json.dump(info, wfile)

if __name__ == "__main__":
    main()