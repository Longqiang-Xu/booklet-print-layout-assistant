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
  selectedPages: [],
  draftSelectedPages: [],
  pageRangeText: "",
  modalRangeText: "",
  isPageSelectorOpen: false,
  isGenerating: false,
  result: null,
  error: "",
};

const el = {
  selectPdfButton: document.getElementById("selectPdfButton"),
  selectOutputButton: document.getElementById("selectOutputButton"),
  generateButton: document.getElementById("generateButton"),
  openOutputButton: document.getElementById("openOutputButton"),
  openPageSelectorButton: document.getElementById("openPageSelectorButton"),
  applyRangeButton: document.getElementById("applyRangeButton"),
  resetPagesButton: document.getElementById("resetPagesButton"),
  closePageSelectorButton: document.getElementById("closePageSelectorButton"),
  cancelPageSelectorButton: document.getElementById("cancelPageSelectorButton"),
  confirmPageSelectorButton: document.getElementById("confirmPageSelectorButton"),
  selectAllPagesButton: document.getElementById("selectAllPagesButton"),
  clearPagesButton: document.getElementById("clearPagesButton"),
  invertPagesButton: document.getElementById("invertPagesButton"),
  applyModalRangeButton: document.getElementById("applyModalRangeButton"),
  statusText: document.getElementById("statusText"),
  pdfName: document.getElementById("pdfName"),
  pdfPath: document.getElementById("pdfPath"),
  pageCount: document.getElementById("pageCount"),
  sheetCount: document.getElementById("sheetCount"),
  pageSelectionSummary: document.getElementById("pageSelectionSummary"),
  pageRangeInput: document.getElementById("pageRangeInput"),
  modalRangeInput: document.getElementById("modalRangeInput"),
  outputDir: document.getElementById("outputDir"),
  modeMaxSheets: document.getElementById("modeMaxSheets"),
  modeFixedCount: document.getElementById("modeFixedCount"),
  maxSheetsInput: document.getElementById("maxSheetsInput"),
  bookletCountInput: document.getElementById("bookletCountInput"),
  planTableBody: document.getElementById("planTableBody"),
  planHint: document.getElementById("planHint"),
  pageSelectorModal: document.getElementById("pageSelectorModal"),
  pageGrid: document.getElementById("pageGrid"),
  pageSelectorDraftSummary: document.getElementById("pageSelectorDraftSummary"),
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

function allPageNumbers(total) {
  return Array.from({ length: total }, (_, index) => index + 1);
}

function selectedPageCount() {
  return state.selectedPages.length;
}

function totalSheetsForPages(pageCount) {
  return pageCount ? Math.ceil(pageCount / 4) : 0;
}

function isAllPagesSelected() {
  return state.pageCount > 0 && selectedPageCount() === state.pageCount;
}

function normalizeSelectedPages(pages, total) {
  const normalized = [...new Set(pages.map((page) => Number(page)))].sort((a, b) => a - b);
  if (!normalized.length) {
    throw new Error("请至少选择 1 页");
  }
  for (const page of normalized) {
    if (!Number.isInteger(page) || page < 1 || page > total) {
      throw new Error(`页码 ${page} 超出范围 1-${total}`);
    }
  }
  return normalized;
}

function parsePageSelection(text, total) {
  const value = String(text || "").trim();
  if (!value || ["*", "all", "全部", "全选"].includes(value.toLowerCase())) {
    return allPageNumbers(total);
  }

  const parts = value
    .replace(/，/g, ",")
    .replace(/、/g, ",")
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
  if (!parts.length) {
    return allPageNumbers(total);
  }

  const excludeMode = parts[0].startsWith("-");
  const selected = new Set(excludeMode ? allPageNumbers(total) : []);

  for (let part of parts) {
    const isRemoval = excludeMode || part.startsWith("-");
    if (part.startsWith("-")) {
      part = part.slice(1).trim();
    }
    if (!part) {
      throw new Error("页码范围不能为空");
    }

    const match = part.match(/^(\d+)(?:\s*-\s*(\d+))?$/);
    if (!match) {
      throw new Error(`无法识别页码范围：${part}`);
    }
    const start = Number(match[1]);
    const end = Number(match[2] || match[1]);
    if (start > end) {
      throw new Error(`页码范围起点不能大于终点：${part}`);
    }
    if (start < 1 || end > total) {
      throw new Error(`页码 ${end} 超出范围 1-${total}`);
    }

    for (let page = start; page <= end; page += 1) {
      if (isRemoval) {
        selected.delete(page);
      } else {
        selected.add(page);
      }
    }
  }

  return normalizeSelectedPages([...selected], total);
}

function selectionSummary() {
  if (!state.pageCount) {
    return "选择 PDF 后可筛选页面";
  }
  if (isAllPagesSelected()) {
    return `已选择全部 ${state.pageCount} 页，约 ${state.totalSheets} 张纸`;
  }
  return `已选择 ${selectedPageCount()} / ${state.pageCount} 页，约 ${state.totalSheets} 张纸`;
}

function draftSelectionSummary() {
  if (!state.pageCount) {
    return "";
  }
  return `已选择 ${state.draftSelectedPages.length} / ${state.pageCount} 页`;
}

function render() {
  const hasPdf = Boolean(state.pdfPath);
  const hasSelectedPages = selectedPageCount() > 0;

  el.statusText.textContent = state.error || (state.pdfPath ? "已读取 PDF" : "选择一个 PDF 开始");
  el.statusText.className = state.error ? "error" : "";
  el.pdfName.textContent = state.pdfName || "未选择";
  el.pdfPath.textContent = state.pdfPath;
  el.pageCount.textContent = state.pageCount || "-";
  el.sheetCount.textContent = hasSelectedPages ? state.totalSheets : "-";
  el.pageSelectionSummary.textContent = selectionSummary();
  el.outputDir.textContent = state.outputDir || "未选择";
  el.modeMaxSheets.checked = state.splitMode === "max_sheets";
  el.modeFixedCount.checked = state.splitMode === "fixed_count";
  el.maxSheetsInput.value = state.maxSheets;
  el.bookletCountInput.value = state.bookletCount;
  el.generateButton.disabled = !state.pdfPath || !hasSelectedPages || state.isGenerating;
  el.generateButton.textContent = state.isGenerating ? "生成中..." : "生成分册 PDF";
  el.openPageSelectorButton.disabled = !hasPdf;
  el.pageRangeInput.disabled = !hasPdf;
  el.applyRangeButton.disabled = !hasPdf;
  el.resetPagesButton.disabled = !hasPdf;
  el.planHint.textContent = state.planOptions.length ? "点击一行可按该册数生成" : "";

  if (document.activeElement !== el.pageRangeInput) {
    el.pageRangeInput.value = state.pageRangeText;
  }
  if (document.activeElement !== el.modalRangeInput) {
    el.modalRangeInput.value = state.modalRangeText;
  }

  renderPlanTable();
  renderPageSelectorModal();
  renderResult();
}

function renderPlanTable() {
  if (!state.pdfPath) {
    el.planTableBody.innerHTML = '<tr><td colspan="5" class="empty">选择 PDF 后显示方案</td></tr>';
    return;
  }
  if (!selectedPageCount()) {
    el.planTableBody.innerHTML = '<tr><td colspan="5" class="empty">请至少选择 1 页</td></tr>';
    return;
  }
  if (!state.planOptions.length) {
    el.planTableBody.innerHTML = '<tr><td colspan="5" class="empty">页面选择后显示方案</td></tr>';
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

function renderPageSelectorModal() {
  el.pageSelectorModal.classList.toggle("hidden", !state.isPageSelectorOpen);
  el.pageSelectorModal.setAttribute("aria-hidden", state.isPageSelectorOpen ? "false" : "true");
  if (!state.isPageSelectorOpen) {
    return;
  }

  el.pageSelectorDraftSummary.textContent = draftSelectionSummary();
  el.confirmPageSelectorButton.disabled = state.draftSelectedPages.length === 0;
  renderPageGrid();
}

function renderPageGrid() {
  const selected = new Set(state.draftSelectedPages);
  const fragment = document.createDocumentFragment();
  for (let page = 1; page <= state.pageCount; page += 1) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `page-cell${selected.has(page) ? " selected" : ""}`;
    button.textContent = String(page);
    button.setAttribute("aria-pressed", selected.has(page) ? "true" : "false");
    button.addEventListener("click", () => toggleDraftPage(page));
    fragment.appendChild(button);
  }
  el.pageGrid.replaceChildren(fragment);
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

async function refreshPlanOptions() {
  const pageCount = selectedPageCount();
  if (!pageCount) {
    setState({ planOptions: [], totalSheets: 0 });
    return;
  }
  if (!apiReady()) {
    return;
  }

  const response = await window.pywebview.api.get_plan_options_for_page_count(
    pageCount,
    Number(state.maxSheets),
    10,
    17,
  );
  if (!response.ok) {
    setState({ error: response.error });
    return;
  }

  const options = response.data.plan_options;
  const recommendedCount = options.find((option) => option.is_recommended)?.booklet_count || 1;
  const maxBookletCount = Math.max(1, response.data.total_sheets || 1);
  const fixedCount = Math.min(Math.max(1, Number(state.bookletCount) || 1), maxBookletCount);
  setState({
    planOptions: options,
    totalSheets: response.data.total_sheets,
    bookletCount: state.splitMode === "fixed_count" ? fixedCount : recommendedCount,
    error: "",
  });
}

async function updateSelectedPages(pages) {
  const selectedPages = normalizeSelectedPages(pages, state.pageCount);
  setState({
    selectedPages,
    totalSheets: totalSheetsForPages(selectedPages.length),
    result: null,
    error: "",
  });
  await refreshPlanOptions();
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
  const selectedPages = allPageNumbers(data.page_count);
  setState({
    pdfPath: data.pdf_path,
    pdfName: data.pdf_name,
    pageCount: data.page_count,
    totalSheets: data.total_sheets,
    outputDir: data.default_output_dir,
    selectedPages,
    draftSelectedPages: selectedPages,
    pageRangeText: "",
    modalRangeText: "",
    planOptions: data.plan_options,
    bookletCount: data.plan_options.find((option) => option.is_recommended)?.booklet_count || 1,
    splitMode: "max_sheets",
    result: null,
    error: "",
    isPageSelectorOpen: false,
  });
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

async function applyMainRangeSelection() {
  try {
    const text = el.pageRangeInput.value;
    const pages = parsePageSelection(text, state.pageCount);
    state.pageRangeText = text.trim();
    await updateSelectedPages(pages);
  } catch (error) {
    setState({ error: error.message });
  }
}

async function resetPageSelection() {
  state.pageRangeText = "";
  await updateSelectedPages(allPageNumbers(state.pageCount));
}

function openPageSelector() {
  if (!state.pageCount) {
    return;
  }
  setState({
    draftSelectedPages: [...state.selectedPages],
    modalRangeText: "",
    isPageSelectorOpen: true,
    error: "",
  });
}

function closePageSelector() {
  setState({ isPageSelectorOpen: false, modalRangeText: "" });
}

function toggleDraftPage(page) {
  const selected = new Set(state.draftSelectedPages);
  if (selected.has(page)) {
    selected.delete(page);
  } else {
    selected.add(page);
  }
  setState({ draftSelectedPages: [...selected].sort((a, b) => a - b), error: "" });
}

function selectAllDraftPages() {
  setState({ draftSelectedPages: allPageNumbers(state.pageCount), error: "" });
}

function clearDraftPages() {
  setState({ draftSelectedPages: [], error: "" });
}

function invertDraftPages() {
  const selected = new Set(state.draftSelectedPages);
  const inverted = allPageNumbers(state.pageCount).filter((page) => !selected.has(page));
  setState({ draftSelectedPages: inverted, error: "" });
}

function applyModalRangeSelection() {
  try {
    const text = el.modalRangeInput.value;
    const pages = parsePageSelection(text, state.pageCount);
    setState({ draftSelectedPages: pages, modalRangeText: text.trim(), error: "" });
  } catch (error) {
    setState({ error: error.message });
  }
}

async function confirmPageSelection() {
  if (!state.draftSelectedPages.length) {
    setState({ error: "请至少选择 1 页" });
    return;
  }
  const draftPages = [...state.draftSelectedPages];
  setState({ isPageSelectorOpen: false, modalRangeText: "" });
  await updateSelectedPages(draftPages);
}

async function generate() {
  if (!state.pdfPath || !selectedPageCount() || !apiReady()) {
    return;
  }

  setState({ isGenerating: true, result: null, error: "" });
  const payload = {
    input_pdf: state.pdfPath,
    output_dir: state.outputDir,
    mode: state.splitMode,
    max_sheets: Number(state.maxSheets),
    booklet_count: Number(state.bookletCount),
  };
  if (!isAllPagesSelected()) {
    payload.selected_pages = state.selectedPages;
  }

  const response = await window.pywebview.api.split_pdf(payload);
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
  el.openPageSelectorButton.addEventListener("click", openPageSelector);
  el.applyRangeButton.addEventListener("click", applyMainRangeSelection);
  el.resetPagesButton.addEventListener("click", resetPageSelection);
  el.closePageSelectorButton.addEventListener("click", closePageSelector);
  el.cancelPageSelectorButton.addEventListener("click", closePageSelector);
  el.confirmPageSelectorButton.addEventListener("click", confirmPageSelection);
  el.selectAllPagesButton.addEventListener("click", selectAllDraftPages);
  el.clearPagesButton.addEventListener("click", clearDraftPages);
  el.invertPagesButton.addEventListener("click", invertDraftPages);
  el.applyModalRangeButton.addEventListener("click", applyModalRangeSelection);
  el.pageRangeInput.addEventListener("input", () => {
    state.pageRangeText = el.pageRangeInput.value;
  });
  el.modalRangeInput.addEventListener("input", () => {
    state.modalRangeText = el.modalRangeInput.value;
  });
  el.pageSelectorModal.addEventListener("click", (event) => {
    if (event.target === el.pageSelectorModal) {
      closePageSelector();
    }
  });
  el.modeMaxSheets.addEventListener("change", async () => {
    setState({ splitMode: "max_sheets", error: "" });
    await refreshPlanOptions();
  });
  el.modeFixedCount.addEventListener("change", () => setState({ splitMode: "fixed_count", error: "" }));
  el.maxSheetsInput.addEventListener("change", async () => {
    const value = Math.max(1, Number(el.maxSheetsInput.value || 14));
    setState({ maxSheets: value, error: "" });
    await refreshPlanOptions();
  });
  el.bookletCountInput.addEventListener("change", () => {
    const maxBookletCount = Math.max(1, state.totalSheets || 1);
    const value = Math.min(maxBookletCount, Math.max(1, Number(el.bookletCountInput.value || 1)));
    setState({ bookletCount: value, error: "" });
  });
}

bindEvents();
render();
