import os
import instaloader
from supabase import create_client, Client

# 1. Configuración de clientes
SUPABASE_URL = os.getenv("SUPABASE_URL", "TU_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "TU_SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
L = instaloader.Instaloader()

def obtener_influencers():
    """Obtiene la lista de influencers registrados en Supabase."""
    response = supabase.table("influencers").select("id, username").execute()
    return response.data

def obtener_seguidores_instagram(username: str) -> int:
    """Extrae el número de seguidores usando Instaloader."""
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        return profile.followers
    except Exception as e:
        print(f" Error al obtener datos de @{username}: {e}")
        return None

def guardar_historial(influencer_id: int, seguidores: int):
    """Guarda el número de seguidores en la tabla historial_seguidores."""
    try:
        datos = {
            "influencer_id": influencer_id,
            "seguidores": seguidores
        }
        # Realizamos el insert en Supabase
        response = supabase.table("historial_seguidores").insert(datos).execute()
        print(f" Registrado correctamente para ID {influencer_id}: {seguidores} seguidores.")
    except Exception as e:
        print(f" Error al guardar en Supabase para ID {influencer_id}: {e}")

def ejecutar_extraccion():
    influencers = obtener_influencers()
    
    if not influencers:
        print("No se encontraron influencers en la base de datos.")
        return

    print(f"Procesando {len(influencers)} influencers...")

    for inf in influencers:
        inf_id = inf["id"]
        username = inf["username"]

        print(f"Obteniendo datos de @{username}...")
        seguidores = obtener_seguidores_instagram(username)

        if seguidores is not None:
            guardar_historial(inf_id, seguidores)

if __name__ == "__main__":
    ejecutar_extraccion()
