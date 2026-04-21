# Plan de Proyecto: Motor de Recomendación de Steam

Este documento describe la arquitectura, la estrategia de datos y el flujo de los entregables para el proyecto de Big Data, tomando en cuenta las especificaciones de las guías de la clase.

## 1. Arquitectura Tecnológica y Base de Datos (Cloud)

> [!TIP]
> **Base de Datos Recomendada**: **Supabase** (Basada en PostgreSQL).
> Se alinea perfectamente con los requerimientos del grupo:
> - **Gratis:** Excelente generador gratuito (500MB de espacio en BD y 2GB de salida de banda ancha).
> - **Colaborativo:** Permite agregar a todo tu grupo en una misma "organización" para acceder a las tablas y métricas.
> - **REST API lista para usarse:** Por debajo utiliza `PostgREST`, lo cual significa que cualquier tabla que subas tiene de manera automática una API (GET, POST, PATCH, DELETE) que podrán usar luego para conectar el proyecto final.
> - **SDK Python:** Librería fácil de usar (`supabase-py`) para inyectar datos masivos directo desde los Jupyter Notebooks.

### Capas del Pipeline a implementar con Python & Supabase:
*   **Raw Data:** Extraída desde Kaggle o la API de Steam (limpieza vía Pandas).
*   **Processed Data:** Tablas subidas a Supabase (ej. `games`, `features`, `interactions`).
*   **Models:** Entrenamiento de modelos en local (Jupyter/Python) consumiendo la DB.
*   **Service Layer:** Notebook interactivo, Streamlit o API directa que consulte las tablas maestras.

---

## 2. Definición Estratégica de las Capas de Big Data (Core Layers)

Según el `semester_group_assignment_brief.md`, el proyecto cubrirá 4 capas:

1.  **Catalog Layer (Catálogo):**
    *   Entidades principales: Juegos (Steam IDs, nombres, géneros).
2.  **Feature Layer (Características):**
    *   Codificación: One-Hot Encoding de etiquetas (tags), specs de hardware, años de lanzamiento. Embeddings si aplicamos NLP en sus descripciones.
3.  **Interaction Layer (Interacciones/Comportamiento):**
    *   Métricas: Horas de juego promedio por usuario, reseñas (positivas/negativas).
4.  **Graph Layer (Grafos):**
    *   Proyección: Grafo Item-Item basado en qué juegos fueron comprados/jugados por los mismos grupos de personas.

---

## 3. Entregables y Cronograma por Semanas

El flujo de progreso estará directamente amarrado a las semanas de la guía `mds_guide_finalproject`.

### Week 3: Ingesta y Dataset Base (Processed V1)
- **Actividades:** Limpiar el archivo `steam-games.csv`, generar joins.
- **Entregable Nube:** Cargar la data maestra limpia como tabla relacional hacia Supabase.
- **Entregable Local:** Diccionario de datos y análisis de forma/sparsidad. Creación de una instrucción y script `ingestion.py`.

### Week 5: Singular Value Decomposition (SVD), PCA & Representación
- **Actividades:** Reducción de dimensionalidad de todas las características (géneros, requisitos).
- **Entregable:** Matriz comprimida implementando PCA/SVD (idealmente graficada usando t-SNE) para validar qué tan cerca caen géneros similares.

### Week 7: Segmentación, K-Means y DBSCAN
- **Actividades:** Clusterizar el catálogo de juegos masivos.
- **Entregable:** Segmentar el dominio (Ej: Cluster 1: AAA shooters; Cluster 2: Indie platforms). Validar los resultados calculando el *Silhouette score*.

### Week 10: Motores de Recomendación (CF o Híbridos)
- **Actividades:** Implementar el "decision engine". 
- **Entregable:** Dos módulos:
  1.  **Baseline:** Filtrado basado en contenido (Cosine Similarity entre géneros).
  2.  **Advanced:** Filtrado colaborativo (apoyado en interacciones si logramos cruzar tablas de usuarios, o factorización matricial implícita).

### Week 12: Grafos, PageRank y Centralidad
- **Actividades:** Entender la red profunda de Steam.
- **Entregable:** Crear un script de grafos (NetworkX o igraph) donde los pesos de aristas son juegos similares. Implementar medición de centralidad y responder: ¿Cuáles son los juegos más troncales del sistema?

### Week 14: Defensa y Sistema Final Interactivo
- **Actividades:** Demo Final.
- **Entregable:** Como vamos a utilizar Supabase desde el inicio, el Demo de la Semana 14 podrá simplemente realizar peticiones a la API desde un Notebook interactivo para generar predicciones en tiempo real frente a los profesores.
