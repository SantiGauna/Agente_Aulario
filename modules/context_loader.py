import os
import json
import pandas as pd
import re
import requests


# Configuración testcases
def leer_configuracion_testcases():
    try:
        with open("data/config_testcases.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠ Error cargando configuración de testcases: {e}")
        return {}

CONFIG_TESTCASES = leer_configuracion_testcases()

# Base de conocimiento
def leer_base_conocimiento():
    try:
        with open("data/aulario_knowledge_base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"roles": []}

knowledge_base = leer_base_conocimiento()

# Resumen desde Excel
def leer_contexto_excel(ruta_excel, tipo, max_ejemplos=5):
    try:
        df = pd.read_excel(ruta_excel, sheet_name=tipo, dtype=str).fillna("")
        columnas_clave = [c for c in df.columns if any(x in c.lower() for x in ["id", "accion", "resultado", "plan"])]
        
        resumen = f"📊 Resumen hoja {tipo}:\n- Total casos: {len(df)}\n"
        if columnas_clave:
            resumen += f"- Columnas clave: {', '.join(columnas_clave)}\n"

        ejemplos = df.head(max_ejemplos)
        for _, row in ejemplos.iterrows():
            fila = " | ".join([f"{col}: {row[col]}" for col in columnas_clave if col in df.columns])
            resumen += f"- {fila[:150]}\n"

        return resumen
    except Exception as e:
        return f"⚠ Error leyendo Excel {tipo}: {e}"

# Confluence
def leer_confluence():
    base_url = os.environ.get("CONFLUENCE_URL")
    user = os.environ.get("JIRA_EMAIL")
    api_token = os.environ.get("JIRA_API_TOKEN")
    space_key = os.environ.get("CONFLUENCE_SPACE_KEY")
    
    if not all([base_url, user, api_token]):
        return ""
    
    auth = (user, api_token)
    headers = {"Accept": "application/json"}
    url = f"{base_url}/rest/api/content"
    params = {"spaceKey": space_key, "limit": 5, "expand": "body.storage"}

    contenido = ""
    try:
        r = requests.get(url, headers=headers, params=params, auth=auth, timeout=10)
        r.raise_for_status()
        for page in r.json().get("results", []):
            title = page.get("title", "Sin título")
            body = re.sub('<[^<]+?>', '', page.get("body", {}).get("storage", {}).get("value", ""))
            contenido += f"\nTítulo: {title}\nContenido:\n{body}\n{'-'*30}\n"
        return contenido
    except:
        return ""
