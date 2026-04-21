const state = {
  token: localStorage.getItem("tecnico_token") || "",
  currentUser: localStorage.getItem("tecnico_user") || "",
  selectedReparacionId: null,
};

const API_LOGIN_URL = "/api/auth/login";

const loginCard = document.getElementById("loginCard");
const panelCard = document.getElementById("panelCard");
const detalleCard = document.getElementById("detalleCard");
const userBadge = document.getElementById("userBadge");
const logoutBtn = document.getElementById("logoutBtn");
const reparacionesBody = document.getElementById("reparacionesBody");
const panelError = document.getElementById("panelError");
const detalleMsg = document.getElementById("detalleMsg");

function authHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${state.token}`,
  };
}

async function readApiJson(res) {
  const raw = await res.text();

  if (!raw) {
    return {
      ok: false,
      error: `Respuesta vacia del servidor (${res.status})`,
    };
  }

  try {
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object") {
      return parsed;
    }
    return {
      ok: false,
      error: `Respuesta invalida del servidor (${res.status})`,
    };
  } catch (err) {
    return {
      ok: false,
      error: `Respuesta no JSON del servidor (${res.status})`,
    };
  }
}

function setLoggedInView(isLoggedIn) {
  loginCard.classList.toggle("hidden", isLoggedIn);
  panelCard.classList.toggle("hidden", !isLoggedIn);
  detalleCard.classList.toggle("hidden", !isLoggedIn);
  userBadge.classList.toggle("hidden", !isLoggedIn);
  logoutBtn.classList.toggle("hidden", !isLoggedIn);
  userBadge.textContent = isLoggedIn ? `Usuario: ${state.currentUser}` : "";
}

function estadoText(estado) {
  if (estado === "en_espera_retiro") return "En espera de retiro";
  if (estado === "retirado") return "Retirado";
  return "En proceso";
}

function renderRows(reparaciones) {
  reparacionesBody.innerHTML = "";

  if (!reparaciones.length) {
    reparacionesBody.innerHTML = "<tr><td colspan='6'>Sin resultados</td></tr>";
    return;
  }

  for (const rep of reparaciones) {
    const tr = document.createElement("tr");
    const equipo = `${rep.dispositivo || ""} ${rep.modelo || ""}`.trim();

    tr.innerHTML = `
      <td>${rep.numero_orden || ""}</td>
      <td>${rep.cliente_nombre || ""}</td>
      <td>${equipo}</td>
      <td><span class="status-pill status-${rep.estado}">${estadoText(rep.estado)}</span></td>
      <td>${rep.fecha_creacion || ""}</td>
      <td><button class="btn" data-id="${rep.id}" data-orden="${rep.numero_orden}">Ver</button></td>
    `;

    reparacionesBody.appendChild(tr);
  }

  reparacionesBody.querySelectorAll("button[data-id]").forEach((btn) => {
    btn.addEventListener("click", () => {
      loadDetalle(btn.dataset.orden);
    });
  });
}

async function loadReparaciones() {
  panelError.textContent = "";
  const q = document.getElementById("searchInput").value.trim();
  const estado = document.getElementById("estadoSelect").value;
  const params = new URLSearchParams();
  params.set("limit", "200");
  if (q) params.set("q", q);
  if (estado) params.set("estado", estado);

  try {
    const res = await fetch(`/api/tecnico/reparaciones?${params.toString()}`, {
      headers: authHeaders(),
    });

    if (res.status === 401) {
      forceLogout("Sesion vencida. Inicia nuevamente.");
      return;
    }

    const data = await readApiJson(res);
    if (!data.ok) {
      panelError.textContent = data.error || "No se pudo obtener reparaciones";
      return;
    }

    renderRows(data.reparaciones || []);
  } catch (err) {
    panelError.textContent = `Error de conexion: ${err.message}`;
  }
}

function renderDetalle(rep) {
  state.selectedReparacionId = rep.id;
  document.getElementById("nuevoEstado").value = rep.estado || "en_proceso";

  const fields = [
    ["Orden", rep.numero_orden],
    ["Cliente", rep.cliente_nombre],
    ["Telefono", rep.cliente_telefono],
    ["Email", rep.cliente_email],
    ["DNI", rep.cliente_dni],
    ["Equipo", `${rep.dispositivo || ""} ${rep.modelo || ""}`.trim()],
    ["Serie", rep.numero_serie],
    ["Problema", rep.problema],
    ["Contrasena", rep.contrasena],
    ["Patron", rep.patron],
    ["Senia", rep.sena],
    ["Total", rep.total],
    ["Estado", estadoText(rep.estado)],
    ["Observaciones", rep.observaciones],
  ];

  const detalle = document.getElementById("detalleContent");
  detalle.innerHTML = "";

  fields.forEach(([label, value]) => {
    const div = document.createElement("div");
    div.className = "detail-item";
    div.innerHTML = `<strong>${label}</strong><span>${value || "-"}</span>`;
    detalle.appendChild(div);
  });
}

async function loadDetalle(numeroOrden) {
  detalleMsg.textContent = "";
  try {
    const res = await fetch(`/api/tecnico/reparaciones/orden/${encodeURIComponent(numeroOrden)}`, {
      headers: authHeaders(),
    });

    if (res.status === 401) {
      forceLogout("Sesion vencida. Inicia nuevamente.");
      return;
    }

    const data = await readApiJson(res);
    if (!data.ok) {
      detalleMsg.textContent = data.error || "No se pudo cargar el detalle";
      return;
    }

    renderDetalle(data.reparacion);
  } catch (err) {
    detalleMsg.textContent = `Error de conexion: ${err.message}`;
  }
}

async function updateEstado() {
  detalleMsg.textContent = "";
  const estado = document.getElementById("nuevoEstado").value;

  if (!state.selectedReparacionId) {
    detalleMsg.textContent = "Selecciona una reparacion primero";
    return;
  }

  try {
    const res = await fetch(`/api/tecnico/reparaciones/${state.selectedReparacionId}/estado`, {
      method: "PUT",
      headers: authHeaders(),
      body: JSON.stringify({ estado }),
    });

    if (res.status === 401) {
      forceLogout("Sesion vencida. Inicia nuevamente.");
      return;
    }

    const data = await readApiJson(res);
    if (!data.ok) {
      detalleMsg.textContent = data.error || "No se pudo actualizar estado";
      return;
    }

    detalleMsg.textContent = "Estado actualizado correctamente";
    await loadReparaciones();
  } catch (err) {
    detalleMsg.textContent = `Error de conexion: ${err.message}`;
  }
}

async function doLogin(evt) {
  evt.preventDefault();
  document.getElementById("loginError").textContent = "";

  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;

  try {
    const res = await fetch(API_LOGIN_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await readApiJson(res);
    if (!data.ok) {
      document.getElementById("loginError").textContent = `${data.error || "Error de login"} [${API_LOGIN_URL}]`;
      return;
    }

    state.token = data.token;
    state.currentUser = data.user?.username || username;
    localStorage.setItem("tecnico_token", state.token);
    localStorage.setItem("tecnico_user", state.currentUser);

    setLoggedInView(true);
    await loadReparaciones();
  } catch (err) {
    document.getElementById("loginError").textContent = `Error de conexion: ${err.message}`;
  }
}

function forceLogout(message = "") {
  state.token = "";
  state.currentUser = "";
  state.selectedReparacionId = null;
  localStorage.removeItem("tecnico_token");
  localStorage.removeItem("tecnico_user");
  setLoggedInView(false);
  reparacionesBody.innerHTML = "";
  document.getElementById("detalleContent").innerHTML = "";
  if (message) {
    document.getElementById("loginError").textContent = message;
  }
}

function initEvents() {
  document.getElementById("loginForm").addEventListener("submit", doLogin);
  document.getElementById("refreshBtn").addEventListener("click", loadReparaciones);
  document.getElementById("estadoSelect").addEventListener("change", loadReparaciones);
  document.getElementById("searchInput").addEventListener("keydown", (evt) => {
    if (evt.key === "Enter") {
      evt.preventDefault();
      loadReparaciones();
    }
  });
  document.getElementById("guardarEstadoBtn").addEventListener("click", updateEstado);
  logoutBtn.addEventListener("click", () => forceLogout());
}

async function bootstrap() {
  initEvents();
  if (state.token) {
    setLoggedInView(true);
    await loadReparaciones();
  } else {
    setLoggedInView(false);
  }
}

bootstrap();
