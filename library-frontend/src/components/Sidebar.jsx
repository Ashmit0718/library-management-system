import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Sidebar() {
    const { user } = useAuth();
    if (!user) return null;

    const isStaff = user.role === "librarian" || user.role === "admin";
    const isAdmin = user.role === "admin";

    return (
        <aside className="sidebar">
            <NavLink className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`} to="/dashboard">
                <span className="sidebar-icon">📊</span> Dashboard
            </NavLink>
            <NavLink className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`} to="/books">
                <span className="sidebar-icon">📖</span> Books
            </NavLink>
            <NavLink className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`} to="/my-borrows">
                <span className="sidebar-icon">🔖</span> My Borrows
            </NavLink>
            <NavLink className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`} to="/analytics">
                <span className="sidebar-icon">📈</span> Analytics
            </NavLink>

            {isStaff && (
                <>
                    <div className="divider" />
                    <NavLink className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`} to="/overdue">
                        <span className="sidebar-icon">⏰</span> Overdue
                    </NavLink>
                </>
            )}

            {isAdmin && (
                <NavLink className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`} to="/admin/users">
                    <span className="sidebar-icon">👥</span> Users
                </NavLink>
            )}
        </aside>
    );
}
