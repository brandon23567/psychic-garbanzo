import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';
import { Upload, Loader2, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function CreateCommunity() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [formData, setFormData] = useState({
        community_name: '',
        community_description: '',
        community_header_image: null
    });
    const [imagePreview, setImagePreview] = useState(null);
    const [error, setError] = useState('');

    const mutation = useMutation({
        mutationFn: async (data) => {
            const formDataToSend = new FormData();
            formDataToSend.append('community_name', data.community_name);
            formDataToSend.append('community_description', data.community_description);
            if (data.community_header_image) {
                formDataToSend.append('community_header_image', data.community_header_image);
            }
            return api.post('/community/new', formDataToSend, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['communities']);
            queryClient.invalidateQueries(['joined_communities']);
            navigate('/dashboard');
        },
        onError: (err) => {
            setError(err.response?.data?.detail || 'Failed to create community.');
        }
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setFormData({ ...formData, community_header_image: file });
            setImagePreview(URL.createObjectURL(file));
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setError('');
        if (!formData.community_header_image) {
            setError("Header image is required");
            return;
        }
        mutation.mutate(formData);
    };

    return (
        <div className="max-w-2xl mx-auto">
            <Link to="/dashboard" className="inline-flex items-center text-gray-400 hover:text-white mb-6">
                <ArrowLeft size={18} className="mr-2" />
                Back to Dashboard
            </Link>

            <div className="bg-gray-900/50 backdrop-blur-xl border border-gray-800 rounded-2xl p-8 shadow-xl">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent mb-6">
                    Create New Community
                </h1>

                {error && (
                    <div className="mb-6 p-4 bg-red-900/20 border border-red-800 text-red-200 rounded-lg text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">

                    {/* Image Upload */}
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Community Header Image</label>
                        <div className={`relative h-48 w-full rounded-xl border-2 border-dashed ${imagePreview ? 'border-gray-700' : 'border-gray-600 hover:border-blue-500'} bg-gray-800/50 flex flex-col items-center justify-center cursor-pointer transition-colors overflow-hidden group`}>
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleFileChange}
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                            />
                            {imagePreview ? (
                                <img src={imagePreview} alt="Preview" className="w-full h-full object-cover" />
                            ) : (
                                <div className="flex flex-col items-center text-gray-400 group-hover:text-blue-400 transition-colors">
                                    <Upload size={32} className="mb-2" />
                                    <span className="text-sm">Click to upload header image</span>
                                </div>
                            )}
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Community Name</label>
                        <input
                            type="text"
                            name="community_name"
                            value={formData.community_name}
                            onChange={handleChange}
                            required
                            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 outline-none transition-all"
                            placeholder="e.g. Tech Enthusiasts"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
                        <textarea
                            name="community_description"
                            value={formData.community_description}
                            onChange={handleChange}
                            rows="4"
                            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 outline-none transition-all resize-none"
                            placeholder="What is this community about?"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={mutation.isPending}
                        className="w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 rounded-lg transition-all shadow-lg shadow-blue-500/20 flex items-center justify-center gap-2"
                    >
                        {mutation.isPending ? (
                            <Loader2 className="animate-spin" size={20} />
                        ) : (
                            "Create Community"
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
}
