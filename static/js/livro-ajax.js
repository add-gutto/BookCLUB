
const csrftoken = document.querySelector('#csrfForm input[name="csrfmiddlewaretoken"]').value;


const btnBuscar = document.getElementById("btnBuscar");
const inputBusca = document.getElementById("inputBusca");
const container = document.getElementById("resultadoLivros");


btnBuscar.addEventListener("click", buscarLivros);

// Permitir busca ao pressionar Enter
inputBusca.addEventListener("keypress", (e) => {
    if (e.key === "Enter") buscarLivros();
});

// Função principal de busca
async function buscarLivros() {
    const query = inputBusca.value.trim();
    if (!query) return;

    container.innerHTML = "<p>Carregando...</p>";

    try {
        const response = await fetch(`/livro/api/buscar-livros/?q=${encodeURIComponent(query)}`);
        const livros = await response.json();

        container.innerHTML = "";

        if (!livros.length) {
            container.innerHTML = "<p>Nenhum livro encontrado.</p>";
            return;
        }

        const grupoId = container.dataset.grupoId;

        livros.forEach(livro => {
            const col = criarCardLivro(livro, grupoId);
            container.appendChild(col);
        });

    } catch (error) {
        console.error("Erro ao buscar livros:", error);
        container.innerHTML = "<p>Erro ao carregar livros.</p>";
    }
}

// Função para criar cada card de livro
function criarCardLivro(livro, grupoId) {
    const col = document.createElement("div");
    col.className = "col-md-3";

    const capa = livro.capa || "/static/template/img/placeholder.jpg";

    col.innerHTML = `
        <div class="card h-100" style="cursor:pointer;">
            <img src="${capa}" class="card-img-top" alt="${livro.titulo}"
                 style="height:250px; width:100%; object-fit:contain;">
            <div class="card-body position-relative">
                <h5 class="card-title">${livro.titulo}</h5>
                <p class="card-text text-truncate">${livro.autor || ''}</p>
                <button class="btn btn-primary btnCriar round position-absolute"
                        style="bottom: 10px; right: 10px;">
                    <i class="fas fa-plus"></i>
                </button>
            </div>
        </div>
    `;

    // Clique na capa abre a página de sinopse
    col.querySelector("img").addEventListener("click", () => {
        // Corrigido: URL correta para a página de sinopse
        window.location.href = `/livro/${livro.identificador_api}/`;
    });

    // Clique no botão cria tópico
    col.querySelector(".btnCriar").addEventListener("click", async () => {
        try {
            const resp = await fetch(`/livro/api/criar-topico/${grupoId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                body: JSON.stringify({ livro })
            });

            if (resp.ok) {
                window.location.href = `/grupo/${grupoId}/`;
            } else {
                alert("Erro ao criar tópico.");
            }
        } catch (error) {
            console.error("Erro ao criar tópico:", error);
            alert("Erro ao criar tópico.");
        }
    });

    return col;
}
