import json
import os
from pathlib import Path
import random
import openai
from datetime import datetime, timedelta
from traceback import print_exception
from dotenv import load_dotenv

import bittensor as bt

from .protocol import (
    DiscordSearchSynapse,
    SortType,
    StructuredSearchSynapse,
    SemanticSearchSynapse,
)
from .utils.version import get_version


def random_query(input_file="queries.txt"):
    if not os.path.exists(input_file):
        bt.logging.error(f"Queries file not found at location: {input_file}")
        exit(1)
    lines = open(input_file).read().strip().splitlines()
    return random.choice(lines)


# The twitter usernames list is from a truncated snapshot of friendtech ( https://dune.com/cryptokoryo/friendtech )
# You are welcome to suggest modifications to the list, by opening Pull Request over GitHub.
def random_twitter_username(input_file="twitter_usernames.txt", num_authors: int = 2):
    if not os.path.exists(input_file):
        bt.logging.error(f"Twitter usernames file not found at location: {input_file}")
        exit(1)
    lines = open(input_file).read().strip().splitlines()
    return random.sample(lines, num_authors)


def random_datetime(start: datetime, end: datetime):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)


def random_past_datetime(start_days_ago: int = 365, end_days_ago: int = 10):
    return random_datetime(
        datetime.now() - timedelta(days=start_days_ago),
        datetime.now() - timedelta(days=end_days_ago),
    )


def generate_author_index_task(
    size: int = 5,
    num_authors: int = 2,
):
    author_usernames = random_twitter_username(num_authors=num_authors)
    return StructuredSearchSynapse(
        size=size,
        author_usernames=author_usernames,
        version=get_version(),
    )


def generate_structured_search_task(
    query_string: str = None,
    size: int = 5,
    sort_by: SortType = None,
    earlier_than: datetime = None,
    later_than: datetime = None,
    author_usernames: list = None,
) -> StructuredSearchSynapse:
    """
    Generates a structured search task for the validator to send to the miner.
    """

    # Randomly generate the query_string if not provided.
    if query_string is None:
        query_string = random_query()

    # Randomly select the earlier_than and later_than if not provided.
    if later_than is None:
        # 0.8 ratio to set the later_than or not
        if random.random() < 0.8:
            later_than = random_past_datetime()
        else:
            later_than = None

    # Note: do not set the earlier_than by default if it is not provided.

    return StructuredSearchSynapse(
        query_string=query_string,
        size=size,
        earlier_than_timestamp=(earlier_than.timestamp() if earlier_than else None),
        later_than_timestamp=(later_than.timestamp() if later_than else None),
        author_usernames=author_usernames,
        sort_by=sort_by,
        version=get_version(),
    )


def random_eth_conf_segments(
    eth_conf_dataset_dir,
    num_sources=3,
):
    dataset_path = Path(eth_conf_dataset_dir)

    files = random.sample(list(dataset_path.glob("*.json")), num_sources)
    segments = []
    for file in files:
        with open(file) as f:
            data = json.load(f)
            segments.append(data)
    return segments


def generate_question_from_eth_conf_segments(llm_client, segments):
    knowledge_text = ""
    for segment in segments:
        knowledge_text += (
            "Talk Title: "
            + segment["episode_title"]
            + "\n"
            + "Speaker: "
            + segment["speaker"]
            + "\n"
            + "Text: "
            + segment["text"]
            + "\n\n"
        )

    prompt = (
        "You are a crypto researcher, and you will be given a list of speaker transcript segments as your source of knowledge in an Ethereum conference. "
        "Your job is to look for a question about the speaker and text that can be answered by this segment"
        "Transcript segments:\n\n"
    )
    prompt += knowledge_text
    prompt += (
        "Provide the question in less than 15 words. "
        "Please give the question text only, without any additional context or explanation."
    )

    bt.logging.debug(f"Prompt: {prompt}")

    try:
        output = llm_client.chat.completions.create(
            model="gpt-4-turbo",
            # response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=1.5,
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


def generate_semantic_search_task(
    query_string: str,
    index_name: str = "eth_denver",
    size: int = 5,
    version: str = None,
) -> SemanticSearchSynapse:
    """
    Generates a semantic search task for the validator to send to the miner.
    """
    if version is None:
        version = get_version()

    return SemanticSearchSynapse(
        query_string=query_string,
        index_name=index_name,
        size=size,
        version=version,
    )


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

BITTENSOR_DISCORD_CHANNEL_PROJECS = {
    0: "Announcements",
    1: "Text Prompting",
    2: "Omron",
    3: "MyShell TTS",
    4: "Targon",
    5: "Open Kaito",
    6: "Infinite Games",
    7: "Subvortex",
    8: "Proprietary Trading Network",
    9: "Pretraining",
    10: "Sturdy",
    11: "Dippy Roleplay",
    12: "Horde",
    13: "Dataverse",
    14: "LLM Defender",
    15: "Blockchain Insights",
    16: "BitAds",
    17: "Three Gen",
    18: "Cortex.t",
    19: "Vision",
    20: "BitAgent",
    21: "Omega Any-to-Any",
    22: "Meta Search",
    23: "SocialTensor",
    24: "Omega Labs",
    25: "Protein Folding",
    26: "Tensor Alchemy",
    27: "Compute",
    28: "Foundry S&P 500 Oracle",
    29: "Coldint",
    30: "Bettensor",
    31: "NAS Chain",
    32: "It's AI",
    33: "Conversation Genome",
    34: "BitMind",
    35: "LogicNet",
    36: "Human Intelligence Primitive",
    37: "Finetuning",
    38: "Unknown",
    39: "EdgeMaxxing",
    40: "Unknown",
    41: "Sportstensor",
    42: "Unknown",
    43: "Graphite",
    44: "Unknown",
    # 45: "Unknown"
}


def generate_discord_query_string(llm_client, subnet_name, msg_category, category_info):
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


# Existing discord tasks before v0.4.5
# discord channel feeds and keyword search tasks
def generate_discord_search_task(
    query_string: str = None,
    index_name: str = "discord",
    channel_ids: list = None,
    earlier_than_timestamp: int = None,
    later_than_timestamp: int = None,
    size: int = 5,
    version: str = None,
) -> DiscordSearchSynapse:
    """
    Generates a discord channel feeds task or discord keyword search task for the validator to send to the miner.
    """
    if not version:
        version = get_version()

    if not channel_ids:
        with open("bittensor_channels.json") as f:
            channels = json.load(f)
        channel_info = random.choice(channels)
        channel_ids = [channel_info["channel_id"]]

    return DiscordSearchSynapse(
        query_string=query_string,
        index_name=index_name,
        channel_ids=channel_ids,
        earlier_than_timestamp=earlier_than_timestamp,
        later_than_timestamp=later_than_timestamp,
        size=size,
        version=version,
    )


# discord channel semantic search tasks
def generate_discord_semantic_search_task(
    llm_client=None,
    query_string: str = None,
    index_name: str = "discord",
    # channel_ids: list = None,
    earlier_than_timestamp: int = None,
    later_than_timestamp: int = None,
    ## set the default size of conversations to be 2
    size: int = 2,
    version: str = None,
) -> DiscordSearchSynapse:
    """
    Generates a semantic search task for the validator to send to the miner.
    """
    if not version:
        version = get_version()

    with open("bittensor_channels.json") as f:
        channels = json.load(f)
    # exclude the announcement channel
    channel_info = random.choice(channels[1:])

    # NOT explicitly set channel id in the request
    # channel_ids = [channel_info["channel_id"]]
    subnet_id = None
    subnet_name = None

    # subnet channel
    if "Subnets" in channel_info["channel_category"]:
        subnet_id = int(channel_info["channel_name"].split("\u30fb")[-1])
        subnet_name = BITTENSOR_DISCORD_CHANNEL_PROJECS[subnet_id]
        msg_category = random.choice(list(DISCORD_MSG_CATEGORIES.keys()))
        query_string = generate_discord_query_string(
            llm_client, subnet_name, msg_category, DISCORD_MSG_CATEGORIES[msg_category]
        )
        bt.logging.debug(
            f"Channel ID: {channel_info['channel_id']}, Subnet ID: {subnet_id}, Subnet Name: {subnet_name}"
        )
    # actually no-op
    else:
        query_string = "What is the latest announcement in Bittensor discord server?"
    bt.logging.debug(f"Generated query string: {query_string}")

    return DiscordSearchSynapse(
        query_string=query_string,
        index_name=index_name,
        channel_ids=None,
        earlier_than_timestamp=earlier_than_timestamp,
        later_than_timestamp=later_than_timestamp,
        size=size,
        version=version,
    )


def find_repo(path):
    "Find repository root from the path's parents"
    for path in Path(path).parents:
        # Check whether "path/.git" exists and is a directory
        git_dir = path / ".git"
        if git_dir.is_dir():
            return path


# `python -m openkatio.tasks`
if __name__ == "__main__":
    # task = generate_structured_search_task("BTC")
    # print(task)
    # print(task.name)

    load_dotenv()
    llm_client = openai.OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        organization=os.getenv("OPENAI_ORGANIZATION"),
        max_retries=3,
    )

    # bt.logging.set_trace(True)
    bt.logging.set_debug(False)
    # repo_root = find_repo(__file__)
    # eth_denver_dataset_dir = repo_root / "datasets/eth_denver_dataset"
    # print(eth_denver_dataset_dir)
    # print("generating question from ETH Denver dataset")
    # segments = random_eth_denver_segments(eth_denver_dataset_dir, num_sources=3)
    # question = generate_question_from_eth_denver_segments(llm_client, segments)
    # print(question)

    # task = generate_semantic_search_task(question)

    # task = generate_discord_search_task(llm_client=llm_client, size=5)

    # print(task)
    subnet_name = "Open Kaito"
    for msg_category in DISCORD_MSG_CATEGORIES.keys():
        question = generate_discord_query_string(
            llm_client=llm_client,
            subnet_name=subnet_name,
            msg_category=msg_category,
            category_info=DISCORD_MSG_CATEGORIES[msg_category],
        )
        print(msg_category)
        print(question)
