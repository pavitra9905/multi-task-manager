import { useState } from "react";
import api, { getErrorMessage } from "../api";

export default function CategoryManager({ categories, onChange }) {
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState("");

  async function add(e) {
    e.preventDefault();
    setError("");
    try {
      await api.post("/api/categories", { name: name.trim() });
      setName("");
      onChange();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function rename(id) {
    setError("");
    try {
      await api.put(`/api/categories/${id}`, { name: editName.trim() });
      setEditingId(null);
      onChange();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function remove(c) {
    if (!window.confirm(`Delete category "${c.name}"? Its tasks will be kept.`)) return;
    setError("");
    try {
      await api.delete(`/api/categories/${c.id}`);
      onChange(c.id);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  return (
    <div className="panel">
      <h2>Categories</h2>
      <form onSubmit={add} className="row">
        <input
          type="text"
          placeholder="New category"
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={50}
          required
        />
        <button type="submit" className="small">Add</button>
      </form>
      {error && <p className="error">{error}</p>}

      {categories.length === 0 && <p className="muted">No categories yet.</p>}
      {categories.map((c) => (
        <div key={c.id} className="cat-item">
          {editingId === c.id ? (
            <>
              <input value={editName} onChange={(e) => setEditName(e.target.value)} maxLength={50} />
              <button type="button" className="small" onClick={() => rename(c.id)}>Save</button>
              <button type="button" className="secondary small" onClick={() => setEditingId(null)}>X</button>
            </>
          ) : (
            <>
              <span>{c.name}</span>
              <span className="row actions">
                <button
                  type="button"
                  className="secondary small"
                  onClick={() => { setEditingId(c.id); setEditName(c.name); }}
                >
                  Rename
                </button>
                <button type="button" className="danger small" onClick={() => remove(c)}>Delete</button>
              </span>
            </>
          )}
        </div>
      ))}
    </div>
  );
}