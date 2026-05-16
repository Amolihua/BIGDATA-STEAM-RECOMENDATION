import nbformat as nbf

nb = nbf.v4.new_notebook()

# Cells
cells = [
    nbf.v4.new_markdown_cell("# Week 7: Clustering and Validation Analysis\n"
                             "## Project: Steam Big Data Recommendation Pipeline\n"
                             "This notebook performs market segmentation of Steam games using K-Means and DBSCAN, "
                             "leveraging the 7 PCA components derived from numerical metrics and semantic embeddings."),
    
    nbf.v4.new_code_cell("import pandas as pd\n"
                        "import numpy as np\n"
                        "import matplotlib.pyplot as plt\n"
                        "import seaborn as sns\n"
                        "from sklearn.cluster import KMeans, DBSCAN\n"
                        "from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score\n"
                        "from sklearn.neighbors import NearestNeighbors\n"
                        "import os\n\n"
                        "# Settings\n"
                        "sns.set(style='whitegrid')\n"
                        "os.makedirs('../reports/figures', exist_ok=True)"),
    
    nbf.v4.new_markdown_cell("### 1. Load Data\n"
                             "We load the Master Table which now contains the 7 PCA components."),
    
    nbf.v4.new_code_cell("df = pd.read_parquet('../data/processed/master_games_ml_enriched.parquet')\n"
                        "pca_cols = [col for col in df.columns if 'pca_component_' in col]\n"
                        "X = df[pca_cols].values\n\n"
                        "print(f'Using {len(pca_cols)} PCA components for clustering.')\n"
                        "print(f'Dataset shape: {df.shape}')"),
    
    nbf.v4.new_markdown_cell("### 2. K-Means Parameter Sweep\n"
                             "We evaluate K from 2 to 15 using Inertia (Elbow Method) and Silhouette Score."),
    
    nbf.v4.new_code_cell("inertias = []\n"
                        "silhouette_avg = []\n"
                        "K_range = range(2, 16)\n\n"
                        "for k in K_range:\n"
                        "    # Using a sample for silhouette calculation to speed up the sweep if dataset is large\n"
                        "    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)\n"
                        "    labels = kmeans.fit_predict(X)\n"
                        "    inertias.append(kmeans.inertia_)\n"
                        "    \n"
                        "    # Sample for silhouette to avoid long wait times\n"
                        "    sample_idx = np.random.choice(len(X), size=min(10000, len(X)), replace=False)\n"
                        "    score = silhouette_score(X[sample_idx], labels[sample_idx])\n"
                        "    silhouette_avg.append(score)\n"
                        "    print(f'K={k} processed.')"),
    
    nbf.v4.new_code_cell("fig, ax1 = plt.subplots(figsize=(10, 5))\n\n"
                        "ax1.plot(K_range, inertias, 'bo-', label='Inertia (Elbow)')\n"
                        "ax1.set_xlabel('Number of clusters (K)')\n"
                        "ax1.set_ylabel('Inertia', color='b')\n"
                        "ax1.tick_params('y', colors='b')\n\n"
                        "ax2 = ax1.twinx()\n"
                        "ax2.plot(K_range, silhouette_avg, 'ro-', label='Silhouette Score')\n"
                        "ax2.set_ylabel('Silhouette Score', color='r')\n"
                        "ax2.tick_params('y', colors='r')\n\n"
                        "plt.title('K-Means Parameter Sweep: Elbow and Silhouette')\n"
                        "plt.savefig('../reports/figures/kmeans_sweep.png')\n"
                        "plt.show()"),
    
    nbf.v4.new_markdown_cell("### 3. DBSCAN and Epsilon Search\n"
                             "DBSCAN requires finding the optimal `eps`. We use the K-Distance plot."),
    
    nbf.v4.new_code_cell("neigh = NearestNeighbors(n_neighbors=14) # 2 * dimensions\n"
                        "nbrs = neigh.fit(X)\n"
                        "distances, indices = nbrs.kneighbors(X)\n\n"
                        "distances = np.sort(distances[:, 13], axis=0)\n"
                        "plt.figure(figsize=(10, 5))\n"
                        "plt.plot(distances)\n"
                        "plt.title('K-Distance Plot for DBSCAN Epsilon')\n"
                        "plt.xlabel('Points sorted by distance')\n"
                        "plt.ylabel('14-th Nearest Neighbor Distance')\n"
                        "plt.savefig('../reports/figures/dbscan_kdistance.png')\n"
                        "plt.show()")
]

nb.cells.extend(cells)

with open('notebooks/clustering_analysis.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Created notebooks/clustering_analysis.ipynb")
