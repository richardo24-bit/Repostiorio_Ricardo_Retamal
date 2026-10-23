Cliente REST Modular para Google Gemini API

Este proyecto implementa un cliente y módulo en Python para interactuar de forma directa con la API REST de Google Gemini. Está diseñado de manera modular y robusta, abarcando desde peticiones básicas hasta control de costos, separación de instrucciones de sistema y validación de esquemas.

***Prerrequisitos e Instalación Paso a Paso**

Abre tu terminal en la carpeta raíz del proyecto (asegúrate de no estar ubicado en otra ruta para que la terminal detecte los archivos locales correctamente).

***Crea el entorno virtual dentro de la carpeta del proyecto ejecutando el siguiente comando:***

python -m venv venv


***Activa el entorno virtual (recuerda hacer esto cada vez que abras una nueva terminal antes de instalar dependencias o ejecutar scripts):***

En Windows (CMD / PowerShell):

venv\Scripts\activate


En macOS / Linux:

source venv/bin/activate


***Instala las dependencias usando el archivo de requerimientos:***

pip install -r requirements.txt


***Configura el archivo de credenciales (.env):**

El repositorio incluye una plantilla de ejemplo llamada .env.example.

Crea una copia de este archivo en la misma carpeta raíz y nómbralo .env (este archivo se mantiene de forma local y está protegido en el .gitignore para no subir tus credenciales).

Abre el archivo .env y configura tu llave personal utilizando exactamente la variable que busca el código (API_KEY):

API_KEY=tu_clave_api_real_aqui



*** Cómo Utilizar el Proyecto***

* Importante: Asegúrate de que tu entorno virtual esté activo (venv) en la terminal antes de ejecutar cualquiera de los siguientes comandos.

1. Ejecutar el Banco de Prompts y Pruebas de Consistencia

Si ejecutas directamente el módulo principal, este validará la consistencia del banco de prompts definido y creará/actualizará automáticamente el archivo registro_resultados.json:

python consumir_gemini.py


2. Realizar consultas personalizadas desde main.py

Tu archivo de ejecución principal importa la función coordinadora obtener_dato_de_prueba para enviar preguntas e instrucciones de sistema personalizadas


## Estructura de carpetas

- `src/` : todo el código fuente del proyecto va aquí.
- `docs/` : documentación técnica del proyecto (diagramas, decisiones de arquitectura, notas).
- `prompts/` : registros de resultados.json 
- `tests/` : pruebas de tu código
- `requirements.txt` : dependencias de Python de tu proyecto, p
- `.env.example` : plantilla de las variables de entorno.  Crear archivo `.env` real (con tus credenciales) no comitearlo
- `.gitignore` : le dice a Git qué archivos y carpetas ignorar (entre ellos, tu entorno virtual y tu archivo `.env`).


Registro del ensayo de instalación limpia

Fecha: 2026-10-22 (20:30 - 21:27 hrs)

Encontrado:

Error No such file or directory: 'requirements.txt' al intentar instalar dependencias debido a que el entorno virtual se había creado fuera de la carpeta raíz del proyecto.

Error No se encontró la API key en las variables de entorno porque el archivo .env utilizaba la clave API_KEY= mientras que el entorno requería concordancia exacta con la lectura de credenciales.

Corregido:

Se recreó el entorno virtual venv estrictamente dentro de la carpeta raíz del repositorio para alinear la ruta de ejecución con el archivo requirements.txt.

Se unificó la nomenclatura en el archivo .env utilizando API_KEY= para asegurar la lectura correcta mediante os.getenv().

Resultado tras la corrección: El proyecto realiza la instalación limpia de dependencias y ejecuta el script main.py sin errores ni intervención manual adicional