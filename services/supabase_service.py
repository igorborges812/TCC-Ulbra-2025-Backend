from supabase import create_client
import os

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
SUPABASE_BUCKET = 'receitas'

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_image_to_supabase(file, filename):
    file_path = f"{SUPABASE_BUCKET}/{filename}"
    result = supabase.storage.from_(SUPABASE_BUCKET).upload(file_path, file)
    return supabase.storage.from_(SUPABASE_BUCKET).get_public_url(file_path)
