import pandas as pd
import numpy as np
import os
import scipy.sparse as sp
from sklearn.decomposition import TruncatedSVD

def load_recommendations():
    print("Loading recommendations...")
    # Using the cleaned recommendations file (Parquet format)
    path = 'data/processed/recommendations_cleaned.parquet'
    
    # Load only necessary columns
    df = pd.read_parquet(path, columns=['user_id', 'app_id', 'hours', 'is_recommended'])
    return df

def build_utility_matrix(df):
    print("Building Utility Matrix (Interaction Layer)...")
    
    # Filter for positive recommendations or significant playtime
    # According to the guide: "Intensidad de Uso: Se integra la métrica de horas jugadas"
    
    # Map IDs to indices
    user_ids = df['user_id'].astype('category')
    app_ids = df['app_id'].astype('category')
    
    users = user_ids.cat.codes
    apps = app_ids.cat.codes
    
    # Weight by hours played (using log scaling to prevent extreme values)
    # We add 1 to avoid log(0)
    weights = np.log1p(df['hours'])
    
    # Create sparse matrix (COO format first, then CSR for efficiency)
    matrix = sp.coo_matrix((weights, (users, apps)))
    matrix = matrix.tocsr()
    
    print(f"Matrix created with shape: {matrix.shape}")
    print(f"Sparsity: {1.0 - matrix.nnz / (matrix.shape[0] * matrix.shape[1]):.4%}")
    
    return matrix, user_ids.cat.categories, app_ids.cat.categories

def main():
    df = load_recommendations()
    
    # Optional: Filter users with very few reviews to reduce noise
    user_counts = df['user_id'].value_counts()
    df = df[df['user_id'].isin(user_counts[user_counts >= 2].index)]
    
    matrix, user_map, app_map = build_utility_matrix(df)
    
    output_dir = 'data/processed'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save sparse matrix
    matrix_path = os.path.join(output_dir, 'interaction_matrix.npz')
    sp.save_npz(matrix_path, matrix)
    
    # Save mappings
    pd.DataFrame({'user_id': user_map}).to_csv(os.path.join(output_dir, 'user_map.csv'), index=False)
    pd.DataFrame({'app_id': app_map}).to_csv(os.path.join(output_dir, 'app_map.csv'), index=False)
    
    print(f"Interaction matrix saved to {matrix_path}")

if __name__ == "__main__":
    main()
