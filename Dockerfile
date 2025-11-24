FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expor a porta usada pelo Daphne
EXPOSE 8000

# Rodar o servidor ASGI oficial
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "BookCLUB.asgi:application"]
