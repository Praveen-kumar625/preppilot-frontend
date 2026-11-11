import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { clearLocalUser, getLocalUser, isValidEmail, saveLocalUser } from "../lib/localUser";
import "./Auth.css";

function Login() {
    const navigate = useNavigate();
    const [user, setUser] = useState(() => getLocalUser());
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    function handleSubmit(event) {
        event.preventDefault();
        if (!isValidEmail(email.trim())) {
            setError("Please enter a valid email address.");
            return;
        }
        if (password.length === 0) {
            setError("Please enter your password.");
            return;
        }
        // There is no account server yet, so this login stays only in
        // this browser. It never says a server login happened.
        saveLocalUser({ email: email.trim() });
        navigate("/");
    }

    function handleSignOut() {
        clearLocalUser();
        setUser(null);
    }

    return (
        <>
            <Navbar />
            <section className="auth">
                <div className="container">
                    <div className="auth-card card">
                        {user ? (
                            <div className="auth-user">
                                <h1>Welcome back</h1>
                                <p>
                                    You are signed in on this device as{" "}
                                    <strong>{user.email}</strong>. This is a
                                    browser-only sign-in - PrePilot does not
                                    have an account server yet.
                                </p>
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={handleSignOut}
                                >
                                    Sign out of this device
                                </button>
                            </div>
                        ) : (
                            <>
                                <h1>Login</h1>
                                <p className="auth-note">
                                    PrePilot does not have an account server
                                    yet. This form checks your details and
                                    keeps the login only in this browser -
                                    no account is made or checked on any
                                    server.
                                </p>
                                <form className="auth-form" onSubmit={handleSubmit} noValidate>
                                    {error && (
                                        <p className="auth-error" role="alert">
                                            {error}
                                        </p>
                                    )}
                                    <label>
                                        Email
                                        <input
                                            type="email"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="you@example.com"
                                            autoComplete="email"
                                        />
                                    </label>
                                    <label>
                                        Password
                                        <input
                                            type="password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            placeholder="Your password"
                                            autoComplete="current-password"
                                        />
                                    </label>
                                    <button type="submit" className="btn btn-primary">
                                        Login
                                    </button>
                                </form>
                                <p className="auth-switch">
                                    New to PrePilot?{" "}
                                    <Link to="/register">Create an account</Link>
                                </p>
                            </>
                        )}
                    </div>
                </div>
            </section>
            <Footer />
        </>
    );
}

export default Login;
