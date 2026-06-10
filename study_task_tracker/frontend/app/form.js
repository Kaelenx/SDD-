import { fields, refs } from "./dom.js";
import { state } from "./state.js";

export function resetFormMode() {
  state.editingId = "";
  refs.editingIdInput.value = "";
  refs.formTitle.textContent = "新增任务";
  refs.submitButton.textContent = "新增任务";
  refs.cancelEditButton.classList.add("hidden");
  refs.form.reset();
}

export function enterEditMode(task) {
  state.editingId = task.id;
  refs.editingIdInput.value = task.id;
  refs.formTitle.textContent = `编辑 ${task.id}`;
  refs.submitButton.textContent = "保存修改";
  refs.cancelEditButton.classList.remove("hidden");
  fields.title.value = task.title;
  fields.course.value = task.course;
  fields.notes.value = task.notes || "";
  fields.dueDate.value = task.due_date;
  fields.estimatedHours.value = task.estimated_hours;
  fields.priority.value = task.priority;
  fields.title.focus();
}

export function taskPayloadFromForm(formData) {
  return {
    title: formData.get("title"),
    course: formData.get("course"),
    due_date: formData.get("dueDate"),
    notes: formData.get("notes"),
    estimated_hours: formData.get("estimatedHours"),
    priority: formData.get("priority"),
  };
}
