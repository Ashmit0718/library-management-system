import { useEffect, useState } from "react";
import api from "../services/api";

export default function Dashboard() {
    const [stats, setStats] = useState(null);
    const [trending, setTrending] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([
            api.get("/analytics/dashboard"),
            api.get("/analytics/trending"),
        ])
            .then(([s, t]) => {
                setStats(s.data);
                setTrending(t.data.slice(0, 5));
            })
            .finally(() => setLoading(false));
    }, []);

    if (loading)
        return <div className="center" style={{ minHeight: "60vh" }}><div className="spinner" /></div>;

    const statItems = [
        { icon: "📚", label: "Total Books", value: stats.total_books },
        { icon: "📖", label: "Available", value: stats.available_books },
        { icon: "👥", label: "Members", value: stats.total_members },
        { icon: "🔖", label: "Active Borrows", value: stats.active_borrows },
        { icon: "⏰", label: "Overdue", value: stats.overdue_count },
        { icon: "📊", label: "Total Borrows", value: stats.total_borrows },
    ];

    return (
        <div>
            <h1 className="page-title">Dashboard</h1>
            <p className="page-sub">Library at a glance</p>

            {/* Stats Grid */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(170px, 1fr))", gap: 16, marginBottom: 36 }}>
                {statItems.map((s) => (
                    <div className="stat-card" key={s.label}>
                        <div className="stat-icon">{s.icon}</div>
                        <div className="stat-value">{s.value}</div>
                        <div className="stat-label">{s.label}</div>
                    </div>
                ))}
            </div>

            {/* Trending */}
            <h2 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: 16 }}>🔥 Trending This Month</h2>
            <div className="card" style={{ padding: 0 }}>
                <div className="table-wrap">
                    <table>
                        <thead>
                            <tr><th>#</th><th>Book</th><th>Author</th><th>Genre</th><th>Borrows</th></tr>
                        </thead>
                        <tbody>
                            {trending.length === 0 ? (
                                <tr><td colSpan={5} style={{ textAlign: "center", color: "var(--clr-muted)", padding: 32 }}>No data yet</td></tr>
                            ) : trending.map((b, i) => (
                                <tr key={b.id}>
                                    <td style={{ color: "var(--clr-muted)" }}>#{i + 1}</td>
                                    <td style={{ fontWeight: 600 }}>{b.title}</td>
                                    <td style={{ color: "var(--clr-muted)" }}>{b.author || "—"}</td>
                                    <td>{b.genre ? <span className="badge badge-purple">{b.genre}</span> : "—"}</td>
                                    <td><span className="badge badge-green">{b.borrow_count}</span></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
