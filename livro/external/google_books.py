# app/external/google_books.py
import requests
from decouple import config

def buscar_livros_google(query, max_results=10):
    url =  config("API_DOMAIN")
    params = {"q": query, "maxResults": max_results}

    r = requests.get(url, params=params)
    data = r.json()

    resultados = []

    for item in data.get("items", []):
        info = item.get("volumeInfo", {})

        resultados.append({
            "titulo": info.get("title"),
            "autor": ", ".join(info.get("authors", [])) if info.get("authors") else None,
            "descricao": info.get("description"),
            "capa": info.get("imageLinks", {}).get("thumbnail"),
            "ano_publicacao": info.get("publishedDate"),
            "identificador": item.get("id"),
        })

    return resultados
