import { useState, useEffect } from "react";
import { listAnime, deleteAnime, updateAnime} from "../api/anime";
import { ANIME_STATUS, STATUS_LABELS } from "../constants";
import "../styles/ListPage.css"

function ListPage() {
    const [groupedAnime, setGroupedAnime] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [editingId, setEditingId] = useState(null);
    const [editStatus, setEditStatus] = useState("");
    const [editProgress, setEditProgress] = useState(0);

    useEffect(() => {
        fetchList();
    }, []);

    // Method to see user's list
    const fetchList = async () => {
        setLoading(true);
        setError("");

        try {
            const { data } = await listAnime();
            setGroupedAnime(data);
        } catch (err) {
            setError("Failed to load your list.");
        } finally {
            setLoading(false);
        }
    };

    // Method to delete anime in user's list
    const handleDelete = async (id) => {
        try {
            await deleteAnime(id);
            fetchList(); // Refresh after deleting an anime from list
        } catch (err) {
            setError("Failed to delete entry.");
        }
    };

    // Method to edit entry existing entry in user's list
    const startEditing = (entry) => {
        setEditingId(entry.id);
        setEditStatus(entry.status);
        setEditProgress(entry.progress);
    };

    // Method to cancel editing when user changes their mind
    const cancelEditing = () => {
        setEditingId(null);
    };

    // Method to save an edit made to an entry
    const saveEdit = async (id) => {
        try {
            await updateAnime(id, { status: editStatus, progress: Number(editProgress) });
            setEditingId(null);
            fetchList();
        } catch (err) {
            setError(err.response?.data?.progress?.[0] || "Failed to update entry.");
        }
    };

    if (loading) return <p>Loading...</p>;

    const franchiseNames = Object.keys(groupedAnime);

    return (
        <div className="list-page">
            <h1>My List</h1>

            {error && <p className="error-text">{error}</p>}
            {franchiseNames.length === 0 && (<p className="empty-message">Your list is empty. Go search for something to add!</p>)}

            {franchiseNames.length > 0 && (
                <table className="anime-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Image</th>
                            <th>Title</th>
                            <th>Status</th>
                            <th>Episodes</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {franchiseNames.map((franchiseName, franchiseIndex) => {
                            const groupEntries = groupedAnime[franchiseName];
                            const isFranchiseComplete = groupEntries.every (
                                (e) => e.status === "completed"
                            );

                            return (
                                <>
                                    <tr 
                                        key={`${franchiseName}-header`}
                                        className={
                                            isFranchiseComplete
                                            ? "franchise-row franchise-complete"
                                            : "franchise-row"
                                        }
                                    >                       
                                        <td colSpan={6}>
                                            {franchiseIndex + 1}. {franchiseName}
                                        </td>            
                                    </tr>
                                    {groupEntries.map((entry) => (
                                        <tr
                                            key={entry.id}
                                            className={entry.status === "completed" ? "row-complete" : ""}
                                        >
                                            <td></td>
                                            <td>
                                                <img
                                                    src={entry.anime.image_url}
                                                    alt={entry.anime.title}
                                                    width="50"
                                                />
                                            </td>
                                            <td>{entry.anime.title}</td>
                                            <td>
                                                {editingId === entry.id ? (
                                                    <select
                                                        value={editStatus}
                                                        onChange={(e) => setEditStatus(e.target.value)}
                                                    >
                                                        {Object.values(ANIME_STATUS).map((s) => (
                                                            <option key={s} value={s}>
                                                                {STATUS_LABELS[s]}
                                                            </option>
                                                        ))}
                                                    </select>
                                                ) : (
                                                    STATUS_LABELS[entry.status]
                                                )}
                                            </td>
                                            <td>
                                                {editingId === entry.id ? (
                                                    <>
                                                        <input 
                                                            type="number"
                                                            min="0"
                                                            max={entry.anime.episodes || undefined}
                                                            value={editProgress}
                                                            onChange={(e) => setEditProgress(e.target.value)}
                                                        />
                                                        {" / "}
                                                        {entry.anime.episodes || "?"}
                                                    </>
                                                ) : (
                                                    `${entry.progress}/${entry.anime.episodes || "?"}`
                                                )}
                                            </td>
                                            <td>
                                                {editingId === entry.id ? (
                                                    <>
                                                        <button 
                                                            className="primary"
                                                            onClick={() => saveEdit(entry.id)}
                                                        >
                                                            Save
                                                        </button>
                                                        <button onClick={cancelEditing}>Cancel</button>
                                                    </>
                                                ) : (
                                                    <>
                                                        <button onClick={() => startEditing(entry)}>Edit</button>
                                                        <button 
                                                            className="danger" onClick={() => handleDelete(entry.id)}
                                                        >Delete</button>
                                                    </>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </>
                            );
                        })}
                    </tbody>
                </table>
            )}
        </div>
    );
}

export default ListPage;
