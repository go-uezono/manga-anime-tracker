import axios from "axios";
import { API_BASE_URL, ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";

const client = axios.create({ baseURL: API_BASE_URL });

client.interceptors.request.use((config) => {
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

client.interceptors.response.use(
    (response) => response,
    async (error) => {
        const original = error.config;

        const isAuthEndpoint = original.url.includes("/token") || original.url.includes("/user/register");

        if (error.response?.status === 401 && !original._retry && !isAuthEndpoint) {
            original._retry = true;
            
            try {
                const refresh = localStorage.getItem(REFRESH_TOKEN);
                const { data } = await axios.post(`${API_BASE_URL}/token/refresh/`, { refresh });
                localStorage.setItem("access_token", data.access);
                original.header.Authorization = `Bearer ${data.access}`;
                return client(original);
            } catch {
                localStorage.clear();
                window.location.href = "/login";
            }
        }
        return Promise.reject(error);
    }
);

export default client;
