import client from "./client"

export const searchAnime = (query) =>
    client.get("/anime/search/", { params: { q: query } });

export const addAnime = (anilist_id, status) => 
    client.post("/anime/add/", { anilist_id, status });

export const listAnime = () => client.get("/anime/list/");

export const updateAnime = (id, data) => client.patch(`/anime/${id}/`, data);

export const deleteAnime = (id) => client.delete(`/anime/${id}/`);
