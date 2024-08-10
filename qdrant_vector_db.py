import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from tqdm import tqdm

from sentence_transformers import SentenceTransformer
import os

# Define the model name and local pathiz
model_name = 'Alibaba-NLP/gte-large-en-v1.5'
local_model_path = './models/gte-large-en-v1.5'

# Function to download the model
def download_model(model_name, save_path):
    if not os.path.exists(save_path):
        print(f"Downloading model {model_name} to {save_path}")
        model = SentenceTransformer(model_name, trust_remote_code=True)
        model.save(save_path)
        print("Model downloaded and saved successfully.")
    else:
        print(f"Model already exists at {save_path}")

# Function to load the model from local storage
def load_local_model(model_path):
    print(f"Loading model from {model_path}")
    return SentenceTransformer(model_path, trust_remote_code=True)

# Download the model (if not already downloaded)
download_model(model_name, local_model_path)

# Load the model from local storage
model = load_local_model(local_model_path)

# Example usage
sentences = ['This is an example sentence', 'Another example sentence']
embeddings = model.encode(sentences)
print(f"Generated embeddings shape: {embeddings.shape}")


# Load the dataset
df = pd.read_csv('sample.csv')  # Replace with your actual file path

# Initialize the sentence transformer model
model = SentenceTransformer('Alibaba-NLP/gte-large-en-v1.5', trust_remote_code=True)

# Initialize Qdrant client
client = QdrantClient("localhost", port=6333)  # Update with your Qdrant server details if different

# Create a new collection
collection_name = "sample_snomeds"
vector_dimension = model.get_sentence_embedding_dimension()

client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=vector_dimension, distance=Distance.COSINE),
)

# Function to process data in batches
def process_batch(batch):
    names = batch['name'].tolist()
    embeddings = model.encode(names)
    return embeddings

# Process data in batches
batch_size = 1000  # Adjust based on your memory constraints
total_batches = len(df) // batch_size + (1 if len(df) % batch_size != 0 else 0)

for i in tqdm(range(total_batches), desc="Processing batches"):
    start_idx = i * batch_size
    end_idx = min((i + 1) * batch_size, len(df))
    batch = df.iloc[start_idx:end_idx]
    
    batch_embeddings = process_batch(batch)
    
    # Add embeddings to Qdrant
    client.upsert(
        collection_name=collection_name,
        points=[
            {
                "id": start_idx + j,
                "vector": embedding.tolist(),
                "payload": {
                    "name": row['name'],
                    "code": row['code'],
                    "type": row['type']
                }
            }
            for j, (embedding, (_, row)) in enumerate(zip(batch_embeddings, batch.iterrows()))
        ]
    )

print(f"Vector database created with {client.get_collection(collection_name).vectors_count} vectors.")

# Example of how to search
def search_similar_names(query, top_k=5):
    query_embedding = model.encode([query])[0]
    
    search_result = client.search(
        collection_name=collection_name,
        query_vector=query_embedding.tolist(),
        limit=top_k
    )
    
    results = []
    for hit in search_result:
        results.append({
            'name': hit.payload['name'],
            'code': hit.payload['code'],
            'type': hit.payload['type'],
            'score': hit.score
        })
    
    return results

# Example usage
print(search_similar_names("heart attack"))
