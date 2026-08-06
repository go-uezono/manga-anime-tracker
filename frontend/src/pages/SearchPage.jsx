import { useState } from "react";
import { searchAnime, addAnime } from "../api/anime";
import { ANIME_STATUS, STATUS_LABELS } from "../constants";
import NavBar from "../components/NavBar";

function SearchPage() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [addedIds, setAddedIds] = useState(new Set());

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        setError("");

        try {
            const { data } = await searchAnime(query);
            setResults(data);
        } catch (err) {
            setError("Search failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleAdd = async (anilistId, status) => {
        try {
            await addAnime(anilistId, status);
            setAddedIds((prev) => new Set(prev).add(anilistId));
        } catch (err) {
            if (err.response?.status === 409) {
                setError("Already in your list.");
            } else {
                setError("Failed to add anime.");
            }
        }
    };

    return (
        <div>
            <NavBar />
            <h1>Search Anime</h1>
 
            <form onSubmit={handleSearch}>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search anime..."
                />
                <button type="submit" disabled={loading}>
                    {loading ? "Searching..." : "Search"}
                </button>
            </form>

            {error && <p style={{ color: "red" }}>{error}</p>}

            <div>
                {results.map((anime) => (
                    <div
                        key={anime.anilist_id}
                        style={{ display: "flex", gap: "1rem", alignItems: "center", marginBottom: "0.5rem" }}
                    >
                        <img src={anime.image_url} alt={anime.title} width="50" />
                        <span>{anime.title}</span>
                        <span>({anime.episodes || "?"})</span>

                        {addedIds.has(anime.anilist_id) ? ( 
                            <span>Added ✓</span>
                        ) : (
                            <select 
                                defaultValue=""
                                onChange={(e) => {
                                    if (e.target.value) {
                                        handleAdd(anime.anilist_id, e.target.value);
                                    }
                                }}
                            >
                                <option value="" disabled>Add as...</option>
                                {Object.values(ANIME_STATUS).map((status) => (
                                    <option key={status} value={status}>
                                        {STATUS_LABELS[status]}
                                    </option>
                                ))}
                            </select>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default SearchPage;
