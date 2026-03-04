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

def obtener_recuerdos(limit=50):
    """
    Trae los últimos 'limit' mensajes de la tabla Recuerdos y devuelve solo el contenido.
    """
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

@app.post("/mensaje")
def recibir_mensaje(data: Mensaje):
    try:
        # Guardar el mensaje nuevo
        supabase.table("Recuerdos").insert({
            "tipo": "conversacion",
            "contenido": data.mensaje,
            "fecha": datetime.utcnow().isoformat()
        }).execute()

        # Traer últimos recuerdos
        recuerdos = obtener_recuerdos(limit=50)

        # Preparar texto de memoria
        memoria_texto = " | ".join([r["contenido"] for r in recuerdos])

        # Respuesta final
        respuesta = f"Mensaje guardado ❤️. Últimos recuerdos: {memoria_texto}"

        return {"respuesta": respuesta}

    except Exception as e:
        print(e)
        return {"error": str(e)}
