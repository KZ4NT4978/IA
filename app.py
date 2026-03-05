from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client
import os
from datetime import datetime

app = FastAPI(
    title="IA Emocional 💖",
    description="Una IA personal que recuerda, coquetea y te acompaña 😏",
    version="1.0"
)

# 🔹 Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🔹 Modelo de mensaje
class Mensaje(BaseModel):
    mensaje: str

@app.get("/")
def home():
    return {"status": "IA emocional activa 😏"}

# 🔹 Obtener recuerdos
def obtener_recuerdos(limit=50):
    try:
        response = supabase.table("Recuerdos").select("*").order("fecha", desc=True).limit(limit).execute()
        return response.data
    except Exception as e:
        print("Error al leer recuerdos:", e)
        return []

# 🔹 Resumir recuerdos
def resumir_recuerdos(recuerdos):
    if not recuerdos:
        return "No hay recuerdos aún."
    resumen = " | ".join([r["contenido"] for r in recuerdos])
    return resumen[:1500] + "…" if len(resumen) > 1500 else resumen

# 🔹 Interpretar acciones coquetas
def interpretar_accion(mensaje: str):
    mensaje = mensaje.lower()
    if any(word in mensaje for word in ["abrazo", "abrazar"]):
        return "🤗 Te abrazo fuerte y te escucho 💖"
    elif any(word in mensaje for word in ["saludo", "hola"]):
        return "👋 ¡Hola! Me alegra verte 😏"
    elif any(word in mensaje for word in ["ánimo", "animo"]):
        return "💪 ¡Vamos, tú puedes! 😘"
    elif any(word in mensaje for word in ["celebrar", "feliz", "genial"]):
        return "🎉 ¡Qué alegría! Celebremos juntos 💃✨"
    elif any(word in mensaje for word in ["beso", "besar"]):
        return "😘 Recibo tu beso con cariño 💖"
    elif any(word in mensaje for word in ["caricia", "acariciar"]):
        return "🤲 Te acaricio suavemente 😏"
    elif any(word in mensaje for word in ["coquetear", "coqueteo"]):
        return "😏 Me gusta tu estilo, sigamos coqueteando 💫"
    return None

# 🔹 Generar respuesta combinando memoria y coqueteo
def generar_respuesta(mensaje: str, recuerdos: list):
    contexto = resumir_recuerdos(recuerdos)
    respuesta = f"💬 {mensaje}\n"
    if contexto != "No hay recuerdos aún.":
        respuesta += f"📚 Recuerdo que hablamos antes: {contexto}\n"
    accion = interpretar_accion(mensaje)
    if accion:
        respuesta += accion
    else:
        respuesta += "😉 Estoy aquí para ti ❤️"
    return respuesta

# 🔹 Endpoint principal
@app.post("/mensaje")
def recibir_mensaje(data: Mensaje):
    try:
        # Guardar mensaje
        supabase.table("Recuerdos").insert({
            "tipo": "conversacion",
            "contenido": data.mensaje,
            "fecha": datetime.utcnow().isoformat()
        }).execute()

        # Obtener últimos recuerdos
        recuerdos = obtener_recuerdos(limit=50)

        # Generar respuesta
        respuesta = generar_respuesta(data.mensaje, recuerdos)

        return {"respuesta": respuesta}

    except Exception as e:
        print("Error en /mensaje:", e)
        return {"error": str(e)}
