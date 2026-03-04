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

# 🟢 Función para leer los últimos recuerdos
def obtener_recuerdos(limit=5):
    """
    Trae los últimos 'limit' mensajes de la tabla Recuerdos.
    """
    try:
        response = supabase.table("Recuerdos")\
            .select("*")\
            .order("fecha", desc=True)\
            .limit(limit)\
            .execute()
        return response.data  # lista de diccionarios
    except Exception as e:
        print(e)
        return []

@app.post("/mensaje")
def recibir_mensaje(data: Mensaje):
    try:
        # 1️⃣ Guardar el mensaje nuevo
        supabase.table("Recuerdos").insert({
            "tipo": "conversacion",
            "contenido": data.mensaje,
            "fecha": datetime.utcnow().isoformat()
        }).execute()

        # 2️⃣ Traer últimos recuerdos
        recuerdos = obtener_recuerdos(limit=100)

        # 3️⃣ Preparar texto de memoria para la respuesta
        memoria_texto = " | ".join([r["contenido"] for r in recuerdos])

        # 4️⃣ Respuesta combinando confirmación + recuerdos
        respuesta = f"Mensaje guardado ❤️. Últimos recuerdos: {memoria_texto}"

        return {"respuesta": respuesta}

    except Exception as e:
        # Mostrar error real si algo falla
        print(e)
        return {"error": str(e)}
