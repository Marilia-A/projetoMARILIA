import os

# no servidor da escola, basta definir MARILIA_API=http://<ip-do-servidor>:8000
API_URL = os.getenv("MARILIA_API", "http://127.0.0.1:8000")