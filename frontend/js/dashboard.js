const token =
    localStorage.getItem(
        "access_token"
    );

if (!token) {

    window.location.href =
        "login.html";
}

fetch(
    "http://127.0.0.1:8000/dashboard",
    {
        headers: {
            Authorization:
                `Bearer ${token}`
        }
    }
)
.then(response => {

    if (!response.ok) {

        localStorage.removeItem(
            "access_token"
        );

        window.location.href =
            "login.html";

        return;
    }

    return response.json();
})
.then(data => {

    document.getElementById(
        "welcome"
    ).textContent =
        `Welcome User ${data.username}!`;
});

function logout() {

    localStorage.removeItem(
        "access_token"
    );

    window.location.href =
        "login.html";
}