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

python -m pip install -r requirements.txt


***Configura el archivo de credenciales (.env):**

El repositorio incluye una plantilla llamada .env.example.

Crea una copia de este archivo en la raíz del proyecto y nómbralo exactamente .env (este archivo se mantiene de forma local y está protegido en .gitignore).

Abre el archivo .env en tu editor, escribe tu clave real bajo la variable configurada en el proyecto (API_KEY):

Fragmento de código
API_KEY=tu_clave_api_real_aqui
⚠️ Importante (VS Code): Asegúrate de guardar los cambios en el archivo .env presionando Ctrl + S (o Cmd + S en Mac). Si el archivo queda sin guardar, el programa no leerá la clave actualizada y arrojará un error de credenciales no válidas.



*** Cómo Utilizar el Proyecto***

* Importante: Asegúrate de que tu entorno virtual esté activo (venv) en la terminal antes de ejecutar cualquiera de los siguientes comandos.

1. Ejecutar el Banco de Prompts y Pruebas de Consistencia

Si ejecutas directamente el módulo principal, este validará la consistencia del banco de prompts definido y creará/actualizará automáticamente el archivo registro_resultados.json:

python src/consumir_gemini.py


2. Realizar consultas personalizadas desde archivo main.py

Tu archivo de ejecución principal importa la función coordinadora obtener_dato_de_prueba para enviar preguntas e instrucciones de sistema personalizadas
 *1* Modificar Instruccion de sistema a la deseada
 *2* Modificar pregunta_usuario para obtener respuesta deseada.
 *3* En la Terminal Ejecutar:
    python src/main.py

## Estructura de carpetas

- `src/` : todo el código fuente del proyecto va aquí.
- `docs/` : documentación técnica del proyecto (diagramas, decisiones de arquitectura, notas).
- `prompts/` : registros de resultados.json 
- `tests/` : pruebas de tu código
- `requirements.txt` : dependencias de Python de tu proyecto, p
- `.env.example` : plantilla de las variables de entorno.  Crear archivo `.env` real (con tus credenciales) no comitearlo
- `.gitignore` : le dice a Git qué archivos y carpetas ignorar (entre ellos, tu entorno virtual y tu archivo `.env`).


📝 Registro del Ensayo de Instalación Limpia e Incidencias
Fecha: 2026-10-22 (Entre las 20:30 y 23:30 hrs)

Incidencia 1: Error No such file or directory: requirements.txt al intentar instalar dependencias.

Causa: Terminal abierta fuera de la raíz del proyecto o antes de configurar la estructura.

Solución: Posicionarse en la carpeta raíz y utilizar python -m pip install -r requirements.txt.

Incidencia 2: Error pip : El término 'pip' no se reconoce como nombre de un cmdlet.

Causa: Restricciones del sistema o PowerShell sin el ejecutable global directo.

Solución: Invocación robusta mediante el módulo de Python (python -m pip).

Incidencia 3: Error por ubicación de archivos de código (consumir_gemini.py no se encontraba).

Causa: Los archivos de lógica están alojados dentro de la subcarpeta src/.

Solución: Ejecución apuntando a la ruta relativa correcta desde la raíz (python src/consumir_gemini.py).

Incidencia 4: Error de API Key no válida o no encontrada al correr las pruebas.

Causa A: Uso de una variable distinta (GEMINI_API_KEY vs API_KEY).

Causa B: Modificación del archivo .env en Visual Studio Code sin guardar los cambios (Ctrl + S).

Solución: Estandarizar la variable a API_KEY según el código y asegurar el guardado físico del archivo .env antes de correr el script.

Resultado final: El proyecto corre de forma fluida, validando credenciales, cargando variables locales y procesando consultas e instrucciones personalizadas sin intervención manual adicional.