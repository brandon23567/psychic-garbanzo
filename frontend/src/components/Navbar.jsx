import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, PlusCircle, LayoutDashboard } from 'lucide-react';

export default function Navbar() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/signin');
    };

    return (
        <nav className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-md sticky top-0 z-50">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                <Link to="/" className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                    CommPlatform
                </Link>

                <div className="flex items-center space-x-6">
                    <Link to="/dashboard" className="text-gray-300 hover:text-white transition-colors flex items-center gap-2">
                        <LayoutDashboard size={18} />
                        Dashboard
                    </Link>
                    <Link to="/create-community" className="text-gray-300 hover:text-white transition-colors flex items-center gap-2">
                        <PlusCircle size={18} />
                        New Community
                    </Link>

                    <div className="h-6 w-px bg-gray-800"></div>

                    <div className="flex items-center gap-4">
                        <div className="flex flex-col items-end">
                            <span className="text-sm font-medium text-white">{user?.username}</span>
                        </div>
                        {user?.user_profile_image && (
                            <img src={user.user_profile_image} alt="Profile" className="w-8 h-8 rounded-full border border-gray-700" />
                        )}
                        <button
                            onClick={handleLogout}
                            className="p-2 text-gray-400 hover:text-red-400 transition-colors"
                            title="Logout"
                        >
                            <LogOut size={20} />
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
}
