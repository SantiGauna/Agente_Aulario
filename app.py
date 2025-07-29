from flask import Flask, render_template, request, send_file, url_for, flash, redirect, jsonify, abort
import os
import json
import pandas as pd
from io import BytesIO
from datetime import datetime


# Importar módulos internos
from modules.incidencia_jira import JiraMonitor
from modules.testcase_generator import generar_casos_prueba
from modules.context_loader import CONFIG_TESTCASES

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

    # Configuración Mistral
    app.config['MISTRAL_API_KEY'] = os.environ.get("MISTRAL_API_KEY")
    app.config['MISTRAL_API_URL'] = "https://api.mistral.ai/v1/chat/completions"

    # Extensión generador
    app.extensions['generator'] = generar_casos_prueba

    # Monitor Jira
    app.jira_monitor = JiraMonitor(app)

    @app.route("/", methods=["GET", "POST"])
    def index():
        test_cases, error, user_story = [], None, ""
        tipo = "BE"  # default

        if request.method == "POST":
            user_story = request.form.get("user_story", "").strip()
            tipo = "FE" if "[FE]" in user_story.upper() else "BE"

            try:
                if user_story:
                    test_cases = generar_casos_prueba(user_story, tipo)
                    flash(f"Casos de prueba ({tipo}) generados exitosamente!", "success")
            except Exception as e:
                error = str(e)
                flash(f"Error: {error}", "danger")

        columnas = CONFIG_TESTCASES.get(tipo, {}).get("fields", [])
        return render_template("index.html", campos=columnas, test_cases=test_cases, user_story=user_story, error=error, tipo=tipo)

    @app.route("/export", methods=["POST"])
    def export():
        try:
            test_cases = json.loads(request.form.get("test_cases", "[]"))
            if not test_cases:
                flash("No hay casos de prueba para exportar", "warning")
                return redirect(url_for("index"))

            df = pd.DataFrame(test_cases)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="TestCases")

            output.seek(0)
            filename = f"test_cases_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            return send_file(output, as_attachment=True, download_name=filename,
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            flash(f"Error al exportar: {str(e)}", "danger")
            return redirect(url_for("index"))

    @app.route("/generated")
    def list_generated():
        folder = "generated_test_cases"
        files = [f for f in os.listdir(folder)] if os.path.exists(folder) else []
        return render_template("list_generated.html", files=files)

    @app.route("/generated/<issue_key>")
    def show_generated(issue_key):
        filepath = os.path.join("generated_test_cases", f"{issue_key}.json")
        if not os.path.exists(filepath):
            abort(404)

        with open(filepath, "r", encoding="utf-8") as f:
            test_cases = json.load(f)

        tipo = test_cases[0].get("_tipo", "BE")
        columnas = CONFIG_TESTCASES.get(tipo, {}).get("fields", [])
        return render_template("show_generated.html", issue_key=issue_key, test_cases=test_cases, campos=columnas)

    @app.route("/api/monitor", methods=["POST"])
    def toggle_monitor():
        action = request.json.get("action", "")
        if action == "start":
            app.jira_monitor.start_monitoring()
            return jsonify({"status": "Monitor started"})
        elif action == "stop":
            app.jira_monitor.stop_monitoring()
            return jsonify({"status": "Monitor stopped"})
        return jsonify({"status": "Invalid action"}), 400
        
    @app.route("/clear_cases", methods=["POST"])
    def clear_cases():
        folder = "generated_test_cases"
        processed_file = "data/processed_issues.json"

        # Eliminar archivos de casos generados
        if os.path.exists(folder):
            for f in os.listdir(folder):
                os.remove(os.path.join(folder, f))

        # Limpiar issues procesados para que se vuelvan a generar
        if os.path.exists(processed_file):
            with open(processed_file, "w", encoding="utf-8") as f:
                json.dump([], f)

        # Resetear set en memoria del monitor para que vuelva a procesar
        app.jira_monitor.processed_issues = set()

        flash("Casos de prueba eliminados. Los issues podrán regenerarse.", "success")
        return redirect(url_for("list_generated"))


    return app



if __name__ == "__main__":
    app = create_app()
    if os.environ.get("START_MONITOR", "false").lower() == "true":
        app.jira_monitor.start_monitoring()
    app.run(debug=True)
