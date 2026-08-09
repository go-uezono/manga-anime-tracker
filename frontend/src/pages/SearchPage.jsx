import { useState, useEffect } from "react";
import { searchAnime, addAnime, getRecentAnime } from "../api/anime";
import { ANIME_STATUS, STATUS_LABELS } from "../constants";
import "../styles/SearchPage.css";

function SearchPage() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [addedIds, setAddedIds] = useState(new Set());
    const [pendingStatus, setPendingStatus] = useState({});
    const [pendingProgress, setPendingProgress] = useState({});
    const [recentAnime, setRecentAnime] = useState([]);
    const [activeRecentId, setActiveRecentId] = useState(null);

    useEffect(() => {
        getRecentAnime()
            .then(({ data }) => setRecentAnime(data))
            .catch(() => {});
    }, []);

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

    const handleAdd = async (anime) => {
        const status = pendingStatus[anime.anilist_id] || "planned";
        const progress = status === "completed" ? anime.episodes : Number(pendingProgress[anime.anilist_id] || 0);

        if (anime.episodes && progress > anime.episodes) {
            setError(`Progress can't exceed ${anime.episodes} episodes.`);
            return;
        }

        try {
            await addAnime(anime.anilist_id, status, progress);
            setAddedIds((prev) => new Set(prev).add(anime.anilist_id));
        } catch (err) {
            if (err.response?.status === 409) {
                setError("Already in your list.");
            } else {
                setError(err.response?.data?.error || "Failed to add anime.");
            }
        }
    };

    const renderAddControls = (anime) => {
        const status = pendingStatus[anime.anilist_id] || "planned";
        return (
            <>
                <select
                    value={status}
                    onChange={(e) =>
                        setPendingStatus((prev) => ({ ...prev, [anime.anilist_id]: e.target.value }))
                    }
                >
                    {Object.values(ANIME_STATUS).map((s) => (
                        <option key={s} value={s}>{STATUS_LABELS[s]}</option>
                    ))}
                </select>

                {status === "watching" && (
                    <input
                        type="number"
                        min="0"
                        max={anime.episodes || undefined}
                        value={pendingProgress[anime.anilist_id] || 0}
                        onChange={(e) =>
                            setPendingProgress((prev) => ({ ...prev, [anime.anilist_id]: e.target.value }))
                        }
                    />
                )}

                <button className="primary" onClick={() => handleAdd(anime)}>Add</button>
            </>
        );
    };

    return (
        <div className="search-page">
            <h1>Search Anime</h1>

            <form className="search-form" onSubmit={handleSearch}>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search anime..."
                />
                <button type="submit" className="primary" disabled={loading}>
                    {loading ? "Searching..." : "Search"}
                </button>
            </form>

            {error && <p className="error-text">{error}</p>}

            {results.length === 0 && recentAnime.length > 0 && (
                <div className="recent-section">
                    <h2>Recently Airing</h2>
                    <div className="recent-grid">
                        {recentAnime.map((anime) => (
                            <div key={anime.anilist_id} className="recent-card">
                                {addedIds.has(anime.anilist_id) ? (
                                    <>
                                        <img src={anime.image_url} alt={anime.title} />
                                        <span>{anime.title}</span>
                                        <span>Added ✓</span>
                                    </>
                                ) : activeRecentId === anime.anilist_id ? (
                                    <>
                                        <img src={anime.image_url} alt={anime.title} />
                                        <span>{anime.title}</span>
                                        <div className="recent-card-controls">
                                            {renderAddControls(anime)}
                                        </div>
                                    </>
                                ) : (
                                    <button
                                        className="recent-card-trigger"
                                        onClick={() => setActiveRecentId(anime.anilist_id)}
                                    >
                                        <img src={anime.image_url} alt={anime.title} />
                                        <span>{anime.title}</span>
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="search-results">
                {results.map((anime) => (
                    <div key={anime.anilist_id} className="result-row">
                        <img src={anime.image_url} alt={anime.title} width="50" />
                        <span className="result-title">{anime.title} ({anime.episodes || "?"} eps)</span>
                        {addedIds.has(anime.anilist_id) ? <span>Added ✓</span> : renderAddControls(anime)}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default SearchPage;