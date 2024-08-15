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
import time
from dotenv import load_dotenv
class get_info:

    def __init__(self):
            load_dotenv()

    def information(self, discord_channel_id):
        channel_id = discord_channel_id
        # channel_id = '1214225551364202496' #subnet 5
        bt.logging.info(f"this is start of information channel_id =  {channel_id}")
        # days_ago = 1  # Retrieve messages from 1 day ago
        limit = 5
        before = None
        meaningful_messages = []
        return_messages = []
        # get id of the last message for this channel          https://discord.com/channels/799672011265015819/1214225551364202496/1260224382341746728
        filtered_messages = []
        recent_messages = []
        cnt = 0
        # is_first_time = 0
        should_llm_start = 0
        should_break = 0
        batch_size = 0
        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time        
            if (elapsed_time >= 12.2):
                print(elapsed_time)
                break
            print("this is new loop, cnt = ", cnt)
            print("\n\n")
            print("batch_size = ", batch_size)
            batch_size += 1
            # fetch messages
            print("enter in get_discord_messages")
            messages_cur = self.get_discord_messages(channel_id, limit=limit, before=before)
            print("message length = ", len(messages_cur))
            messages = messages_cur
            current_time = datetime.now(timezone.utc)
            llm_messages = []
            if should_llm_start == 0 :
                for i, message in enumerate(messages):                    
                    if ((current_time - datetime.fromisoformat(message["timestamp"].rstrip("Z"))).days > 1) :
                        recent_messages.append(message)
                        llm_messages.append(message)
                        should_llm_start = 1
                    else:
                        continue
                if len(llm_messages) > 0:
                    llm = llm_evaluator()
                    llm_ranking_score = llm.llm_rank_evaluator(llm_messages)
                    for i, message in enumerate(llm_messages):
                        if llm_ranking_score[i] == 1:
                            filtered_messages.append(message)
                            cnt += 1
                            if (cnt >= 3) :
                                should_break = 1
                                break
            else:
                # if is_first_time == 0:
                #     llm_messages = messages
                #     is_first_time = 1
                # else:
                for message in messages:
                    if len(recent_messages) < 5:
                        recent_messages.append(message)
                    if len(message["content"]) > 50:
                        llm_messages.append(message)
                if len(llm_messages) > 0:
                    llm = llm_evaluator()
                    llm_ranking_scores = llm.llm_rank_evaluator(llm_messages)
                    for i, message in enumerate(llm_messages):
                        if llm_ranking_scores[i] == 1:
                            filtered_messages.append(message)
                            cnt += 1
                            if (cnt >= 2) :
                                should_break = 1
                                break

            # print("last of 10 message is as follows")
            # print(messages[9]["content"])
            # print("passed number of messages_cur = ", len(messages))
            if len(messages) == 0:
                print("len(messages) ==0 this is error")
                break
            # llm_ranking_scores = [1] * len(messages)
            # llm_ranking_scores = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]
            # for i, message in enumerate(messages):
            #     if llm_ranking_scores[i] == 1:
            #         filtered_messages.append(message)
            #         if ((current_time - datetime.fromisoformat(message["timestamp"].rstrip("Z"))).days > 1) :
            #             cnt += 1
            #             if (cnt >= 5) :
            #                 break
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
            
            before = messages[len(messages) - 1]["id"]
            print("before is follows ", before)
            print("return_messages is as follows")
            # print(return_messages[-5:])
            if (should_break == 1) :
                break
            print("cnt is as follows cnt = ", cnt)
        # return return_messages

        filtered_messages = sorted(filtered_messages, key=lambda x: len(x["content"]), reverse = True)

        ids = []
        for message in filtered_messages:
            ids.append(message["id"])
        size_fill = 5 - len(filtered_messages)
        return_size_fill = size_fill
        print("size_fill is ", size_fill)
        for message in recent_messages:
            if  size_fill == 0:
                break
            if message["id"] in ids:
                continue
            else:
                filtered_messages.append(message)
                size_fill -= 1
        print("return_message_length = ", len(return_messages))
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

        return return_messages, return_size_fill
        # print("return values", return_messages)    
        # last_message_ids = {}
        # last_message_ids[channel_id] = before
        # json.dump(last_message_ids, open("last_messages.json", "w"))
        # print("channel_id = ", channel_id)
        # data = {
        #     channel_id : return_messages
        # }
        # print(data)
        # try:
        # # Load the existing data from the JSON file
        #     with open("ans_channel.json", "r") as file:
        #         existing_data = json.load(file)
        # except (FileNotFoundError, json.JSONDecodeError):
        #     # If the file doesn't exist or is empty, start with an empty dictionary
        #     existing_data = {}

        # # Merge the new data with the existing data
        # for key, value in data.items():
        #     if key in existing_data:
        #         existing_data[key].extend(value)
        #     else:
        #         existing_data[key] = value

        # # Save the updated data to the JSON file
        # with open("ans_channel.json", "w") as file:
        #     json.dump(existing_data, file, indent=4)




    def get_discord_messages(self, channel_id, limit=10, before = None):
        print("I am in channel get messages")
        # DISCORD_TOKEN = os.environ["DISCORD_TOKEN"],
        headers = {
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
        