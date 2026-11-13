import os

# Por padrão o app usa a API publicada na nuvem (Render + Neon).
# Para desenvolvimento local ou servidor da escola, defina a variável de ambiente
# MARILIA_API, por exemplo: MARILIA_API=http://127.0.0.1:8000
API_PADRAO = "https://marilia-api.onrender.com"
API_URL = os.getenv("MARILIA_API", API_PADRAO).strip().rstrip("/")
