import polars as pl
import json
import os

def load_data():
    print("Loading datasets with Polars...")
    # Load Games
    games_df = pl.read_csv('data/processed/games_cleaned.csv')
    
    # Load Metadata (JSON Lines) - Polars can read ndjson directly
    metadata_df = pl.read_ndjson('data/processed/games_metadata_cleaned.json')
    
    # Load Recommendations (Parquet)
    recs_df = pl.read_parquet('data/processed/recommendations_cleaned.parquet', 
                             columns=['user_id', 'app_id', 'hours', 'is_recommended'])
    
    # Load Users
    users_df = pl.read_csv('data/processed/users_cleaned.csv', has_header=True).select(['user_id', 'products'])
    
    return games_df, metadata_df, recs_df, users_df

def engineer_features(games_df, metadata_df, recs_df, users_df):
    print("Engineering aggregate features with Polars...")
    
    # 1. Recommendation Aggregations
    agg_recs = recs_df.group_by('app_id').agg([
        pl.col('hours').mean().alias('hours_mean'),
        pl.col('hours').median().alias('hours_median'),
        pl.col('hours').std().alias('hours_std'),
        pl.col('is_recommended').mean().alias('rec_ratio'),
        pl.col('app_id').count().alias('review_count')
    ])
    
    # 2. User Profile Aggregations (Fan vs Hater)
    # Join recs with users
    recs_with_users = recs_df.join(users_df, on='user_id', how='inner')
    
    # Fan stats
    fan_stats = (recs_with_users
                 .filter(pl.col('is_recommended') == True)
                 .group_by('app_id')
                 .agg(pl.col('products').mean().alias('fan_avg_products')))
    
    # Hater stats
    hater_stats = (recs_with_users
                   .filter(pl.col('is_recommended') == False)
                   .group_by('app_id')
                   .agg(pl.col('products').mean().alias('hater_avg_products')))
    
    # 3. Master Merge
    print("Consolidating Master Table...")
    master_df = (games_df
                 .join(metadata_df, on='app_id', how='inner')
                 .join(agg_recs, on='app_id', how='left')
                 .join(fan_stats, on='app_id', how='left')
                 .join(hater_stats, on='app_id', how='left'))
    
    # Fill nulls with 0
    master_df = master_df.fill_null(0)
    
    return master_df

def main():
    games_df, metadata_df, recs_df, users_df = load_data()
    master_df = engineer_features(games_df, metadata_df, recs_df, users_df)
    
    output_path = 'data/processed/master_games_ml.parquet'
    master_df.write_parquet(output_path)
    print(f"Master Table created successfully at: {output_path}")
    print(f"Total columns: {len(master_df.columns)}")
    print(f"Total rows (games): {len(master_df)}")

if __name__ == "__main__":
    main()
