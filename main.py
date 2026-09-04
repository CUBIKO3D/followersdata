import os
import time
import instaloader
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
IG_USER = os.getenv("INSTAGRAM_USER")
IG_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configurar Instaloader con Login
L = instaloader.Instaloader()
if IG_USER and IG_PASSWORD:
    try:
        L.login(IG_USER, IG_PASSWORD)
        print("Login exitoso en Instagram.")
    except Exception as e:
        print(f"Error al iniciar sesión en Instagram: {e}")

def obtener_influencers():
    response = supabase.table("influencers").select("id, username").execute()
    return response.data

def obtener_seguidores_instagram(username: str) -> int:
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        return profile.followers
    except Exception as e:
        print(f"Error al obtener datos de @{username}: {e}")
        return None

def guardar_historial(influencer_id: int, seguidores: int):
    try:
        datos = {
            "influencer_id": influencer_id,
            "seguidores": seguidores
        }
        supabase.table("historial_seguidores").insert(datos).execute()
        print(f"Registrado correctamente para ID {influencer_id}: {seguidores} seguidores.")
    except Exception as e:
        print(f"Error al guardar en Supabase: {e}")

def ejecutar_extraccion():
    influencers = obtener_influencers()
    if not influencers:
        print("No se encontraron influencers.")
        return

    for inf in influencers:
        print(f"Procesando @{inf['username']}...")
        seguidores = obtener_seguidores_instagram(inf["username"])
        if seguidores is not None:
            guardar_historial(inf["id"], seguidores)
        # Pausa de 3 segundos entre cada consulta para evitar saturar
        time.sleep(3)

if __name__ == "__main__":
    ejecutar_extraccion()
