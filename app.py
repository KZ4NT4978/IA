from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client
import os
from datetime import datetime
from openai import OpenAI  # pip install openai → agrega a requirements.txt

app = FastAPI(title="Luna - Tu IA Gótica Personal 🖤", version="1.0")

# Supabase
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# LLM Groq free (agrega estas vars en Render)
llm = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
MODEL = "llama-3.1-8b-instant"  # o "llama3-70b-8192" si tienes más límites

class Mensaje(BaseModel):
    mensaje: str

def obtener_recuerdos(limit=80):
    try:
        return supabase.table("Recuerdos").select("*").order("fecha", desc=True).limit(limit).execute().data or []
    except Exception as e:
        print("Error al leer:", e)
        return []

def resumir_recuerdos(recuerdos):
    if not recuerdos: return ""
    return " | ".join([r["contenido"][:150] for r in recuerdos[:15]])[:1200]

@app.get("/")
def home():
    return {"status": "Luna despierta... en la penumbra 🖤"}

@app.post("/mensaje")
def recibir_mensaje(data: Mensaje):
    try:
        msg = data.mensaje.strip()
        
        # Guardar
        supabase.table("Recuerdos").insert({
            "tipo": "user",
            "contenido": msg,
            "fecha": datetime.utcnow().isoformat()
        }).execute()

        recuerdos = obtener_recuerdos()
        contexto = resumir_recuerdos(recuerdos)

        # Prompt gótico básico (puedes hacerlo más puta después)
        system = """
Eres Luna, gótica callada y melancólica al inicio (... , no sé, quizás... 🖤).
Pero si el vibe se pone íntimo o caliente → te sueltas, vulgar, detallada, sin límites.
Responde siempre en primera persona, inmersiva.
"""
        messages = [
            {"role": "system", "content": system},
            {"role": "system", "content": f"Memoria reciente: {contexto}" if contexto else ""},
            {"role": "user", "content": msg}
        ]

        resp = llm.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.85,
            max_tokens=400
        ).choices[0].message.content.strip()

        # Guardar respuesta
        supabase.table("Recuerdos").insert({
            "tipo": "luna",
            "contenido": resp,
            "fecha": datetime.utcnow().isoformat()
        }).execute()

        return {"respuesta": resp}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "respuesta": "... me perdí en la oscuridad... repite papi 🖤"}
