import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
    const { register } = useAuth();
    const navigate = useNavigate();
    const [form, setForm] = useState({ name: "", email: "", password: "" });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleChange = (e) =>
        setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        if (form.password.length < 8 ||
            !/[A-Z]/.test(form.password) ||
            !/[0-9]/.test(form.password) ||
            !/[!@#$%^&*(),.?":{}|<>_\-]/.test(form.password)) {
            setError("Password needs: 8+ chars · uppercase · number · special char");
            return;
        }
        setLoading(true);
        try {
            await register(form.name, form.email, form.password);
            navigate("/dashboard");
        } catch (err) {
            setError(err.response?.data?.error || "Registration failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="card auth-card">
                <h1 className="auth-title">Create account 🚀</h1>
                <p className="auth-sub">Join the library and start exploring</p>
                {error && <div className="alert alert-error">{error}</div>}
                <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                    <div className="form-group">
                        <label className="form-label">Full Name</label>
                        <input className="form-input" name="name" type="text"
                            placeholder="Jane Doe" value={form.name} onChange={handleChange} required />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Email</label>
                        <input className="form-input" name="email" type="email"
                            placeholder="you@example.com" value={form.email} onChange={handleChange} required />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Password</label>
                        <input className="form-input" name="password" type="password"
                            placeholder="e.g. Secret@123" value={form.password} onChange={handleChange} required />
                        <span style={{ fontSize: "0.75rem", color: "var(--clr-muted)", marginTop: 2 }}>
                            Must include: uppercase · number · special char (!@#$%^&*)
                        </span>
                    </div>
                    <button className="btn btn-primary btn-full" type="submit" disabled={loading}>
                        {loading ? "Creating account…" : "Create Account"}
                    </button>
                </form>
                <p style={{ marginTop: 20, color: "var(--clr-muted)", fontSize: "0.9rem", textAlign: "center" }}>
                    Already have an account? <Link to="/login">Sign in</Link>
                </p>
            </div>
        </div>
    );
}
