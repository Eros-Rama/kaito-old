"""Vector Search of Eth Denver dataset using Elasticsearch and Transformers

This script extracts the Eth Denver dataset (open-sourced by https://portal.kaito.ai/events/ETHDenver2024 ), indexes the documents in Elasticsearch, and indexes the embeddings of the documents in Elasticsearch.
It also provides a test query to retrieve the top-k similar documents to the query.

This script is intentionally kept transparent and hackable, and miners may do their own customizations.
"""

import os
from pathlib import Path
import json
from tqdm import tqdm
import torch

from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv


from openkaito.utils.embeddings import pad_tensor, text_embedding, MAX_EMBEDDING_DIM


root_dir = __file__.split("ranking_model")[0]
index_name = "eth_denver-base-v2-model"
# index_name = "eth_cc7-base-v2-model"
# index_name = "eth_denver-s-bert-add-speaker"


### Extract Eth Denver dataset
def extract_eth_denver_dataset():
    """Extract Eth Denver dataset to datasets/eth_denver_dataset directory"""

    if os.path.exists(root_dir + "datasets/eth_denver_dataset"):
        print(
            "Eth Denver data already extracted to: ",
            root_dir + "datasets/eth_denver_dataset",
        )
    else:
        import tarfile

        with tarfile.open(
            root_dir + "datasets/eth_denver_dataset.tar.gz", "r:gz"
        ) as tar:
            tar.extractall(root_dir + "datasets")

        print(
            "Eth Denver data extracted to: ", root_dir + "datasets/eth_denver_dataset"
        )

    dataset_dir = root_dir + "datasets/eth_denver_dataset"
    dataset_path = Path(dataset_dir)
    print(f"{len(list(dataset_path.glob('*.json')))} files in {dataset_dir}")

def extract_eth_cc7_dataset():
    """Extract Eth cc7 dataset to datasets/eth_cc7_dataset directory"""

    if os.path.exists(root_dir + "datasets/eth_cc7_dataset"):
        print(
            "Eth cc7 data already extracted to: ",
            root_dir + "datasets/eth_cc7_dataset",
        )
    else:
        import tarfile

        with tarfile.open(
            root_dir + "datasets/eth_cc7_dataset.tar.gz", "r:gz"
        ) as tar:
            tar.extractall(root_dir + "datasets")

        print(
            "Eth cc7 data extracted to: ", root_dir + "datasets/eth_cc7_dataset"
        )

    dataset_dir = root_dir + "datasets/eth_cc7_dataset"
    dataset_path = Path(dataset_dir)
    print(f"{len(list(dataset_path.glob('*.json')))} files in {dataset_dir}")

def init_eth_denver_index(search_client):
    """Initialize Eth Denver index in Elasticsearch"""

    if not search_client.indices.exists(index=index_name):
        print("creating index...", index_name)
        search_client.indices.create(
            index=index_name,
            body={
                "mappings": {
                    "properties": {
                        "doc_id": {"type": "keyword"},
                        "episode_id": {"type": "keyword"},
                        "segment_id": {"type": "long"},
                        "episode_title": {"type": "text"},
                        "episode_url": {"type": "text"},
                        "created_at": {"type": "date"},
                        "company_name": {"type": "keyword"},
                        "segment_start_time": {"type": "float"},
                        "segment_end_time": {"type": "float"},
                        "text": {"type": "text"},
                        "speaker": {"type": "keyword"},
                        "embedding": {
                            "type": "dense_vector",
                            "dims": MAX_EMBEDDING_DIM,
                        },
                    }
                }
            },
        )
        print("Index created: ", index_name)
    else:
        print("Index already exists: ", index_name)


def drop_index(search_client, index_name):
    """Drop index in Elasticsearch"""

    if search_client.indices.exists(index=index_name):
        search_client.indices.delete(index=index_name)
        print("Index deleted: ", index_name)
    else:
        print("Index does not exist: ", index_name)


def indexing_docs(search_client):
    """Index documents in Elasticsearch"""

    dataset_dir = root_dir + "datasets/eth_denver_dataset"
    dataset_path = Path(dataset_dir)

    num_files = len(list(dataset_path.glob("*.json")))
    print(f"Indexing {num_files} files in {dataset_dir}")
    for doc_file in tqdm(
        dataset_path.glob("*.json"), total=num_files, desc="Indexing docs"
    ):
        with open(doc_file, "r") as f:
            doc = json.load(f)
            search_client.index(index=index_name, body=doc, id=doc["doc_id"])


def indexing_embeddings(search_client):
    """Index embeddings of documents in Elasticsearch"""
    counter = 0
    for doc in tqdm(
        helpers.scan(search_client, index=index_name, size=10),
        desc="Indexing embeddings",
        total=search_client.count(index=index_name)["count"],
    ):
        
        doc_id = doc["_id"]
        text_cur = doc["_source"]["text"]
        text_cur = doc["_source"]["speaker"] + " said like this : " + text_cur
        text = text_cur[:2000]
        embedding = text_embedding(text)
        print(text)
        embedding = pad_tensor(embedding, max_len=MAX_EMBEDDING_DIM)
        embedding = embedding.tolist()
        print(embedding)
        response = search_client.update(
            index=index_name,
            id=doc_id,
            body={"doc": {"embedding": embedding}, "doc_as_upsert": True},
        )
        print("response")
        print(response)
        


def test_retrieval(search_client, query, topk=5):
    """Test retrieval of top-k similar documents to query"""

    embedding = text_embedding(query)
    speaker = "Rahul Sethuram"
    # embedding = pad_tensor(embedding, max_len=MAX_EMBEDDING_DIM)
    # body = {
    #     "knn": {
    #         "field": "embedding",
    #         "query_vector": embedding.tolist(),
    #         "k": topk,
    #         "num_candidates": 5 * topk,
    #     },
    #     "query": {
    #         "bool": {
    #             "should": [
    #                 {"match": {"speaker": {"query": speaker, "boost": 2}}},
    #                 {"match": {"speaker": {"query": speaker, "fuzziness": "AUTO"}}}
    #             ]
    #         }
    #     },
    #     "_source": {
    #         "excludes": ["embedding"],
    #     },
    # }
    speaker_query = {
        "query": {
            "bool": {
                "should": [
                    {"match": {"speaker": {"query": speaker, "boost": 2}}},
                    {"match": {"speaker": {"query": speaker, "fuzziness": "AUTO"}}}
                ]
            }
        },
        "_source": ["_id"]  # Retrieve only the document IDs
    }

    # Execute the first search
    speaker_response = search_client.search(index=index_name, body=speaker_query)
    speaker_doc_ids = [doc["_id"] for doc in speaker_response["hits"]["hits"]]

    # Save the intermediate results (document IDs)
    # This can be done in-memory, or you can store them in a temporary index or a file.

    # Step 2: Find content similarity within the filtered documents

    content_query = {
        "field":"embedding",
        "query_vector":embedding.tolist(),
        "k" : 5,
        "num_candidates" : 14,
        # "filter": [
        #     {
        #     "terms": {
        #         "_id": speaker_doc_ids  # Filter by document IDs from the first search
        #         }
        #     }
        # ]
    }



    # Execute the second search
    response = search_client.search(index=index_name, knn=content_query)
    return response

    # response = search_client.search(index=index_name, body=body)
    # return response


if __name__ == "__main__":
    load_dotenv()

    search_client = Elasticsearch(
        os.environ["ELASTICSEARCH_HOST"],
        basic_auth=(
            os.environ["ELASTICSEARCH_USERNAME"],
            os.environ["ELASTICSEARCH_PASSWORD"],
        ),
        verify_certs=False,
        ssl_show_warn=False,
    )

    # extract_eth_denver_dataset()
    # extract_eth_cc7_dataset()

    dataset_dir1 = root_dir + "datasets/eth_denver_dataset"
    dataset_path1 = Path(dataset_dir1)
    num_files1 = len(list(dataset_path1.glob("*.json")))

    dataset_dir2 = root_dir + "datasets/eth_cc7_dataset"
    dataset_path2 = Path(dataset_dir2)
    num_files2 = len(list(dataset_path2.glob("*.json")))

    print(num_files1, num_files2)

    # for doc_file in tqdm(
    #     dataset_path.glob("*.json"), total=num_files, desc="adding speaker to text"
    # ):   
    #     with open(doc_file, "r") as f:
    #         doc = json.load(f)
    #     doc["text"] = f'{doc["speaker"]} said like that: {doc["text"]}'
    #     with open(doc_file, "w") as f:
    #         json.dump(doc, f, indent=4)

    drop_index(search_client, index_name)

    init_eth_denver_index(search_client)
    indexing_docs(search_client)
    indexing_embeddings(search_client)

    # doc_id = 'xBN-cew6Fu8.142'
    # response = search_client.get(index='eth_denver-base-v2-model', id=doc_id)

    # # Print the document to check the embedding field
    # print(response['_source'])

    # r = search_client.count(index=index_name)
    # print(r)
    # # print(r["count"])
    # response = search_client.search(
    # index=index_name,
    # body={
    #     "query": {
    #         "match_all": {}
    #     },
    #     "from": 5,  # Skip the first 9,999 documents
    #     "size": 2     # Retrieve only one document
    # }
    # )

    # # # Print the 10,000th document
    # if response['hits']['hits'][0]:
    #     doc = response['hits']['hits'][0]
    #     print(doc["_source"]["embedding"])
    # else:
    #     print("No document found at the 10,000th index.")






    # if r["count"] != num_files1:
    #     print(
    #         f"Number of docs in {index_name}: {r['count']} != total files {num_files1}, reindexing docs..."
    #     )
    #     indexing_docs(search_client)
    # else:
    #     print(
    #         f"Number of docs in {index_name}: {r['count']} == total files {num_files1}, no need to reindex docs"
    #     )


    # query = "What did Rahul Sethuram say about bit thing of meme"
    # response = test_retrieval(search_client, query, topk=5)
    # # print(response)
    # cnt = 0
    # for response in response["hits"]["hits"]:
    #     print(response["_source"]["created_at"])
    #     print(response["_source"]["episode_title"])
    #     print(response["_source"]["speaker"])
    #     print(response["_source"]["text"])
    #     print(response["_score"])
    #     cnt += 1

    # print(cnt)
    





































