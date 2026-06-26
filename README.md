TwitterScraper

Scraper de tweets para el proyecto de investigación "Plataforma Inteligente para la Detección de Tendencias Emergentes y Desinformación Digital"

Recolecta tweets y los guarda en CSVs permitiendo unificar todos los datos en una sola base de datos Neo4j.


¿Qué hace?

Dado un hashtag, una búsqueda o un perfil de usuario, el scraper extrae:


Texto completo del tweet y los primeros 100 caracteres como título
URL, fecha, tipo (tweet / retweet / reply / quote)
Autor: nombre, @usuario, cantidad de seguidores
Hashtags usados en el tweet
Métricas: likes, retweets, replies, views
Oraciones del tweet clasificadas automáticamente como cita, estadística o sin clasificar — base para el análisis de verificabilidad


Todo queda guardado en CSVs listos para importar a Neo4j.


Estructura del proyecto

twitter_scraper/
├── main.py                        # Punto de entrada CLI
├── requirements.txt               # Dependencias
├── setup_cookies.py               # Script para configurar la cuenta de Twitter
├── .env                           # Credenciales
├── .env.example                   # Plantilla del .env sin valores reales
├── .gitignore
├── modelos/
│   └── esquema.py                 # Dataclasses del modelo de datos
├── scraper/
│   ├── recolector.py              # Lógica principal de scraping
│   └── parseador_tweet.py        # Convierte tweets al esquema de nodos/relaciones
├── salida/
│   └── escritor_csv.py            # Escritura incremental a CSVs sin duplicados
└── tests/
    ├── test_esquema.py
    ├── test_parseador_tweet.py
    └── test_escritor_csv.py


Instalación

Requiere Python 3.11+.

bashcd twitter_scraper
python -m venv venv
venv\Scripts\activate        # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
pip install python-dotenv


Configuración (primera vez)

Cuenta del proyecto

Para este proyecto cree una cuenta de Twitter dedicada: @proyinvestigaci (proyectoinvestigacionok@gmail.com). Las credenciales y cookies están en el archivo .env que  comparto por el grupo de forma privada.

Paso 1 — Crear el archivo .env

Completalo con las credenciales que te pase.

Paso 2 — Obtener las cookies de Twitter

Twitter bloquea los logins automáticos desde Argentina usando Cloudflare. Por eso en vez de loguearse con usuario y contraseña, el scraper usa las cookies de una sesión ya abierta en el navegador.


Instalá la extensión Cookie-Editor en Chrome
Entrá a twitter.com y logueate con la cuenta @proyinvestigaci
Hacé clic en el ícono del puzzle (extensiones) → Cookie-Editor
En el popup que se abre, hacé clic en el último ícono abajo a la derecha (Export)
Se copia un JSON al portapapeles con todas las cookies
Del JSON, extraé los valores de auth_token, ct0 y twid y armalos así en el .env:


TW_COOKIES=auth_token=VALOR; ct0=VALOR; twid=VALOR

Las cookies duran aproximadamente 30 días. Cuando el scraper deje de funcionar, hay que repetir este proceso y actualizar el .env.



Paso 3 — Registrar la cuenta

bashpython setup_cookies.py

Si todo está bien, deberías ver:

Usuario: proyinvestigaci | Activa: True | Status: None

Si dice active=False o aparece un error de Cloudflare, las cookies expiraron asi que hay que repetir el Paso 2.


Uso

Búsqueda por hashtag o palabras clave

bashpython main.py --query "#FakeNews lang:es" --max 200
python main.py --query "desinformacion Argentina" --max 500
python main.py --query "fake news -filter:retweets lang:es" --max 300

Perfil de usuario

bashpython main.py --usuario infobae --max 100
python main.py --usuario clarincom --max 100
python main.py --usuario LANACION --max 100

Tweet individual

bashpython main.py --url https://twitter.com/usuario/status/123456789

Opciones disponibles

OpciónDefaultDescripción--query—Búsqueda por palabras clave o hashtag--usuario—Perfil de usuario a scrapear--url—URL o ID de un tweet individual--max100Máximo de tweets a recolectar--salidadatos/Carpeta de salida para los CSVs--delay2.0Segundos entre requests (no bajar de 1.5)

Los CSVs se guardan en la carpeta datos/ (incluida en .gitignore, no se sube al repo).


CSVs generados

Nodos

ArchivoNodo Neo4jContenidomedios.csv(:Medio)Siempre Twitter/Xnoticias.csv(:Noticia)Tweets con texto, fecha, métricasautores.csv(:Autor)Usuario, seguidores, verificadotemas.csv(:Tema)Hashtags normalizadosverificaciones.csv(:Verificacion)Oraciones clasificadas del tweet

Relaciones

ArchivoRelación Neo4jrel_publica.csv(Medio)-[:PUBLICA]->(Noticia)rel_escrito_por.csv(Noticia)-[:ESCRITO_POR]->(Autor)rel_menciona.csv(Noticia)-[:MENCIONA]->(Tema)rel_verifica.csv(Verificacion)-[:VERIFICA]->(Noticia)


Cargar en Neo4j Desktop

Paso 1 — Encontrar la carpeta import

Abrí Neo4j Desktop → tres puntitos ... de tu base de datos → Open neo4j.conf → abrilo con el Bloc de notas → buscá la línea server.windows_service_name y copiá el ID que aparece ahí.

La carpeta import está en:

C:\Users\TU_USUARIO\.Neo4jDesktop2\Data\dbmss\dbms-ID_QUE_COPIASTE\import\

Pegá esa ruta en el explorador de archivos y copiá todos los CSVs de la carpeta datos/ ahí adentro.

Paso 2 — Ejecutar las queries en Neo4j Browser

Abrí tu base de datos → botón Open → pegá estas queries una por una:

cypher// Nodos
LOAD CSV WITH HEADERS FROM 'file:///medios.csv' AS row
MERGE (:Medio {id: row.medio_id, nombre: row.nombre});

LOAD CSV WITH HEADERS FROM 'file:///autores.csv' AS row
MERGE (:Autor {id: row.autor_id, nombre: row.nombre, username: row.username, seguidores: toInteger(row.seguidores)});

LOAD CSV WITH HEADERS FROM 'file:///temas.csv' AS row
MERGE (:Tema {id: row.tema_id, nombre: row.nombre});

LOAD CSV WITH HEADERS FROM 'file:///noticias.csv' AS row
CREATE (:Noticia {id: row.noticia_id, url: row.url, titulo: row.titulo, fecha: row.fecha_publicacion, seccion: row.seccion, likes: toInteger(row.likes), retweets: toInteger(row.retweets)});

LOAD CSV WITH HEADERS FROM 'file:///verificaciones.csv' AS row
CREATE (:Verificacion {id: row.verificacion_id, texto: row.texto, tipo: row.tipo});

// Relaciones
LOAD CSV WITH HEADERS FROM 'file:///rel_publica.csv' AS row
MATCH (m:Medio {id: row.medio_id}), (n:Noticia {id: row.noticia_id})
CREATE (m)-[:PUBLICA]->(n);

LOAD CSV WITH HEADERS FROM 'file:///rel_escrito_por.csv' AS row
MATCH (n:Noticia {id: row.noticia_id}), (a:Autor {id: row.autor_id})
CREATE (n)-[:ESCRITO_POR]->(a);

LOAD CSV WITH HEADERS FROM 'file:///rel_menciona.csv' AS row
MATCH (n:Noticia {id: row.noticia_id}), (t:Tema {id: row.tema_id})
CREATE (n)-[:MENCIONA]->(t);

LOAD CSV WITH HEADERS FROM 'file:///rel_verifica.csv' AS row
MATCH (v:Verificacion {id: row.verificacion_id}), (n:Noticia {id: row.noticia_id})
CREATE (v)-[:VERIFICA]->(n);

Paso 3 — Ver el grafo

cypherMATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 50

