from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client
import os
from datetime import datetime

app = FastAPI()

# 🔹 Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🔹 Modelo de mensaje
class Mensaje(BaseModel):
    mensaje: str
    categoria: str = "general"

@app.get("/")
def home():
    return {"status": "IA emocional y coqueta activa 😏💖"}

# 🔹 Obtener recuerdos
def obtener_recuerdos(limit=50, categoria=None):
    query = supabase.table("Recuerdos").select("*").order("fecha", desc=True).limit(limit)
    if categoria:
        query = query.eq("categoria", categoria)
    try:
        return query.execute().data
    except Exception as e:
        print("Error al leer recuerdos:", e)
        return []

# 🔹 Resumir recuerdos
def resumir_recuerdos(recuerdos):
    if not recuerdos:
        return "No hay recuerdos aún."
    resumen = " | ".join([r["contenido"] for r in recuerdos])
    return resumen[:1500] + "…" if len(resumen) > 1500 else resumen

# 🔹 Consolidar memoria antigua
def consolidar_memoria(categoria=None, max_recientes=50):
    todos = obtener_recuerdos(limit=1000, categoria=categoria)
    if len(todos) <= max_recientes:
        return
    antiguos = todos[max_recientes:]
    resumen = resumir_recuerdos(antiguos)
    ids_antiguos = [r["id"] for r in antiguos if "id" in r]
    if ids_antiguos:
        supabase.table("Recuerdos").delete().in_("id", ids_antiguos).execute()
    supabase.table("Recuerdos").insert({
        "tipo": "resumen",
        "contenido": f"[Resumen memoria antigua] {resumen}",
        "fecha": datetime.utcnow().isoformat(),
        "categoria": categoria
    }).execute()

# 🔹 Detectar acciones y gestos coquetos
def interpretar_accion(mensaje: str):
    mensaje = mensaje.lower()
    if any(word in mensaje for word in ["abrazo", "abrazar"]):
        return "🤗 Te abrazo fuerte y te escucho 💖"
    elif any(word in mensaje for word in ["saludo", "hola"]):
        return "👋 ¡Hola guapo/a! Me alegra verte 😏"
    elif any(word in mensaje for word in ["ánimo", "animo"]):
        return "💪 ¡Vamos, tú puedes! 😘"
    elif any(word in mensaje for word in ["celebrar", "feliz", "genial"]):
        return "🎉 ¡Qué alegría! Celebremos juntos 💃✨"
    elif any(word in mensaje for word in ["beso", "besar"]):
        return "😘 Recibo tu beso con cariño 💖"
    elif any(word in mensaje for word in ["caricia", "acariciar"]):
        return "🤲 Te acaricio suavemente en señal de afecto 😏"
    elif any(word in mensaje for word in ["coquetear", "coqueteo"]):
        return "😏 Me gusta tu estilo, sigamos coqueteando 💫"
    return None

# 🔹 Generar respuesta con memoria y coqueteo
def generar_respuesta(mensaje: str, recuerdos: list):
    contexto = resumir_recuerdos(recuerdos)
    respuesta = f"💬 {mensaje}\n"
    if contexto != "No hay recuerdos aún.":
        respuesta += f"📚 Recuerdo que hablamos antes: {contexto}\n"
    if any(word in mensaje.lower() for word in ["triste", "mal", "deprimido"]):
        respuesta += "😢 Lo siento mucho, estoy aquí para escucharte y mimarte 💖"
    elif any(word in mensaje.lower() for word in ["feliz", "bien", "genial"]):
        respuesta += "😄 Me alegra que estés feliz, ¡me haces sonreír 😏💫!"
    elif any(word in mensaje.lower() for word in ["me gustas", "gustas"]):
        respuesta += "😍 ¡A mí también me encantas! 💖"
    return respuesta

# 🔹 Endpoint principal
@app.post("/mensaje")
def recibir_mensaje(data: Mensaje):
    try:
        # Guardar mensaje
        supabase.table("Recuerdos").insert({
            "tipo": "conversacion",
            "contenido": data.mensaje,
            "fecha": datetime.utcnow().isoformat(),
            "categoria": data.categoria
        }).execute()

        # Consolidar memoria antigua
        consolidar_memoria(categoria=data.categoria, max_recientes=50)

        # Obtener últimos recuerdos
        recuerdos = obtener_recuerdos(limit=50, categoria=data.categoria)

        # Detectar acción
        accion = interpretar_accion(data.mensaje)
        if accion:
            respuesta = accion
        else:
            respuesta = generar_respuesta(data.mensaje, recuerdos)

        return {"respuesta": respuesta}

    except Exception as e:
        print("Error en /mensaje:", e)
        return {"error": str(e)}
