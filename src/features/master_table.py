import pandas as pd
import json
import os
import numpy as np

def load_data():
    print("Loading datasets...")
    games_df = pd.read_csv('data/processed/games_cleaned.csv')
    

    metadata = []
    with open('data/processed/games_metadata_cleaned.json', 'r') as f:
        for line in f:
            metadata.append(json.loads(line))
    metadata_df = pd.DataFrame(metadata)
    
    
    recs_df = pd.read_parquet('data/processed/recommendations_cleaned.parquet', 
                             columns=['user_id', 'app_id', 'hours', 'is_recommended'])
    
    
    users_df = pd.read_csv('data/processed/users_cleaned.csv', usecols=['user_id', 'products'])
    
    return games_df, metadata_df, recs_df, users_df

def engineer_features(games_df, metadata_df, recs_df, users_df):
    print("Engineering aggregate features...")
    
    agg_recs = recs_df.groupby('app_id').agg(
        hours_mean=('hours', 'mean'),
        hours_median=('hours', 'median'),
        hours_std=('hours', 'std'),
        rec_ratio=('is_recommended', 'mean'),
        review_count=('app_id', 'count')
    ).reset_index()
    
    
    recs_with_users = pd.merge(recs_df, users_df, on='user_id', how='inner')
    

    fan_stats = recs_with_users[recs_with_users['is_recommended'] == True].groupby('app_id')['products'].mean().reset_index()
    fan_stats.columns = ['app_id', 'fan_avg_products']
    

    hater_stats = recs_with_users[recs_with_users['is_recommended'] == False].groupby('app_id')['products'].mean().reset_index()
    hater_stats.columns = ['app_id', 'hater_avg_products']
    
  
    print("Consolidating Master Table...")
    master_df = pd.merge(games_df, metadata_df, on='app_id', how='inner')
    master_df = pd.merge(master_df, agg_recs, on='app_id', how='left')
    master_df = pd.merge(master_df, fan_stats, on='app_id', how='left')
    master_df = pd.merge(master_df, hater_stats, on='app_id', how='left')
    
 
    fill_cols = ['hours_mean', 'hours_median', 'hours_std', 'rec_ratio', 'review_count', 'fan_avg_products', 'hater_avg_products']
    master_df[fill_cols] = master_df[fill_cols].fillna(0)
    
    return master_df

def main():
    games_df, metadata_df, recs_df, users_df = load_data()
    master_df = engineer_features(games_df, metadata_df, recs_df, users_df)
    
    output_path = 'data/processed/master_games_ml.parquet'
    master_df.to_parquet(output_path, index=False)
    print(f"Master Table created successfully at: {output_path}")
    print(f"Total columns: {len(master_df.columns)}")
    print(f"Total rows (games): {len(master_df)}")

if __name__ == "__main__":
    main()
