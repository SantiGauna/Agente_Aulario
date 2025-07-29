🧠 Agente Aulario – Generador de Casos de Prueba Automatizados
Agente Aulario es una aplicación Flask que monitorea Jira en busca de issues listos para QA Testing, genera casos de prueba automáticamente (basados en contexto funcional y reglas configuradas) y permite exportarlos a Excel, visualizarlos y gestionarlos desde una interfaz web.

🚀 Características
📡 Monitoreo automático de Jira (proyecto AUL2, estado QA TESTING).

📝 Generación automática de casos de prueba (Front-End y Back-End) según contexto configurado.

📤 Exportación a Excel con formato listo para uso en QA.

📂 Gestión de casos generados (ver, limpiar y regenerar casos).

⚙️ Configuración modular (contexto, reglas, campos).

🔒 Manejo seguro de credenciales con .env.

📂 Estructura del Proyecto
Agent_Aulario/
│
├── app.py                     # Aplicación Flask principal
├── requirements.txt           # Dependencias del proyecto
├── .env                       # Variables de entorno sensibles
├── data/
│   ├── config_testcases.json  # Configuración JSON para tipos de casos
│   ├── aulario_knowledge_base.json  # Base de conocimiento local
│   ├── Contexto_Extra.xlsx    # Archivo Excel con contexto adicional
│   └── processed_issues.json  # Issues Jira ya procesados
│
├── generated_test_cases/      # Casos de prueba generados (JSON)
│
├── modules/
│   ├── __init__.py
│   ├── incidencia_jira.py     # Monitor Jira
│   ├── testcase_generator.py  # Generador de casos de prueba
│   ├── context_loader.py      # Carga de contexto/configuración
│   └── utils.py               # Funciones utilitarias
│
├── templates/                 # Plantillas HTML (Flask Jinja2)
│   ├── index.html
│   ├── list_generated.html
│   └── show_generated.html
│
└── static/                    # Archivos estáticos (CSS, JS)

⚙️ Instalación y Ejecución
1️⃣ Clonar el repositorio
git clone https://github.com/TU_USUARIO/Agente_Aulario.git
cd Agente_Aulario

2️⃣ Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

3️⃣ Instalar dependencias
pip install -r requirements.txt

4️⃣ Configurar variables de entorno
FLASK_SECRET_KEY=clave_secreta
MISTRAL_API_KEY=tu_api_key
JIRA_URL=https://tu-jira.com
JIRA_USER=tu_usuario
JIRA_TOKEN=tu_token
START_MONITOR=true

5️⃣ Ejecutar aplicación
python app.py
Acceder a: http://127.0.0.1:5000

🖥️ Uso
Pantalla principal: ingresar User Story y generar casos manualmente.
Se generan casos automáticos cuando el sistema detecta que hay nuevas incidencias en la columna de QA TESTING

Pantalla de generados: listar, ver y limpiar casos ya generados.

Exportación: generar archivo Excel con casos listos para QA.


🧩 Tecnologías
Python 3.12

Flask

Jinja2

Pandas

Jira API

Bootstrap 5
