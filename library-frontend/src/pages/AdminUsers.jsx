import { useEffect, useState } from "react";
import api from "../services/api";

export default function AdminUsers() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [updating, setUpdating] = useState({});

    const fetchUsers = () => {
        setLoading(true);
        api.get("/users", { params: { search, per_page: 50 } })
            .then(({ data }) => setUsers(data.users))
            .finally(() => setLoading(false));
    };

    useEffect(() => { fetchUsers(); }, []);

    const handleRoleChange = async (userId, newRole) => {
        setUpdating((u) => ({ ...u, [userId]: true }));
        try {
            await api.put(`/users/${userId}`, { role: newRole });
            setUsers((prev) => prev.map((u) => u.id === userId ? { ...u, role: newRole } : u));
        } finally {
            setUpdating((u) => ({ ...u, [userId]: false }));
        }
    };

    const handleToggleActive = async (userId, isActive) => {
        setUpdating((u) => ({ ...u, [userId]: true }));
        try {
            await api.put(`/users/${userId}`, { is_active: !isActive });
            setUsers((prev) => prev.map((u) => u.id === userId ? { ...u, is_active: !isActive } : u));
        } finally {
            setUpdating((u) => ({ ...u, [userId]: false }));
        }
    };

    return (
        <div>
            <h1 className="page-title">User Management</h1>
            <p className="page-sub">{users.length} registered users</p>

            <form className="search-bar" onSubmit={(e) => { e.preventDefault(); fetchUsers(); }}>
                <input className="form-input" placeholder="Search name or email…"
                    value={search} onChange={(e) => setSearch(e.target.value)} />
                <button className="btn btn-ghost" type="submit">Search</button>
            </form>

            {loading ? (
                <div className="center" style={{ minHeight: 200 }}><div className="spinner" /></div>
            ) : (
                <div className="card" style={{ padding: 0 }}>
                    <div className="table-wrap">
                        <table>
                            <thead>
                                <tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Actions</th></tr>
                            </thead>
                            <tbody>
                                {users.map((u) => (
                                    <tr key={u.id}>
                                        <td style={{ fontWeight: 600 }}>{u.name}</td>
                                        <td style={{ color: "var(--clr-muted)", fontSize: "0.85rem" }}>{u.email}</td>
                                        <td>
                                            <select className="form-input" style={{ padding: "4px 8px", fontSize: "0.82rem" }}
                                                value={u.role} disabled={updating[u.id]}
                                                onChange={(e) => handleRoleChange(u.id, e.target.value)}>
                                                <option value="member">Member</option>
                                                <option value="librarian">Librarian</option>
                                                <option value="admin">Admin</option>
                                            </select>
                                        </td>
                                        <td>
                                            {u.is_active
                                                ? <span className="badge badge-green">Active</span>
                                                : <span className="badge badge-red">Inactive</span>}
                                        </td>
                                        <td>
                                            <button className={`btn btn-sm ${u.is_active ? "btn-danger" : "btn-ghost"}`}
                                                disabled={updating[u.id]}
                                                onClick={() => handleToggleActive(u.id, u.is_active)}>
                                                {u.is_active ? "Deactivate" : "Activate"}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
