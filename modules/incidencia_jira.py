import os
import time
import threading
import requests
import json
import base64
from datetime import datetime
from flask import current_app

class JiraMonitor:
    def __init__(self, app):
        self.app = app
        self.active = False
        self.thread = None

        self.jira_domain = "ucc.atlassian.net"
        self.project_key = "AUL2"
        self.polling_interval = 60  # cada 1 minuto

        self.email = os.environ.get("JIRA_EMAIL")
        self.api_token = os.environ.get("JIRA_API_TOKEN")

        if not self.email or not self.api_token:
            raise ValueError("JIRA_EMAIL y JIRA_API_TOKEN deben estar configurados")

        self.encoded_auth = base64.b64encode(f"{self.email}:{self.api_token}".encode()).decode()

        self.processed_file = "data/processed_issues.json"
        self.processed_issues = self.load_processed_issues()

        # NUEVO: variable para incidencia que está procesándose
        self.current_issue = None

    def load_processed_issues(self):
        if os.path.exists(self.processed_file):
            with open(self.processed_file, "r", encoding="utf-8") as f:
                return set(json.load(f))
        return set()

    def save_processed_issues(self):
        os.makedirs("data", exist_ok=True)
        with open(self.processed_file, "w", encoding="utf-8") as f:
            json.dump(list(self.processed_issues), f, indent=2)

    def start_monitoring(self):
        if not self.active:
            self.active = True
            self.thread = threading.Thread(target=self.monitor_issues, daemon=True)
            self.thread.start()
            self.log(f"Monitor de Jira iniciado para proyecto {self.project_key}")

    def stop_monitoring(self):
        self.active = False
        self.log("Monitor de Jira detenido")

    def monitor_issues(self):
        while self.active:
            try:
                self.check_jira_issues()
            except Exception as e:
                self.log(f"Error en monitorización: {e}", level="error")
            time.sleep(self.polling_interval)

    def check_jira_issues(self):
        jql = f"project = {self.project_key} AND status = 'QA TESTING'"
        self.log(f"Consultando Jira con JQL: {jql}")

        headers = {
            "Authorization": f"Basic {self.encoded_auth}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(
                f"https://{self.jira_domain}/rest/api/3/search",
                headers=headers,
                params={"jql": jql, "fields": "summary,description"}
            )
            response.raise_for_status()
            issues = response.json().get("issues", [])

            for issue in issues:
                issue_key = issue.get("key")

                if issue_key in self.processed_issues:
                    self.log(f"Issue {issue_key} ya procesado, ignorando...")
                    continue

                self.log(f"Nuevo issue detectado en QA TESTING: {issue_key}")
                self.processed_issues.add(issue_key)
                self.save_processed_issues()

                self.process_jira_issue(issue)

        except requests.exceptions.RequestException as e:
            self.log(f"Error al consultar Jira: {e}", level="error")

    def process_jira_issue(self, issue):
        issue_key = issue.get("key")
        fields = issue.get("fields", {})
        title = fields.get("summary", "")
        description = fields.get("description", "")

        if "[BE]" in title.upper():
            tipo = "BE"
        elif "[FE]" in title.upper():
            tipo = "FE"
        else:
            tipo = "BE"
            self.log(f"Issue {issue_key} sin etiqueta, asignado a BE por defecto")

        user_story = f"{title}\n\n{description}"

        self.current_issue = issue_key  # <-- Aquí asignamos la incidencia en proceso

        try:
            with self.app.app_context():
                test_cases = current_app.extensions['generator'](user_story, tipo)
                self.save_test_cases(issue_key, test_cases, title)
                self.update_jira_issue(issue_key, test_cases)
                self.log(f"Generados {len(test_cases)} casos ({tipo}) para {issue_key}")
        except Exception as e:
            self.log(f"Error procesando {issue_key}: {e}", level="error")
        finally:
            self.current_issue = None  # <-- Al finalizar limpiamos

    def save_test_cases(self, issue_key, test_cases, title):
        os.makedirs("generated_test_cases", exist_ok=True)
        safe_title = "".join(c if c.isalnum() or c in "._-" else "_" for c in title)[:30]
        filename = f"generated_test_cases/{issue_key}_{safe_title}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(test_cases, f, indent=2)

    def update_jira_issue(self, issue_key, test_cases):
        headers = {
            "Authorization": f"Basic {self.encoded_auth}",
            "Content-Type": "application/json"
        }
        comment = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{
                        "type": "text",
                        "text": f"Se generaron {len(test_cases)} casos de prueba automáticamente."
                    }]
                }]
            }
        }
        try:
            requests.post(
                f"https://{self.jira_domain}/rest/api/3/issue/{issue_key}/comment",
                headers=headers,
                json=comment
            )
        except requests.exceptions.RequestException as e:
            self.log(f"Error actualizando {issue_key}: {e}", level="error")

    def log(self, message, level="info"):
        with self.app.app_context():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [{level.upper()}] {message}")
