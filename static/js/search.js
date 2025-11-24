let tipoAtual = "grupo"; // padrão inicial

    // Alternar tipo ao clicar nos botões
    document.getElementById("btn-grupo").addEventListener("click", function () {
        tipoAtual = "grupo";
        this.classList.replace("btn-secondary", "btn-primary");
        document.getElementById("btn-usuario").classList.replace("btn-primary", "btn-secondary");
    });

    document.getElementById("btn-usuario").addEventListener("click", function () {
        tipoAtual = "usuario";
        this.classList.replace("btn-secondary", "btn-primary");
        document.getElementById("btn-grupo").classList.replace("btn-primary", "btn-secondary");
    });

    // Buscar dinamicamente
    document.getElementById("campo-busca").addEventListener("input", function () {
        const query = this.value.trim();
        const searchUrl = this.dataset.url;
        const lista = document.getElementById("lista");

        if (!query) {
            lista.innerHTML = "";
            return;
        }

        fetch(`${searchUrl}?q=${query}&tipo=${tipoAtual}`)
            .then(res => res.json())
            .then(data => {
                let html = "";

                data.results.forEach(item => {

                    // ----- GRUPO -----
                    if (item.tipo === "grupo") {
                        html += `
<a class="list-group-item list-group-item-action d-flex align-items-center justify-content-between"
   href="/grupo/${item.id}/" style="border: none;">
    <div class="d-flex align-items-center gap-2">
        <img src="${item.imagem}" class="rounded-circle"
            width="40" height="40" style="object-fit: cover;">
        <div>${item.nome}</div>
    </div>
</a>`;
                    }

                    // ----- USUÁRIO -----
                    else if (item.tipo === "usuario") {
                        html += `
<a class="list-group-item  list-group-item-action d-flex align-items-center justify-content-between p-2" href="/user/profile/${item.id}/" style="border: none;">
    <div class="d-flex align-items-center gap-3">
        <img class="img-profile rounded-circle"
             src="${item.imagem}"
             width="50" height="50" style="object-fit: cover;">
        <div class="fw-semibold">${item.nome}</div>
        <div class="text-muted">@${item.username}</div>
    </div>
</a>`;
                    }

                });

                if (!html) {
                    html = `<p class="text-center text-muted">Nenhum resultado encontrado.</p>`;
                }

                lista.innerHTML = html;
            });
    });