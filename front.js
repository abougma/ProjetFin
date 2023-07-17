const messageContainer = document.getElementById('message-container');
const senderInput = document.getElementById('sender-input');
const recipientInput = document.getElementById('recipient-input');
const contentInput = document.getElementById('content-input');
const sendButton = document.getElementById('send-button');
const sidebarNames = document.getElementById('sidebar-names');

sendButton.addEventListener('click', () => {
    const sender = senderInput.value;
    const recipient = recipientInput.value;
    const content = contentInput.value;
    const dateTime = new Date().toISOString();

    // Effectuez ici une requête POST vers votre API REST pour envoyer le message

    fetch('http://localhost:8000/messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            sender: sender,
            recipient: recipient,
            content: content,
            date_time: dateTime
        })
    })
    .then(response => response.json())
    .then(data => {
        // Ajoutez le message à l'interface utilisateur
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.innerHTML = `
            <div class="message-sender">${sender}</div>
            <div class="message-content">${content}</div>
            <div class="message-datetime">${dateTime}</div>
        `;
        messageContainer.appendChild(messageElement);

        // Vérifier si le nom de l'expéditeur est déjà dans la liste
        const senderExists = Array.from(sidebarNames.children).some(
            (item) => item.textContent === sender
        );

        if (!senderExists) {
            const senderElement = document.createElement('li');
            senderElement.textContent = sender;
            sidebarNames.appendChild(senderElement);
        }

        // Réinitialisez les champs de saisie
        senderInput.value = '';
        recipientInput.value = '';
        contentInput.value = '';

        // Faites défiler vers le bas pour afficher le dernier message
        messageContainer.scrollTop = messageContainer.scrollHeight;
    })
    .catch(error => {
        console.error('Une erreur s\'est produite lors de l\'envoi du message:', error);
    });
});
