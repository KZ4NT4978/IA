from fastapi import FastAPI
from supabase import create_client, Client
import os

app = FastAPI()

# Variables de entorno
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
def home():
    return {"status": "IA emocional activa"}

@app.get("/recuerdos")
def obtener_recuerdos():
    data = supabase.table("recuerdos").select("*").execute()
    return data.data
