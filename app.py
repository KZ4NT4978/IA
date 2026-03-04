from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client, Client
import os
from datetime import datetime

app = FastAPI()

# Variables de entorno
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class Mensaje(BaseModel):
    mensaje: str

@app.get("/")
def home():
    return {"status": "IA emocional activa"}

# 🔹 Función para leer últimos recuerdos
def obtener_recuerdos(limit=50):
    try:
        response = supabase.table("Recuerdos")\
            .select("*")\
            .order("fecha", desc=True)\
            .limit(limit)\
            .execute()
        return response.data
    except Exception as e:
        print(e)
        return []

# 🔹 Función para detectar emoción básica
def detectar_emocion(mensaje: str):
    mensaje = mensaje.lower()
    if any(palabra in mensaje for palabra in ["feliz", "genial", "excelente", "alegre", "emocionado"]):
        return "feliz"
    elif any(palabra in mensaje for palabra in ["triste", "mal", "deprimido", "enojado", "frustrado"]):
        return "triste"
    else:
        return "neutral"

# 🔹 Función para generar respuesta emocional
def respuesta_emocional(mensaje: str, recuerdos: list):
    emocion = detectar_emocion(mensaje)
    
    if emocion == "feliz":
        return f"¡Qué bueno escuchar eso! 😄 | Últimos recuerdos: {' | '.join([r['contenido'] for r in recuerdos])}"
    elif emocion == "triste":
        return f"Oh, lo siento 😢. No te preocupes, estoy aquí. | Últimos recuerdos: {' | '.join([r['contenido'] for r in recuerdos])}"
    else:
        return f"Mensaje recibido 👍 | Últimos recuerdos: {' | '.join([r['contenido'] for r in recuerdos])}"

# 🔹 Endpoint principal que guarda mensaje y responde con emoción
@app.post("/mensaje")
def recibir_mensaje(data: Mensaje):
    try:
        # Guardar mensaje nuevo
        supabase.table("Recuerdos").insert({
            "tipo": "conversacion",
            "contenido": data.mensaje,
            "fecha": datetime.utcnow().isoformat()
        }).execute()

        # Traer últimos recuerdos
        recuerdos = obtener_recuerdos(limit=50)

        # Generar respuesta emocional
        respuesta = respuesta_emocional(data.mensaje, recuerdos)

        return {"respuesta": respuesta}

    except Exception as e:
        print(e)
        return {"error": str(e)}
