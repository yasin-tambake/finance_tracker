const token =
    localStorage.getItem(
        "access_token"
    );

fetch(
    "http://127.0.0.1:8000/categories",
    {
        method: "POST",
        headers: {
            "Content-Type":
                "application/json",
            "Authorization":
                `Bearer ${token}`
        },
        body: JSON.stringify({
            name: "Food"
        })
    }
);