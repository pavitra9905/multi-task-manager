export default function TaskItem({ task, onStatusChange, onEdit, onDelete }) {
  const today = new Date().toLocaleDateString("en-CA"); // YYYY-MM-DD
  const overdue = task.due_date && task.due_date < today && task.status !== "done";

  return (
    <div className={`task ${task.status === "done" ? "done" : ""} ${overdue ? "overdue" : ""}`}>
      <div className="row between">
        <strong className="title">{task.title}</strong>
        <select
          className="status-select"
          value={task.status}
          onChange={(e) => onStatusChange(task.id, e.target.value)}
        >
          <option value="todo">To do</option>
          <option value="in_progress">In progress</option>
          <option value="done">Done</option>
        </select>
      </div>

      {task.description && <p className="muted">{task.description}</p>}

      <div className="row meta">
        <span className={`badge p-${task.priority}`}>{task.priority}</span>
        {task.category && <span className="badge">{task.category.name}</span>}
        {task.due_date && (
          <span className={`muted ${overdue ? "late" : ""}`}>
            Due {task.due_date}{overdue ? " (overdue)" : ""}
          </span>
        )}
      </div>

      <div className="row actions">
        <button type="button" className="secondary small" onClick={() => onEdit(task.id)}>Edit</button>
        <button type="button" className="danger small" onClick={() => onDelete(task)}>Delete</button>
      </div>
    </div>
  );
}