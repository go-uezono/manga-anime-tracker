import { Link, useNavigate } from "react-router-dom";
import { logout } from "../api/auth";
import "../styles/NavBar.css";

function NavBar() {
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate("/login");
    };

    return (
        <nav className="navbar">
            <div className="navbar-links">
                <Link to="/">My List</Link>
                <Link to="/search">Search</Link>
            </div>
            <button onClick={handleLogout}>Logout</button>
        </nav>
    );
}

export default NavBar;
