import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { User, Mail, Lock, Upload, Loader2, ArrowRight } from 'lucide-react';

export default function SignUp() {
    const navigate = useNavigate();
    const { login } = useAuth();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        user_profile_image: null
    });
    const [imagePreview, setImagePreview] = useState(null);
    const [error, setError] = useState('');

    const mutation = useMutation({
        mutationFn: async (data) => {
            const formDataToSend = new FormData();
            formDataToSend.append('username', data.username);
            formDataToSend.append('email', data.email);
            formDataToSend.append('password', data.password);
            if (data.user_profile_image) {
                formDataToSend.append('user_profile_image', data.user_profile_image);
            }
            return api.post('/auth/signup', formDataToSend, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
        },
        onSuccess: (response) => {
            // After signup, we get the user data and tokens
            const { access_token, refresh_token, ...userData } = response.data;
            login(access_token, refresh_token, userData);
            navigate('/dashboard');
        },
        onError: (err) => {
            setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
        }
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setFormData({ ...formData, user_profile_image: file });
            setImagePreview(URL.createObjectURL(file));
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setError('');
        mutation.mutate(formData);
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-950 px-4 py-8">
            <div className="w-full max-w-md bg-gray-900/50 backdrop-blur-xl border border-gray-800 rounded-2xl p-8 shadow-2xl">
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                        Create Account
                    </h2>
                    <p className="text-gray-400 mt-2">Join the community today</p>
                </div>

                {error && (
                    <div className="mb-6 p-4 bg-red-900/20 border border-red-800 text-red-200 rounded-lg text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="flex justify-center mb-6">
                        <div className="relative group cursor-pointer">
                            <input
                                type="file"
                                id="profile-image"
                                accept="image/*"
                                onChange={handleFileChange}
                                className="hidden"
                            />
                            <label
                                htmlFor="profile-image"
                                className="block w-24 h-24 rounded-full border-2 border-dashed border-gray-600 flex items-center justify-center overflow-hidden hover:border-blue-500 transition-colors bg-gray-800/50 cursor-pointer"
                            >
                                {imagePreview ? (
                                    <img src={imagePreview} alt="Preview" className="w-full h-full object-cover" />
                                ) : (
                                    <Upload className="text-gray-400 group-hover:text-blue-400 transition-colors" size={24} />
                                )}
                            </label>
                            <div className="absolute -bottom-2 -right-2 bg-blue-600 rounded-full p-1.5 border-4 border-gray-950">
                                <PlusIcon size={12} />
                            </div>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="relative">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                            <input
                                type="text"
                                name="username"
                                placeholder="Username"
                                value={formData.username}
                                onChange={handleChange}
                                required
                                className="w-full bg-gray-800/50 border border-gray-700 rounded-lg py-3 pl-10 pr-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
                            />
                        </div>

                        <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                            <input
                                type="email"
                                name="email"
                                placeholder="Email Address"
                                value={formData.email}
                                onChange={handleChange}
                                required
                                className="w-full bg-gray-800/50 border border-gray-700 rounded-lg py-3 pl-10 pr-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
                            />
                        </div>

                        <div className="relative">
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                            <input
                                type="password"
                                name="password"
                                placeholder="Password"
                                value={formData.password}
                                onChange={handleChange}
                                required
                                className="w-full bg-gray-800/50 border border-gray-700 rounded-lg py-3 pl-10 pr-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={mutation.isPending}
                        className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-semibold py-3 rounded-lg transition-all transform hover:scale-[1.02] shadow-lg shadow-blue-500/25 flex items-center justify-center gap-2 group"
                    >
                        {mutation.isPending ? (
                            <Loader2 className="animate-spin" size={20} />
                        ) : (
                            <>
                                Create Account
                                <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                            </>
                        )}
                    </button>
                </form>

                <div className="mt-6 text-center text-gray-400 text-sm">
                    Already have an account?{' '}
                    <Link to="/signin" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
                        Sign In
                    </Link>
                </div>
            </div>
        </div>
    );
}

function PlusIcon({ size }) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-white"
        >
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
    );
}
