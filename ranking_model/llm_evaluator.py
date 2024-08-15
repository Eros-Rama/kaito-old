
import os
import json
import requests
import time
from datetime import datetime
from openai import OpenAI, AsyncOpenAI
import bittensor as bt
from traceback import print_exception

class llm_evaluator:

    def llm_rank_evaluator(self, docs):
        a = time.time()
        llm_client = OpenAI(
            
        )
        newline = '\n'
        prompt_docs = "\n\n".join(
                [
                    f"ItemId: {i}\nTime: {doc['timestamp'].split('T')[0]}\nText: {doc['content'][:1000].replace(newline, '  ')}"
                    for i, doc in enumerate(docs)
                ]
            )



            
        
        output = llm_client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": """You will be given a list of messages from a discord channel and you have to rate them based on its information and meaningfulness.
A message is meaningful if it is self-contained with valuable information, for example, it can be an announcement, a news, an instruction about code, or a opinion towards a subnet.
A message is meaningless if it contains no valuable information or is a piece of conversation taken out of contexts.
For example, meaningless messages can be a question without context, a response to an unknown question, log without explanation, code without context, very short messages, or an announcement from six months ago.
Note even if a message itself is informative, it should still be categorized into meaningless if it is part of a conversation or lacks context to understand the information based on the message itself.
""",
                    },
                    {
                        "role": "system",
                        "content": f"Current Time: {datetime.now().isoformat().split('T')[0]}",
                    },
                    {
                        "role": "user",
                        "content": f"You will be given a list of documents with id and timestamp, please rate them based on its information and meaningfulness. The documents are as follows:\n"
                        + prompt_docs,
                    },
                    {
                        "role": "user",
                        "content": f"Use the metric choices [meaningful, meaningless] to evaluate the text.",
                    },
                    {
                        "role": "user",
                        "content": "Must answer in JSON format of a list of choices with item ids for all the given items: "
                        + "{'results': [{'item_id': the item id of choice, e.g. 0, 'reason': a very short explanation of your choice, 'choice':The choice of answer. }, {'item_id': 1, 'reason': explanation, 'choice': answer } , ... ] } ",
                    },
                ],
                temperature=0,
        )
        bt.logging.debug(f"LLM response: {output.choices[0].message.content}")
        bt.logging.debug(
            f"LLM usage: {output.usage}, finish reason: {output.choices[0].finish_reason}"
        )
        result = json.loads(output.choices[0].message.content)
        choice_mapping = {
            "meaningless": 0,
            "meaningful": 1,
        }
        # bt.logging.debug(f"LLM result: {result}")
        ranking = [choice_mapping[doc["choice"]] for doc in result["results"]]
        bt.logging.info(f"LLM ranking: {ranking}")
        if len(ranking) != len(docs):
            raise ValueError(
                f"Length of ranking {len(ranking)} does not match input docs length {len(docs)}"
            )
        print("ranking array is as follows \n\n\n", ranking)
        return ranking
    


    def llm_author_index_data_evaluation(self, docs, retries=3):
        if docs is None or len(docs) == 0:
            return [0]
        try:
            newline = "\n"
            prompt_docs = "\n\n".join(
                [
                    f"ItemId: {i}\nTime: {doc['created_at'].split('T')[0]}\nText: {doc['text'][:1000].replace(newline, '  ')}"
                    for i, doc in enumerate(docs)
                ]
            )

            bt.logging.debug(
                f"Querying LLM of author index data with docs:\n" + prompt_docs
            )
            llm_client = OpenAI(
            
            )
            output = llm_client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": """Below are the metrics and definitions: 
outdated: Time-sensitive information that is no longer current or relevant.
insightless: Superficial content lacking depth and comprehensive insights.
somewhat insightful: Offers partial insight but lacks depth and comprehensive coverage.
Insightful: Comprehensive, insightful content suitable for informed decision-making.""",
                    },
                    {
                        "role": "system",
                        "content": f"Current Time: {datetime.now().isoformat().split('T')[0]}",
                    },
                    {
                        "role": "system",
                        "content": """
Example 1:
ItemId: 0
Time: "2023-11-25" 
Text: Also driving the charm is Blast's unique design: Depositors start earning yields on the transferred ether alongside BLAST points. "Blast natively participates in ETH staking, and the staking yield is passed back to the L2's users and dapps," the team said in a post Tuesday. 'We've redesigned the L2 from the ground up so that if you have 1 ETH in your wallet on Blast, over time, it grows to 1.04, 1.08, 1.12 ETH automatically."
As such, Blast is invite-only as of Tuesday, requiring a code from invited users to gain access. Besides, the BLAST points can be redeemed starting in May.Blast raised over $20 million in a round led by Paradigm and Standard Crypto and is headed by pseudonymous figurehead @PacmanBlur, one of the co-founders of NFT marketplace Blur.
@PacmanBlur said in a separate post that Blast was an extension of the Blur ecosystem, letting Blur users earn yields on idle assets while improving the technical aspects required to offer sophisticated NFT products to users.
BLUR prices rose 12%% in the past 24 hours following the release of Blast


Output:
item_id: 0
choice: insightful
reason: It is contains insightful information about the Blast project.

Example 2:
ItemId: 1
Time: "2024-03-19"
Text: $SLERF to the moon!
$BOME $SOL $MUMU $BONK $BOPE $WIF $NAP 🥳

Output:
item_id: 1
choice: insightless
reason: It does not contain much meaningful information, just sentiment about some tickers.
""",
                    },
                    {
                        "role": "user",
                        "content": f"You will be given a list of documents with id and you have to rate them based on its information and insightfulness. The documents are as follows:\n"
                        + prompt_docs,
                    },
                    {
                        "role": "user",
                        "content": f"Use the metric choices [outdated, insightless, somewhat insightful, insightful] to evaluate the text.",
                    },
                    {
                        "role": "user",
                        "content": "Must answer in JSON format of a list of choices with item ids for all the given items: "
                        + "{'results': [{'item_id': the item id of choice, e.g. 0, 'reason': a very short explanation of your choice, 'choice':The choice of answer. }, {'item_id': 1, 'reason': explanation, 'choice': answer } , ... ] } ",
                    },
                ],
                temperature=0,
            )
            bt.logging.debug(f"LLM response: {output.choices[0].message.content}")
            bt.logging.debug(
                f"LLM usage: {output.usage}, finish reason: {output.choices[0].finish_reason}"
            )
        except Exception as e:
            bt.logging.error(f"Error while querying LLM: {e}")
            return [0]

        try:
            result = json.loads(output.choices[0].message.content)
            choice_mapping = {
                "outdated": 0,
                "insightless": 0,
                "somewhat insightful": 0.5,
                "insightful": 1,
            }
            ranking = [choice_mapping[doc["choice"]] for doc in result["results"]]
            # bt.logging.debug(f"LLM result: {result}")
            bt.logging.info(f"LLM ranking: {ranking}")
            if len(ranking) != len(docs):
                raise ValueError(
                    f"Length of ranking {len(ranking)} does not match input docs length {len(docs)}"
                )
            return ranking
        except Exception as e:
            bt.logging.error(f"Error while parsing LLM result: {e}, retrying...")
            if retries > 0:
                return self.llm_author_index_data_evaluation(docs, retries - 1)
            else:
                bt.logging.error(
                    f"Failed to parse LLM result after retrying. Returning [0]."
                )
            return [0]
    
     
    def llm_semantic_search_evaluation(self, query_string, docs, k, retries=3):
        if docs is None or len(docs) == 0:
            return [0]
        try:
            newline = "\n"
            prompt_docs = "\n\n".join(
                [
                    f"ItemId: {i}\nTalk Title: {doc['episode_title']}\nSpeaker: {doc['speaker']}\nText: {doc['text'][:2000].replace(newline, '  ')}"
                    for i, doc in enumerate(docs)
                ]
            )
            bt.logging.debug(
                f"Querying LLM of semantic search with docs:\n" + prompt_docs
            )
            llm_client = OpenAI(
            
            )
            output = llm_client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": """Below are the metrics and definitions:
off topic: Superficial or unrelevant content that can not answer the given question.
somewhat relevant: Offers partial insight to partially answer the given question.
relevant: Comprehensive, insightful content suitable for answering the given question.""",
                    },
                    {
                        "role": "user",
                        "content": f"You will be given a list of documents with id and you have to rate them based on its information and relevance to the question. The documents are as follows:\n"
                        + prompt_docs,
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Use the metric choices [off topic, somewhat relevant, relevant] to evaluate whether the text can answer the given question:\n"
                            f"{query_string}"
                        ),
                    },
                    {
                        "role": "user",
                        "content": "Must answer in JSON format of a list of choices with item ids for all the given items: "
                        + "{'results': [{'item_id': the item id of the text, e.g. 0, 'reason': a very short explanation of your choice, 'choice':The choice of answer. }, {'item_id': 1, 'reason': explanation, 'choice': answer } , ... ] } ",
                    },
                ],
                temperature=0,
            )
            bt.logging.debug(f"LLM response: {output.choices[0].message.content}")
            # if k == 0 :
                # self.second_logger.info(output.choices[0].message.content)

            bt.logging.debug(
                f"LLM usage: {output.usage}, finish reason: {output.choices[0].finish_reason}"
            )
        except Exception as e:
            bt.logging.error(f"Error while querying LLM: {e}")
            bt.logging.debug(print_exception(type(e), e, e.__traceback__))
            return [0]

        try:
            result = json.loads(output.choices[0].message.content)
            # bt.logging.debug(f"LLM result: {result}")
            choice_mapping = {
                "outdated": 0,
                "off topic": 0,
                "somewhat relevant": 0.5,
                "relevant": 1,
            }
            ranking = [choice_mapping[doc["choice"]] for doc in result["results"]]
            # self.second_logger.info(result)
            bt.logging.info(f"LLM ranking: {ranking}")
            if len(ranking) != len(docs):
                raise ValueError(
                    f"Length of ranking {len(ranking)} does not match input docs length {len(docs)}"
                )
            return ranking
        except Exception as e:
            bt.logging.error(f"Error while parsing LLM result: {e}, retrying...")
            if retries > 0:
                return self.llm_semantic_search_evaluation(
                    query_string, docs, retries - 1
                )
            else:
                bt.logging.error(
                    f"Failed to parse LLM result after retrying. Returning [0]."
                )
            return [0]








# prompt_docs = "\n\n".join(
        #                 [
        # """
        # ItemId: 0
        # Speaker: dex1049
        # Text: same empty

        # ItemId: 1
        # Speaker: hhan_26
        # Text: sorry, try `curl -u username:password https://localhost:9200 -k`

        # ItemId: 2
        # Speaker: dex1049
        # Text: curl: (52) Empty reply from server

        # ItemId: 3
        # Speaker: hhan_26
        # Text: could you try curl -u username:password http://localhost:9200  to see if it can connect correctly?

        # ItemId: 4
        # Speaker: dex1049
        # Text: {"@timestamp":"2024-03-05T01:04:42.848Z", "log.level": "INFO", "message":"Authentication of [elastic] was terminated by realm [reserved] - failed to authenticate user [elastic]", "ecs.version": "1.2.0","service.name":"ES_ECS","event.dataset":"elasticsearch.server","process.thread.name":"elasticsearch[f62a74277767][system_critical_read][T#4]","log.logger":"org.elasticsearch.xpack.security.authc.RealmsAuthenticator","elasticsearch.cluster.uuid":"KLexvVefS7-5kDh64zRzeA","elasticsearch.node.id":"ke0GlfWwSdqj6OkZBn9Ovg","elasticsearch.node.name":"f62a74277767","elasticsearch.cluster.name":"docker-cluster"}

        # ItemId: 5
        # Speaker: hhan_26
        # Text: what is the output of  `docker logs elasticsearch`

        # ItemId: 6
        # Speaker: dex1049
        # Text: same AuthenticationException 401 unfortunately...  I am starting miner with  python3 neurons/miner.py --netuid 5 --subtensor.network finney --wallet.name ColdWallet --wallet.hotkey HotWallet --logging.debug --blacklist.force_validator_permit --axon.port 1234 --axon.external_port 1234 --axon.ip 192.168.1.8 --axon.external_ip 12.345.678.90

        # ItemId: 7
        # Speaker: hhan_26
        # Text: emmm….could you reset the password then try again?

        # ItemId: 8
        # Speaker: dex1049
        # Text: yes, I have it in openkaito folder:

        # ItemId: 9
        # Speaker: hhan_26
        # Text: did you move the  .env.example to .env?

        # ItemId: 10
        # Speaker: dex1049
        # Text: looks like it's running:  f62a74277767   docker.elastic.co/elasticsearch/elasticsearch:8.12.1   "/bin/tini -- /usr/l…"   38 minutes ago   Up 38 minutes   0.0.0.0:9200->9200/tcp, :::9200->9200/tcp, 0.0.0.0:9300->9300/tcp, :::9300->9300/tcp   elasticsearch

        # ItemId: 11
        # Speaker: hhan_26
        # Text: could you check if the elasticsearch instance running properly? e.g., docker ps

        # ItemId: 12
        # Speaker: dex1049
        # Text: I have set elastic search password, but still getting AuthenticationException 401

        # ItemId: 13
        # Speaker: hhan_26
        # Text: no

        # ItemId: 14
        # Speaker: dex1049
        # Text: Do we need OPENAI_API_KEY for running miners too?

        # ItemId: 15
        # Speaker: hhan_26
        # Text: this is because some validators are sending wrong requests, just ignore it: 🙂

        # ItemId: 16
        # Speaker: tkots9
        # Text: about an hour for me

        # ItemId: 17
        # Speaker: sahit2509
        # Text: about 2 hrs

        # ItemId: 18
        # Speaker: vinhdao3600
        # Text: how long did you run

        # ItemId: 19
        # Speaker: sahit2509
        # Text: yep just wait guys! 😛

        # ItemId: 20
        # Speaker: vinhdao3600
        # Text: i think over 1hour from run

        # ItemId: 21
        # Speaker: vinhdao3600
        # Text: soon

        # ItemId: 22
        # Speaker: vinhdao3600
        # Text: so wait for emission

        # ItemId: 23
        # Speaker: vinhdao3600
        # Text: got request

        # ItemId: 24
        # Speaker: tkots9
        # Text: yep i see it now haha

        # ItemId: 25
        # Speaker: sahit2509
        # Text: I see mine directly in the logging but you can check on tao stats as well

        # ItemId: 26
        # Speaker: tkots9
        # Text: really? where did you see it?

        # ItemId: 27
        # Speaker: sahit2509
        # Text: I started getting emission! you might too, but the error is still a problem.. I hope that doesnt effect our incentives or something

        # ItemId: 28
        # Speaker: tkots9
        # Text: is this telling us to do something? or just why we got the error? Also, any knowledge on why we aren't getting emmisssion?

        # ItemId: 29
        # Speaker: vinhdao3600
        # Text: ERROR       | UnknownSynapseError: Synapse name 'CoreSynapse' not found. Available synapses ['Synapse', 'SearchSynapse']

        # ItemId: 30
        # Speaker: vinhdao3600
        # Text: i got this error

        # ItemId: 31
        # Speaker: vinhdao3600
        # Text: File "/home/user/.bittensor/bittensor/bittensor/axon.py", line 1046, in dispatch      synapse: bittensor.Synapse = await self.preprocess(request)                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^    File "/home/user/.bittensor/bittensor/bittensor/axon.py", line 1176, in preprocess      raise UnknownSynapseError(  bittensor.errors.UnknownSynapseError: Synapse name 'CoreSynapse' not found. Available synapses ['Synapse', 'SearchSynapse']

        # ItemId: 32
        # Speaker: sahit2509
        # Text: Damn.. and the price was expensive too.. It worked well in the testnet, so I thought I'd give it a shot hopefully.. the emissions come up soon

        # ItemId: 33
        # Speaker: vinhdao3600
        # Text: thank you

        # ItemId: 34
        # Speaker: tkots9
        # Text: same

        # ItemId: 35
        # Speaker: sahit2509
        # Text: I'm having the same issue been running for about 90min and no emissions, althought I'm generating results

        # ItemId: 36
        # Speaker: sahit2509
        # Text: Does the axon port has to be 8091?

        # ItemId: 37
        # Speaker: tkots9
        # Text: 

        # ItemId: 38
        # Speaker: tkots9
        # Text: not sure how I did the elastic search port, I followed the GH

        # ItemId: 39
        # Speaker: tkots9
        # Text: 

        # ItemId: 40
        # Speaker: vinhdao3600
        # Text: how did you setup your port on ElasticSearch and Axon port when run miner ?

        # ItemId: 41
        # Speaker: tkots9
        # Text: am I supposed to be getting emissions?

        # ItemId: 42
        # Speaker: tkots9
        # Text: are you just using the base twitter crawler from GH?

        # ItemId: 43
        # Speaker: tkots9
        # Text: i am also getting this

        # ItemId: 44
        # Speaker: sahit2509
        # Text: I updated my repo to the latest and yet still I'm getting a warning like this

        # ItemId: 45
        # Speaker: sahit2509
        # Text: 0|miner-1  | 2024-03-04 19:42:20.043 |      ERROR       | UnknownSynapseError: Synapse name 'CoreSynapse' not found. Available synapses ['Synapse', 'SearchSynapse']      I got this error on the miner. Any help?

        # ItemId: 46
        # Speaker: tkots9
        # Text: i'm registered on finney now, and i've got this error twice since starting the miner.. anyone know?

        # ItemId: 47
        # Speaker: sahit2509
        # Text: because there aren't any miners so far

        # ItemId: 48
        # Speaker: sahit2509
        # Text: Do you recommend I run as a miner or validator on the mainnet?

        # ItemId: 49
        # Speaker: sahit2509
        # Text: Got it! thanks

        # ItemId: 50
        # Speaker: hhan_26
        # Text: yes, but better to use different —axon.port args

        # ItemId: 51
        # Speaker: sahit2509
        # Text: Alright! cool, thanks for the help. also one more question, is it possible to run as a validator and miner on the same machine?

        # ItemId: 52
        # Speaker: hhan_26
        # Text: maybe some validator not sending correct requests, should be fine if it can handle other requests

        # ItemId: 53
        # Speaker: sahit2509
        # Text: nope

        # ItemId: 54
        # Speaker: hhan_26
        # Text: this is fine，did you also run a validator on the same machine?

        # ItemId: 55
        # Speaker: tkots9
        # Text: did you manage to get your miner working on finney actually doing mining?

        # ItemId: 56
        # Speaker: sahit2509
        # Text: Hey! I'm getting one strange error on the testnet    1|miner-2  | 2024-03-04 18:19:07.056 |      ERROR       | NotVerifiedException: Not Verified with error: Signature mismatch with 463780114358498.5CBDcd5233gumVCggSp6yb4AWMvnft4Qapim1nhTpB4pd2CM.5GNQXxWYfY8a4uF47NBeoQnF2SGYLLbdksFsRgRcXzepjPbp.30ab502a-da48-11ee-a974-8b3305cef166.a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a and 0x4c0bef60533abf3ea95a765f77bf66377ffdf1c482cb1d186aef8d2fd438cc587f1009955eeecf1d762e6a958d3fc767407ae285b6fa1d25675bc0486f680a81      Most of the queries are successful but for some I get this error, any idea?

        # ItemId: 57
        # Speaker: 0xjchen
        # Text: Mr. keith (uid 4) got 40k tao staked, which is around $30M, am I understanding that correctly 🙃

        # ItemId: 58
        # Speaker: 0xjchen
        # Text: thank you! I saw my node.

        # ItemId: 59
        # Speaker: hhan_26
        # Text: this seems it is working fine, for taostats, it is not real time updated, you may try ‘  btcli s metagraph —netuid 5

        # ItemId: 60
        # Speaker: 0xjchen
        # Text: 

        # ItemId: 61
        # Speaker: 0xjchen
        # Text: i have successfully registered (spent 0.47 tao) and run the `pm2 start run.sh --name openkaito_validator_autoupdate -- --netuid 5 --subtensor.network finney --wallet.name validator --wallet.hotkey default  --logging.debug`    now I find 1. my node (uid/hotkey/coldkey) does not appear on the taostat 2. my `pm2` monitor shows as follows. just curious if I am on the right track : )

        # ItemId: 62
        # Speaker: hhan_26
        # Text: I can see your emission now 🙂

        # ItemId: 63
        # Speaker: hhan_26
        # Text: you might refer to https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html to find guidance on how to install elasticsearch, then use pm2 to start the executable binary

        # ItemId: 64
        # Speaker: vinhdao3600
        # Text: by pm2

        # ItemId: 65
        # Speaker: vinhdao3600
        # Text: any guide to install Elasticsearch

        # ItemId: 66
        # Speaker: hhan_26
        # Text: sure, in whatever method, as long as your miner can access it

        # ItemId: 67
        # Speaker: vinhdao3600
        # Text: can I run Elasticsearch on pm2 ?

        # ItemId: 68
        # Speaker: sahit2509
        # Text: Fixed now! thanks just had to wait a bit xd

        # ItemId: 69
        # Speaker: hhan_26
        # Text: yeah might need to wait longer for validator to sync the new metagraph and send requests to your miner. or you can just start a validator on testnet by yourself

        # ItemId: 70
        # Speaker: hhan_26
        # Text: looks operating normally, perhaps need more time

        # ItemId: 71
        # Speaker: keith_keith_keith
        # Text: 👀

        # ItemId: 72
        # Speaker: p383_54249
        # Text: the other validators are probably running the old code, so you aren't in consensus

        # ItemId: 73
        # Speaker: sahit2509
        # Text: Hey! I have been running on testnet for the last 5min, I'm not getting any requests, is that normal?

        # ItemId: 74
        # Speaker: keith_keith_keith
        # Text: validator up for 82 minutes

        # ItemId: 75
        # Speaker: keith_keith_keith
        # Text: 

        # ItemId: 76
        # Speaker: hhan_26
        # Text: did your miner receive requests and respond correctly? how long has your miner been running?

        # ItemId: 77
        # Speaker: keith_keith_keith
        # Text: UID 4

        # ItemId: 78
        # Speaker: keith_keith_keith
        # Text: Any idea why i am not generating emissions?

        # ItemId: 79
        # Speaker: 0xjchen
        # Text: thanks!

        # ItemId: 80
        # Speaker: hhan_26
        # Text: not sure 🙂 you may try the starter plan then pay as you go, or you may also implement a crawler with/without apify by yourself, which could be more challenging but may make your miner outperform others:)

        # ItemId: 81
        # Speaker: tkots9
        # Text: anyone know what Apify plan is needed for this to run smoothly all month?

        # ItemId: 82
        # Speaker: tkots9
        # Text: I did get get 1 test request 🙂 thanks

        # ItemId: 83
        # Speaker: hurricane0097
        # Text: thanks working great.

        # ItemId: 84
        # Speaker: hhan_26
        # Text: do you mean the uid 11? uid 11 is getting rewards from `incentive`, which means it is running a miner

        # ItemId: 85
        # Speaker: hhan_26
        # Text: yes, according to https://docs.bittensor.com/subnets/register-validate-mine , top 64 stakers will be eligible to be validators

        # ItemId: 86
        # Speaker: hhan_26
        # Text: you may also try to run validator on testnet by yourself 🙂

        # ItemId: 87
        # Speaker: hhan_26
        # Text: I have setup a validator running on testnet 88 now, you may receive requests shortly. cc <@563012209727373337>

        # ItemId: 88
        # Speaker: tkots9
        # Text: +1 on this... not sure if there is supposed to be traffic or not on test subnet 88?

        # ItemId: 89
        # Speaker: 0xjchen
        # Text: And participator 10 staked nothing but eligible for daily rewards?

        # ItemId: 90
        # Speaker: 0xjchen
        # Text: Does it mean that all participators are validators right now (all have checkbox on the left)?

        # ItemId: 91
        # Speaker: 0xjchen
        # Text: 

        # ItemId: 92
        # Speaker: hurricane0097
        # Text: Hi iam running miner on test net 88 . How do i check if everything is working well and debug. My UID is 4. <@567997325268615168> please help.

        # ItemId: 93
        # Speaker: kat_defiants
        # Text: 

        # ItemId: 94
        # Speaker: hhan_26
        # Text: you need to deposit you TAO into the cold key of your wallet, in your case, that is miner or validator. the ‘default’ is your wallet hotkey. you may find more information on https://docs.bittensor.com/subnets/register-validate-mine

        # ItemId: 95
        # Speaker: 0xjchen
        # Text: <@567997325268615168>ser your tutorial looks really cool and clear. love it!

        # ItemId: 96
        # Speaker: 0xjchen
        # Text: gm gm, may I ask a question about depositing tao to be a validator.     I am followiing the guide here(https://github.com/OpenKaito/openkaito/blob/main/docs/running_on_mainnet.md)    where I create wallets by   ```  btcli wallet new_coldkey --wallet.name miner  btcli wallet new_hotkey --wallet.name miner --wallet.hotkey default  btcli wallet new_coldkey --wallet.name validator  btcli wallet new_hotkey --wallet.name validator --wallet.hotkey default  ```    now I run `btcli wallet list` it shows 4 wallet like:    ```  -miner:    -default:    -validator:    -default  ```    now I am wondering which wallet should I deposit tao into?

        # ItemId: 97
        # Speaker: johnkmj
        # Text: gm lfg

        # ItemId: 98
        # Speaker: hhan_26
        # Text: Hello all! Our initial version of openkaito is up and running on SN5.    Please checkout our Github repo if you're interested in getting started https://github.com/OpenKaito/openkaito

        # ItemId: 99
        # Speaker: kat_defiants
        # Text: <@1003934492878176306> I believe this channel is yours -- you should have perms to repost and pin your intro information & links and get folks started on your subnet. : )
        # """
                    #     ]
                    # )