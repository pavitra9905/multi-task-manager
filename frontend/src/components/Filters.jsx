export default function Filters({ filters, setFilters, categories, onClear }) {
  function set(name, value) {
    setFilters((f) => ({ ...f, [name]: value }));
  }

  return (
    <div className="panel">
      <h2>Filters</h2>
      <div className="row">
        <input
          type="text"
          placeholder="Search title..."
          value={filters.q}
          onChange={(e) => set("q", e.target.value)}
        />
        <select value={filters.status} onChange={(e) => set("status", e.target.value)}>
          <option value="">All status</option>
          <option value="todo">To do</option>
          <option value="in_progress">In progress</option>
          <option value="done">Done</option>
        </select>
        <select value={filters.priority} onChange={(e) => set("priority", e.target.value)}>
          <option value="">All priority</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <select value={filters.category_id} onChange={(e) => set("category_id", e.target.value)}>
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
        <button type="button" className="secondary small" onClick={onClear}>Clear</button>
      </div>
    </div>
  );
}