import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * roles: optional array of allowed roles, e.g. ['admin', 'librarian']
 * If not provided, any authenticated user can access the route.
 */
export default function ProtectedRoute({ children, roles }) {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="center" style={{ minHeight: "60vh" }}>
                <div className="spinner" />
            </div>
        );
    }

    if (!user) return <Navigate to="/login" replace />;
    if (roles && !roles.includes(user.role)) return <Navigate to="/dashboard" replace />;

    return children;
}
