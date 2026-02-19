import { useEffect, useState } from "react";
import api from "../services/api";

export default function Overdue() {
    const [records, setRecords] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get("/analytics/overdue")
            .then(({ data }) => setRecords(data))
            .finally(() => setLoading(false));
    }, []);

    if (loading)
        return <div className="center" style={{ minHeight: "60vh" }}><div className="spinner" /></div>;

    return (
        <div>
            <h1 className="page-title">Overdue Books</h1>
            <p className="page-sub">{records.length} borrow{records.length !== 1 ? "s" : ""} past due date</p>

            {records.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-icon">✅</div>
                    <p>No overdue books! All clear.</p>
                </div>
            ) : (
                <div className="card" style={{ padding: 0 }}>
                    <div className="table-wrap">
                        <table>
                            <thead>
                                <tr><th>Member</th><th>Email</th><th>Book</th><th>Due Date</th><th>Days Overdue</th></tr>
                            </thead>
                            <tbody>
                                {records.map((r) => (
                                    <tr key={r.id}>
                                        <td style={{ fontWeight: 600 }}>{r.user_name}</td>
                                        <td style={{ color: "var(--clr-muted)", fontSize: "0.85rem" }}>{r.email}</td>
                                        <td>{r.book_title}</td>
                                        <td style={{ color: "var(--clr-danger)", fontSize: "0.85rem" }}>
                                            {new Date(r.due_date).toLocaleDateString()}
                                        </td>
                                        <td>
                                            <span className="badge badge-red">{r.days_overdue} day{r.days_overdue !== 1 ? "s" : ""}</span>
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
