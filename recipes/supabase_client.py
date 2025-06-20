# recipes/supabase_client.py
from supabase import create_client

SUPABASE_URL = "https://sizovghaygzecxbgvqvb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpem92Z2hheWd6ZWN4Ymd2cXZiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTYwODYxMywiZXhwIjoyMDY1MTg0NjEzfQ.ErTX-Bj568patz2nDz9DMVsZ-x-DJrTLxDl9OkBPEPI"  

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
