import pandas as pd
import json
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import TruncatedSVD
import scipy.sparse as sp

def load_data():
    print("Loading data...")
    games_path = 'data/processed/games_cleaned.csv'
    metadata_path = 'data/processed/games_metadata_cleaned.json'
    
    games_df = pd.read_csv(games_path)
    
    metadata = []
    with open(metadata_path, 'r') as f:
        for line in f:
            metadata.append(json.loads(line))
    
    metadata_df = pd.DataFrame(metadata)
    
    # Merge datasets
    df = pd.merge(games_df, metadata_df, on='app_id', how='inner')
    return df

def feature_engineering(df):
    print("Starting feature engineering (Bridge Titles Layer)...")
    
    # 1. Fill missing values
    df['description'] = df['description'].fillna('')
    df['tags'] = df['tags'].apply(lambda x: ' '.join(x) if isinstance(x, list) else '')
    
    # 2. Categorical features
    bool_cols = ['win', 'mac', 'linux', 'steam_deck']
    for col in bool_cols:
        df[col] = df[col].astype(int)
    
    # 3. Text features - TF-IDF + LSA for tags (Identifying Latent Themes)
    print("Vectorizing tags and identifying latent themes (LSA)...")
    tfidf_tags = TfidfVectorizer(max_features=1000)
    tags_tfidf = tfidf_tags.fit_transform(df['tags'])
    
    lsa_tags = TruncatedSVD(n_components=50, random_state=42)
    tags_lsa = lsa_tags.fit_transform(tags_tfidf)
    
    # 4. Text features - TF-IDF + LSA for description (Identifying Latent Themes)
    print("Vectorizing description and identifying latent themes (LSA)...")
    tfidf_desc = TfidfVectorizer(max_features=2000, stop_words='english')
    desc_tfidf = tfidf_desc.fit_transform(df['description'])
    
    lsa_desc = TruncatedSVD(n_components=100, random_state=42)
    desc_lsa = lsa_desc.fit_transform(desc_tfidf)
    
    # 5. Numeric and Categorical (Rating) Pipeline
    print("Scaling numeric features and encoding rating...")
    numeric_features = ['positive_ratio', 'user_reviews', 'price_final']
    categorical_features = ['rating']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    
    other_features = preprocessor.fit_transform(df)
    
    # 6. Boolean features
    bool_matrix = df[bool_cols].values
    
    # 7. Combine all matrices
    print("Combining feature matrices...")
    final_matrix = np.hstack([
        tags_lsa,
        desc_lsa,
        other_features,
        bool_matrix
    ])
    
    return final_matrix, df['app_id'].values

def main():
    df = load_data()
    feature_matrix, app_ids = feature_engineering(df)
    
    output_dir = 'data/processed'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Final feature matrix shape: {feature_matrix.shape}")
    
    # Save matrix and IDs
    matrix_path = os.path.join(output_dir, 'game_features.npz') # We'll save it as npz but it's dense now
    ids_path = os.path.join(output_dir, 'game_ids.csv')
    
    # Save as compressed numpy
    np.savez_compressed(matrix_path, features=feature_matrix)
    pd.DataFrame({'app_id': app_ids}).to_csv(ids_path, index=False)
    
    print(f"Features saved to {matrix_path}")
    print(f"IDs saved to {ids_path}")

if __name__ == "__main__":
    main()
