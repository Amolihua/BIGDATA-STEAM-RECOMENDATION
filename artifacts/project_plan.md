# 🗺️ Plan de Implementación (Actualizado: Reemplazo Limpio con Kaggle)

## Fase 1: Data Lake y Setup (Semana 9-10)
- **Origen de datos:** Dataset de Anton Kozyriev en Kaggle ("Game Recommendations on Steam").
  - Archivos base: `games.csv`, `recommendations.csv`, `users.csv`, `games_metadata.json`.
- **Estrategia:** Descartar la extracción web (APIs) propensa a bloqueos, y utilizar este dataset estructurado para evitar dolores de cabeza con uniones o campos vacíos.
- **Ingesta Veloz:** Utilizar concurrencia en **Go** para subir masivamente estos gigantescos CSVs directamente a nuestra base de datos en la nube.

## Fase 2: Almacenamiento Estructurado (Semana 10)
- **Plataforma:** Supabase (PostgreSQL).
- **Esquema:**
  - `games` (Catálogo Maestro)
  - `users` (Tabla de Usuarios)
  - `recommendations` (Interacciones explícitas e implícitas)
- **Integridad:** Aplicaremos Llaves Primarias y Llaves Foráneas directamente en la consola de Supabase una vez subida la data.

## Fase 3: Algoritmos de Recomendación (Semanas 11-12)
- Modelo de Filtrado Colaborativo usando la tabla `recommendations`.
- Grafo de interacciones usando NetworkX / Neo4j.

## Fase 4: Despliegue y Demo (Semanas 13-14)
- API web que lea de Supabase con `anon key` (protegida con RLS).
- Frontend simple para buscar un juego y recibir recomendaciones.
