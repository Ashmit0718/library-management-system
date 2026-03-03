import { useEffect, useState } from "react";
import api from "../services/api";

export default function MyBorrows() {
    const [borrows, setBorrows] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState("");

    const fetchBorrows = () => {
        setLoading(true);
        api.get("/borrows", { params: { per_page: 50, ...(filter && { status: filter }) } })
            .then(({ data }) => setBorrows(data.borrows))
            .finally(() => setLoading(false));
    };

    useEffect(() => { fetchBorrows(); }, [filter]);

    const statusBadge = (s) => {
        if (s === "returned") return <span className="badge badge-green">Returned</span>;
        if (s === "overdue") return <span className="badge badge-red">Overdue</span>;
        return <span className="badge badge-yellow">Borrowed</span>;
    };

    return (
        <div>
            <h1 className="page-title">My Borrows</h1>
            <p className="page-sub">Track all your borrowed books</p>

            <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
                {["", "borrowed", "returned", "overdue"].map((s) => (
                    <button key={s} className={`btn btn-sm ${filter === s ? "btn-primary" : "btn-ghost"}`}
                        onClick={() => setFilter(s)}>
                        {s === "" ? "All" : s.charAt(0).toUpperCase() + s.slice(1)}
                    </button>
                ))}
            </div>

            {loading ? (
                <div className="center" style={{ minHeight: 200 }}><div className="spinner" /></div>
            ) : borrows.length === 0 ? (
                <div className="empty-state"><div className="empty-icon">🔖</div><p>No borrows found.</p></div>
            ) : (
                <div className="card" style={{ padding: 0 }}>
                    <div className="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>Book</th><th>Borrowed</th><th>Due Date</th><th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {borrows.map((r) => (
                                    <tr key={r.id}>
                                        <td style={{ fontWeight: 600 }}>{r.book?.title || `Book #${r.book_id}`}</td>
                                        <td style={{ color: "var(--clr-muted)", fontSize: "0.85rem" }}>
                                            {new Date(r.borrowed_at).toLocaleDateString()}
                                        </td>
                                        <td style={{ color: r.status === "overdue" ? "var(--clr-danger)" : "var(--clr-muted)", fontSize: "0.85rem" }}>
                                            {new Date(r.due_date).toLocaleDateString()}
                                        </td>
                                        <td>{statusBadge(r.status)}</td>
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
