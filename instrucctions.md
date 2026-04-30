# Technical Guide: "Bridge Titles" Recommendation Model

This guide outlines the architecture and logic for the Steam Recommendation System, specifically focusing on identifying "Bridge Titles" to break users out of their typical consumption "bubbles."

## 1. Feature Layer
**Objective:** Transform semantic game information into processable numerical vectors.

*   **Metadata Processing:** Extract descriptions and tags from the raw `games_metadata` dataset.
*   **Vectorization & NLP:** Apply Natural Language Processing (NLP) techniques (like TF-IDF or Word2Vec) on enriched texts to identify latent themes.
*   **Dimensionality Reduction:** Utilize methods such as **SVD** (Singular Value Decomposition) or **PCA** (Principal Component Analysis) on feature vectors to find similarities between titles across diverse genres.

## 2. Interaction Layer
**Objective:** Identify user communities based on real consumption patterns.

*   **Utility Matrix:** Build a sparse matrix of interactions using `user_id` and `app_id`.
*   **Usage Intensity:** Integrate "hours played" to weight the strength of each interaction, ensuring the model prioritizes games the user actually invested in.
*   **Profile Clustering:** Group users into behavioral clusters to define "consumption communities," moving beyond simple genre-based filtering.

## 3. Graph Layer
**Objective:** Map the connections between different game "bubbles."

*   **Induced Graph Construction:** Represent the ecosystem as a graph where nodes are games and edges represent shared users (co-occurrence).
*   **Bridge Identification:** Apply **Betweenness Centrality** metrics to detect "Bridge Titles"—nodes that mathematically act as connectors between genre clusters that are otherwise isolated.

## 4. "Anti-Bubble" Recommendation Logic
**Objective:** The final algorithmic flow to generate cross-genre recommendations.

1.  **Current Bubble Detection:** Identify the specific behavior cluster the user currently resides in based on their play history.
2.  **Bridge Title Selection:** Query the graph for high-centrality nodes (Bridges) that link the user's current cluster to foreign communities.
3.  **Quality Filter:** Rank selected bridge titles by `positive_ratio` and review volume to ensure recommendations are high-quality and reliable.
