import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Tasks from "./pages/Tasks";
import ServerWakeBanner from "./components/ServerWakeBanner";

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="center">Loading...</p>;
  return user ? children : <Navigate to="/login" replace />;
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="center">Loading...</p>;
  return user ? <Navigate to="/" replace /> : children;
}

export default function App() {
  return (
    <>
      <ServerWakeBanner />
      <Routes>
        <Route path="/" element={<ProtectedRoute><Tasks /></ProtectedRoute>} />
        <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}