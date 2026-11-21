import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../AuthContext";
import api, { getErrorMessage } from "../api";
import Filters from "../components/Filters";
import TaskForm from "../components/TaskForm";
import TaskItem from "../components/TaskItem";
import CategoryManager from "../components/CategoryManager";

const EMPTY_FILTERS = { status: "", priority: "", category_id: "", q: "" };
const PER_PAGE = 10;

export default function Tasks() {
  const { user, logout } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [debouncedQ, setDebouncedQ] = useState("");
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState({ total: 0, pages: 1 });
  const [refreshKey, setRefreshKey] = useState(0);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = () => setRefreshKey((k) => k + 1);

  // Any filter change goes back to page 1
  function updateFilters(next) {
    setFilters(next);
    setPage(1);
  }

  const loadCategories = useCallback(async () => {
    try {
      const res = await api.get("/api/categories");
      setCategories(res.data);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }, []);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  // Wait 300ms after typing stops before searching
  useEffect(() => {
    const id = setTimeout(() => setDebouncedQ(filters.q.trim()), 300);
    return () => clearTimeout(id);
  }, [filters.q]);

  // Load tasks whenever a filter or the page changes
  useEffect(() => {
    let cancelled = false;
    const params = { page, per_page: PER_PAGE };
    if (filters.status) params.status = filters.status;
    if (filters.priority) params.priority = filters.priority;
    if (filters.category_id) params.category_id = filters.category_id;
    if (debouncedQ) params.q = debouncedQ;

    setLoading(true);
    api
      .get("/api/tasks", { params })
      .then((res) => {
        if (cancelled) return;
        const { items, total, pages } = res.data;
        // If the last task on the last page was deleted, step back one page
        if (items.length === 0 && page > 1) {
          setPage(Math.max(1, pages));
          return;
        }
        setTasks(items);
        setMeta({ total, pages: Math.max(1, pages) });
        setError("");
      })
      .catch((err) => {
        if (!cancelled) setError(getErrorMessage(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [filters.status, filters.priority, filters.category_id, debouncedQ, page, refreshKey]);

  async function createTask(payload) {
    await api.post("/api/tasks", payload);
    setPage(1); // new tasks appear first
    refresh();
  }

  async function updateTask(id, payload) {
    await api.put(`/api/tasks/${id}`, payload);
    setEditingId(null);
    refresh();
  }

  async function changeStatus(id, status) {
    try {
      await api.put(`/api/tasks/${id}`, { status });
      refresh();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function deleteTask(task) {
    if (!window.confirm(`Delete "${task.title}"?`)) return;
    try {
      await api.delete(`/api/tasks/${task.id}`);
      refresh();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  function categoriesChanged(deletedId) {
    loadCategories();
    refresh();
    if (deletedId && String(deletedId) === filters.category_id) {
      updateFilters({ ...filters, category_id: "" });
    }
  }

  return (
    <div className="container">
      <div className="header">
        <h1>My Tasks</h1>
        <div className="row">
          <span className="muted">{user.email}</span>
          <button type="button" className="secondary small" onClick={logout}>Log out</button>
        </div>
      </div>

      <div className="layout">
        <aside>
          <CategoryManager categories={categories} onChange={categoriesChanged} />
        </aside>

        <main>
          <TaskForm categories={categories} onSubmit={createTask} />
          <Filters
            filters={filters}
            setFilters={updateFilters}
            categories={categories}
            onClear={() => updateFilters(EMPTY_FILTERS)}
          />

          {error && <p className="error">{error}</p>}
          {loading && <p className="muted">Loading...</p>}
          {!loading && tasks.length === 0 && <p className="muted">No tasks found.</p>}

          {tasks.map((t) =>
            editingId === t.id ? (
              <TaskForm
                key={t.id}
                initial={t}
                categories={categories}
                onSubmit={(payload) => updateTask(t.id, payload)}
                onCancel={() => setEditingId(null)}
              />
            ) : (
              <TaskItem
                key={t.id}
                task={t}
                onStatusChange={changeStatus}
                onEdit={setEditingId}
                onDelete={deleteTask}
              />
            )
          )}

          {meta.total > 0 && (
            <div className="pager">
              <button
                type="button"
                className="secondary small"
                disabled={page <= 1 || loading}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </button>
              <span className="muted">
                Page {page} of {meta.pages} ({meta.total} {meta.total === 1 ? "task" : "tasks"})
              </span>
              <button
                type="button"
                className="secondary small"
                disabled={page >= meta.pages || loading}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}