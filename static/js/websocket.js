document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chatMain");
    const chatMessages = document.getElementById("chatMessages");
    const messageInput = document.getElementById("messageInput");
    const sendBtn = document.getElementById("sendButton");
    const imageInput = document.getElementById("imageInput");
    const filePreview = document.getElementById("filePreview");
    const spoilerInput = document.getElementById("spoilerInput");

    const chatId = chatBox.dataset.chatId;
    const userId = chatBox.dataset.userId;
    const username = chatBox.dataset.username;

    // Conexão WebSocket
    const socket = new WebSocket("ws://" + window.location.host + "/ws/chat/" + chatId + "/");

    socket.onopen = () => console.log("WebSocket conectado");
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "chat_message") {
            renderMessage(data);
        }
    };

    // Preview da imagem
    imageInput.addEventListener("change", () => {
        filePreview.innerHTML = "";
        const file = imageInput.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            const img = document.createElement("img");
            img.src = e.target.result;
            img.style.maxHeight = "100px";
            img.classList.add("rounded");
            filePreview.appendChild(img);
        };
        reader.readAsDataURL(file);
    });

    // Função para converter arquivo em base64
    function fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
            reader.readAsDataURL(file);
        });
    }

    // Enviar mensagem
    sendBtn.addEventListener("click", async () => {
        const text = messageInput.value.trim();
        const capitulo = spoilerInput.value || null;
        let imagemBase64 = null;

        if (imageInput.files[0]) {
            imagemBase64 = await fileToBase64(imageInput.files[0]);
        }

        if (!text && !imagemBase64) return;

        socket.send(JSON.stringify({
            type: "chat_message",
            message: text,
            user_id: userId,
            username: username,
            spoiler_capitulo: capitulo,
            imagem: imagemBase64
        }));

        messageInput.value = "";
        imageInput.value = "";
        spoilerInput.value = "";
        filePreview.innerHTML = "";
    });

    // Renderizar mensagens no chat
    function renderMessage(data) {
    const div = document.createElement("div");
    const isSelf = parseInt(data.user_id) === parseInt(userId);

    if (isSelf) {
        div.className = "message sent";
        div.dataset.messageId = data.id;

        div.innerHTML = `
            <div class="message-wrapper">
                <div class="message-content">
                    ${data.imagem_url ? `<div class="image-message mt-2">
                        <img src="${data.imagem_url}" alt="Imagem" loading="lazy">
                    </div>` : ""}
                    <div class="message-text mt-1">${data.message}</div>
                </div>
                <div class="message-timestamp">${data.timestamp}</div>
            </div>
        `;
    } else {
        div.className = "d-flex align-items-end gap-2 message received";
        div.dataset.messageId = data.id;

        div.innerHTML = `
            <img class="img-profile rounded-circle"
                 src="${data.user_profile_picture || '/static/template/img/placeholder.jpg'}"
                 width="40" height="40" style="object-fit: cover;">

            <div class="message-wrapper">
                <div class="message-content">
                    ${data.username ? `<a href="/user/profile/${data.user_id}/">
                        <span class="d-none d-lg-inline text-gray-600 me-2">
                            ${data.username}
                        </span>
                    </a>` : ""}
                    
                    ${data.imagem_url ? `<div class="image-message mt-2">
                        <img src="${data.imagem_url}" alt="Imagem" loading="lazy">
                    </div>` : ""}

                    ${data.is_spoiler ? `<div class="spoiler-box mt-2 position-relative">
                        <div class="spoiler-blurred p-3" id="spoiler-${data.id}">
                            ${data.message}
                        </div>
                        <button class="btnMostrarSpoiler mt-1" data-target="spoiler-${data.id}"
                            style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                                   background: transparent; border: none; color: var(--primary-color);
                                   padding: 0; font-size: 0.9rem; cursor: pointer;">
                            spoiler do cap. ${data.capitulo || "?"}
                        </button>
                    </div>` : (!data.imagem_url ? `<div class="message-text mt-2">${data.message}</div>` : "")}
                </div>

                <div class="message-timestamp">${data.timestamp}</div>
            </div>
        `;
    }

    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight; // scroll automático
}


    // Mostrar spoilers ao clicar
    document.addEventListener("click", (e) => {
        if (e.target.classList.contains("btnMostrarSpoiler")) {
            const target = document.getElementById(e.target.dataset.target);
            target.classList.add("revealed");
            e.target.remove();
        }
    });
});