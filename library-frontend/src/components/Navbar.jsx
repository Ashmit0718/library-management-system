import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    return (
        <nav className="navbar">
            <div className="container flex justify-between align-center" style={{ width: "100%" }}>
                <span className="logo">📚 LibraryMS</span>
                <div className="navbar-links">
                    {user ? (
                        <>
                            <span style={{ color: "var(--clr-muted)", fontSize: "0.85rem", marginRight: 8 }}>
                                {user.name} <span className="badge badge-purple">{user.role}</span>
                            </span>
                            <button className="btn btn-ghost btn-sm" onClick={handleLogout}>Logout</button>
                        </>
                    ) : (
                        <>
                            <NavLink className="nav-link" to="/login">Login</NavLink>
                            <NavLink className="nav-link" to="/register">Register</NavLink>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
}
