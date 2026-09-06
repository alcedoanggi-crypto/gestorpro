// Formularios y confirmaciones en modal (sin cambiar de pagina).
//  - [data-modal-form][data-url]  -> carga un formulario por AJAX y lo envia
//  - [data-modal-confirm][data-url][data-message] -> confirma y hace POST
(function () {
  "use strict";

  var modalEl = document.getElementById("ajaxModal");
  if (!modalEl || typeof bootstrap === "undefined") return;

  var bsModal = new bootstrap.Modal(modalEl);
  var dialog = modalEl.querySelector(".modal-dialog");

  function csrf() {
    return (window.GP && window.GP.csrf && window.GP.csrf()) || "";
  }

  function toast(message, type) {
    var stack = document.getElementById("toastStack");
    if (!stack) { window.alert(message); return; }
    var el = document.createElement("div");
    el.className = "alert alert-" + (type || "danger") + " alert-dismissible shadow-sm gp-toast";
    el.setAttribute("role", "alert");
    el.innerHTML = message +
      '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>';
    stack.appendChild(el);
    setTimeout(function () {
      el.classList.add("out");
      setTimeout(function () { el.remove(); }, 300);
    }, 4500);
  }
  if (window.GP) window.GP.toast = toast;

  var spinnerContent =
    '<div class="modal-content gp-modal">' +
    '<div class="modal-body text-center py-5">' +
    '<span class="spinner-border text-primary" role="status"></span></div></div>';

  function busy(btn, on) {
    if (!btn) return;
    if (on) {
      btn.dataset.html = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
    } else {
      btn.disabled = false;
      if (btn.dataset.html) btn.innerHTML = btn.dataset.html;
    }
  }

  function bindForm(form) {
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var submitBtn = form.querySelector('[type="submit"]');
      busy(submitBtn, true);

      fetch(form.action, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest", "X-CSRFToken": csrf() },
        body: new FormData(form),
      })
        .then(function (res) {
          var ct = res.headers.get("content-type") || "";
          if (res.ok && ct.indexOf("application/json") !== -1) {
            return res.json().then(function (data) {
              bsModal.hide();
              window.location = data.redirect || window.location.href;
            });
          }
          // 422: el servidor devuelve el formulario con los errores marcados
          return res.text().then(function (html) {
            dialog.innerHTML = html;
            bindForm(dialog.querySelector("form"));
          });
        })
        .catch(function () {
          busy(submitBtn, false);
          toast("No se pudo guardar. Revisa tu conexion e intenta de nuevo.");
        });
    });
  }

  function openForm(url) {
    dialog.innerHTML = spinnerContent;
    bsModal.show();
    fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
      .then(function (res) {
        if (!res.ok) throw new Error(res.status);
        return res.text();
      })
      .then(function (html) {
        dialog.innerHTML = html;
        bindForm(dialog.querySelector("form"));
        var first = dialog.querySelector("input:not([type=hidden]), textarea, select");
        if (first) first.focus();
      })
      .catch(function () {
        bsModal.hide();
        toast("No se pudo abrir el formulario.");
      });
  }

  function openConfirm(opts) {
    var warn = opts.variant === "warn";
    var headClass = warn ? "gp-modal" : "gp-modal gp-modal-danger";
    var btnClass = warn ? "btn btn-primary" : "btn btn-danger";
    var headIcon = warn ? "fa-circle-question" : "fa-triangle-exclamation";
    var goIcon = opts.icon || (warn ? "fa-check" : "fa-trash-can");
    dialog.innerHTML =
      '<div class="modal-content ' + headClass + '">' +
      '<div class="modal-header"><h5 class="modal-title">' +
      '<i class="fa-solid ' + headIcon + ' me-2"></i><span data-slot="title"></span>' +
      '</h5><button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button></div>' +
      '<div class="modal-body" data-slot="message"></div>' +
      '<div class="modal-footer">' +
      '<button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancelar</button>' +
      '<button type="button" class="' + btnClass + '" data-confirm-go>' +
      '<i class="fa-solid ' + goIcon + ' me-1"></i><span data-slot="action"></span></button></div></div>';
    dialog.querySelector('[data-slot="title"]').textContent = opts.title || "Confirmar";
    dialog.querySelector('[data-slot="message"]').textContent =
      opts.message || "¿Confirmas esta accion?";
    dialog.querySelector('[data-slot="action"]').textContent = opts.action || "Eliminar";
    bsModal.show();

    dialog.querySelector("[data-confirm-go]").addEventListener("click", function () {
      var go = this;
      busy(go, true);
      fetch(opts.url, {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest", "X-CSRFToken": csrf() },
      })
        .then(function (res) {
          return res.json().catch(function () { return { ok: res.ok }; });
        })
        .then(function (data) {
          bsModal.hide();
          if (data.ok === false) {
            toast(data.error || "No se pudo completar la accion.", "warning");
          } else {
            window.location = data.redirect || window.location.href;
          }
        })
        .catch(function () {
          busy(go, false);
          toast("No se pudo completar la accion.");
        });
    });
  }

  document.addEventListener("click", function (e) {
    var opener = e.target.closest("[data-modal-form]");
    if (opener) {
      e.preventDefault();
      openForm(opener.getAttribute("data-url") || opener.getAttribute("href"));
      return;
    }
    var confirmer = e.target.closest("[data-modal-confirm]");
    if (confirmer) {
      e.preventDefault();
      openConfirm({
        url: confirmer.getAttribute("data-url"),
        title: confirmer.getAttribute("data-title"),
        message: confirmer.getAttribute("data-message"),
        action: confirmer.getAttribute("data-action"),
        variant: confirmer.getAttribute("data-variant"),
        icon: confirmer.getAttribute("data-icon"),
      });
    }
  });
})();
