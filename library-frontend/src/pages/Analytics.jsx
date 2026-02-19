import { useEffect, useState } from "react";
import api from "../services/api";

export default function Analytics() {
    const [leaderboard, setLeaderboard] = useState([]);
    const [genreStats, setGenreStats] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([api.get("/analytics/leaderboard"), api.get("/analytics/genre-stats")])
            .then(([l, g]) => { setLeaderboard(l.data); setGenreStats(g.data); })
            .finally(() => setLoading(false));
    }, []);

    if (loading)
        return <div className="center" style={{ minHeight: "60vh" }}><div className="spinner" /></div>;

    const maxGenreBorrows = Math.max(...genreStats.map(g => g.borrow_count), 1);

    return (
        <div>
            <h1 className="page-title">Analytics</h1>
            <p className="page-sub">SQL-driven intelligence layer</p>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
                {/* Leaderboard */}
                <div className="card" style={{ padding: 0 }}>
                    <h2 style={{ padding: "18px 24px 0", fontWeight: 700, fontSize: "1rem" }}>🏆 Member Leaderboard</h2>
                    <div className="table-wrap">
                        <table>
                            <thead>
                                <tr><th>Rank</th><th>Member</th><th>Borrows</th><th>Returned</th><th>Overdue</th></tr>
                            </thead>
                            <tbody>
                                {leaderboard.length === 0 ? (
                                    <tr><td colSpan={5} className="empty-state">No data</td></tr>
                                ) : leaderboard.map((u) => (
                                    <tr key={u.id}>
                                        <td style={{ fontWeight: 700, color: u.rank_pos <= 3 ? "var(--clr-warning)" : "var(--clr-muted)" }}>
                                            #{u.rank_pos}
                                        </td>
                                        <td style={{ fontWeight: 600 }}>{u.name}</td>
                                        <td><span className="badge badge-purple">{u.total_borrows}</span></td>
                                        <td><span className="badge badge-green">{u.returned}</span></td>
                                        <td>{u.overdue > 0
                                            ? <span className="badge badge-red">{u.overdue}</span>
                                            : <span style={{ color: "var(--clr-muted)" }}>—</span>}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Genre Stats */}
                <div className="card">
                    <h2 style={{ fontWeight: 700, fontSize: "1rem", marginBottom: 20 }}>📊 Popularity by Genre</h2>
                    {genreStats.length === 0 ? (
                        <div className="empty-state"><p>No genre data yet.</p></div>
                    ) : genreStats.map((g) => (
                        <div key={g.genre} style={{ marginBottom: 14 }}>
                            <div className="flex justify-between" style={{ marginBottom: 4 }}>
                                <span style={{ fontSize: "0.88rem", fontWeight: 600 }}>{g.genre}</span>
                                <span style={{ fontSize: "0.8rem", color: "var(--clr-muted)" }}>{g.borrow_count} borrows</span>
                            </div>
                            <div style={{ height: 8, background: "var(--clr-surface2)", borderRadius: 99 }}>
                                <div style={{
                                    height: "100%",
                                    width: `${(g.borrow_count / maxGenreBorrows) * 100}%`,
                                    background: "linear-gradient(90deg, var(--clr-primary), var(--clr-accent))",
                                    borderRadius: 99,
                                    transition: "width 0.4s ease"
                                }} />
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
