import pandas as pd
import numpy as np
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import tqdm
import os

def load_master_table():
    path = 'data/processed/master_games_ml.parquet'
    if not os.path.exists(path):
        raise FileNotFoundError("Master table not found. Run master_table.py first.")
    return pd.read_parquet(path)

def analyze_sentiment(df):
    print("Initializing Sentiment Analysis (HuggingFace)...")
    sentiment_task = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english", device=-1)
    
    descriptions = df['description'].fillna("No description").tolist()
    results = []
    
    print("Processing descriptions for sentiment...")
    for i in range(0, len(descriptions), 32):
        batch = descriptions[i:i+32]
        batch_truncated = [d[:512] for d in batch]
        batch_results = sentiment_task(batch_truncated)
        results.extend(batch_results)
    
    # Convert results to numeric score: POSITIVE = 1, NEGATIVE = 0
    df['sentiment_label'] = [r['label'] for r in results]
    df['sentiment_score'] = [r['score'] if r['label'] == 'POSITIVE' else 1 - r['score'] for r in results]
    
    return df

def generate_embeddings(df):
    print("Initializing Sentence Embeddings (HuggingFace/MiniLM)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Combine Tags and Description for a richer semantic representation
    text_to_embed = (df['tags'].apply(lambda x: ' '.join(x) if isinstance(x, list) else str(x)) + 
                     " " + 
                     df['description'].fillna("")).tolist()
    
    print("Generating embeddings (this might take a while)...")
    embeddings = model.encode(text_to_embed, show_progress_bar=True, batch_size=64)
    
    np.save('data/processed/game_embeddings.npy', embeddings)
    print("Embeddings saved to data/processed/game_embeddings.npy")
    
    return df

def main():
    df = load_master_table()
    
    df = analyze_sentiment(df)
    
    df = generate_embeddings(df)
    
    output_path = 'data/processed/master_games_ml_enriched.parquet'
    df.to_parquet(output_path, index=False)
    print(f"Enriched Master Table saved to: {output_path}")

if __name__ == "__main__":

    main()
