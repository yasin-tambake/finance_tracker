async function loginUser() {

    const username_or_email =
        document.getElementById("username_or_email").value;

    const password =
        document.getElementById("password").value;

    const response = await fetch(
        "http://127.0.0.1:8000/login",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username_or_email,
                password
            })
        }
    );

    const data = await response.json();

    const message =
        document.getElementById("message");

    if (response.ok) {

        console.log(data);

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