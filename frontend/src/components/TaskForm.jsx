import { useState } from "react";
import { getErrorMessage } from "../api";

export default function TaskForm({ categories, initial, onSubmit, onCancel }) {
  const [title, setTitle] = useState(initial?.title || "");
  const [description, setDescription] = useState(initial?.description || "");
  const [priority, setPriority] = useState(initial?.priority || "medium");
  const [status, setStatus] = useState(initial?.status || "todo");
  const [dueDate, setDueDate] = useState(initial?.due_date || "");
  const [categoryId, setCategoryId] = useState(initial?.category ? String(initial.category.id) : "");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || null,
        priority,
        status,
        due_date: dueDate || null,
        category_id: categoryId ? Number(categoryId) : null,
      });
      if (!initial) {
        setTitle("");
        setDescription("");
        setPriority("medium");
        setStatus("todo");
        setDueDate("");
        setCategoryId("");
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className={initial ? "task" : "panel"}>
      {!initial && <h2>Add task</h2>}
      <input
        type="text"
        placeholder="Task title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        maxLength={150}
        required
      />
      <textarea
        placeholder="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        maxLength={2000}
        rows={2}
      />
      <div className="grid2">
        <select value={priority} onChange={(e) => setPriority(e.target.value)}>
          <option value="low">Low priority</option>
          <option value="medium">Medium priority</option>
          <option value="high">High priority</option>
        </select>
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="todo">To do</option>
          <option value="in_progress">In progress</option>
          <option value="done">Done</option>
        </select>
        <input type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
        <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
          <option value="">No category</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>
      {error && <p className="error">{error}</p>}
      <div className="row actions">
        <button type="submit" disabled={busy}>
          {busy ? "Saving..." : initial ? "Save changes" : "Add task"}
        </button>
        {onCancel && (
          <button type="button" className="secondary" onClick={onCancel}>Cancel</button>
        )}
      </div>
    </form>
  );
}