import { Link } from "react-router-dom";

function Footer() {
    return (
        <footer>
            <h3>PrePilot</h3>
            <p>
                Know your interview readiness before the real interview.
            </p>
            <p>
                <Link to="/">Home</Link>
                {" · "}
                <Link to="/login">Login</Link>
                {" · "}
                <Link to="/register">Register</Link>
            </p>
            <p>
                Readiness model: Random Forest classifier · 92.89% accuracy on a
                12,000-record held-out test set
            </p>
        </footer>
    );
}

export default Footer;
