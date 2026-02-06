import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchUser();
    }, []);

    const fetchUser = async () => {
        try {
            const { data } = await api.get('/auth/');
            setUser(data);
        } catch (error) {
            // If 401, it means not authenticated, which is fine
            console.log("No active session or failed to fetch user");
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    const login = async () => {
        // Just fetch user, as login endpoint sets cookies
        await fetchUser();
    };

    const logout = async () => {
        try {
            await api.post('/auth/logout');
            setUser(null);
        } catch (error) {
            console.error("Logout failed", error);
            // Force logout client-side anyway
            setUser(null);
        }
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
