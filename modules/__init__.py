from flask import Flask
from .config import FLASK_SECRET_KEY, MISTRAL_API_KEY, MISTRAL_API_URL
from .incidencia_jira import JiraMonitor
from .testcase_generator import generar_casos_prueba

def create_app():
    app = Flask(__name__)
    app.secret_key = FLASK_SECRET_KEY
    
    # Config API
    app.config['MISTRAL_API_KEY'] = MISTRAL_API_KEY
    app.config['MISTRAL_API_URL'] = MISTRAL_API_URL
    
    # Extensiones
    app.extensions['generator'] = generar_casos_prueba
    app.jira_monitor = JiraMonitor(app)
    
    return app
