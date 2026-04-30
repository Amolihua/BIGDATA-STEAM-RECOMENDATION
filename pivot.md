Paso 1: El Pivote de "Granularidad" (Hazle caso al profe)
Ustedes plantearon originalmente agrupar (clusterizar) "perfiles de jugadores". El profe notó un problema lógico: en su tabla users.csv solo tienen IDs y cantidad de reviews, no tienen edades, países ni gustos.

- La solución del profe: En lugar de agrupar jugadores, agrupen JUEGOS. Es decir, la granularidad de su dataset final debe ser a nivel de juego. Cada fila de su dataset será un único juego (app_id), y las columnas serán todas las características de ese juego.

- ¿Por qué es mejor? Porque con esto cumplen su objetivo de encontrar "títulos puente" (ej. un juego del Clúster A que comparte características con el Clúster B, pero tiene géneros distintos) sin tener que inventar (generar data sintética) datos demográficos de los jugadores.

Paso 2: Desnormalizar (Crear la Tabla "Maestra")

Actualmente, ustedes tienen 4 archivos separados muy bien estructurados (recommendations, games, users, metadata) . Eso es "data normalizada". El algoritmo de clustering no entiende de relaciones cruzadas; necesita todo masticado en una sola tabla.

- Acción: Tienen que hacer un JOIN masivo (pueden usar Pandas, PySpark o SQL en Supabase) para consolidar todo. El objetivo final es tener un solo archivo (ej. juegos_para_ml.csv) donde la llave primaria sea app_id.

Paso 3: Feature Engineering

Aquí es donde van a brillar. El profe quiere que creen variables nuevas (columnas) a partir de la data que ya tienen. Como cada fila es un juego, deben calcularle métricas usando la tabla de recomendaciones.

Basado en lo que el profe pide y lo que ustedes tienen, tu compañero encargado de Python debe crear estas columnas para cada app_id:

1. Estadísticas de Ratings: Promedio de horas jugadas para ese juego, mediana de horas, desviación estándar.

2. El perfil del "Fan": El promedio de juegos comprados (products de la tabla users ) que tienen los usuarios que SÍ recomendaron este juego.

3. El perfil del "Hater": El promedio de juegos comprados que tienen los usuarios que NO recomendaron este juego.

4. Tono de la Descripción (NLP): Usar la tabla games_metadata.json. Tienen que pasar la description por un modelo preentrenado de HuggingFace (ej. RoBERTa para análisis de sentimientos) que les devuelva un número: qué tan positiva, negativa o neutral es la descripción del juego.

5. Embeddings: Convertir la descripción y los tags en vectores numéricos (esto será vital para la semana 5 que mencionan en su documento ).

Paso 4: Prepararse para la Reducción de Dimensionalidad

- Una vez que tengan esa tabla gigante con unas 50-100 columnas (variables), van a tener demasiadas dimensiones. El profe les advierte que para el Entregable 2 usarán PCA o SVD (que ustedes mismos propusieron ) para reducir esas columnas a 3 o 5 "Componentes Principales".
