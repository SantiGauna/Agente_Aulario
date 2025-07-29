import json
import os
import re
from datetime import datetime
from flask import current_app
import requests
from modules.context_loader import knowledge_base, leer_contexto_excel, leer_confluence, CONFIG_TESTCASES

def construir_contexto(tipo):
    config_tipo = CONFIG_TESTCASES.get(tipo, {})
    contexto = config_tipo.get("context", "Eres un experto en QA.")
    contexto += "\nBase de conocimiento Aulario:\n"

    for rol in knowledge_base.get("roles", []):
        contexto += f"- {rol['name']}:\n"
        for grupo in rol.get("groups", []):
            contexto += f"  * {grupo['name']}: {', '.join(grupo.get('actions', []))}\n"

    contexto += leer_contexto_excel("data/Contexto_Extra.xlsx", tipo)
    contexto += "\nInformación Confluence:\n" + (leer_confluence() or "Sin contenido")
    return contexto

def generar_casos_prueba(user_story, tipo="BE"):
    columnas = CONFIG_TESTCASES.get(tipo, {}).get("fields", [])
    contexto = construir_contexto(tipo)

    headers = {
        "Authorization": f"Bearer {current_app.config['MISTRAL_API_KEY']}",
        "Content-Type": "application/json"
    }

    prompt = f"""
{contexto}

Genera exactamente 6 casos de prueba en formato JSON con las columnas:
{columnas}

User Story:
{user_story}

La respuesta debe ser SOLO el array JSON, sin texto adicional.
"""

    try:
        r = requests.post(
            current_app.config['MISTRAL_API_URL'], headers=headers,
            json={"model": "mistral-tiny", "messages": [
                {"role": "system", "content": "Eres un asistente QA JSON estricto."},
                {"role": "user", "content": prompt}
            ], "temperature": 0.3},
            timeout=30
        )
        r.raise_for_status()
        raw = r.json()["choices"][0]["message"]["content"]
        match = re.search(r'\[.*\]', raw, re.S)
        casos = json.loads(match.group() if match else raw)

        for caso in casos:
            for campo in columnas:
                caso.setdefault(campo, "")
            caso.setdefault("Fecha", datetime.now().strftime("%d/%m/%Y"))
            caso["_tipo"] = tipo

        return casos
    except Exception as e:
        return [{"Error": f"No se pudieron generar casos: {e}"}]
