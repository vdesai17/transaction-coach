import { useState } from "react"
import { login, register } from "../services/api"

function Auth({ onLogin }) {

  // toggle between login and register forms
  const [isLogin, setIsLogin] = useState(true)

  // form fields
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  // error and loading states
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit() {
    if (!email || !password) return
    setError(null)
    setLoading(true)

    try {
      // call login or register depending on which form is showing
      const res = isLogin
        ? await login(email, password)
        : await register(email, password)

      // save token to localStorage so it persists across refreshes
      localStorage.setItem("token", res.data.token)
      localStorage.setItem("email", res.data.email)

      // tell parent component the user is now logged in
      onLogin(res.data.email)

    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-box">

        <div className="app-header" style={{ marginBottom: "32px" }}>
          <h1>Transaction Coach</h1>
          <p>Classify your spending. Understand your money.</p>
        </div>

        {/* tab switcher */}
        <div className="auth-tabs">
          <button
            className={`auth-tab ${isLogin ? "active" : ""}`}
            onClick={() => { setIsLogin(true); setError(null); }}
          >
            Login
          </button>
          <button
            className={`auth-tab ${!isLogin ? "active" : ""}`}
            onClick={() => { setIsLogin(false); setError(null); }}
          >
            Register
          </button>
        </div>

        {/* form */}
        <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "24px" }}>
          <div>
            <label className="form-label" style={{ fontSize: "11px", letterSpacing: "1.5px", color: "var(--text-dim)", marginBottom: "5px", display: "block", textTransform: "uppercase" }}>
              Email
            </label>
            <input
              type="email"
              placeholder="your@email.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label className="form-label" style={{ fontSize: "11px", letterSpacing: "1.5px", color: "var(--text-dim)", marginBottom: "5px", display: "block", textTransform: "uppercase" }}>
              Password
            </label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSubmit()}
            />
          </div>

          <button
            onClick={handleSubmit}
            style={{ marginTop: "8px" }}
          >
            {loading ? "..." : isLogin ? "Login" : "Create Account"}
          </button>

          {error && <p className="error">{error}</p>}
        </div>

      </div>
    </div>
  )
}

export default Auth