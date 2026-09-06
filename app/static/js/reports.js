(function () {
  "use strict";
  var d = window.GP_REPORTS;
  if (!d || typeof Chart === "undefined") return;
  var c = window.GP.chartColors();
  Chart.defaults.color = c.text;
  Chart.defaults.font.family = "'Inter', sans-serif";

  var bar = function (id, cfg) {
    var el = document.getElementById(id);
    if (el) new Chart(el, cfg);
  };
  var gridScales = { y: { beginAtZero: true, grid: { color: c.grid } }, x: { grid: { display: false } } };

  bar("cProgress", { type: "bar", data: d.progress, options: { indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { max: 100, grid: { color: c.grid } } } } });
  bar("cWorkload", { type: "bar", data: d.workload, options: { plugins: { legend: { display: false } }, scales: gridScales } });
  bar("cStatus", { type: "doughnut", data: d.status, options: { plugins: { legend: { position: "bottom" } }, cutout: "60%" } });
  bar("cCompliance", { type: "pie", data: d.compliance, options: { plugins: { legend: { position: "bottom" } } } });
  bar("cPriority", { type: "doughnut", data: d.priority, options: { plugins: { legend: { position: "bottom" } }, cutout: "60%" } });
  bar("cMonthly", { type: "line", data: d.monthly, options: { plugins: { legend: { display: false } }, scales: gridScales } });
})();
