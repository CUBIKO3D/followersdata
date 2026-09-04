import os
import time
import requests
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def obtener_influencers():
    response = supabase.table("influencers").select("id, username").execute()
    return response.data

def obtener_seguidores_instagram(username: str) -> int:
    """Obtiene seguidores haciendo un fetch directo sin Instaloader para evitar el error 429."""
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "X-IG-App-ID": "936619743392459",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            seguidores = data["data"]["user"]["edge_followed_by"]["count"]
            return seguidores
        else:
            print(f"⚠️ HTTP {response.status_code} al consultar @{username}")
            return None
    except Exception as e:
        print(f" Error al obtener datos de @{username}: {e}")
        return None

def guardar_historial(influencer_id: int, seguidores: int):
    try:
        datos = {
            "influencer_id": influencer_id,
            "seguidores": seguidores
        }
        supabase.table("historial_seguidores").insert(datos).execute()
        print(f" Registrado en Supabase (ID {influencer_id}): {seguidores} seguidores.")
    except Exception as e:
        print(f" Error al guardar en Supabase: {e}")

def ejecutar_extraccion():
    influencers = obtener_influencers()
    if not influencers:
        print("No hay influencers en la base de datos.")
        return

    for inf in influencers:
        username = inf["username"]
        print(f"Procesando @{username}...")
        
        seguidores = obtener_seguidores_instagram(username)
        
        if seguidores is not None:
            guardar_historial(inf["id"], seguidores)
        else:
            print(f"Saltando @{username} por fallo en la consulta.")
            
        # Esperar 5 segundos entre peticiones
        time.sleep(5)

if __name__ == "__main__":
    ejecutar_extraccion()
