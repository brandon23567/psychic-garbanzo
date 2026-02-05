import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Loader2, Trash2, MessageSquare, Send, Plus, LogOut } from 'lucide-react';
import { clsx } from 'clsx';
import { cn } from '../utils';

export default function CommunityDetails() {
    const { id: communityId } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const queryClient = useQueryClient();
    const [newPostContent, setNewPostContent] = useState('');
    const [activeCommentPostId, setActiveCommentPostId] = useState(null);

    // 1. Fetch Community Details (to show header, etc. - using list endpoint filter as there's no single detail endpoint?)
    // Actually, checking user routes, there IS NO single community detail endpoint in `community_routes.py`.
    // We only have `display_all_communities`. So we need to fetch all and find one. 
    // Optimization: In a real app we'd want a detail endpoint. For now, we filter.

    const { data: communities } = useQuery({
        queryKey: ['communities'],
        queryFn: async () => (await api.get('/community/')).data
    });

    const community = communities?.find(c => c.id === communityId);

    // 2. Fetch Joined Status
    const { data: joinedCommunities } = useQuery({
        queryKey: ['joined_communities'],
        queryFn: async () => (await api.get('/community/joined_communities')).data,
        enabled: !!user
    });

    const isJoined = joinedCommunities?.some(c => c.associated_community_id === communityId);

    // 3. Fetch Posts
    const { data: posts, isLoading: loadingPosts } = useQuery({
        queryKey: ['posts', communityId],
        queryFn: async () => (await api.get(`/app/${communityId}`)).data,
        enabled: !!communityId
    });

    // Mutations
    const joinMutation = useMutation({
        mutationFn: () => api.post(`/community/join_community/${communityId}`),
        onSuccess: () => {
            queryClient.invalidateQueries(['joined_communities']);
        }
    });

    const leaveMutation = useMutation({
        mutationFn: () => api.delete(`/community/leave/${communityId}`),
        onSuccess: () => {
            queryClient.invalidateQueries(['joined_communities']);
            navigate('/dashboard');
        }
    });

    const deleteCommunityMutation = useMutation({
        mutationFn: () => api.delete(`/community/${communityId}`),
        onSuccess: () => {
            queryClient.invalidateQueries(['communities']);
            navigate('/dashboard');
        }
    });

    const createPostMutation = useMutation({
        mutationFn: (body) => api.post(`/app/new/${communityId}?post_body=${encodeURIComponent(body)}`),
        onSuccess: () => {
            setNewPostContent('');
            queryClient.invalidateQueries(['posts', communityId]);
        }
    });
    // Note: the post endpoint takes query param `post_body` or body? 
    // Routes: `post_body: str` is a query param by default in FastAPI if not `Body()`.
    // Let's check `community_posts_routes.py`. It says `post_body: str`. Yes, likely query param. 
    // Wait, if it's `upload_new_post_to_community_route(..., post_body: str, ...)` without `Body(...)`, it's query param.
    // I should double check user code. 
    // Code: `post_body: str` -> Query param.

    const deletePostMutation = useMutation({
        mutationFn: (postId) => api.delete(`/app/${communityId}/${postId}`),
        onSuccess: () => {
            queryClient.invalidateQueries(['posts', communityId]);
        }
    });


    if (!community) return <div className="p-8 text-center">Loading Community...</div>;

    const isOwner = community.associated_user_id === user?.id;

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            {/* Header */}
            <div className="relative h-64 rounded-2xl overflow-hidden group">
                <img src={community.community_header_image} alt={community.community_name} className="w-full h-full object-cover" />
                <div className="absolute inset-0 bg-black/50 flex flex-col justify-end p-8">
                    <h1 className="text-4xl font-bold text-white mb-2">{community.community_name}</h1>
                    <p className="text-gray-200 text-lg opacity-90">{community.community_description}</p>
                </div>
            </div>

            {/* Actions Bar */}
            <div className="flex justify-between items-center bg-gray-900/50 p-4 rounded-xl border border-gray-800">
                <div className="text-gray-400 text-sm">
                    Created by {isOwner ? "You" : "User " + community.associated_user_id.slice(0, 8)}
                </div>
                <div className="flex gap-3">
                    {!isJoined ? (
                        <button
                            onClick={() => joinMutation.mutate()}
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium transition-colors"
                        >
                            Join Community
                        </button>
                    ) : (
                        <>
                            <button
                                onClick={() => leaveMutation.mutate()}
                                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-red-400 rounded-lg font-medium transition-colors flex items-center gap-2"
                            >
                                <LogOut size={16} /> Leave
                            </button>
                            {isOwner && (
                                <button
                                    onClick={() => {
                                        if (confirm("Are you sure you want to delete this community?")) deleteCommunityMutation.mutate();
                                    }}
                                    className="px-4 py-2 bg-red-900/20 hover:bg-red-900/40 text-red-400 rounded-lg font-medium transition-colors flex items-center gap-2 border border-red-900/50"
                                >
                                    <Trash2 size={16} /> Delete Community
                                </button>
                            )}
                        </>
                    )}
                </div>
            </div>

            {/* Create Post */}
            {isJoined && (
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                    <h3 className="text-lg font-semibold mb-4">Create a Post</h3>
                    <div className="flex gap-4">
                        <textarea
                            value={newPostContent}
                            onChange={(e) => setNewPostContent(e.target.value)}
                            placeholder="Share something with the community..."
                            className="flex-grow bg-gray-800 border border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 outline-none resize-none h-24"
                        />
                    </div>
                    <div className="flex justify-end mt-4">
                        <button
                            onClick={() => newPostContent.trim() && createPostMutation.mutate(newPostContent)}
                            disabled={!newPostContent.trim() || createPostMutation.isPending}
                            className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {createPostMutation.isPending ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} />}
                            Post
                        </button>
                    </div>
                </div>
            )}

            {/* Posts Feed */}
            <div className="space-y-6">
                <h2 className="text-2xl font-bold">Latest Posts</h2>
                {loadingPosts ? (
                    <div className="flex justify-center py-10"><Loader2 className="animate-spin text-blue-500" /></div>
                ) : posts?.length === 0 ? (
                    <div className="text-gray-500 text-center py-10">No posts yet. Be the first to share!</div>
                ) : (
                    posts?.map(post => (
                        <PostCard
                            key={post.id}
                            post={post}
                            communityId={communityId}
                            currentUser={user}
                            onDelete={() => deletePostMutation.mutate(post.id)}
                            activeCommentPostId={activeCommentPostId}
                            setActiveCommentPostId={setActiveCommentPostId}
                        />
                    ))
                )}
            </div>
        </div>
    );
}

function PostCard({ post, communityId, currentUser, onDelete, activeCommentPostId, setActiveCommentPostId }) {
    const queryClient = useQueryClient();
    const [commentBody, setCommentBody] = useState('');
    const showComments = activeCommentPostId === post.id;

    // Fetch Comments
    const { data: comments, isLoading: loadingComments } = useQuery({
        queryKey: ['comments', post.id],
        queryFn: async () => (await api.get(`/app/comments/${communityId}/${post.id}`)).data,
        enabled: showComments
    });

    const commentMutation = useMutation({
        mutationFn: (body) => api.post(`/app/add_comment/${communityId}/${post.id}/new?comment_body=${encodeURIComponent(body)}`),
        onSuccess: () => {
            setCommentBody('');
            queryClient.invalidateQueries(['comments', post.id]);
        }
    });

    const deleteCommentMutation = useMutation({
        mutationFn: (commentId) => api.delete(`/app/comment/${communityId}/${post.id}/${commentId}`),
        onSuccess: () => {
            queryClient.invalidateQueries(['comments', post.id]);
        }
    });

    const isAuthor = post.associated_user_id === currentUser?.id;

    return (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 transition-all hover:border-gray-700">
            <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                        {/* Avatar placeholder or user image if we had it in post schema */}
                        U
                    </div>
                    <div>
                        <div className="font-semibold text-white">User {post.associated_user_id.slice(0, 6)}</div>
                        <div className="text-xs text-gray-500">{new Date(post.date_posted).toLocaleString()}</div>
                    </div>
                </div>
                {isAuthor && (
                    <button onClick={onDelete} className="text-gray-500 hover:text-red-400 transition-colors p-2">
                        <Trash2 size={18} />
                    </button>
                )}
            </div>

            <p className="text-gray-200 mb-6 whitespace-pre-wrap leading-relaxed">{post.post_body}</p>

            <div className="flex items-center gap-4 pt-4 border-t border-gray-800">
                <button
                    onClick={() => setActiveCommentPostId(showComments ? null : post.id)}
                    className={cn(
                        "flex items-center gap-2 text-sm font-medium transition-colors px-3 py-1.5 rounded-lg",
                        showComments ? "bg-blue-900/30 text-blue-400" : "text-gray-400 hover:bg-gray-800 hover:text-white"
                    )}
                >
                    <MessageSquare size={18} />
                    {showComments ? "Hide Comments" : "Comments"}
                </button>
            </div>

            {/* Comments Section */}
            {showComments && (
                <div className="mt-4 pl-4 border-l-2 border-gray-800 space-y-4 animate-in slide-in-from-top-2 duration-200">
                    <div className="flex gap-3">
                        <input
                            type="text"
                            value={commentBody}
                            onChange={(e) => setCommentBody(e.target.value)}
                            placeholder="Write a comment..."
                            className="flex-grow bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                            onKeyDown={(e) => e.key === 'Enter' && commentBody.trim() && commentMutation.mutate(commentBody)}
                        />
                        <button
                            onClick={() => commentBody.trim() && commentMutation.mutate(commentBody)}
                            disabled={!commentBody.trim() || commentMutation.isPending}
                            className="bg-blue-600 hover:bg-blue-500 text-white p-2 rounded-lg disabled:opacity-50"
                        >
                            <Send size={16} />
                        </button>
                    </div>

                    <div className="space-y-3 mt-4">
                        {loadingComments ? (
                            <div className="text-center py-2"><Loader2 className="animate-spin inline" size={16} /></div>
                        ) : comments?.length === 0 ? (
                            <div className="text-gray-500 text-sm italic">No comments yet.</div>
                        ) : (
                            comments?.map(comment => (
                                <div key={comment.id} className="bg-gray-800/50 rounded-lg p-3 flex justify-between group">
                                    <div>
                                        <div className="text-xs text-blue-400 mb-1">User {comment.associated_user_id.slice(0, 6)}</div>
                                        <p className="text-sm text-gray-200">{comment.comment_body}</p>
                                    </div>
                                    {comment.associated_user_id === currentUser?.id && (
                                        <button
                                            onClick={() => deleteCommentMutation.mutate(comment.id)}
                                            className="text-gray-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                                        >
                                            <Trash2 size={14} />
                                        </button>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
