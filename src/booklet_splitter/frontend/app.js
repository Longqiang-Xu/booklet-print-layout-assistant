const state = {
  pdfPath: "",
  pdfName: "",
  pageCount: 0,
  totalSheets: 0,
  outputDir: "",
  splitMode: "max_sheets",
  maxSheets: 14,
  bookletCount: 1,
  planOptions: [],
  isGenerating: false,
  result: null,
  error: "",
};

const el = {
  selectPdfButton: document.getElementById("selectPdfButton"),
  selectOutputButton: document.getElementById("selectOutputButton"),
  generateButton: document.getElementById("generateButton"),
  openOutputButton: document.getElementById("openOutputButton"),
  statusText: document.getElementById("statusText"),
  pdfName: document.getElementById("pdfName"),
  pdfPath: document.getElementById("pdfPath"),
  pageCount: document.getElementById("pageCount"),
  sheetCount: document.getElementById("sheetCount"),
  outputDir: document.getElementById("outputDir"),
  modeMaxSheets: document.getElementById("modeMaxSheets"),
  modeFixedCount: document.getElementById("modeFixedCount"),
  maxSheetsInput: document.getElementById("maxSheetsInput"),
  bookletCountInput: document.getElementById("bookletCountInput"),
  planTableBody: document.getElementById("planTableBody"),
  planHint: document.getElementById("planHint"),
  resultPanel: document.getElementById("resultPanel"),
  resultSummary: document.getElementById("resultSummary"),
  resultList: document.getElementById("resultList"),
};

function apiReady() {
  return Boolean(window.pywebview && window.pywebview.api);
}

function setState(patch) {
  Object.assign(state, patch);
  render();
}

function render() {
  el.statusText.textContent = state.error || (state.pdfPath ? "已读取 PDF" : "选择一个 PDF 开始");
  el.statusText.className = state.error ? "error" : "";
  el.pdfName.textContent = state.pdfName || "未选择";
  el.pdfPath.textContent = state.pdfPath;
  el.pageCount.textContent = state.pageCount || "-";
  el.sheetCount.textContent = state.totalSheets || "-";
  el.outputDir.textContent = state.outputDir || "未选择";
  el.modeMaxSheets.checked = state.splitMode === "max_sheets";
  el.modeFixedCount.checked = state.splitMode === "fixed_count";
  el.maxSheetsInput.value = state.maxSheets;
  el.bookletCountInput.value = state.bookletCount;
  el.generateButton.disabled = !state.pdfPath || state.isGenerating;
  el.generateButton.textContent = state.isGenerating ? "生成中..." : "生成分册 PDF";
  el.planHint.textContent = state.planOptions.length ? "点击一行可按该册数生成" : "";

  renderPlanTable();
  renderResult();
}

function renderPlanTable() {
  if (!state.planOptions.length) {
    el.planTableBody.innerHTML = '<tr><td colspan="5" class="empty">选择 PDF 后显示方案</td></tr>';
    return;
  }

  el.planTableBody.innerHTML = "";
  for (const option of state.planOptions) {
    const row = document.createElement("tr");
    row.className = "option-row";
    if (state.splitMode === "fixed_count" && Number(state.bookletCount) === option.booklet_count) {
      row.classList.add("selected");
    }
    row.innerHTML = `
      <td>${option.booklet_count}</td>
      <td>${option.sheet_counts.join(" / ")}</td>
      <td>${option.ranges.join("<br>")}</td>
      <td>${option.blank_count}</td>
      <td>${option.is_recommended ? '<span class="badge">推荐</span>' : ""}</td>
    `;
    row.addEventListener("click", () => {
      setState({ splitMode: "fixed_count", bookletCount: option.booklet_count, error: "" });
    });
    el.planTableBody.appendChild(row);
  }
}

function renderResult() {
  if (!state.result) {
    el.resultPanel.classList.add("hidden");
    return;
  }

  el.resultPanel.classList.remove("hidden");
  el.resultSummary.textContent = `已生成 ${state.result.booklet_count} 个分册 PDF。清单：${state.result.manifest_path}`;
  el.resultList.innerHTML = "";
  for (const booklet of state.result.booklets) {
    const item = document.createElement("li");
    item.textContent = `${booklet.file_name} | 第 ${booklet.start_page}-${booklet.end_page} 页 | ${booklet.sheet_count} 张纸 | 补 ${booklet.blank_count} 页`;
    el.resultList.appendChild(item);
  }
}

async function selectPdf() {
  if (!apiReady()) {
    setState({ error: "桌面 API 尚未就绪" });
    return;
  }
  const response = await window.pywebview.api.select_pdf();
  if (!response.ok) {
    setState({ error: response.error });
    return;
  }
  if (response.data.cancelled) {
    return;
  }
  applyPdfAnalysis(response.data);
}

function applyPdfAnalysis(data) {
  setState({
    pdfPath: data.pdf_path,
    pdfName: data.pdf_name,
    pageCount: data.page_count,
    totalSheets: data.total_sheets,
    outputDir: data.default_output_dir,
    planOptions: data.plan_options,
    bookletCount: data.plan_options.find((option) => option.is_recommended)?.booklet_count || 1,
    splitMode: "max_sheets",
    result: null,
    error: "",
  });
}

async function refreshPlanOptions() {
  if (!state.pdfPath || !apiReady()) {
    return;
  }
  const response = await window.pywebview.api.get_plan_options(state.pdfPath, Number(state.maxSheets), 10, 17);
  if (!response.ok) {
    setState({ error: response.error });
    return;
  }
  setState({ planOptions: response.data.plan_options, error: "" });
}

async function selectOutputDir() {
  if (!apiReady()) {
    setState({ error: "桌面 API 尚未就绪" });
    return;
  }
  const response = await window.pywebview.api.select_output_dir(state.outputDir || null);
  if (!response.ok) {
    setState({ error: response.error });
    return;
  }
  if (!response.data.cancelled) {
    setState({ outputDir: response.data.path, error: "" });
  }
}

async function generate() {
  if (!state.pdfPath || !apiReady()) {
    return;
  }

  setState({ isGenerating: true, result: null, error: "" });
  const response = await window.pywebview.api.split_pdf({
    input_pdf: state.pdfPath,
    output_dir: state.outputDir,
    mode: state.splitMode,
    max_sheets: Number(state.maxSheets),
    booklet_count: Number(state.bookletCount),
  });
  if (!response.ok) {
    setState({ isGenerating: false, error: response.error });
    return;
  }
  setState({ isGenerating: false, result: response.data, error: "" });
}

async function openOutputFolder() {
  if (!state.result || !apiReady()) {
    return;
  }
  const response = await window.pywebview.api.open_output_folder(state.result.output_dir);
  if (!response.ok) {
    setState({ error: response.error });
  }
}

function bindEvents() {
  el.selectPdfButton.addEventListener("click", selectPdf);
  el.selectOutputButton.addEventListener("click", selectOutputDir);
  el.generateButton.addEventListener("click", generate);
  el.openOutputButton.addEventListener("click", openOutputFolder);
  el.modeMaxSheets.addEventListener("change", () => setState({ splitMode: "max_sheets", error: "" }));
  el.modeFixedCount.addEventListener("change", () => setState({ splitMode: "fixed_count", error: "" }));
  el.maxSheetsInput.addEventListener("change", async () => {
    const value = Math.max(1, Number(el.maxSheetsInput.value || 14));
    setState({ maxSheets: value, error: "" });
    await refreshPlanOptions();
  });
  el.bookletCountInput.addEventListener("change", () => {
    const value = Math.max(1, Number(el.bookletCountInput.value || 1));
    setState({ bookletCount: value, error: "" });
  });
}

bindEvents();
render();
