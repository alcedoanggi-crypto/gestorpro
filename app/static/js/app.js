// Utilidades globales: tema, sidebar, notificaciones, confirmaciones.
(function () {
  "use strict";

  window.GP = {
    csrf: function () {
      var m = document.querySelector('meta[name="csrf-token"]');
      return m ? m.getAttribute("content") : "";
    },
    postJSON: function (url, body) {
      return fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": window.GP.csrf() },
        body: JSON.stringify(body || {}),
      }).then(function (r) { return r.json(); });
    },
    chartColors: function () {
      var dark = document.documentElement.getAttribute("data-bs-theme") === "dark";
      return {
        grid: dark ? "rgba(255,255,255,.08)" : "rgba(0,0,0,.06)",
        text: dark ? "#8b949e" : "#6b7280",
      };
    },
  };

  // ----- Tema claro / oscuro -----
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem("gp-theme"); } catch (e) {}
  if (saved) root.setAttribute("data-bs-theme", saved);

  var themeBtn = document.getElementById("themeToggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = root.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-bs-theme", next);
      try { localStorage.setItem("gp-theme", next); } catch (e) {}
      document.dispatchEvent(new CustomEvent("gp:themechange", { detail: next }));
    });
  }

  // ----- Sidebar movil -----
  var sidebar = document.getElementById("sidebar");
  var backdrop = document.getElementById("sidebarBackdrop");
  function openSidebar(open) {
    if (!sidebar) return;
    sidebar.classList.toggle("open", open);
    if (backdrop) backdrop.classList.toggle("show", open);
  }
  ["sidebarToggle"].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) el.addEventListener("click", function () { openSidebar(true); });
  });
  ["sidebarClose", "sidebarBackdrop"].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) el.addEventListener("click", function () { openSidebar(false); });
  });

  // ----- Confirmacion en formularios peligrosos -----
  document.querySelectorAll("form.js-confirm").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      if (!window.confirm(f.dataset.message || "Confirmas esta accion?")) e.preventDefault();
    });
  });

  // ----- Notificaciones: marcar como leidas -----
  var markAll = document.getElementById("markAllRead");
  if (markAll) {
    markAll.addEventListener("click", function () {
      window.GP.postJSON("/api/notifications/read", {}).then(function () {
        document.querySelectorAll(".notif-item.unread").forEach(function (n) {
          n.classList.remove("unread");
        });
        var dot = document.getElementById("notifDot");
        if (dot) dot.remove();
      });
    });
  }
})();
