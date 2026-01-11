import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Home from './pages/Home';
import Resumes from './pages/Resumes';
import Jobs from './pages/Jobs';
import Applications from './pages/Applications';

const ProtectedRoute = ({ children }) => {
    const { token, loading } = useAuth();
    if (loading) return <div>Loading...</div>;
    if (!token) return <Navigate to="/login" />;
    return children;
};

function App() {
    return (
        <Routes>
            <Route path="/login" element={<Login />} />

            <Route path="/" element={
                <ProtectedRoute>
                    <Layout />
                </ProtectedRoute>
            }>
                <Route index element={<Home />} />
                <Route path="resumes" element={<Resumes />} />
                <Route path="jobs" element={<Jobs />} />
                <Route path="applications" element={<Applications />} />
                <Route path="settings" element={<div>Settings Page (WIP)</div>} />
            </Route>
        </Routes>
    );
}

export default App;
