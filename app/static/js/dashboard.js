(function () {
  "use strict";
  var data = window.GP_CHARTS;
  if (!data || typeof Chart === "undefined") return;
  var c = window.GP.chartColors();
  Chart.defaults.color = c.text;
  Chart.defaults.font.family = "'Inter', sans-serif";

  new Chart(document.getElementById("chartMonthly"), {
    type: "line",
    data: data.monthly,
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, grid: { color: c.grid } }, x: { grid: { display: false } } },
    },
  });

  new Chart(document.getElementById("chartStatus"), {
    type: "doughnut",
    data: data.status,
    options: { responsive: true, plugins: { legend: { position: "bottom" } }, cutout: "62%" },
  });
})();
