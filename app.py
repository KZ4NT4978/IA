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

@app.post("/mensaje")
def recibir_mensaje(data: Mensaje):
    try:
        # Guardar mensaje en la base de datos (tabla con R mayúscula)
        supabase.table("Recuerdos").insert({
            "tipo": "conversacion",
            "contenido": data.mensaje,
            "fecha": datetime.utcnow().isoformat()
        }).execute()

        return {"respuesta": "Mensaje guardado en memoria ❤️"}

    except Exception as e:
        # Mostrar error real si algo falla
        print(e)
        return {"error": str(e)}
