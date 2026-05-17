import nbformat as nbf

notebook_path = 'notebooks/clustering_analysis.ipynb'
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

# Cells to append
extra_cells = [
    nbf.v4.new_markdown_cell("### 4. Final Clustering Selection (K-Means)\n"
                             "Based on the sweep, we select an optimal K (e.g., K=6) to perform the detailed analysis."),
    
    nbf.v4.new_code_cell("optimal_k = 6\n"
                        "kmeans_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)\n"
                        "df['kmeans_cluster'] = kmeans_final.fit_predict(X)\n\n"
                        "print(f'Games per cluster:\\n{df[\"kmeans_cluster\"].value_counts()}')"),
    
    nbf.v4.new_markdown_cell("### 5. DBSCAN Implementation\n"
                             "We apply DBSCAN with the selected `eps` (e.g., 0.5) and `min_samples`."),
    
    nbf.v4.new_code_cell("dbscan = DBSCAN(eps=0.5, min_samples=14)\n"
                        "df['dbscan_cluster'] = dbscan.fit_predict(X)\n\n"
                        "print(f'DBSCAN Clusters found (including -1 for noise):\\n{df[\"dbscan_cluster\"].value_counts()}')"),
    
    nbf.v4.new_markdown_cell("### 6. Validation Table\n"
                             "We compare the two methods using standard metrics."),
    
    nbf.v4.new_code_cell("metrics = []\n\n"
                        "for label_col, name in [('kmeans_cluster', 'K-Means'), ('dbscan_cluster', 'DBSCAN')]:\n"
                        "    labels = df[label_col].values\n"
                        "    # Filter out noise for DBSCAN metrics if needed, or include it\n"
                        "    mask = labels != -1\n"
                        "    if mask.sum() > 1:\n"
                        "        metrics.append({\n"
                        "            'Method': name,\n"
                        "            'Silhouette': silhouette_score(X[sample_idx], labels[sample_idx]),\n"
                        "            'Calinski-Harabasz': calinski_harabasz_score(X, labels),\n"
                        "            'Davies-Bouldin': davies_bouldin_score(X, labels)\n"
                        "        })\n\n"
                        "validation_df = pd.DataFrame(metrics)\n"
                        "print(validation_df)"),
    
    nbf.v4.new_markdown_cell("### 7. Cluster Profile Analysis\n"
                             "We analyze the mean values of original features to characterize the clusters."),
    
    nbf.v4.new_code_cell("profile_cols = [\n"
                        "    'hours_mean', 'rec_ratio', 'review_count', \n"
                        "    'fan_avg_products', 'sentiment_score', 'price_original'\n"
                        "]\n\n"
                        "cluster_profiles = df.groupby('kmeans_cluster')[profile_cols].mean()\n"
                        "print(cluster_profiles)\n\n"
                        "plt.figure(figsize=(12, 8))\n"
                        "sns.heatmap(cluster_profiles.T, annot=True, cmap='YlGnBu')\n"
                        "plt.title('Cluster Profiling Heatmap (K-Means Means)')\n"
                        "plt.savefig('../reports/figures/cluster_profiles.png')\n"
                        "plt.show()"),
    
    nbf.v4.new_markdown_cell("### 8. Failure Analysis\n"
                             "We look for points with low Silhouette values or clusters with extreme variance."),
    
    nbf.v4.new_code_cell("# Identifying games in the most ambiguous cluster or near boundaries\n"
                        "sample_silhouette_values = silhouette_score(X[sample_idx], df.loc[sample_idx, 'kmeans_cluster'], sample_size=1000)\n"
                        "# This is a placeholder for a more complex per-point calculation if needed\n\n"
                        "print('Failure Analysis: Cluster -1 in DBSCAN represents games that are semantically and numerically unique (outliers).')\n"
                        "outliers = df[df['dbscan_cluster'] == -1].head(10)\n"
                        "print('Example Outliers (Noise):')\n"
                        "print(outliers[['name', 'review_count', 'hours_mean']])")
]

nb.cells.extend(extra_cells)

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Updated {notebook_path}")
