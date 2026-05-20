// useState for managing form state
import { useState } from "react"

// api functions from our services layer
import { login, register } from "../services/api"

// onLogin is a function passed from App.jsx
// we call it after successful login/register to tell App the user is in
function Auth({ onLogin }) {

  // true = show login form, false = show register form
  const [isLogin, setIsLogin] = useState(true)

  // email and password inputs
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  // error msg to show if login/register fails
  const [error, setError] = useState(null)

  // true while waiting for api response
  const [loading, setLoading] = useState(false)

  // called when user clicks the button or presses enter
  async function handleSubmit() {
    if (!email || !password) return
    setError(null)
    setLoading(true)

    try {
      // call login or register based on which tab is active
      const res = isLogin
        ? await login(email, password)
        : await register(email, password)

      // save token and email to localstorage
      // this is how the app remembers the user after a refresh
      localStorage.setItem("token", res.data.token)
      localStorage.setItem("email", res.data.email)

      // tell App.jsx the user logged in so it switches to the main screen
      onLogin(res.data.email)

    } catch (err) {
      // err.response?.data?.detail is the error message from fastapi
      // fallback to generic message if no detail
      setError(err.response?.data?.detail || "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-box">

        {/* app title */}
        <div className="app-header" style={{ marginBottom: "32px" }}>
          <h1>Finsnap</h1>
          <p>Understand your money in one page.</p>
        </div>

        {/* login / register tab switcher */}
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

        {/* email + password form */}
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

          {/* button text changes based on tab and loading state */}
          <button onClick={handleSubmit} style={{ marginTop: "8px" }}>
            {loading ? "..." : isLogin ? "Login" : "Create Account"}
          </button>

          {/* only shows if there was an error */}
          {error && <p className="error">{error}</p>}

        </div>
      </div>
    </div>
  )
}

export default Auth