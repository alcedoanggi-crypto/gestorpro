(function () {
  "use strict";
  var cfg = window.GP_GANTT;
  if (!cfg || !cfg.tasks.length || typeof Gantt === "undefined") return;

  var gantt = new Gantt("#gantt", cfg.tasks, {
    view_mode: "Week",
    date_format: "YYYY-MM-DD",
    language: "es",
    readonly: !cfg.canEdit,
    popup_trigger: "click",
    custom_popup_html: function (task) {
      return (
        '<div class="gantt-popup p-2">' +
        "<strong>" + task.name + "</strong><br>" +
        "<small>" + task._start.toISOString().slice(0, 10) +
        " &rarr; " + task._end.toISOString().slice(0, 10) + "</small><br>" +
        "<small>Avance: " + task.progress + "%</small>" +
        '</div>'
      );
    },
    on_date_change: function (task, start, end) {
      if (!cfg.canEdit) return;
      var url = cfg.scheduleUrl.replace(/0$/, task.id);
      window.GP.postJSON(url, {
        start: start.toISOString().slice(0, 10),
        end: end.toISOString().slice(0, 10),
      }).then(function (res) {
        if (!res.ok) alert("No se pudo guardar la nueva fecha.");
      });
    },
  });

  document.querySelectorAll("#ganttModes button").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll("#ganttModes button").forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
      gantt.change_view_mode(btn.dataset.mode);
    });
  });
})();
