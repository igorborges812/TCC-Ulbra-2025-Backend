import httpx
import base64

SUPABASE_URL = "https://sizovghaygzecxbgvqvb.supabase.co"
SUPABASE_BUCKET = "receitas"
SUPABASE_KEY = "SUA_CHAVE_ANON"  # substitua pela sua SUPABASE ANON KEY

def upload_image_to_supabase(filename: str, base64_data: str) -> str:
    binary_data = base64.b64decode(base64_data)

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/octet-stream",
    }

    url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{filename}"

    response = httpx.put(url, headers=headers, content=binary_data)

    if response.status_code != 200:
        raise Exception(f"Erro ao fazer upload: {response.text}")

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
    return public_url
