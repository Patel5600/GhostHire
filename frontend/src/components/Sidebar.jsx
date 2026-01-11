import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, Home, FileText, Briefcase, PlayCircle, Settings } from 'lucide-react';

const Sidebar = () => {
    const { logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const navItems = [
        { label: 'Dashboard', path: '/', icon: Home },
        { label: 'Resumes', path: '/resumes', icon: FileText },
        { label: 'Marketplace', path: '/jobs', icon: Briefcase },
        { label: 'Applications', path: '/applications', icon: PlayCircle },
        { label: 'Settings', path: '/settings', icon: Settings },
    ];

    return (
        <div className="flex flex-col h-screen w-64 bg-white border-r">
            <div className="flex items-center justify-center h-16 border-b">
                <h1 className="text-xl font-bold text-primary">GhostHire</h1>
            </div>
            <nav className="flex-1 overflow-y-auto py-4">
                <ul>
                    {navItems.map((item) => (
                        <li key={item.path}>
                            <button
                                onClick={() => navigate(item.path)}
                                className="flex items-center w-full px-6 py-3 text-gray-600 hover:bg-gray-100 hover:text-primary transition-colors"
                            >
                                <item.icon className="w-5 h-5 mr-3" />
                                {item.label}
                            </button>
                        </li>
                    ))}
                </ul>
            </nav>
            <div className="p-4 border-t">
                <button
                    onClick={handleLogout}
                    className="flex items-center justify-center w-full px-4 py-2 text-sm text-red-600 bg-red-50 rounded-md hover:bg-red-100"
                >
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                </button>
            </div>
        </div>
    );
};

export default Sidebar;
