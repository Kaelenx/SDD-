const state = {
  status: "",
  priority: "",
  query: "",
  tasks: [],
  editingId: "",
};

const taskList = document.querySelector("#task-list");
const form = document.querySelector("#task-form");
const message = document.querySelector("#form-message");
const filters = document.querySelectorAll(".filter");
const searchInput = document.querySelector("#search");
const priorityFilter = document.querySelector("#priority-filter");
const formTitle = document.querySelector("#form-title");
const editingIdInput = document.querySelector("#editing-id");
const submitButton = document.querySelector("#submit-button");
const cancelEditButton = document.querySelector("#cancel-edit");

const fields = {
  title: document.querySelector("#title"),
  course: document.querySelector("#course"),
  dueDate: document.querySelector("#due-date"),
  priority: document.querySelector("#priority"),
};

const priorityLabel = {
  high: "高",
  medium: "中",
  low: "低",
};

function api(path, options = {}) {
  return fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  }).then(async (response) => {
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "请求失败");
    }
    return payload;
  });
}

function setMessage(text, isError = false) {
  message.textContent = text;
  message.classList.toggle("error", isError);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[char]);
}

function isOverdue(task) {
  const today = new Date().toISOString().slice(0, 10);
  return task.status === "pending" && task.due_date < today;
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

function renderTasks(tasks) {
  if (tasks.length === 0) {
    taskList.innerHTML = '<div class="empty-state">暂无匹配任务</div>';
    return;
  }

  taskList.innerHTML = tasks.map((task) => {
    const overdue = isOverdue(task);
    const classes = ["task-card", task.status === "done" ? "done" : "", overdue ? "overdue" : ""]
      .filter(Boolean)
      .join(" ");
    const doneButton = task.status === "pending"
      ? `<button type="button" class="task-action" data-action="complete" data-id="${escapeHtml(task.id)}">完成</button>`
      : "";
    return `
      <article class="${classes}">
        <div>
          <p class="task-title">${escapeHtml(task.title)}</p>
          <div class="task-meta">
            <span class="pill">${escapeHtml(task.id)}</span>
            <span class="pill">${task.status === "done" ? "已完成" : "待完成"}</span>
            <span class="pill ${escapeHtml(task.priority)}">优先级 ${priorityLabel[task.priority]}</span>
            <span class="pill">截止 ${escapeHtml(task.due_date)}</span>
            <span class="pill">${escapeHtml(task.course)}</span>
            ${overdue ? '<span class="pill high">逾期</span>' : ""}
          </div>
        </div>
        <div class="task-actions">
          <button type="button" class="task-action" data-action="edit" data-id="${escapeHtml(task.id)}">编辑</button>
          ${doneButton}
          <button type="button" class="task-action danger" data-action="delete" data-id="${escapeHtml(task.id)}">删除</button>
        </div>
      </article>
    `;
  }).join("");
}

function updateProgress(summary) {
  const rate = summary.total === 0 ? 0 : Math.round((summary.done / summary.total) * 100);
  document.querySelector("#completion-rate").textContent = `${rate}%`;
  document.querySelector("#completion-bar").style.width = `${rate}%`;
}

async function refreshSummary() {
  const summary = await api("/api/summary");
  document.querySelector("#summary-total").textContent = summary.total;
  document.querySelector("#summary-pending").textContent = summary.pending;
  document.querySelector("#summary-done").textContent = summary.done;
  document.querySelector("#summary-overdue").textContent = summary.overdue;
  updateProgress(summary);
}

async function refreshTasks() {
  const tasks = await api(`/api/tasks${buildTaskQuery()}`);
  state.tasks = tasks;
  renderTasks(tasks);
  await refreshSummary();
}

function resetFormMode() {
  state.editingId = "";
  editingIdInput.value = "";
  formTitle.textContent = "新增任务";
  submitButton.textContent = "新增任务";
  cancelEditButton.classList.add("hidden");
  form.reset();
}

function enterEditMode(task) {
  state.editingId = task.id;
  editingIdInput.value = task.id;
  formTitle.textContent = `编辑 ${task.id}`;
  submitButton.textContent = "保存修改";
  cancelEditButton.classList.remove("hidden");
  fields.title.value = task.title;
  fields.course.value = task.course;
  fields.dueDate.value = task.due_date;
  fields.priority.value = task.priority;
  fields.title.focus();
}

function taskPayloadFromForm(formData) {
  return {
    title: formData.get("title"),
    course: formData.get("course"),
    due_date: formData.get("dueDate"),
    priority: formData.get("priority"),
  };
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const payload = taskPayloadFromForm(formData);
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

cancelEditButton.addEventListener("click", () => {
  resetFormMode();
  setMessage("已取消编辑");
});

filters.forEach((button) => {
  button.addEventListener("click", async () => {
    filters.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    state.status = button.dataset.status;
    await refreshTasks();
  });
});

priorityFilter.addEventListener("change", async () => {
  state.priority = priorityFilter.value;
  await refreshTasks();
});

searchInput.addEventListener("input", async () => {
  state.query = searchInput.value.trim();
  await refreshTasks();
});

taskList.addEventListener("click", async (event) => {
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
