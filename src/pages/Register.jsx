import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { isValidEmail, saveLocalUser } from "../lib/localUser";
import "./Auth.css";

function Register() {
    const navigate = useNavigate();
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");

    function handleSubmit(event) {
        event.preventDefault();
        if (name.trim().length < 2) {
            setError("Please enter your name.");
            return;
        }
        if (!isValidEmail(email.trim())) {
            setError("Please enter a valid email address.");
            return;
        }
        if (password.length < 8) {
            setError("Password must be at least 8 characters long.");
            return;
        }
        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }
        // There is no account server yet, so this sign-up stays only in
        // this browser. The password is never saved.
        saveLocalUser({ name: name.trim(), email: email.trim() });
        navigate("/");
    }

    return (
        <>
            <Navbar />
            <section className="auth">
                <div className="container">
                    <div className="auth-card card">
                        <h1>Create your account</h1>
                        <p className="auth-note">
                            PrePilot does not have an account server yet. This
                            form checks your details and keeps the sign-up
                            only in this browser - no account is made on any
                            server, and your password is never saved.
                        </p>
                        <form className="auth-form" onSubmit={handleSubmit} noValidate>
                            {error && (
                                <p className="auth-error" role="alert">
                                    {error}
                                </p>
                            )}
                            <label>
                                Full name
                                <input
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="Your name"
                                    autoComplete="name"
                                />
                            </label>
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
                                    placeholder="At least 8 characters"
                                    autoComplete="new-password"
                                />
                            </label>
                            <label>
                                Confirm password
                                <input
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    placeholder="Repeat your password"
                                    autoComplete="new-password"
                                />
                            </label>
                            <button type="submit" className="btn btn-primary">
                                Register
                            </button>
                        </form>
                        <p className="auth-switch">
                            Already registered? <Link to="/login">Login</Link>
                        </p>
                    </div>
                </div>
            </section>
            <Footer />
        </>
    );
}

export default Register;
