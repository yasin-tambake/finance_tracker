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
async function loadCategories() {

    const token =
        localStorage.getItem(
            "access_token"
        );

    const response =
        await fetch(
            "http://127.0.0.1:8000/categories/",
            {
                headers: {
                    Authorization:
                        `Bearer ${token}`
                }
            }
        );

    const categories =
        await response.json();

    const list =
        document.getElementById(
            "category-list"
        );

    list.innerHTML = "";

    categories.forEach(category => {

        const li =
            document.createElement("li");

        li.innerHTML = `
            ${category.name}
            (${category.type})

            <button
                onclick="deleteCategory(${category.id})"
            >
                Delete
            </button>
        `;

        list.appendChild(li);
    });
}
async function addCategory() {

    const token =
        localStorage.getItem(
            "access_token"
        );

    const name =
        document.getElementById(
            "category-name"
        ).value;

    const type =
        document.getElementById(
            "category-type"
        ).value;

    await fetch(
        "http://127.0.0.1:8000/categories",
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json",

                Authorization:
                    `Bearer ${token}`
            },

            body: JSON.stringify({
                name,
                type
            })
        }
    );

    loadCategories();
}

async function deleteCategory(id) {

    const token =
        localStorage.getItem(
            "access_token"
        );

    await fetch(
        `http://127.0.0.1:8000/categories/${id}`,
        {
            method: "DELETE",

            headers: {
                Authorization:
                    `Bearer ${token}`
            }
        }
    );

    loadCategories();
}