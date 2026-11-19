// FindHome Frontend Engine for FindHome USA
const CONFIG = {
  brand: "FindHome USA",
  currency: "$",
  areaUnit: "sq ft",
  mapCenter: [39.8283, -98.5795],
  mapZoom: 4,
  lang: "en",
  apiPrefix: window.location.pathname.includes("/USA") ? "/USA/api/v1" : "/api/v1"
};

let mainMap = null;
let mapMarkers = [];
let allProperties = [];

document.addEventListener("DOMContentLoaded", () => {
  initRentCalculator();
  initMap();
  loadProperties();
  initFilters();
  initVoiceAssistant();
  initAdminModal();
});

function initRentCalculator() {
  const rentInput = document.getElementById("calc-total-rent");
  const roomBtns = document.querySelectorAll(".btn-roommate");
  const perPersonSpan = document.getElementById("calc-per-person");
  const savingsSpan = document.getElementById("calc-savings");
  const waBtn = document.getElementById("btn-calc-whatsapp");

  let selectedRooms = 4;

  roomBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      roomBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedRooms = parseInt(btn.dataset.rooms);
      calculate();
    });
  });

  rentInput.addEventListener("input", calculate);

  function calculate() {
    const rent = parseFloat(rentInput.value) || 0;
    const perPerson = Math.round(rent / selectedRooms);
    const soloBaseline = Math.round(rent * 0.75);
    const savings = Math.max(0, soloBaseline - perPerson);

    perPersonSpan.textContent = `${CONFIG.currency} ${perPerson.toLocaleString()} / mo`;
    savingsSpan.textContent = `~ ${CONFIG.currency} ${savings.toLocaleString()} / mo`;

    const waText = encodeURIComponent(`Hi ${CONFIG.brand}, I want to reserve a co-living split of ${CONFIG.currency} ${rent} for ${selectedRooms} roommates (${CONFIG.currency} ${perPerson}/person).`);
    waBtn.href = `https://wa.me/34603331391?text=${waText}`;
  }

  calculate();
}

function initMap() {
  const mapEl = document.getElementById("main-map");
  if (!mapEl) return;

  mainMap = L.map("main-map").setView(CONFIG.mapCenter, CONFIG.mapZoom);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
  }).addTo(mainMap);
}

async function loadProperties(filters = {}) {
  const grid = document.getElementById("properties-grid");
  const countLabel = document.getElementById("properties-count");

  try {
    let url = `${CONFIG.apiPrefix}/properties?`;
    if (filters.city) url += `city=${encodeURIComponent(filters.city)}&`;
    if (filters.subdivision) url += `subdivision=${encodeURIComponent(filters.subdivision)}&`;
    if (filters.min_bedrooms) url += `min_bedrooms=${filters.min_bedrooms}&`;
    if (filters.max_total_rent) url += `max_total_rent=${filters.max_total_rent}&`;

    const res = await fetch(url);
    const data = await res.json();
    allProperties = data;

    countLabel.textContent = `${data.length} listings available across regions`;
    grid.innerHTML = "";

    // Clear map markers
    mapMarkers.forEach(m => mainMap.removeLayer(m));
    mapMarkers = [];

    data.forEach(p => {
      const card = createPropertyCard(p);
      grid.appendChild(card);

      if (mainMap && p.latitude && p.longitude) {
        const marker = L.marker([p.latitude, p.longitude]).addTo(mainMap);
        marker.bindPopup(`
          <div style="font-family: inherit; min-width: 200px;">
            <strong style="color: #6366f1;">${p.title}</strong><br>
            <span style="font-size: 13px; color: #64748b;">${p.city}, ${p.subdivision}</span><br>
            <strong style="font-size: 14px; color: #10b981;">${CONFIG.currency} ${p.rent_per_person} / person</strong><br>
            <small>${p.bedrooms} Beds • ${p.surface} ${CONFIG.areaUnit}</small><br>
            <a href="${p.source_url}" target="_blank" style="color: #3b82f6; text-decoration: underline;">View on ${p.source_portal}</a>
          </div>
        `);
        mapMarkers.push(marker);
      }
    });

  } catch (err) {
    console.error("Failed to load properties:", err);
    countLabel.textContent = "Error loading properties.";
  }
}

function createPropertyCard(p) {
  const div = document.createElement("div");
  div.className = "property-card";
  const imgUrl = (p.images && p.images.length > 0) ? p.images[0] : "static/images/prop-mad-01-1.jpg";

  div.innerHTML = `
    <div class="card-img-container">
      <img src="${imgUrl}" alt="${p.title}" class="card-img" onerror="this.src='static/images/prop-mad-01-1.jpg'">
      <div class="card-badge">${p.source_portal}</div>
    </div>
    <div class="card-body">
      <div class="card-location">${p.city}, ${p.subdivision}</div>
      <h3 class="card-title">${p.title}</h3>
      <div class="card-specs">
        <span>🛏️ ${p.bedrooms} Beds</span>
        <span>🚿 ${p.bathrooms} Baths</span>
        <span>📐 ${p.surface} ${CONFIG.areaUnit}</span>
      </div>
      <div class="card-pricing">
        <div>
          <span class="price-split">${CONFIG.currency} ${p.rent_per_person.toLocaleString()}</span>
          <span class="price-sub">/ person</span>
        </div>
        <div>
          <span class="price-total">${CONFIG.currency} ${p.total_rent.toLocaleString()}</span>
          <span class="price-sub">total</span>
        </div>
      </div>
      <div class="card-actions">
        <a href="${p.source_url}" target="_blank" class="btn btn-outline btn-sm">Portal Listing</a>
        <a href="https://wa.me/34603331391?text=${encodeURIComponent('Hi, inquiring about ' + p.title + ' in ' + p.city)}" target="_blank" class="btn btn-primary btn-sm">WhatsApp Tour</a>
      </div>
    </div>
  `;
  return div;
}

function initFilters() {
  const btnApply = document.getElementById("btn-apply-filters");
  const btnReset = document.getElementById("btn-reset-filters");

  btnApply.addEventListener("click", () => {
    const city = document.getElementById("filter-city").value.trim();
    const subdivision = document.getElementById("filter-subdivision").value.trim();
    const min_bedrooms = document.getElementById("filter-bedrooms").value;
    const max_total_rent = document.getElementById("filter-max-price").value;

    loadProperties({ city, subdivision, min_bedrooms, max_total_rent });
  });

  btnReset.addEventListener("click", () => {
    document.getElementById("filter-city").value = "";
    document.getElementById("filter-subdivision").value = "";
    document.getElementById("filter-bedrooms").value = "3";
    document.getElementById("filter-max-price").value = "";
    loadProperties();
  });
}

function initVoiceAssistant() {
  const fab = document.getElementById("fab-toggle-btn");
  const modal = document.getElementById("voice-modal");
  const closeBtn = document.getElementById("voice-modal-close");
  const sendBtn = document.getElementById("btn-voice-send");
  const input = document.getElementById("voice-text-input");
  const micBtn = document.getElementById("btn-voice-mic");
  const resBox = document.getElementById("voice-response-box");
  const status = document.getElementById("voice-status");

  fab.addEventListener("click", () => modal.classList.add("active"));
  closeBtn.addEventListener("click", () => modal.classList.remove("active"));

  sendBtn.addEventListener("click", () => {
    const q = input.value.trim();
    if (!q) return;
    handleVoiceQuery(q);
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const q = input.value.trim();
      if (!q) return;
      handleVoiceQuery(q);
    }
  });

  let recognition = null;
  if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRec();
    recognition.lang = CONFIG.lang === "es" ? "es-ES" : "en-US";
    recognition.continuous = false;

    recognition.onstart = () => {
      status.textContent = "Listening...";
      micBtn.classList.add("listening");
    };

    recognition.onresult = (evt) => {
      const transcript = evt.results[0][0].transcript;
      input.value = transcript;
      handleVoiceQuery(transcript);
    };

    recognition.onend = () => {
      status.textContent = "Processing speech...";
      micBtn.classList.remove("listening");
    };

    micBtn.addEventListener("click", () => {
      recognition.start();
    });
  } else {
    micBtn.style.display = "none";
  }

  async function handleVoiceQuery(queryText) {
    status.textContent = "Thinking...";
    try {
      const res = await fetch(`${CONFIG.apiPrefix}/voice/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: queryText, lang: CONFIG.lang })
      });
      const data = await res.json();
      status.textContent = "Response received";

      resBox.innerHTML = `
        <div class="voice-bubble bot">
          <p>${data.reply_text}</p>
          ${data.whatsapp_url ? `<a href="${data.whatsapp_url}" target="_blank" class="btn btn-sm btn-primary" style="margin-top: 8px; display: inline-block;">Open on WhatsApp</a>` : ""}
        </div>
      `;

      // Speak text aloud
      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(data.reply_text);
        utter.lang = CONFIG.lang === "es" ? "es-ES" : "en-US";
        window.speechSynthesis.speak(utter);
      }

    } catch (e) {
      status.textContent = "Error communicating with voice agent.";
    }
  }
}

function initAdminModal() {
  const openBtn = document.getElementById("btn-open-admin");
  const modal = document.getElementById("admin-modal");
  const closeBtn = document.getElementById("admin-modal-close");
  const submitBtn = document.getElementById("btn-admin-login-submit");
  const passInput = document.getElementById("admin-pass-input");
  const loginView = document.getElementById("admin-login-view");
  const dashView = document.getElementById("admin-dashboard-view");

  openBtn.addEventListener("click", () => modal.classList.add("active"));
  closeBtn.addEventListener("click", () => modal.classList.remove("active"));

  submitBtn.addEventListener("click", doAdminLogin);
  passInput.addEventListener("keydown", (e) => { if (e.key === "Enter") doAdminLogin(); });

  async function doAdminLogin() {
    const pwd = passInput.value.trim();
    if (!pwd) return;

    try {
      const res = await fetch(`${CONFIG.apiPrefix}/admin/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password: pwd })
      });
      const data = await res.json();
      if (res.ok && (data.authenticated || data.status === "authenticated")) {
        loginView.classList.add("hidden");
        dashView.classList.remove("hidden");
        loadAdminDashboard();
      } else {
        alert("Incorrect password.");
      }
    } catch (err) {
      alert("Error logging in.");
    }
  }

  let adminMap = null;
  async function loadAdminDashboard() {
    const statsRow = document.getElementById("admin-stats-row");
    const tbody = document.getElementById("admin-logs-tbody");

    const [statsRes, logsRes] = await Promise.all([
      fetch(`${CONFIG.apiPrefix}/admin/stats`),
      fetch(`${CONFIG.apiPrefix}/admin/access-logs`)
    ]);

    const stats = await statsRes.json();
    const logs = await logsRes.json();

    statsRow.innerHTML = `
      <div class="stat-box"><strong>${stats.total_visits}</strong><span>Total Visits</span></div>
      <div class="stat-box"><strong>${stats.unique_countries}</strong><span>Countries</span></div>
      <div class="stat-box"><strong>${stats.unique_cities}</strong><span>Metro Nodes</span></div>
      <div class="stat-box"><strong>100%</strong><span>Uptime</span></div>
    `;

    tbody.innerHTML = "";
    logs.slice(0, 30).forEach(l => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${l.ip}</td>
        <td>${l.city || "Metro"}, ${l.country || "Global"}</td>
        <td>${l.path || "/"}</td>
        <td>${l.device_type || "Desktop"}</td>
        <td>${l.timestamp || "Just now"}</td>
      `;
      tbody.appendChild(tr);
    });

    // Initialize Admin Ingress Map
    const mapEl = document.getElementById("admin-origin-map");
    if (mapEl && !adminMap) {
      adminMap = L.map("admin-origin-map").setView(CONFIG.mapCenter, CONFIG.mapZoom);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19
      }).addTo(adminMap);

      logs.forEach(l => {
        if (l.latitude && l.longitude) {
          L.circleMarker([l.latitude, l.longitude], {
            radius: 7,
            color: "#6366f1",
            fillColor: "#818cf8",
            fillOpacity: 0.7
          }).addTo(adminMap).bindPopup(`${l.city}, ${l.country} (${l.ip})`);
        }
      });
    }
  }
}
