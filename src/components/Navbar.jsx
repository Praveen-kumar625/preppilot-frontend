import { Link } from "react-router-dom";

function Navbar() {
    return (
        <nav>
            <h2>
                <Link to="/">PrePilot</Link>
            </h2>

            <div>
                <Link to="/">Home</Link>
                <a href="/#features">Features</a>
                <a href="/#predictor">Readiness Check</a>
                <Link to="/login">
                    <button type="button">Login</button>
                </Link>
            </div>
        </nav>
    );
}

export default Navbar;
