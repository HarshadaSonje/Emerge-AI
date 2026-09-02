import { useState } from "react";
import { Eye, EyeOff, ShieldCheck, Activity, LockKeyhole } from "lucide-react";
import { login } from "../api/auth";

function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      await login(email, password);
      onLogin();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Invalid email or password."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-page">
      <div className="login-grid" aria-hidden="true"></div>
      <div className="login-shell">
        <section className="login-hero">
          <div className="login-brand">
            <div className="brand-mark">E</div>
            <div><strong>EMERGE-AI</strong><span>Emergency Response Intelligence</span></div>
          </div>
          <div className="login-hero-copy">
            <span className="login-kicker"><Activity size={14}/> LIVE EMERGENCY OPERATIONS</span>
            <h1>Respond faster.<br/>Coordinate smarter.</h1>
            <p>One command center for emergency intelligence, ambulance dispatch and live field operations.</p>
          </div>
          <div className="login-system-cards">
            <div><span className="status-dot"></span><strong>Systems online</strong><small>Real-time operations stream</small></div>
            <div><ShieldCheck size={22}/><strong>Secure access</strong><small>Role-based command center</small></div>
          </div>
        </section>

        <section className="login-card">
          <div className="login-heading">
            <span className="eyebrow">SECURE SIGN IN</span>
            <h2>Welcome back</h2>
            <p>Sign in to continue to the EMERGE-AI command center.</p>
          </div>

          <form onSubmit={handleSubmit}>
            <label htmlFor="login-email">Email address</label>
            <input id="login-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="name@organization.com" autoComplete="email" required />

            <label htmlFor="login-password">Password</label>
            <div className="password-field">
              <LockKeyhole size={17}/>
              <input id="login-password" type={showPassword ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter your password" autoComplete="current-password" required />
              <button type="button" className="password-toggle" onClick={() => setShowPassword(v => !v)} aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? <EyeOff size={17}/> : <Eye size={17}/>}</button>
            </div>

            {error && <div className="login-error">{error}</div>}

            <button className="login-submit" type="submit" disabled={loading}>
              {loading ? "Authenticating secure session…" : "Enter Command Center"}
            </button>
          </form>

          <div className="login-footer"><span className="status-dot"></span>SECURE EMERGENCY OPERATIONS PLATFORM</div>
        </section>
      </div>
    </main>
  );
}

export default Login;
