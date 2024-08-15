import requests
import time
import json
from datetime import datetime, timezone
import dateutil
import dateutil.parser
from pydantic import BaseModel
import bittensor as bt
from apify_client import ApifyClient
import os





class miner_selfcheck:



    def miner_check(self, result, query):
        channel_id = query.channel_ids[0]
        # channel_id = '1214225551364202496' #subnet 5 
        flag = 1
        for doc in result:
            doc_id = doc["id"]
            DISCORD_MESSAGE_VALIDATE_API_URL = (
                "https://hx36hc3ne0.execute-api.us-west-2.amazonaws.com/dev/discord/{msg_id}"
            )

            discord_msg_validate_url = DISCORD_MESSAGE_VALIDATE_API_URL.format(
                msg_id=doc_id
            )
            response = requests.get(discord_msg_validate_url)
            # response = requests.get(url, headers=headers)
            # print("response code = ", response.status_code)
            # print(messages_100)
            if response.status_code != 200:
                print("Failed with doc_id")
                return False
            groundtruth = response.json()
            try:
                if groundtruth["id"] != doc_id:
                    bt.logging.warning(
                        f"Discord message id {doc_id} not match url id {groundtruth['id']}"
                    )
                    flag = 0
                    break
                if groundtruth["text"] != doc["text"]:
                    bt.logging.warning(
                        f"Document text {doc['text']} not match ground truth {groundtruth['text']}"
                    )
                    flag = 0
                    break
                if groundtruth["author_username"] != doc["author_username"]:
                    bt.logging.warning(
                        f"Document author_username {doc['author_username']} not match ground truth {groundtruth['author_username']}"
                    )
                    flag = 0
                    break
                if dateutil.parser.isoparse(
                    groundtruth["created_at"]
                ) != dateutil.parser.isoparse(doc["created_at"]):
                    bt.logging.warning(
                        f"Document created_at {doc['created_at']} not match ground truth {groundtruth['created_at']}"
                    )
                    flag = 0
                    break

            except Exception as e:
                bt.logging.error(f"Error while validating discord message: {e}")
                flag = 0
                break

        if query.author_usernames is not None:
            if not all(
                doc["author_username"] in query.author_usernames
                for doc in result
            ):
                bt.logging.warning(
                    f"Author username not in query author usernames {query.author_usernames}"
                )
                flag = 0
               

        # if query.sort_by == SortType.RECENCY:
        #     # check if the response is sorted by recency
        #     if not all(
        #         dateutil.parser.isoparse(a["created_at"])
        #         > dateutil.parser.isoparse(b["created_at"])
        #         for a, b in zip(result, result[1:])
        #     ):
        #         bt.logging.warning("result not sorted by recency")
        #         # not sorted by recency
        #         flag = 0
        #         break

        if query.channel_ids is not None:
            if not all(
                doc["channel_id"] in query.channel_ids for doc in result
            ):
                bt.logging.warning(
                    f"Channel id not in query channel ids {query.channel_ids}"
                )
                flag = 0
              

        # check if the response is within the time range filter
        if query.earlier_than_timestamp is not None:
            if not all(
                dateutil.parser.isoparse(doc["created_at"]).timestamp()
                < query.earlier_than_timestamp
                for doc in result
            ):
                bt.logging.warning(
                    f"created_at {doc['created_at']} is later than earlier_than_timestamp {query.earlier_than_timestamp}"
                )
                flag = 0
         
        if query.later_than_timestamp is not None:
            if not all(
                dateutil.parser.isoparse(doc["created_at"]).timestamp()
                > query.later_than_timestamp
                for doc in result
            ):
                bt.logging.warning(
                    f"created_at {doc['created_at']} is earlier than later_than_timestamp {query.later_than_timestamp}"
                )
                flag = 0
           
        if flag == 0 :
            return False
        else :
            return True


            
            
        
