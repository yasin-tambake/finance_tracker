async function loginUser() {

    const username =
        document.getElementById("username_or_email").value;

    const password =
        document.getElementById("password").value;

    const formData = new URLSearchParams();

    formData.append(
        "username",
        username
    );

    formData.append(
        "password",
        password
    );

    const response = await fetch(
        "http://127.0.0.1:8000/login",
        {
            method: "POST",
            headers: {
                "Content-Type":
                    "application/x-www-form-urlencoded"
            },
            body: formData
        }
    );

    const data = await response.json();

    const message =
        document.getElementById("message");

    if (response.ok) {

        localStorage.setItem(
            "access_token",
            data.access_token
        );

        window.location.href =
            "dashboard.html";
    }
    else {

        message.innerText =
            data.detail || "Invalid Credentials";
    }
}