const API = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

if (!token) {
    window.location.href = "login.html";
}

let editingTransactionId = null;

window.onload = function () {

    document.getElementById("transaction-date").value =
        new Date().toISOString().split("T")[0];

    loadCategoriesByType();
    loadTransactions();
};

function logout() {

    localStorage.removeItem("access_token");

    window.location.href = "login.html";
}

async function loadCategoriesByType() {

    const type =
        document.getElementById("transaction-type").value;

    const response = await fetch(
        `${API}/categories/type/${type}`,
        {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );

    const categories = await response.json();

    const select =
        document.getElementById("transaction-category");

    select.innerHTML = "";

    categories.forEach(category => {

        select.innerHTML += `
            <option value="${category.id}">
                ${category.name}
            </option>
        `;
    });
}

async function addTransaction() {

    const category_id =
        Number(document.getElementById("transaction-category").value);

    const amount =
        Number(document.getElementById("transaction-amount").value);

    const description =
        document.getElementById("transaction-description").value;

    const transaction_date =
        document.getElementById("transaction-date").value;

    const response = await fetch(
        `${API}/transactions/`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },

            body: JSON.stringify({
                category_id,
                amount,
                description,
                transaction_date
            })
        }
    );

    if (!response.ok) {

        alert("Unable to add transaction.");

        return;
    }

    clearTransactionForm();

    loadTransactions();
}

async function loadTransactions() {

    const response = await fetch(
        `${API}/transactions/`,
        {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );

    const transactions =
        await response.json();

    const tbody =
        document.getElementById("transaction-table");

    tbody.innerHTML = "";

    transactions.forEach(transaction => {

        tbody.innerHTML += `

        <tr>

            <td>${transaction.transaction_date}</td>

            <td>${transaction.category.type}</td>

            <td>${transaction.category.name}</td>

            <td>${transaction.amount}</td>

            <td>${transaction.description ?? ""}</td>

            <td>

                <button
                    onclick="editTransaction(${transaction.id})">
                    Edit
                </button>

                <button
                    onclick="deleteTransaction(${transaction.id})">
                    Delete
                </button>

            </td>

        </tr>

        `;
    });
}

async function deleteTransaction(id) {

    if (!confirm("Delete transaction?"))
        return;

    await fetch(
        `${API}/transactions/${id}`,
        {
            method: "DELETE",

            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );

    loadTransactions();
}

async function editTransaction(id) {

    const response = await fetch(
        `${API}/transactions/${id}`,
        {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );

    const transaction =
        await response.json();

    editingTransactionId = id;

    document.getElementById("transaction-type").value =
        transaction.category.type;

    await loadCategoriesByType();

    document.getElementById("transaction-category").value =
        transaction.category.id;

    document.getElementById("transaction-amount").value =
        transaction.amount;

    document.getElementById("transaction-description").value =
        transaction.description;

    document.getElementById("transaction-date").value =
        transaction.transaction_date;

    const button =
        document.querySelector(
            "button[onclick='addTransaction()']"
        );

    button.innerText = "Update Transaction";

    button.onclick = updateTransaction;
}

async function updateTransaction() {

    const category_id =
        Number(document.getElementById("transaction-category").value);

    const amount =
        Number(document.getElementById("transaction-amount").value);

    const description =
        document.getElementById("transaction-description").value;

    const transaction_date =
        document.getElementById("transaction-date").value;

    const response = await fetch(
        `${API}/transactions/${editingTransactionId}`,
        {
            method: "PUT",

            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },

            body: JSON.stringify({
                category_id,
                amount,
                description,
                transaction_date
            })
        }
    );

    if (!response.ok) {

        alert("Unable to update transaction.");

        return;
    }

    editingTransactionId = null;

    const button =
        document.querySelector("button");

    button.innerText = "Add Transaction";

    button.onclick = addTransaction;

    clearTransactionForm();

    loadTransactions();
}

function clearTransactionForm() {

    document.getElementById("transaction-amount").value = "";

    document.getElementById("transaction-description").value = "";

    document.getElementById("transaction-date").value =
        new Date().toISOString().split("T")[0];
}

async function addCategory() {

    const name =
        document.getElementById("category-name").value;

    const type =
        document.getElementById("category-type").value;

    const response = await fetch(
        `${API}/categories/`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },

            body: JSON.stringify({
                name,
                type
            })
        }
    );

    if (!response.ok) {

        alert("Unable to add category.");

        return;
    }

    document.getElementById("category-name").value = "";

    loadCategories();
}

async function loadCategories() {

    const response = await fetch(
        `${API}/categories/`,
        {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );

    const categories =
        await response.json();

    const list =
        document.getElementById("category-list");

    list.innerHTML = "";

    categories.forEach(category => {

        list.innerHTML += `
            <li>
                ${category.name}
                (${category.type})
            </li>
        `;
    });
}