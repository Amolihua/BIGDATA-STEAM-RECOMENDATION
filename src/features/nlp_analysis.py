import pandas as pd
import numpy as np
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import torch
import os

def load_master_table():
    path = 'data/processed/master_games_ml.parquet'
    if not os.path.exists(path):
        raise FileNotFoundError("Master table not found. Run master_table.py first.")
    return pd.read_parquet(path)

def analyze_sentiment(df):
    print("Initializing Sentiment Analysis on GPU (CUDA)...")
    # Set device to 0 for the first GPU
    device = 0 if torch.cuda.is_available() else -1
    if device == 0:
        print(f"CUDA detected: {torch.cuda.get_device_name(0)}")
    
    sentiment_task = pipeline("sentiment-analysis", 
                              model="distilbert-base-uncased-finetuned-sst-2-english", 
                              device=device)
    
    descriptions = df['description'].fillna("No description").tolist()
    results = []
    
    print("Processing descriptions for sentiment (GPU accelerated)...")
    # Larger batch size for GPU
    batch_size = 128 if device == 0 else 32
    
    for i in range(0, len(descriptions), batch_size):
        batch = descriptions[i:i+batch_size]
        batch_truncated = [d[:512] for d in batch]
        batch_results = sentiment_task(batch_truncated)
        results.extend(batch_results)
    
    df['sentiment_label'] = [r['label'] for r in results]
    df['sentiment_score'] = [r['score'] if r['label'] == 'POSITIVE' else 1 - r['score'] for r in results]
    
    return df

def generate_embeddings(df):
    print("Initializing Sentence Embeddings on GPU (CUDA)...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    
    text_to_embed = (df['tags'].apply(lambda x: ' '.join(x) if isinstance(x, list) else str(x)) + 
                     " " + 
                     df['description'].fillna("")).tolist()
    
    print("Generating embeddings (GPU accelerated)...")
    embeddings = model.encode(text_to_embed, show_progress_bar=True, batch_size=128)
    
    np.save('data/processed/game_embeddings.npy', embeddings)
    print("Embeddings saved to data/processed/game_embeddings.npy")
    
    return df

def main():
    df = load_master_table()
    
    # 1. Sentiment Analysis
    df = analyze_sentiment(df)
    
    # 2. Embeddings
    df = generate_embeddings(df)
    
    output_path = 'data/processed/master_games_ml_enriched.parquet'
    df.to_parquet(output_path, index=False)
    print(f"Enriched Master Table saved to: {output_path}")

if __name__ == "__main__":
    main()
