import httpx
import random
import string

SUPABASE_URL = "https://sizovghaygzecxbgvqvb.supabase.co"
SUPABASE_BUCKET = "receitas"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpem92Z2hheWd6ZWN4Ymd2cXZiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTYwODYxMywiZXhwIjoyMDY1MTg0NjEzfQ.ErTX-Bj568patz2nDz9DMVsZ-x-DJrTLxDl9OkBPEPI"

def upload_image_to_supabase(binary_data: bytes) -> str:
    # Gera nome aleatório do arquivo com extensão .jpg
    filename = ''.join(random.choices(string.ascii_letters + string.digits, k=30)) + ".jpg"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/octet-stream",
    }

    url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{filename}"

    response = httpx.put(url, headers=headers, content=binary_data)

    if response.status_code != 200:
        raise Exception(f"Erro ao fazer upload: {response.text}")

    # ✅ Retorna apenas o nome do arquivo salvo
    return filename
