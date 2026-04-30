# Pivot Plan: Game-Centric Representation for Bridge Titles

This plan pivots the project's focus from clustering player profiles to clustering **Game Profiles** at an `app_id` granularity, as requested by the professor.

## 1. Phase: Data Denormalization (Master Table)
**Goal:** Consolidate all normalized tables into a single wide-format dataset.
- Merge `games_cleaned.csv` with `games_metadata_cleaned.json`.
- Join with aggregated statistics from `recommendations_cleaned.parquet` and `users_cleaned.csv`.
- **Target File:** `data/processed/master_games_ml.csv` (or `.parquet`).

## 2. Phase: Advanced Feature Engineering
**Goal:** Create high-signal variables for clustering.
- **Recommendation Metrics:** For each game, calculate:
    - Mean, Median, and Standard Deviation of `hours` played.
    - Recommendation ratio (Percentage of `True` in `is_recommended`).
- **User Profile Aggregation:** 
    - **Fan Profile:** Average `products` count of users who recommended the game.
    - **Hater Profile:** Average `products` count of users who did NOT recommend the game.
- **NLP Sentiment:** Pass descriptions through a pre-trained model to get a "Tone" score (Pos/Neg/Neu).
- **Latent Embeddings:** Generate semantic vectors for `description` and `tags`.

## 3. Phase: Dimensionality Reduction & Cluster Analysis
**Goal:** Prepare for the second deliverable using PCA/SVD.
- Apply **PCA** to the master table to reduce 50+ variables to 3-5 Principal Components.
- Explain the variance captured and justify the number of components.
- Visualize clusters using **UMAP/t-SNE** to identify "Bridge Titles" (games sitting between genre clusters).

## 4. Phase: Pipeline Integration
**Goal:** Ensure reproducibility.
- Update `run_pipeline.py` to reflect the new workflow.
- Replace the old Week 5 scripts with the new Master Table and NLP logic.

## 5. Phase: Validation
- Verify that every game in the database has a full feature vector.
- Check for data leakage or missing values in the master table.
