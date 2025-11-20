document.addEventListener('DOMContentLoaded', () => {
        const container = document.getElementById('chats-lista');
        const route = container.dataset.route;

        fetch(route)
            .then(response => response.text())
            .then(html => {
                const cleanHtml = DOMPurify.sanitize(html, {
                    ADD_TAGS: ['a', 'div', 'img'],
                    ADD_ATTR: ['class', 'style', 'href']
                });
                container.innerHTML = cleanHtml;
            })
            .catch(err => console.error("Erro ao carregar chats:", err));

        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));
    });