# Steam Big Data Recommendation Pipeline

This repository contains Phase 1 (Data Lake & Setup) for the Steam game recommendation engine, using the massive dataset by Anton Kozyriev (Kaggle).

## 🛠️ Pipeline Architecture

The ingestion and cleaning pipeline is divided into two highly efficient phases:
1. **Exploratory Data Analysis and Cleaning (Python):** Jupyter Notebooks powered by `pyarrow` for in-memory data cleaning of files up to 2GB.
2. **Concurrent Cloud Ingestion (Go):** Golang orchestrators designed with Goroutines and Channels to inject massive amounts of data into PostgreSQL (Supabase), overcoming the I/O limitations of traditional languages.

---

## 🚀 Documented Execution Commands (Runbook)

To reproduce the complete workflow of this project, follow these steps:

### 1. Environment Setup
Install the necessary Python dependencies:
```bash
pip install -r requirements.txt
```

### 2. Extraction and Cleaning (Python Phase)
Execute the following notebooks in the `notebooks/` folder sequentially:
1. `download_dataset.ipynb` (Downloads data via `kagglehub` to `data/raw/`)
2. `eda_games.ipynb` (Cleans the base catalog)
3. `eda_metadata.ipynb` (Filters the JSONL metadata by joining it with the catalog)
4. `eda_users.ipynb` (Cleans user profiles)
5. `eda_recommendations.ipynb` (Processes the 2GB dataset and exports to Parquet)

### 3. Cloud Ingestion (Go Phase)
Make sure to copy the `.env.example` file to `.env` and set your Supabase `DATABASE_URL`. Then, navigate to the ingestion folder:

```bash
cd src/ingestion/
```

Run the concurrent orchestrators depending on the file you want to upload:

**To upload the games catalog:**
```bash
go run games.go
```

**To upload the users:**
```bash
go run users.go
```

**To upload the structured metadata (JSONB):**
```bash
go run games_metadata.go
```

**To inject the massive interactions dataset (Parquet, 2GB):**
```bash
go run recommendations.go
```

## 🔒 Privacy and Security (Ethics Note)
All processed data is anonymized through encrypted `app_id` and `user_id` identifiers straight from their public Kaggle source. Cloud connection secrets are protected via global Git exclusion (`.gitignore`).
