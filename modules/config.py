import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# 🔹 Configuración de Flask
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", os.urandom(24))

# 🔹 Configuración de Mistral API
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# 🔹 Configuración de Jira
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "AUL2")
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN", "ucc.atlassian.net")

# 🔹 Configuración de Confluence
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")

# 🔹 Archivos y carpetas
PATH_CONFIG_TESTCASES = "data/config_testcases.json"
PATH_KNOWLEDGE_BASE = "data/aulario_knowledge_base.json"
PATH_CONTEXTO_EXCEL = "data/Contexto_Extra.xlsx"
PATH_PROCESSED_ISSUES = "data/processed_issues.json"
PATH_GENERATED_CASES = "generated_test_cases"
