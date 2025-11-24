const csrftoken = document.querySelector('#csrfForm input[name="csrfmiddlewaretoken"]').value;
const btnBuscar = document.getElementById("btnBuscar");
const inputBusca = document.getElementById("inputBusca");
const container = document.getElementById("resultadoLivros");

btnBuscar.addEventListener("click", async () => {
    const query = inputBusca.value.trim();

    const response = await fetch(`/livro/api/buscar-livros/?q=${encodeURIComponent(query)}`);
    const livros = await response.json();

    container.innerHTML = "";

    if (!livros.length) {
        container.innerHTML = "<p>Nenhum livro encontrado.</p>";
        return;
    }

    livros.forEach(livro => {
        const col = document.createElement("div");
        col.className = "col-md-3";

        const card = document.createElement("div");
        card.className = "card h-100";

        const capa = livro.capa || "{% static 'template/img/placeholder.jpg' %}";

        card.innerHTML = `
            <img src="${capa}" class="card-img-top" alt="${livro.titulo}"
                style="height:250px; width:100%; object-fit:contain;">
            <div class="card-body position-relative">
                <h5 class="card-title">${livro.titulo}</h5>
                <p class="card-text text-truncate">${livro.autor || ''}</p>
                <button class="btn btn-primary btnCriarTopico round position-absolute"
                        style="bottom: 10px; right: 10px;">
                    <i class="fas fa-plus"></i>
                </button>
            </div>
        `;

        col.appendChild(card);
        container.appendChild(col);

        const grupoId = container.dataset.grupoId;
        const btnCriar = card.querySelector(".btnCriarTopico");

        btnCriar.addEventListener("click", async () => {
            const resp = await fetch(`/livro/api/criar-topico/${grupoId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                credentials: 'include',
                body: JSON.stringify({ livro })
            });

            if (resp.ok) {
                window.location.href = `/grupo/${grupoId}/`;
            } else {
                const erro = await resp.json();
                alert("Erro: " + JSON.stringify(erro));
            }
        });
    });
});
