import subprocess
import sys
import time

def run_command(command, cwd=None):
    print(f"\n{'='*60}")
    print(f"🚀 Executing: {command}")
    if cwd:
        print(f"📂 Directory: {cwd}")
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
            print(f"\n❌ Critical error executing: {command}")
            sys.exit(process.returncode)
            
        elapsed = time.time() - start_time
        print(f"\n✅ Completed successfully in {elapsed:.2f} seconds.")
        
    except Exception as e:
        print(f"\n❌ Exception while attempting to execute: {e}")
        sys.exit(1)

def main():
    print("STARTING STEAM BIG DATA END-TO-END MASTER PIPELINE")
    print("Complete Orchestration: Extraction -> Cleaning -> Schema -> Ingestion\n")
    

    # --- PHASE 1: Raw Data Extraction ---
    # Using jupyter nbconvert to run .ipynb notebooks from terminal without GUI
    run_command("jupyter nbconvert --to notebook --execute download_dataset.ipynb", cwd="notebooks")

    # --- PHASE 2: Transformation and Cleaning (EDA) ---
    run_command("jupyter nbconvert --to notebook --execute eda_games.ipynb", cwd="notebooks")
    run_command("jupyter nbconvert --to notebook --execute eda_metadata.ipynb", cwd="notebooks")
    run_command("jupyter nbconvert --to notebook --execute eda_users.ipynb", cwd="notebooks")
    run_command("jupyter nbconvert --to notebook --execute eda_recommendations.ipynb", cwd="notebooks")

    # --- PHASE 3: Cloud Ingestion (Independent Nodes) ---
    run_command("go run games.go", cwd="src/ingestion")
    run_command("go run users.go", cwd="src/ingestion")
    
    # --- PHASE 4: Cloud Ingestion (Dependent Nodes) ---
    run_command("go run games_metadata.go", cwd="src/ingestion")
    run_command("go run recommendations.go", cwd="src/ingestion")
    

    print("\n🎉 PIPELINE EXECUTED AND COMPLETED SUCCESSFULLY! 🎉")

if __name__ == "__main__":
    main()
