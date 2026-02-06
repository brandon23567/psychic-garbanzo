import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    withCredentials: true,
});

api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        // If error is 401 and we haven't retried yet
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                // Attempt to refresh token
                await api.post('/auth/refresh');

                // Retry original request
                return api(originalRequest);
            } catch (refreshError) {
                // If refresh fails, redirect to login
                console.error("Token refresh failed:", refreshError);
                // window.location.href = '/signin'; // Removed to prevent infinite loop
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

export default api;
