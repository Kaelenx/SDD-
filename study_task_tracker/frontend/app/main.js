import { api, downloadJson } from "./api.js";
import { refs } from "./dom.js";
import { enterEditMode, resetFormMode, taskPayloadFromForm } from "./form.js";
import { renderCourseStats, renderTasks, updateSelectionBar, updateSummary } from "./render.js";
import { state } from "./state.js";

function setMessage(text, isError = false) {
  refs.message.textContent = text;
  refs.message.classList.toggle("error", isError);
}

function buildTaskQuery() {
  const params = new URLSearchParams();
  if (state.status) {
    params.set("status", state.status);
  }
  if (state.priority) {
    params.set("priority", state.priority);
  }
  if (state.query) {
    params.set("q", state.query);
  }
  const query = params.toString();
  return query ? `?${query}` : "";
}

async function refreshSummary() {
  updateSummary(await api("/api/summary"));
}

async function refreshCourseStats() {
  renderCourseStats(await api("/api/courses"));
}

async function refreshTasks() {
  const tasks = await api(`/api/tasks${buildTaskQuery()}`);
  state.tasks = tasks;
  renderTasks(tasks);
  await refreshSummary();
  await refreshCourseStats();
}

refs.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = taskPayloadFromForm(new FormData(refs.form));
  try {
    if (state.editingId) {
      const task = await api(`/api/tasks/${encodeURIComponent(state.editingId)}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
      resetFormMode();
      setMessage(`已保存 ${task.id}`);
    } else {
      const task = await api("/api/tasks", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      resetFormMode();
      setMessage(`已新增 ${task.id}`);
    }
    await refreshTasks();
  } catch (error) {
    setMessage(error.message, true);
  }
});

refs.cancelEditButton.addEventListener("click", () => {
  resetFormMode();
  setMessage("已取消编辑");
});

refs.filters.forEach((button) => {
  button.addEventListener("click", async () => {
    refs.filters.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    state.status = button.dataset.status;
    await refreshTasks();
  });
});

refs.priorityFilter.addEventListener("change", async () => {
  state.priority = refs.priorityFilter.value;
  await refreshTasks();
});

refs.searchInput.addEventListener("input", async () => {
  state.query = refs.searchInput.value.trim();
  await refreshTasks();
});

refs.bulkCompleteButton.addEventListener("click", async () => {
  if (state.selectedIds.size === 0) {
    return;
  }
  try {
    const completed = await api("/api/tasks/bulk-complete", {
      method: "PATCH",
      body: JSON.stringify({ task_ids: [...state.selectedIds] }),
    });
    state.selectedIds.clear();
    setMessage(`已批量完成 ${completed.length} 项`);
    await refreshTasks();
  } catch (error) {
    setMessage(error.message, true);
  }
});

refs.exportButton.addEventListener("click", async () => {
  try {
    downloadJson("study-task-export.json", await api("/api/export"));
    setMessage("已导出 JSON");
  } catch (error) {
    setMessage(error.message, true);
  }
});

refs.taskList.addEventListener("change", (event) => {
  const checkbox = event.target.closest(".select-task");
  if (!checkbox) {
    return;
  }
  if (checkbox.checked) {
    state.selectedIds.add(checkbox.dataset.id);
  } else {
    state.selectedIds.delete(checkbox.dataset.id);
  }
  updateSelectionBar();
});

refs.taskList.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) {
    return;
  }
  const { action, id } = button.dataset;
  const task = state.tasks.find((item) => item.id === id);
  try {
    if (action === "edit" && task) {
      enterEditMode(task);
      setMessage(`正在编辑 ${id}`);
      return;
    }
    if (action === "complete") {
      await api(`/api/tasks/${encodeURIComponent(id)}/complete`, { method: "PATCH" });
      if (state.editingId === id) {
        resetFormMode();
      }
      setMessage(`已完成 ${id}`);
    }
    if (action === "delete") {
      await api(`/api/tasks/${encodeURIComponent(id)}`, { method: "DELETE" });
      if (state.editingId === id) {
        resetFormMode();
      }
      setMessage(`已删除 ${id}`);
    }
    await refreshTasks();
  } catch (error) {
    setMessage(error.message, true);
  }
});

refreshTasks().catch((error) => setMessage(error.message, true));
