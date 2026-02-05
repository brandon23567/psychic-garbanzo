import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';

// Placeholder Pages
import Home from './pages/Home';
import SignIn from './pages/SignIn';
import SignUp from './pages/SignUp';
import Dashboard from './pages/Dashboard';
import CreateCommunity from './pages/CreateCommunity';
import CommunityDetails from './pages/CommunityDetails';

const queryClient = new QueryClient();

const ProtectedRoute = () => {
  const { token, loading } = useAuth();
  if (loading) return <div>Loading...</div>;
  return token ? <Outlet /> : <Navigate to="/signin" />;
};

const Layout = () => (
  <div className="min-h-screen bg-gray-950 text-white flex flex-col">
    <Navbar />
    <main className="flex-grow container mx-auto px-4 py-8">
      <Outlet />
    </main>
  </div>
);

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AuthProvider>
          <Routes>
            {/* Public Routes */}
            <Route path="/signin" element={<SignIn />} />
            <Route path="/signup" element={<SignUp />} />

            {/* Protected Routes */}
            <Route element={<ProtectedRoute />}>
              <Route element={<Layout />}>
                <Route path="/" element={<Home />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/create-community" element={<CreateCommunity />} />
                <Route path="/community/:id" element={<CommunityDetails />} />
              </Route>
            </Route>
          </Routes>
        </AuthProvider>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
