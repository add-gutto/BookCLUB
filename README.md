# BOOKCLUB 

Sistema API (Django/DRF) para uma rede social de leitura dinâmica, com foco em grupos de leitura, discussão de livros e interação entre leitores.

Sistema Cliente Flutter disponível em: https://github.com/Pazcifico/BookCLUB_App.git



## Funcionalidades

- Cadastro de usuários com criação automática de perfil
- Criação e gerenciamento de Grupos de Leitura
- Criação de Tópicos vinculados a um livro
- Envio de mensagens via WebSocket + Channels, com suporte a marcação de spoilers
- Avaliação de livros
- Autenticação JWT(SimpleJWT)
- API desenvolvida em Django Rest Framework
- Servidor ASGI com Daphne + Redis (channels-redis)

## Instalação e Configuração

Siga estes passos para configurar o ambiente de desenvolvimento.

### 1. Pré-requisitos

#### Ferramentas

* Python 3.10+ (recomendado 3.11)
* Docker (versão recente) e Docker Compose (ou docker compose incluído no Docker)
 
 #### Dependências
 No requirements.txt constam as dependências de instalação do projeto

### 2. Passos de Instalação

1.  Clone o repositório:
    ```bash
    git clone  https://github.com/add-gutto/BookCLUB.git
    cd BookCLUB
    ```
2.  Crie o arquivo .env na raiz do projeto:
    ```env
    # Definições do projeto
    APP_NAME=BookCLUB

    # Configuração de e-mail
    EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_USE_TLS=True
    EMAIL_HOST_USER=seuemail@gmail.com
    EMAIL_HOST_PASSWORD=senhaemail
    DEFAULT_FROM_EMAIL=BookCLUB <seuemail@gmail.com>

    # Hosts
    ALLOWED_HOSTS=SEU_IP, localhost, 127.0.0.1
    CORS_ALLOW_ALL_ORIGINS=False
    CSRF_TRUSTED_ORIGINS=SEU_IP

    # API de livros
    API_DOMAIN=https://www.googleapis.com/books/v1/volumes
    ``` 

3.  Crie o ambiente virtual e instale as dependências:
    ```bash
    python -m venv venv

    # Linux / macOS
    source venv/bin/activate
    # Windows (PowerShell)
    .\venv\Scripts\Activate.ps1

    # Instalar dependências
    pip install -r requirements.txt

    ```

4.  Aplique as migrações:
    ```bash
    python manage.py migrate
    ```

5. Descobrir o IP da máquina: 
    ```bash 
    # Linux / macOS
    hostname -I
    # Windows (PowerShell)
    ipconfig
    ```
        * Copie o IP retornado e adicione ao .env:
            ALLOWED_HOSTS=SEU_IP,
            CSRF_TRUSTED_ORIGINS=SEU_IP

5.  Rodando o Projeto: 

    Rodando sem Docker (desenvolvimento)
    ```bash 
    # ativa venv
    python manage.py runserver 0.0.0.0:8000
    ```

    Suba o ambiente com Docker:
    ```bash
    docker compose up --build
    ```

## Usuário Administrador

O projeto já está configurado (via Django Signals) para criar automaticamente um usuário admin padrão após as migrações.

Credenciais iniciais:
* **Email:** `admin@gmail.com`
* **Senha:** `admin123`

[Demonstração](https://youtu.be/33TmvDi-VZY?si=I_p-ShJbEM22cGui)
