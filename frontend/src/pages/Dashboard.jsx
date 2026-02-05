import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';
import { PlusCircle, Users, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Dashboard() {
    const { user } = useAuth();
    const queryClient = useQueryClient();

    const { data: allCommunities, isLoading: loadingAll } = useQuery({
        queryKey: ['communities'],
        queryFn: async () => {
            const res = await api.get('/community/');
            return res.data;
        }
    });

    const { data: joinedCommunities, isLoading: loadingJoined } = useQuery({
        queryKey: ['joined_communities'],
        queryFn: async () => {
            const res = await api.get('/community/joined_communities');
            return res.data;
        },
        enabled: !!user
    });

    const joinMutation = useMutation({
        mutationFn: (communityId) => api.post(`/community/join_community/${communityId}`),
        onSuccess: () => {
            queryClient.invalidateQueries(['joined_communities']);
        }
    });

    const isJoined = (communityId) => {
        return joinedCommunities?.some(c => c.associated_community_id === communityId);
    };

    if (loadingAll || loadingJoined) {
        return (
            <div className="flex justify-center items-center h-[50vh]">
                <Loader2 className="animate-spin text-blue-500" size={40} />
            </div>
        );
    }

    return (
        <div className="space-y-10">
            {/* Header Section */}
            <div className="flex flex-col md:flex-row justify-between items-center gap-4 bg-gray-900/50 p-8 rounded-2xl border border-gray-800 backdrop-blur-sm">
                <div>
                    <h1 className="text-3xl font-bold text-white">Community Dashboard</h1>
                    <p className="text-gray-400 mt-2">Explore and manage your communities</p>
                </div>
                <Link
                    to="/create-community"
                    className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold transition-all shadow-lg shadow-blue-500/20"
                >
                    <PlusCircle size={20} />
                    Create Community
                </Link>
            </div>

            {/* Stats / Joined Section (Optional, maybe just list them prominently) */}
            {joinedCommunities?.length > 0 && (
                <section>
                    <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                        <Users className="text-purple-400" />
                        Your Communities
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {/* Filter allCommunities based on joined IDs to get details (Image, Name) 
                 Since joinedCommunities endpoint only returns IDs/dates, we need to map via allCommunities 
                 OR generic card if details missing. 
                 Wait, joined endpoint schema: associated_community_id. 
                 We don't get names there. We must match with allCommunities.
             */}
                        {joinedCommunities.map(joined => {
                            const community = allCommunities?.find(c => c.id === joined.associated_community_id);
                            if (!community) return null;
                            return (
                                <CommunityCard
                                    key={community.id}
                                    community={community}
                                    isJoined={true}
                                />
                            );
                        })}
                    </div>
                </section>
            )}

            {/* All Communities Section */}
            <section>
                <h2 className="text-2xl font-bold mb-6 text-gray-200">Explore Communities</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {allCommunities?.map((community) => (
                        <CommunityCard
                            key={community.id}
                            community={community}
                            isJoined={isJoined(community.id)}
                        />
                    ))}
                </div>
                {allCommunities?.length === 0 && (
                    <div className="text-center text-gray-500 py-12">
                        No communities found. Be the first to create one!
                    </div>
                )}
            </section>
        </div>
    );
}

function CommunityCard({ community, isJoined }) {
    return (
        <Link
            to={`/community/${community.id}`}
            className="group block bg-gray-900 border border-gray-800 rounded-xl overflow-hidden hover:border-blue-500/50 transition-all hover:shadow-xl hover:shadow-blue-500/10"
        >
            <div className="h-40 overflow-hidden relative">
                <img
                    src={community.community_header_image}
                    alt={community.community_name}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-gray-900 to-transparent opacity-60" />
            </div>
            <div className="p-5">
                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">
                    {community.community_name}
                </h3>
                <p className="text-gray-400 text-sm line-clamp-2 mb-4">
                    {community.community_description}
                </p>
                <div className="flex items-center justify-between mt-auto">
                    <span className="text-xs text-gray-500">
                        Created {new Date(community.date_created).toLocaleDateString()}
                    </span>
                    {isJoined && (
                        <span className="px-3 py-1 bg-green-900/30 text-green-400 text-xs rounded-full border border-green-800">
                            Joined
                        </span>
                    )}
                </div>
            </div>
        </Link>
    );
}
