import os
from dotenv import load_dotenv
from django.apps import AppConfig

class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    # sb = supabase
    sb_bucket_name = "recipes"
    sb_bucket_path = "recipes/"

    # Loads supabase config
    load_dotenv()
    sb_url: str = os.environ.get("SUPABASE_URL")
    sb_key: str = os.environ.get("SUPABASE_KEY")
