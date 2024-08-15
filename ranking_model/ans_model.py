import json
import requests
from datetime import datetime, timezone
from .rank_model import sort_model
import os
from dotenv import load_dotenv
class ans_model:

    def __init__(self):
        load_dotenv()

    def giving_ans(self, search_query):
        print("i am in giving_ans")
        current_time = datetime.now(timezone.utc)
        channel_id = search_query.channel_ids[0]
        # channel_id = '1214225551364202496'
        with open("ans_channels.json") as f:
            messages_cur = json.load(f)
            messages = messages_cur[channel_id]
            print("messages is fetched in gining_ans module")
        cnt = 0
        cur_array = []
        print("messages_len = ", len(messages))
        for message in messages:
            if ((current_time - datetime.fromisoformat(message["created_at"].rstrip("Z"))).days > 1) :
                cur_array.append(message)
                if (cnt >= 5) :
                    break
        DISCORD_TOKEN = os.environ["DISCORD_TOKEN"],
        headers = {
                'Authorization': {DISCORD_TOKEN},
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15',
            'Content-Type': 'application/json'
        }
        limit = 100
        # url = f"https://discord.com/api/v9/channels/{channel_id}/messages?&after{timestamp}&fields=id,timestamp,length(content)"
        url = f'https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}'
        print(url)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("success response")
            recent_messages = response.json()
        else:
            print(f'Failed to fetch messages: {response.status_code} - {response.text}')
        # return cur_array
        # cnt = 0
        # recent_5_messages = []
        # for msg in recent_messages:
        #     if ((current_time - datetime.fromisoformat(msg["timestamp"].rstrip("Z"))).days > 1) :
        #         recent_5_messages.append(message)
        #         if (cnt >= 5) :
        #             break
        # print("recent_5_messages = ", len(recent_5_messages))
        # recent_messages = [
        #     {
        #         "channel_id": channel_id,
        #         "server_name": "Bittensor",
        #         "server_id": "Bittensor",
        #         "id": message["id"],
        #         "text": message["content"],
        #         "author_username": message["author"]["username"],
        #         "created_at": message["timestamp"],
        #     } for message in recent_5_messages
        # ]
        # for msg in recent_messages:
        #     is_duplicate = any(item["id"] == msg["id"] for item in cur_array)
        #     if is_duplicate == 0:
        #         cur_array.append(msg)
        
        print("I calculated cur_array successfully")
        print("cur_array length = ", len(cur_array))
        # rank = sort_model()
        # return_array = rank.select_obj(cur_array)
        # return return_array
