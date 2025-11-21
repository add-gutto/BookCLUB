import requests


def buscar_livros_google(query):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": query, "maxResults": 12}  # ⚡ máximo 12 resultados
    r = requests.get(url, params=params)
    data = r.json()
    livros = []

    for item in data.get("items", []):
        volume_info = item.get("volumeInfo", {})
        livros.append({
            "titulo": volume_info.get("title", "Sem título"),
            "autor": ", ".join(volume_info.get("authors", [])) if volume_info.get("authors") else "",
            "descricao": volume_info.get("description", ""),
            "ano_publicacao": volume_info.get("publishedDate", ""),
            "capa": volume_info.get("imageLinks", {}).get("thumbnail", ""),
            "identificador_api": item.get("id")  # ⚡ obrigatório
        })

    return livros
