async function registerUser() {

    const username =
        document.getElementById("username").value.trim();

    const name =
        document.getElementById("name").value.trim();

    const email =
        document.getElementById("email").value.trim();

    const password =
        document.getElementById("password").value;

    const confirmPassword =
        document.getElementById("confirm_password").value;

    const message =
        document.getElementById("message");

    message.textContent = "";

    // Username validation
    if (username.length < 3) {
        message.textContent =
            "Username must be at least 3 characters long.";
        return;
    }

    // Name validation
    if (name.length === 0) {
        message.textContent =
            "Name is required.";
        return;
    }

    // Email validation
    const emailPattern =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {
        message.textContent =
            "Please enter a valid email address.";
        return;
    }

    // Password validation
    if (password.length < 8) {
        message.textContent =
            "Password must be at least 8 characters long.";
        return;
    }

    // Confirm password validation
    if (password !== confirmPassword) {
        message.textContent =
            "Passwords do not match.";
        return;
    }

    const userData = {
        username: username,
        name: name,
        email: email,
        password: password
    };

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/users",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(userData)
            }
        );

        const result = await response.json();

        if (response.ok) {
            message.textContent =
                "Registration successful!";
        } else {

            if (Array.isArray(result.detail)) {
                message.textContent =
                    result.detail[0].msg;
            } else {
                message.textContent =
                    result.detail;
            }
        }

    } catch (error) {
        message.textContent =
            "Unable to connect to server.";
    }
}
