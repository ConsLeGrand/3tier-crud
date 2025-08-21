const API = (window.CONFIG && window.CONFIG.API_BASE_URL) || "";

async function fetchStudents() {
  const res = await fetch(`${API}/students`);
  const data = await res.json();
  const tbody = document.querySelector("#tbl tbody");
  tbody.innerHTML = "";
  data.forEach(st => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${st.id}</td>
      <td><input value="${st.first_name}" data-id="${st.id}" data-field="first_name"/></td>
      <td><input value="${st.last_name}" data-id="${st.id}" data-field="last_name"/></td>
      <td><input value="${st.email}" data-id="${st.id}" data-field="email"/></td>
      <td class="actions">
        <button onclick="updateStudent(${st.id}, this)">Mettre à jour</button>
        <button onclick="deleteStudent(${st.id}, this)" style="background:#e53935">Supprimer</button>
      </td>`;
    tbody.appendChild(tr);
  });
}

async function createStudent(e) {
  e.preventDefault();
  const body = {
    first_name: document.getElementById("fn").value,
    last_name: document.getElementById("ln").value,
    email: document.getElementById("em").value
  };
  const res = await fetch(`${API}/students`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const j = await res.json().catch(()=>({}));
    alert("Erreur: " + (j.message || res.status));
    return;
  }
  document.getElementById("create-form").reset();
  fetchStudents();
}

async function updateStudent(id, btn) {
  const tr = btn.closest("tr");
  const inputs = tr.querySelectorAll("input[data-id='"+id+"']");
  const body = {};
  inputs.forEach(i => body[i.dataset.field] = i.value);
  const res = await fetch(`${API}/students/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const j = await res.json().catch(()=>({}));
    alert("Erreur: " + (j.message || res.status));
    return;
  }
  fetchStudents();
}

async function deleteStudent(id) {
  if (!confirm("Supprimer l'étudiant ?")) return;
  const res = await fetch(`${API}/students/${id}`, { method: "DELETE" });
  if (res.status !== 204) {
    const j = await res.json().catch(()=>({}));
    alert("Erreur: " + (j.message || res.status));
    return;
  }
  fetchStudents();
}

document.getElementById("create-form").addEventListener("submit", createStudent);
fetchStudents();
