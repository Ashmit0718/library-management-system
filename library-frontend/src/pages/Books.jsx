import { useEffect, useState, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

export default function Books() {
    const { user } = useAuth();
    const isStaff = user?.role === "librarian" || user?.role === "admin";

    const [books, setBooks] = useState([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [pages, setPages] = useState(1);
    const [search, setSearch] = useState("");
    const [genre, setGenre] = useState("");
    const [loading, setLoading] = useState(true);

    // Add-book modal state
    const [showModal, setShowModal] = useState(false);
    const [newBook, setNewBook] = useState({ title: "", author: "", isbn: "", genre: "", description: "", total_copies: 1 });
    const [formErr, setFormErr] = useState("");
    const [borrowMsg, setBorrowMsg] = useState({});

    const fetchBooks = useCallback(() => {
        setLoading(true);
        api.get("/books", { params: { page, per_page: 12, search, genre } })
            .then(({ data }) => {
                setBooks(data.books);
                setTotal(data.total);
                setPages(data.pages);
            })
            .finally(() => setLoading(false));
    }, [page, search, genre]);

    useEffect(() => { fetchBooks(); }, [fetchBooks]);

    const handleSearch = (e) => { e.preventDefault(); setPage(1); fetchBooks(); };

    const handleBorrow = async (bookId) => {
        try {
            await api.post("/borrows", { book_id: bookId });
            setBorrowMsg((m) => ({ ...m, [bookId]: "success" }));
            fetchBooks();
        } catch (err) {
            setBorrowMsg((m) => ({ ...m, [bookId]: err.response?.data?.error || "Error" }));
        }
    };

    const handleAddBook = async (e) => {
        e.preventDefault();
        setFormErr("");
        try {
            await api.post("/books", { ...newBook, total_copies: Number(newBook.total_copies) });
            setShowModal(false);
            setNewBook({ title: "", author: "", isbn: "", genre: "", description: "", total_copies: 1 });
            fetchBooks();
        } catch (err) {
            setFormErr(err.response?.data?.error || "Failed to add book");
        }
    };

    const genres = ["Fiction", "Non-fiction", "Science", "History", "Technology", "Philosophy", "Biography", "Other"];

    return (
        <div>
            <div className="flex justify-between align-center" style={{ marginBottom: 8 }}>
                <div>
                    <h1 className="page-title">Books</h1>
                    <p className="page-sub">{total} book{total !== 1 ? "s" : ""} in the library</p>
                </div>
                {isStaff && (
                    <button className="btn btn-primary" onClick={() => setShowModal(true)}>+ Add Book</button>
                )}
            </div>

            {/* Search */}
            <form className="search-bar" onSubmit={handleSearch}>
                <input className="form-input" placeholder="Search title, author, ISBN…"
                    value={search} onChange={(e) => setSearch(e.target.value)} />
                <select className="form-input" style={{ maxWidth: 160 }} value={genre} onChange={(e) => setGenre(e.target.value)}>
                    <option value="">All genres</option>
                    {genres.map(g => <option key={g} value={g}>{g}</option>)}
                </select>
                <button className="btn btn-ghost" type="submit">Search</button>
                {(search || genre) && (
                    <button className="btn btn-ghost" type="button" onClick={() => { setSearch(""); setGenre(""); setPage(1); }}>Clear</button>
                )}
            </form>

            {loading ? (
                <div className="center" style={{ minHeight: 300 }}><div className="spinner" /></div>
            ) : books.length === 0 ? (
                <div className="empty-state"><div className="empty-icon">📭</div><p>No books found.</p></div>
            ) : (
                <>
                    <div className="grid-auto">
                        {books.map((b) => (
                            <div className="card book-card" key={b.id}>
                                <div className="book-genre">{b.genre || "General"}</div>
                                <div className="book-title">{b.title}</div>
                                <div className="book-author">{b.author || "Unknown author"}</div>
                                {b.description && (
                                    <p style={{ fontSize: "0.82rem", color: "var(--clr-muted)", marginBottom: 8 }}>
                                        {b.description.slice(0, 100)}{b.description.length > 100 ? "…" : ""}
                                    </p>
                                )}
                                <div className="book-meta">
                                    <span className={`copies-pill ${b.available_copies > 0 ? "available" : ""}`}>
                                        {b.available_copies}/{b.total_copies} available
                                    </span>
                                    {b.available_copies > 0 ? (
                                        <button className="btn btn-accent btn-sm"
                                            onClick={() => handleBorrow(b.id)}
                                            disabled={borrowMsg[b.id] === "success"}>
                                            {borrowMsg[b.id] === "success" ? "Borrowed ✓" : "Borrow"}
                                        </button>
                                    ) : (
                                        <span className="badge badge-red">Unavailable</span>
                                    )}
                                </div>
                                {borrowMsg[b.id] && borrowMsg[b.id] !== "success" && (
                                    <div className="alert alert-error" style={{ marginTop: 8, marginBottom: 0 }}>{borrowMsg[b.id]}</div>
                                )}
                            </div>
                        ))}
                    </div>

                    {/* Pagination */}
                    <div className="pagination">
                        <button className="page-btn" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Prev</button>
                        <span style={{ color: "var(--clr-muted)", fontSize: "0.85rem" }}>Page {page} of {pages}</span>
                        <button className="page-btn" disabled={page >= pages} onClick={() => setPage(p => p + 1)}>Next →</button>
                    </div>
                </>
            )}

            {/* Add Book Modal */}
            {showModal && (
                <div style={{
                    position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)",
                    display: "flex", alignItems: "center", justifyContent: "center", zIndex: 200, padding: 24
                }}>
                    <div className="card" style={{ width: "100%", maxWidth: 480 }}>
                        <div className="flex justify-between align-center" style={{ marginBottom: 20 }}>
                            <h2 style={{ fontWeight: 700 }}>Add New Book</h2>
                            <button className="btn btn-ghost btn-sm" onClick={() => setShowModal(false)}>✕</button>
                        </div>
                        {formErr && <div className="alert alert-error">{formErr}</div>}
                        <form onSubmit={handleAddBook} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                            {[
                                { name: "title", label: "Title *", placeholder: "Book title" },
                                { name: "author", label: "Author", placeholder: "Author name" },
                                { name: "isbn", label: "ISBN", placeholder: "978-…" },
                            ].map(f => (
                                <div className="form-group" key={f.name}>
                                    <label className="form-label">{f.label}</label>
                                    <input className="form-input" name={f.name} placeholder={f.placeholder}
                                        value={newBook[f.name]} onChange={e => setNewBook(b => ({ ...b, [e.target.name]: e.target.value }))}
                                        required={f.name === "title"} />
                                </div>
                            ))}
                            <div className="form-group">
                                <label className="form-label">Genre</label>
                                <select className="form-input" value={newBook.genre}
                                    onChange={e => setNewBook(b => ({ ...b, genre: e.target.value }))}>
                                    <option value="">Select genre</option>
                                    {genres.map(g => <option key={g} value={g}>{g}</option>)}
                                </select>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Copies</label>
                                <input className="form-input" type="number" min={1} value={newBook.total_copies}
                                    onChange={e => setNewBook(b => ({ ...b, total_copies: e.target.value }))} />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Description</label>
                                <textarea className="form-input" rows={3} placeholder="Short description…"
                                    value={newBook.description}
                                    onChange={e => setNewBook(b => ({ ...b, description: e.target.value }))} />
                            </div>
                            <button className="btn btn-primary btn-full" type="submit">Add Book</button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
