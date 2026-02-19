import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Books from "./pages/Books";
import MyBorrows from "./pages/MyBorrows";
import Analytics from "./pages/Analytics";
import Overdue from "./pages/Overdue";
import AdminUsers from "./pages/AdminUsers";

function AppLayout({ children }) {
  return (
    <>
      <Navbar />
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">{children}</main>
      </div>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected – any authenticated user */}
          <Route path="/dashboard" element={
            <ProtectedRoute><AppLayout><Dashboard /></AppLayout></ProtectedRoute>
          } />
          <Route path="/books" element={
            <ProtectedRoute><AppLayout><Books /></AppLayout></ProtectedRoute>
          } />
          <Route path="/my-borrows" element={
            <ProtectedRoute><AppLayout><MyBorrows /></AppLayout></ProtectedRoute>
          } />
          <Route path="/analytics" element={
            <ProtectedRoute><AppLayout><Analytics /></AppLayout></ProtectedRoute>
          } />

          {/* Staff only */}
          <Route path="/overdue" element={
            <ProtectedRoute roles={["librarian", "admin"]}><AppLayout><Overdue /></AppLayout></ProtectedRoute>
          } />

          {/* Admin only */}
          <Route path="/admin/users" element={
            <ProtectedRoute roles={["admin"]}><AppLayout><AdminUsers /></AppLayout></ProtectedRoute>
          } />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
