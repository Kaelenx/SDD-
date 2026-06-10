import { refs } from "./dom.js";
import { escapeHtml, isOverdue, priorityLabel } from "./format.js";
import { state } from "./state.js";

export function renderTasks(tasks) {
  if (tasks.length === 0) {
    refs.taskList.innerHTML = '<div class="empty-state">暂无匹配任务</div>';
    updateSelectionBar();
    return;
  }

  refs.taskList.innerHTML = tasks.map((task) => taskCardTemplate(task)).join("");
  updateSelectionBar();
}

export function renderCourseStats(courses) {
  if (courses.length === 0) {
    refs.courseStats.innerHTML = '<div class="empty-state">暂无课程数据</div>';
    return;
  }
  refs.courseStats.innerHTML = courses.map((course) => `
    <div class="course-row">
      <strong>${escapeHtml(course.course)}</strong>
      <span>${course.total} 项 / 待完成 ${course.pending} / 已完成 ${course.done}</span>
      <span>逾期 ${course.overdue} / 剩余 ${course.remaining_estimated_hours} 小时</span>
    </div>
  `).join("");
}

export function updateSummary(summary) {
  refs.summaryTotal.textContent = summary.total;
  refs.summaryPending.textContent = summary.pending;
  refs.summaryDone.textContent = summary.done;
  refs.summaryOverdue.textContent = summary.overdue;
  refs.summaryHours.textContent = summary.remaining_estimated_hours;
  updateProgress(summary);
}

export function updateSelectionBar() {
  const visibleIds = new Set(state.tasks.map((task) => task.id));
  state.selectedIds = new Set([...state.selectedIds].filter((id) => visibleIds.has(id)));
  refs.selectionCount.textContent = `已选择 ${state.selectedIds.size} 项`;
  refs.bulkCompleteButton.disabled = state.selectedIds.size === 0;
}

function updateProgress(summary) {
  const rate = summary.total === 0 ? 0 : Math.round((summary.done / summary.total) * 100);
  refs.completionRate.textContent = `${rate}%`;
  refs.completionBar.style.width = `${rate}%`;
}

function taskCardTemplate(task) {
  const overdue = isOverdue(task);
  const classes = ["task-card", task.status === "done" ? "done" : "", overdue ? "overdue" : ""]
    .filter(Boolean)
    .join(" ");
  const checked = state.selectedIds.has(task.id) ? "checked" : "";
  const doneButton = task.status === "pending"
    ? `<button type="button" class="task-action" data-action="complete" data-id="${escapeHtml(task.id)}">完成</button>`
    : "";
  const notes = task.notes ? `<p class="task-notes">${escapeHtml(task.notes)}</p>` : "";

  return `
    <article class="${classes}">
      <input class="select-task" type="checkbox" data-id="${escapeHtml(task.id)}" ${checked} aria-label="选择 ${escapeHtml(task.id)}" />
      <div>
        <p class="task-title">${escapeHtml(task.title)}</p>
        <div class="task-meta">
          <span class="pill">${escapeHtml(task.id)}</span>
          <span class="pill">${task.status === "done" ? "已完成" : "待完成"}</span>
          <span class="pill ${escapeHtml(task.priority)}">优先级 ${priorityLabel[task.priority]}</span>
          <span class="pill">${escapeHtml(task.estimated_hours)} 小时</span>
          <span class="pill">截止 ${escapeHtml(task.due_date)}</span>
          <span class="pill">${escapeHtml(task.course)}</span>
          ${overdue ? '<span class="pill high">逾期</span>' : ""}
        </div>
        ${notes}
      </div>
      <div class="task-actions">
        <button type="button" class="task-action" data-action="edit" data-id="${escapeHtml(task.id)}">编辑</button>
        ${doneButton}
        <button type="button" class="task-action danger" data-action="delete" data-id="${escapeHtml(task.id)}">删除</button>
      </div>
    </article>
  `;
}
