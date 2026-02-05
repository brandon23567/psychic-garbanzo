import { Link } from 'react-router-dom';

export default function Home() {
    return (
        <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-6">
            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
                Welcome to Community Platform
            </h1>
            <p className="text-gray-400 text-xl max-w-2xl">
                Discover, create, and join communities that matter to you. Connect with like-minded people in a premium, secure environment.
            </p>
            <Link
                to="/dashboard"
                className="px-8 py-3 bg-blue-600 hover:bg-blue-700 rounded-full font-semibold transition-all transform hover:scale-105 shadow-lg shadow-blue-500/30"
            >
                Go to Dashboard
            </Link>
        </div>
    );
}
