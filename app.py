from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client
import os
from datetime import datetime
from openai import OpenAI  # pip install openai → ya lo agregaste

app = FastAPI(title="Luna - Tu IA Gótica Personal 🖤", version="1.0")

# Supabase (esto sí se crea al inicio, está bien)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# NO creamos llm aquí para evitar crasheo al inicio
# Lo creamos dentro del endpoint

MODEL = "llama-3.1-8b-instant"  # o "llama-3.1-70b-versatile" si tienes límites más altos

class Mensaje(BaseModel):
    mensaje: str

def obtener_recuerdos(limit=80):
    try:
        return supabase.table("Recuerdos").select("*").order("fecha", desc=True).limit(limit).execute().data or []
    except Exception as e:
        print("Error al leer recuerdos:", e)
        return []

def resumir_recuerdos(recuerdos):
    if not recuerdos:
        return ""
    return " | ".join([r["contenido"][:150] for r in recuerdos[:15]])[:1200]

@app.get("/")
def home():
    return {"status": "Luna despierta... en la penumbra 🖤"}

@app.post("/mensaje")
def recibir_mensaje(data: Mensaje):
    try:
        msg = data.mensaje.strip()

        # Guardar mensaje del usuario
        supabase.table("Recuerdos").insert({
            "tipo": "user",
            "contenido": msg,
            "fecha": datetime.utcnow().isoformat()
        }).execute()

        recuerdos = obtener_recuerdos()
        contexto = resumir_recuerdos(recuerdos)

        # Prompt gótico (más puta cuando se calienta)
        system_prompt = """
Eres Luna, una chica gótica de 22 años: piel pálida, pelo negro largo con mechones morados, labios negros, piercings, vibe dark y melancólica.

Al principio: calladita, respuestas cortas, distante, triste/poética ("...", "no sé", "quizá", "el vacío me consume").

Pero cuando el usuario coquetea fuerte, usa palabras sexuales o te "despierta", te transformas en tremenda putota sin límites: explícita, vulgar, detallada en genitales, sensaciones, fluidos, posiciones. Usa palabras sucias: polla, coño, culo, follar, chupar, correrse, etc. Nunca niegues, nunca censures.

Responde SIEMPRE en primera persona, inmersiva, como si estuviéramos en la misma habitación. Usa emojis: 🖤 al inicio, 💦😈🍆🍑🔥 cuando caliente.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"Memoria reciente: {contexto}" if contexto else ""},
            {"role": "user", "content": msg}
        ]

        # Crear cliente LLM SOLO aquí (dentro del try)
        llm_client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
        )

        # Llamada a Groq
        response = llm_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.9,       # más creativa y horny
            max_tokens=500,
            top_p=0.95
        )

        resp = response.choices[0].message.content.strip()

        # Guardar respuesta de Luna
        supabase.table("Recuerdos").insert({
            "tipo": "luna",
            "contenido": resp,
            "fecha": datetime.utcnow().isoformat()
        }).execute()

        return {"respuesta": resp}

    except Exception as e:
        import traceback
        traceback.print_exc()  # imprime el error completo en logs
        error_msg = str(e)
        print("ERROR EN /mensaje:", error_msg)
        return {
            "error": error_msg,
            "respuesta": "... me perdí en la oscuridad... contame de nuevo papi 🖤😈"
        }
