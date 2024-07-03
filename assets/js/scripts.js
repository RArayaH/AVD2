function logout(csrfToken, logoutUrl, loginUrl) {
    fetch(logoutUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrfToken
        }
    }).then(response => {
        if (response.ok) {
            window.location.href = loginUrl;
        } else {
            console.error('Error al cerrar sesión');
        }
    });
}