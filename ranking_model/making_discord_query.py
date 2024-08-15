
import os
import json
import requests
import time
from datetime import datetime
from openai import OpenAI, AsyncOpenAI
import bittensor as bt
from traceback import print_exception

def generate_discord_semantic_search_task(msg_category, category_info):
    """
    Generates a semantic search task for the validator to send to the miner.
    """
    subnet_name = "Open kaito"
    llm_client = OpenAI(
        api_key="",
        )
    prompt = (
        f"Imagine you are testing a semantic search engine about project {subnet_name} in a discord channel of its developers and users, "
        + f"please generate a search query around any {msg_category} around the project? "
        + f"{msg_category} is about {category_info}."
    )
    prompt += (
        "Provide the query string in less than 20 words. "
        "Please give the question text only, without any additional context or explanation."
    )

    bt.logging.debug(f"Discord Query Prompt: {prompt}")
    try:
        output = llm_client.chat.completions.create(
            model="gpt-4o",
            # response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            # temperature=1.5,
            temperature=1,
            timeout=60,
        )

        bt.logging.debug(
            f"generation questions LLM response: {output.choices[0].message.content}"
        )
        bt.logging.debug(
            f"LLM usage: {output.usage}, finish reason: {output.choices[0].finish_reason}"
        )
        return output.choices[0].message.content
    except Exception as e:
        bt.logging.error(f"Error during LLM completion: {e}")
        bt.logging.debug(print_exception(type(e), e, e.__traceback__))

DISCORD_MSG_CATEGORIES = {
"Announcements": "Official updates or important news",
"Questions": "Inquiries seeking information or clarification",
"Advice": "Suggestions and guidance on various topics",
"Technical Support": "Assistance with technical issues or troubleshooting",
"Planning": "Discussions about organizing events or activities",
"Resources": "Sharing useful links, tools, or educational content",
"Controversy": "Debates or heated discussions",
"Feedback": "General neutral opinions about any topic discussed, while not explicitly positive or negative",
"Praise": "Positive feedback and compliments",
"Criticism": "Negative feedback or constructive criticism",
"Exploit": "Exploring vulnerabilities or flaws in systems or software",
# "Casual Conversation": "Informal chat and everyday discussions",
# "Humor": "Jokes, memes, and other light-hearted content",
# "Answers": "Direct responses to users' questions",
# "Warnings": "Alerts or cautionary advice about potential issues",
# "Introductions": "Welcoming new members or personal introductions",
# "Hack": "Innovative tricks or shortcuts to improve efficiency or solve problems",
# "Off-Topic": "Messages that stray from the main subject or theme",
}

for msg_category, category_info in DISCORD_MSG_CATEGORIES.items():

    n = 50
    root_dir = __file__.split("ranking_model")[0]
    output_file_path = root_dir + "discord_sample_query2.json"
    with open(output_file_path, 'a') as json_file:
        json_file.write("\n\n\n\n\n")
        while(n):
            n -= 1
            msg = generate_discord_semantic_search_task(msg_category, category_info)
            print(msg)
            json_file.write('"' + msg + '",\n')