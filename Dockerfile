# 1. Image de base officielle et légère de Python
FROM python:3.11-slim

# 2. On définit le dossier de travail dans le conteneur
WORKDIR /app

# 3. On copie d'abord les dépendances (optimisation du cache Docker)
COPY requirements.txt .

# 4. On installe les librairies Python
RUN pip install --no-cache-dir -r requirements.txt

# 5. On copie le reste de notre code source
COPY . .

# 6. On expose le port sur lequel Uvicorn (FastAPI) va tourner
EXPOSE 8000

# 7. La commande pour démarrer le serveur web
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]