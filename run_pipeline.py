import subprocess
import sys
import time

def run_command(command, cwd=None):
    print(f"\n{'='*60}")
    print(f"Executing: {command}")
    if cwd:
        print(f"Directory: {cwd}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    try:
        process = subprocess.Popen(
            command, 
            shell=True, 
            cwd=cwd,
            stdout=sys.stdout, 
            stderr=sys.stderr
        )
        process.communicate()
        
        if process.returncode != 0:
            print(f"\nCritical error executing: {command}")
            sys.exit(process.returncode)
            
        elapsed = time.time() - start_time
        print(f"\nCompleted successfully in {elapsed:.2f} seconds.")
        
    except Exception as e:
        print(f"\nException while attempting to execute: {e}")
        sys.exit(1)

def main():
    print("STARTING STEAM BIG DATA END-TO-END MASTER PIPELINE")
    print("Strategy: PIVOT - Game-Centric Representation for Bridge Titles\n")
    

    # --- PHASE 1: Raw Data Extraction ---
    #run_command("python -m nbconvert --to notebook --execute download_dataset.ipynb", cwd="notebooks")

    # --- PHASE 2: Transformation and Cleaning (EDA) ---
    #run_command("python -m nbconvert --to notebook --execute eda_games.ipynb", cwd="notebooks")
    #run_command("python -m nbconvert --to notebook --execute eda_metadata.ipynb", cwd="notebooks")
    #run_command("python -m nbconvert --to notebook --execute eda_users.ipynb", cwd="notebooks")
    #run_command("python -m nbconvert --to notebook --execute eda_recommendations.ipynb", cwd="notebooks")

    # --- PHASE 3: Cloud Ingestion (Independent Nodes) ---
    # WARNING: These scripts push data to Supabase. Check your 500MB limit.
    # run_command("go run games.go", cwd="src/ingestion")
    # run_command("go run users.go", cwd="src/ingestion")
    
    # --- PHASE 4: Cloud Ingestion (Dependent Nodes) ---
    # run_command("go run games_metadata.go", cwd="src/ingestion")
    # run_command("go run recommendations.go", cwd="src/ingestion")
    
    # --- PHASE 5: Master Table Denormalization (PIVOT) ---
    print("\n--- Phase 5: Building Master Table ---")
    run_command("python src/features/master_table.py")

    # --- PHASE 6: NLP Enrichment (Sentiment & Embeddings) ---
    print("\n--- Phase 6: NLP Analysis (GPU Accelerated with CUDA) ---")
    run_command("python src/features/nlp_analysis.py")

    # --- PHASE 7: Dimensionality Reduction & Clustering ---
    print("\n--- Phase 7: Dimensionality Analysis ---")
    #run_command("python -m nbconvert --to notebook --execute dimensionality_analysis.ipynb", cwd="notebooks")

    print("\nPIPELINE READY! (Some phases commented out to save resources)")

if __name__ == "__main__":
    main()
