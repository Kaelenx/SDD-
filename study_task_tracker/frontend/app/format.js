export const priorityLabel = {
  high: "高",
  medium: "中",
  low: "低",
};

export function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[char]);
}

export function isOverdue(task) {
  const today = new Date().toISOString().slice(0, 10);
  return task.status === "pending" && task.due_date < today;
}
