import client from "./client";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";

export const register = (username, password) =>
    client.post("user/register/", { username, password });

export const login = async (username, password) => {
    const { data } = await client.post("/token/", { username, password });
    localStorage.setItem(ACCESS_TOKEN, data.access);
    localStorage.setItem(REFRESH_TOKEN, data.refresh);
    return data;
};

export const logout = () => {
    localStorage.removeItem(ACCESS_TOKEN);
    localStorage.removeItem(REFRESH_TOKEN);
};

export const isAuthenticated = () => !!localStorage.getItem(ACCESS_TOKEN);
