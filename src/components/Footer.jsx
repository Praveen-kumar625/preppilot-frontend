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
                Readiness model: Random Forest · 92.89% right on a test set
                of 12,000 records
            </p>
        </footer>
    );
}

export default Footer;
