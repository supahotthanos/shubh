const API = "";
const fmt = (n) => `$${(n ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const state = {
  months: [],
  selected: null,
  report: null,
  budgets: {},
  categories: [],
};

const charts = {};

// ---------- Tab nav ----------
$$(".tab").forEach((b) => {
  b.addEventListener("click", () => {
    $$(".tab").forEach((x) => x.classList.remove("active"));
    b.classList.add("active");
    const tab = b.dataset.tab;
    $$(".tab-panel").forEach((p) => p.classList.remove("active"));
    $(`#tab-${tab}`).classList.add("active");
    if (tab === "trends") loadTrend();
    if (tab === "budget") loadBudgetEditor();
    if (tab === "transactions") loadTransactions();
  });
});

// ---------- API ----------
async function api(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    let msg = res.statusText;
    try { msg = (await res.json()).detail || msg; } catch {}
    throw new Error(msg);
  }
  return res.json();
}

// ---------- Months ----------
async function loadMonths(preferredPeriod = null) {
  state.months = await api("/api/months");
  const sel = $("#monthSelect");
  sel.innerHTML = "";
  if (state.months.length === 0) {
    const opt = document.createElement("option");
    opt.value = ""; opt.textContent = "— upload a statement to begin —";
    sel.appendChild(opt);
    state.selected = null;
    renderEmpty();
    return;
  }
  state.months.forEach((m) => {
    const opt = document.createElement("option");
    opt.value = m.period;
    opt.textContent = `${formatPeriod(m.period)} — ${fmt(m.statement_total)} (${m.txn_count} txns)`;
    sel.appendChild(opt);
  });
  state.selected = preferredPeriod && state.months.some((m) => m.period === preferredPeriod)
    ? preferredPeriod
    : state.months[0].period;
  sel.value = state.selected;
  await loadReport();
}

function formatPeriod(p) {
  const [y, m] = p.split("-");
  return new Date(+y, +m - 1, 1).toLocaleString(undefined, { month: "long", year: "numeric" });
}

$("#monthSelect").addEventListener("change", async (e) => {
  state.selected = e.target.value;
  await loadReport();
});

$("#newMonthBtn").addEventListener("click", () => {
  $("#pdfInput").click();
});

// ---------- Upload ----------
$("#uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = $("#pdfInput").files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append("file", file);
  const period = $("#periodInput").value;
  const url = period ? `/api/upload?period=${period}` : "/api/upload";
  $("#uploadStatus").textContent = "Parsing…";
  try {
    const result = await fetch(API + url, { method: "POST", body: fd }).then(async (r) => {
      if (!r.ok) throw new Error((await r.json()).detail || r.statusText);
      return r.json();
    });
    $("#uploadStatus").textContent = `✓ ${formatPeriod(result.period)}: ${result.transaction_count} transactions, ${fmt(result.statement_total)}`;
    $("#pdfInput").value = "";
    $("#periodInput").value = "";
    await loadMonths(result.period);
  } catch (err) {
    $("#uploadStatus").textContent = "✗ " + err.message;
  }
});

// ---------- Report (dashboard) ----------
async function loadReport() {
  if (!state.selected) return;
  const r = await api(`/api/months/${state.selected}`);
  state.report = r;
  renderDashboard(r);
}

function renderEmpty() {
  $("#kpiTotal").textContent = "—";
  $("#kpiCount").textContent = "—";
  $("#kpiNet").textContent = "—";
  $("#kpiTopCat").textContent = "—";
  $("#recommendations").innerHTML = '<div class="empty">Upload an Amex PDF to see your report.</div>';
  $("#merchantTable tbody").innerHTML = "";
  $("#recurringTable tbody").innerHTML = "";
  $("#budgetBars").innerHTML = "";
  if (charts.cat) { charts.cat.destroy(); charts.cat = null; }
}

function renderDashboard(r) {
  $("#kpiTotal").textContent = fmt(r.total_spend);
  $("#kpiCount").textContent = r.transaction_count;
  $("#kpiNet").textContent = fmt(r.net);
  const top = r.by_category[0];
  $("#kpiTopCat").textContent = top ? `${top.category} — ${fmt(top.total)}` : "—";

  // Category chart
  const ctx = document.getElementById("categoryChart");
  if (charts.cat) charts.cat.destroy();
  charts.cat = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: r.by_category.map((c) => c.category),
      datasets: [{
        data: r.by_category.map((c) => c.total),
        backgroundColor: ["#6ee7b7", "#60a5fa", "#fbbf24", "#f87171", "#a78bfa", "#f472b6", "#34d399", "#fb923c", "#22d3ee", "#94a3b8", "#facc15", "#e879f9", "#4ade80", "#fcd34d"],
        borderColor: "#0f1115", borderWidth: 2,
      }],
    },
    options: {
      plugins: { legend: { position: "right", labels: { color: "#e7eaf0", boxWidth: 12 } } },
      responsive: true,
    },
  });

  // Top merchants
  const tb = $("#merchantTable tbody");
  tb.innerHTML = "";
  r.top_merchants.forEach((m) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${escapeHtml(m.merchant)}</td><td>${m.category}</td><td>${m.count}</td><td class="r">${fmt(m.total)}</td>`;
    tb.appendChild(row);
  });
  if (r.top_merchants.length === 0) tb.innerHTML = '<tr><td colspan="4" class="empty">No charges yet.</td></tr>';

  // Recommendations
  const rec = $("#recommendations");
  rec.innerHTML = "";
  if (r.recommendations.length === 0) {
    rec.innerHTML = '<div class="empty">No specific cuts found — your spending looks balanced this month.</div>';
  } else {
    r.recommendations.forEach((x) => {
      const div = document.createElement("div");
      div.className = "rec";
      div.innerHTML = `
        <div class="save">${fmt(x.estimated_monthly_savings)}</div>
        <div class="body">
          <div class="title">${escapeHtml(x.title)}<span class="pill">${x.category}</span></div>
          <div class="detail">${escapeHtml(x.detail)}</div>
        </div>`;
      rec.appendChild(div);
    });
  }

  // Recurring
  const rt = $("#recurringTable tbody");
  rt.innerHTML = "";
  r.recurring_charges.forEach((m) => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${escapeHtml(m.merchant)}</td><td>${m.category}</td><td>${m.months_seen}</td><td class="r">${fmt(m.amount)}</td>`;
    rt.appendChild(row);
  });
  if (r.recurring_charges.length === 0) rt.innerHTML = '<tr><td colspan="4" class="empty">Need 2+ months of data to detect recurring charges.</td></tr>';

  // Budget status
  const bb = $("#budgetBars");
  bb.innerHTML = "";
  if (r.budget_status.length === 0) {
    bb.innerHTML = '<div class="empty">No budgets set yet — try the Budget tab.</div>';
  } else {
    r.budget_status.forEach((b) => {
      const pct = Math.min(b.pct_used, 100);
      const cls = b.pct_used > 100 ? "over" : b.pct_used > 85 ? "warn" : "";
      const div = document.createElement("div");
      div.className = "budget-row";
      div.innerHTML = `
        <div>${b.category}</div>
        <div class="bar-wrap"><div class="bar ${cls}" style="width:${pct}%"></div></div>
        <div class="pct">${fmt(b.spent)} / ${fmt(b.limit)} (${b.pct_used}%)</div>`;
      bb.appendChild(div);
    });
  }
}

// ---------- Transactions ----------
async function loadTransactions() {
  if (!state.selected) {
    $("#txnTable tbody").innerHTML = '<tr><td colspan="4" class="empty">No month selected.</td></tr>';
    return;
  }
  const [txns, b] = await Promise.all([
    api(`/api/months/${state.selected}/transactions`),
    api("/api/budgets"),
  ]);
  state.categories = b.categories;
  const tb = $("#txnTable tbody");
  tb.innerHTML = "";
  txns.forEach((t) => {
    const row = document.createElement("tr");
    const opts = b.categories.map((c) => `<option value="${c}" ${c === t.category ? "selected" : ""}>${c}</option>`).join("");
    row.innerHTML = `
      <td>${t.txn_date}</td>
      <td>${escapeHtml(t.merchant)}</td>
      <td><select class="cat-select" data-id="${t.id}">${opts}</select></td>
      <td class="r" style="color:${t.amount < 0 ? '#6ee7b7' : 'inherit'}">${fmt(t.amount)}</td>`;
    tb.appendChild(row);
  });
  $$(".cat-select").forEach((s) => {
    s.addEventListener("change", async (e) => {
      const id = +e.target.dataset.id;
      await api(`/api/transactions/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ category: e.target.value }),
      });
      await loadReport(); // refresh dashboard totals
    });
  });
}

// ---------- Budget editor ----------
async function loadBudgetEditor() {
  const [b, proj] = await Promise.all([
    api("/api/budgets"),
    api("/api/budgets/projection"),
  ]);
  state.budgets = b.budgets;
  state.categories = b.categories;
  const projMap = Object.fromEntries(proj.projections.map((p) => [p.category, p]));
  const ed = $("#budgetEditor");
  ed.innerHTML = "";
  b.categories.forEach((cat) => {
    const cur = b.budgets[cat] ?? "";
    const p = projMap[cat];
    const suggested = p ? p.suggested_budget : null;
    const row = document.createElement("div");
    row.className = "budget-row";
    row.style.gridTemplateColumns = "150px 130px 1fr";
    row.innerHTML = `
      <div>${cat}</div>
      <div><input type="number" min="0" step="10" data-cat="${cat}" value="${cur}" placeholder="0"/></div>
      <div class="hint">${p ? `3-mo avg ${fmt(p.trailing_avg)} · suggested ${fmt(suggested)}` : "no history yet"}
        ${suggested ? `<button class="btn-secondary apply-suggest" data-cat="${cat}" data-val="${suggested}" style="margin-left:8px;padding:2px 8px;font-size:11px;">use</button>` : ""}
      </div>`;
    ed.appendChild(row);
  });
  $$(".apply-suggest").forEach((btn) => {
    btn.addEventListener("click", () => {
      const inp = ed.querySelector(`input[data-cat="${btn.dataset.cat}"]`);
      inp.value = btn.dataset.val;
    });
  });
}

$("#saveBudgets").addEventListener("click", async () => {
  const inputs = $("#budgetEditor").querySelectorAll("input[data-cat]");
  const budgets = [];
  inputs.forEach((i) => {
    const v = parseFloat(i.value);
    if (!isNaN(v) && v > 0) budgets.push({ category: i.dataset.cat, monthly_limit: v });
  });
  $("#budgetStatus").textContent = "Saving…";
  try {
    await api("/api/budgets", { method: "PUT", body: JSON.stringify({ budgets }) });
    $("#budgetStatus").textContent = "✓ Saved";
    if (state.selected) await loadReport();
  } catch (e) {
    $("#budgetStatus").textContent = "✗ " + e.message;
  }
});

// ---------- Trend ----------
async function loadTrend() {
  const t = await api("/api/trend");
  const ctx1 = document.getElementById("trendChart");
  if (charts.trend) charts.trend.destroy();
  charts.trend = new Chart(ctx1, {
    type: "bar",
    data: {
      labels: t.periods.map(formatPeriod),
      datasets: [{ label: "Total spend", data: t.totals, backgroundColor: "#60a5fa" }],
    },
    options: {
      plugins: { legend: { labels: { color: "#e7eaf0" } } },
      scales: {
        x: { ticks: { color: "#8b94a3" }, grid: { color: "#2a313d" } },
        y: { ticks: { color: "#8b94a3" }, grid: { color: "#2a313d" } },
      },
    },
  });

  const ctx2 = document.getElementById("categoryTrendChart");
  if (charts.catTrend) charts.catTrend.destroy();
  const palette = ["#6ee7b7", "#60a5fa", "#fbbf24", "#f87171", "#a78bfa", "#f472b6", "#34d399", "#fb923c", "#22d3ee", "#94a3b8", "#facc15", "#e879f9", "#4ade80", "#fcd34d"];
  charts.catTrend = new Chart(ctx2, {
    type: "line",
    data: {
      labels: t.periods.map(formatPeriod),
      datasets: t.series.map((s, i) => ({
        label: s.category, data: s.values,
        borderColor: palette[i % palette.length],
        backgroundColor: palette[i % palette.length] + "33",
        tension: 0.3, fill: false,
      })),
    },
    options: {
      plugins: { legend: { labels: { color: "#e7eaf0" } } },
      scales: {
        x: { ticks: { color: "#8b94a3" }, grid: { color: "#2a313d" } },
        y: { ticks: { color: "#8b94a3" }, grid: { color: "#2a313d" } },
      },
    },
  });
}

// ---------- Helpers ----------
function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}

// ---------- Boot ----------
loadMonths();
