# import torch
# import numpy as np

# from transformers import BertTokenizer, BertModel
# from sentence_transformers import SentenceTransformer
# MAX_EMBEDDING_DIM = 1024


# # padding tensor to MAX_EMBEDDING_DIM with zeros
# # applicable to embeddings with shape (d) or (n, d) where d < MAX_EMBEDDING_DIM
# def pad_tensor(tensor, max_len=MAX_EMBEDDING_DIM):
#     """Pad tensor with zeros to max_len dimensions"""

#     if isinstance(tensor, np.ndarray):
#         tensor = torch.from_numpy(tensor)
#     if tensor.ndim == 1:
#         if tensor.shape[0] < max_len:
#             pad = torch.zeros(max_len - tensor.shape[0], device=tensor.device)
#             tensor = torch.cat((tensor, pad), dim=0)
#     elif tensor.ndim == 2:
#         if tensor.shape[1] < max_len:
#             pad = torch.zeros(
#                 tensor.shape[0], max_len - tensor.shape[1], device=tensor.device
#             )
#             tensor = torch.cat((tensor, pad), dim=1)
#     else:
#         raise ValueError("Invalid tensor shape")
#     return tensor


# # for semantic search
# # Note: you may consider more powerful embedding models here, or even finetune your own embedding model
# # but make sure the query embedding is compatible with the indexed document embeddings
# # def text_embedding(text, model_name="bert-base-uncased"):
# def text_embedding(text, model_name="all-mpnet-base-v2"):
#     """Get text embedding using Bert model"""

#     model - 

#     encoded_input = tokenizer(text, return_tensors="pt")

#     with torch.no_grad():
#         model_output = model(**encoded_input)

#     # cls pooling
#     # embedding = model_output[0][:, 0]

#     # mean pooling
#     embedding = torch.mean(model_output[0], dim=1)

#     # Note: miners are encouraged to explore more pooling strategies, finetune the model, etc.

#     return embedding






import torch
import numpy as np
from sentence_transformers import SentenceTransformer

# Correct dimensionality for all-mpnet-base-v2
MAX_EMBEDDING_DIM =1024

# Padding tensor to MAX_EMBEDDING_DIM with zeros
# Applicable to embeddings with shape (d) or (n, d) where d < MAX_EMBEDDING_DIM
def pad_tensor(tensor, max_len=MAX_EMBEDDING_DIM):
    """Pad tensor with zeros to max_len dimensions"""

    if isinstance(tensor, np.ndarray):
        tensor = torch.from_numpy(tensor)
    print("tensor is follws")
    print(tensor.ndim)
    if tensor.ndim == 1:
        if tensor.shape[0] < max_len:
            pad = torch.zeros(max_len - tensor.shape[0], device=tensor.device)
            tensor = torch.cat((tensor, pad), dim=0)
    elif tensor.ndim == 2:
        if tensor.shape[1] < max_len:
            pad = torch.zeros(
                tensor.shape[0], max_len - tensor.shape[1], device=tensor.device
            )
            tensor = torch.cat((tensor, pad), dim=1)
    elif tensor.ndim == 3:
        if tensor.shape[2] < max_len:
            pad = torch.zeros(
                tensor.shape[0], tensor.shape[1], max_len - tensor.shape[2], device=tensor.device
            )
            tensor = torch.cat((tensor, pad), dim=2)
    else:
        raise ValueError("Invalid tensor shape")
    return tensor

# For semantic search
def text_embedding(text, model_name="all-mpnet-base-v2"):
    """Get text embedding using SentenceTransformer"""

    model = SentenceTransformer(model_name)

    # Get the embedding
    embedding = model.encode(text)
    # print(embedding, ":this is embedding")
    # print(embedding.shape)
    if not isinstance(embedding, torch.Tensor):
        embedding = torch.tensor(embedding)

    # Pad the embedding if necessary
    # embedding = pad_tensor(embedding)

    return embedding