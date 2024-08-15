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
from .llm_evaluator import llm_evaluator
from dotenv import load_dotenv

class sync_update:

    def __init__(self):
        load_dotenv()

    def update(self, discord_channel_id):
        # channel_id = discord_channel_id
        channel_id = '1214225551364202496' #subnet 5
        bt.logging.info(f"this is start of information channel_id =  {channel_id}")
        # days_ago = 1  # Retrieve messages from 1 day ago
        limit = 11
        before = None
        meaningful_messages = []
        return_messages = []
        # get id of the last message for this channel          https://discord.com/channels/799672011265015819/1214225551364202496/1260224382341746728
        filtered_messages = []
        recent_messages = []

        should_break = 0
        
        while True:
            # fetch messages
            print("enter in get_discord_messages")
            messages_cur = self.get_discord_messages(channel_id, limit=limit, before=before)
            print("message length = ", len(messages_cur))
            messages = messages_cur
            # print("last of 10 message is as follows")
            # print(messages[9]["content"])
            # print("passed number of messages_cur = ", len(messages))
            if len(messages) == 0:
                print("len(messages) ==0 this is error")
                break
            llm = llm_evaluator()
            llm_ranking_scores = llm.llm_rank_evaluator(messages)
            # llm_ranking_scores = [1] * len(messages)
            # llm_ranking_scores = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
            current_time = datetime.now(timezone.utc)
            for i, message in enumerate(messages):
                if llm_ranking_scores[i] == 1:
                    if ((current_time - datetime.fromisoformat(message["timestamp"].rstrip("Z"))).days >= 1) :
                        should_break = 1
                        break
                    filtered_messages.append(message)
            # if is_first_get:
            #     for i, message in enumerate(messages):
            #         cur = {
            #             "channel_id": channel_id,
            #             "server_name": "Bittensor",
            #             "server_id": "Bittensor",
            #             "id": message["id"],
            #             "text": message["content"],
            #             "author_username": message["author"]["username"],
            #             "created_at": message["timestamp"]
            #         }
                
            print("passed checking")
            return_messages = [
                {
                    "channel_id": channel_id,
                    "server_name": "Bittensor",
                    "server_id": "Bittensor",
                    "id": message["id"],
                    "text": message["content"],
                    "author_username": message["author"]["username"],
                    "created_at": message["timestamp"],
                } for message in filtered_messages
            ]
            before = messages[len(messages) - 1]["id"]
            print("before is follows ", before)
                         
            print("return_messages is as follows")
            # print(return_messages[-5:])


            if should_break == 1:
                break
        # print("return values", return_messages)    
        last_message_ids = {}
        last_message_ids[channel_id] = before
        json.dump(last_message_ids, open("last_messages.json", "w"))
        
        data = {
            channel_id : return_messages
        }
        with open("ans_channels.json", "w") as f:
            json.dump(data, f, indent=4)
                




    def get_discord_messages(self, channel_id, limit=10, before = None):
        print("I am in channel get messages")
        DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
        headers = {
                'Authorization': {DISCORD_TOKEN},
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15',
            'Content-Type': 'application/json'
        }
        # url = f"https://discord.com/api/v9/channels/{channel_id}/messages?&after{timestamp}&fields=id,timestamp,length(content)"
        url = f'https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}'
        if before:
            url += f'&before={before}'
        print(url)
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("success response")
            messages = response.json()
            return messages
        
        else:
            print(f'Failed to fetch messages: {response.status_code} - {response.text}')

        # print("response code = ", response.status_code)
        