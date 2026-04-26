const logoutBtn = document.getElementById("logoutBtn");
const profileMenuBtn = document.getElementById("profileMenuBtn");
const profileMenu = document.getElementById("profileMenu");
const saveProfileBtn = document.getElementById("saveProfileBtn");
const profilePrevBtn = document.getElementById("profilePrevBtn");
const profileNextBtn = document.getElementById("profileNextBtn");
const profileMessage = document.getElementById("profileMessage");
const profilesNode = document.getElementById("profiles");
const profilesCount = document.getElementById("profilesCount");
const filterGender = document.getElementById("filterGender");
const filterCity = document.getElementById("filterCity");
const loadProfilesBtn = document.getElementById("loadProfilesBtn");
const profileStepTabs = Array.from(document.querySelectorAll("[data-step-tab]"));
const profileStepPanels = Array.from(document.querySelectorAll("[data-step-panel]"));

let currentProfileStep = 0;

function closeProfileMenu() {
  profileMenu.hidden = true;
  profileMenuBtn.setAttribute("aria-expanded", "false");
}

function openProfileMenu() {
  profileMenu.hidden = false;
  profileMenuBtn.setAttribute("aria-expanded", "true");
}

async function api(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
    },
    ...options,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || data.message || "Request failed.");
  }
  return data;
}

function ageFromDob(dob) {
  if (!dob) {
    return "-";
  }
  const diff = Date.now() - new Date(dob).getTime();
  return Math.floor(diff / (1000 * 60 * 60 * 24 * 365.25));
}

function showProfileMessage(type, text) {
  profileMessage.className = `status-message ${type}`;
  profileMessage.textContent = text;
}

function setProfileStep(stepIndex) {
  currentProfileStep = stepIndex;

  profileStepTabs.forEach((tab, index) => {
    tab.classList.toggle("active", index === stepIndex);
  });

  profileStepPanels.forEach((panel, index) => {
    panel.classList.toggle("active", index === stepIndex);
  });

  profilePrevBtn.style.display = stepIndex === 0 ? "none" : "inline-flex";
  profileNextBtn.style.display = stepIndex === profileStepPanels.length - 1 ? "none" : "inline-flex";
  saveProfileBtn.style.display = stepIndex === profileStepPanels.length - 1 ? "inline-flex" : "none";
}

function renderProfiles(items) {
  profilesNode.innerHTML = "";
  profilesCount.textContent = `${items.length} ${t("profiles_count")}`;

  if (!items.length) {
    profilesNode.innerHTML = `<div class="profile-card"><div class="meta">${t("no_profiles_found")}</div></div>`;
    return;
  }

  for (const item of items) {
    const card = document.createElement("article");
    card.className = "profile-card";
    const imageMarkup = item.photo_b64
      ? `<img class="avatar" src="data:image/jpeg;base64,${item.photo_b64}" alt="${item.full_name}">`
      : '<div class="avatar"></div>';

    card.innerHTML = `
      <div class="profile-head">
        ${imageMarkup}
        <div>
          <div class="profile-title">${item.full_name}</div>
          <div class="meta">${item.gender || "-"} | ${ageFromDob(item.dob)} yrs | ${item.city || "-"}</div>
        </div>
      </div>
      <div class="profile-copy">
        <strong>${t("gotra")}:</strong> ${item.gotra || "-"}<br>
        <strong>${t("manglik")}:</strong> ${item.manglik || "-"}<br>
        <strong>${t("education")}:</strong> ${item.education || "-"}<br>
        <strong>${t("occupation")}:</strong> ${item.occupation || "-"}<br>
        <strong>${t("phone")}:</strong> ${item.contact_phone || "-"} / ${item.contact_email || "-"}<br>
        <strong>${t("about")}:</strong> ${item.about || "-"}
      </div>
    `;
    profilesNode.appendChild(card);
  }
}

async function loadProfiles() {
  const params = new URLSearchParams({
    gender: filterGender.value,
    city: filterCity.value.trim(),
  });
  const data = await api(`/api/profiles?${params.toString()}`, { method: "GET" });
  renderProfiles(data.profiles);
}

logoutBtn.addEventListener("click", async () => {
  await api("/api/signout", { method: "POST" });
  window.location.href = "/auth";
});

profileMenuBtn.addEventListener("click", () => {
  if (profileMenu.hidden) {
    openProfileMenu();
    return;
  }
  closeProfileMenu();
});

document.addEventListener("click", (event) => {
  if (profileMenu.hidden) {
    return;
  }
  if (profileMenu.contains(event.target) || profileMenuBtn.contains(event.target)) {
    return;
  }
  closeProfileMenu();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeProfileMenu();
  }
});

saveProfileBtn.addEventListener("click", async () => {
  const form = new FormData();
  form.append("full_name", document.getElementById("fullName").value.trim());
  form.append("gender", document.getElementById("gender").value);
  form.append("dob", document.getElementById("dob").value);
  form.append("gotra", document.getElementById("gotra").value.trim());
  form.append("manglik", document.getElementById("manglik").value);
  form.append("education", document.getElementById("education").value.trim());
  form.append("occupation", document.getElementById("occupation").value.trim());
  form.append("city", document.getElementById("city").value.trim());
  form.append("about", document.getElementById("about").value.trim());
  form.append("contact_phone", document.getElementById("contactPhone").value.trim());
  form.append("contact_email", document.getElementById("contactEmail").value.trim());

  const file = document.getElementById("photo").files[0];
  if (file) {
    form.append("photo", file);
  }

  try {
    const data = await api("/api/profiles", { method: "POST", body: form });
    showProfileMessage("success", data.message);
    await loadProfiles();
  } catch (error) {
    showProfileMessage("error", error.message);
  }
});

profilePrevBtn.addEventListener("click", () => {
  if (currentProfileStep > 0) {
    setProfileStep(currentProfileStep - 1);
  }
});

profileNextBtn.addEventListener("click", () => {
  if (currentProfileStep < profileStepPanels.length - 1) {
    setProfileStep(currentProfileStep + 1);
  }
});

profileStepTabs.forEach((tab, index) => {
  tab.addEventListener("click", () => {
    setProfileStep(index);
  });
});

loadProfilesBtn.addEventListener("click", loadProfiles);
filterGender.addEventListener("change", loadProfiles);
filterCity.addEventListener("input", loadProfiles);

setProfileStep(0);
loadProfiles().catch(() => {
  renderProfiles([]);
});
