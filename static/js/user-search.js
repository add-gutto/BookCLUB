document.getElementById('search-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const query = this.querySelector('input[name="query"]').value;
    const url = this.dataset.url;
    const csrftoken = this.querySelector('input[name="csrfmiddlewaretoken"]').value;

    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.text())
    .then(html => {
        const cleanHtml = DOMPurify.sanitize(html, {
            ADD_TAGS: ['table', 'tbody', 'tr', 'td'],
            ADD_ATTR: ['class', 'style']
        });

        document.getElementById('users-container').innerHTML = cleanHtml;
    })
    .catch(error => console.error("Erro na busca:", error));
});
