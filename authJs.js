function submitForm(event) {
    event.preventDefault();
  
    const pseudo = document.getElementById('pseudo').value;
    const password = document.getElementById('password').value;
  
    const data = {
      pseudo: pseudo,
      password: password
    };
  
    fetch('http://localhost:8000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
      .then(response => response.json())
      .then(result => {
        if (result.message) {
          alert(result.message);
          window.location.href = "front.html";
        } else if (result.error) {
          alert(result.error);
        }
      })
      .catch(error => {
        console.error('Erreur :', error);
        alert('Une erreur est survenue lors de la connexion.');
      });
  }
  
  document.getElementById('loginForm').addEventListener('submit', submitForm);
  