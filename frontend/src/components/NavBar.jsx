import { Link, useNavigate } from "react-router-dom";
import { logout } from "../api/auth";

function NavBar() {
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    return (
        <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
            <div style={{ display: "flex", gap: "1rem" }}>
                <Link to="/">My List</Link>
                <Link to="/search">Search</Link>
            </div>
            <button onClick={handleLogout}>Logout</button>
        </nav>
    );
}

export default NavBar;
