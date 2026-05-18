// useState for state management, useEffect to run stuff on load
import { useState, useEffect } from "react"

// papaparse to read csv files
import Papa from "papaparse"

import "./App.css"

// recharts stuff for the donut chart
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts"

// auth page - shows when not logged in
import Auth from "./pages/Auth"

// all api calls go thru here instead of writing fetch everywhere
import { classifyAndSave, getTransactions, submitFeedback } from "./services/api"

// colors for the chart slices
const COLORS = [
  "#4A7FA0", "#7BADC8", "#8B7355", "#5A8F7A",
  "#9B7EA0", "#7A8FA0", "#A07A5A", "#5A7A8F"
]

function App() {

  // null = not logged in, string = logged in (holds email)
  const [user, setUser] = useState(null)

  // what user types in description box
  const [description, setDescription] = useState("")

  // what user types in amount box
  const [amount, setAmount] = useState("")

  // all transactions for this user, loaded from db on login
  const [transactions, setTransactions] = useState([])

  // true while waiting for api to respond
  const [loading, setLoading] = useState(false)

  // holds error msg if something breaks
  const [error, setError] = useState(null)

  // id of transaction being corrected rn, null if none
  const [correctingId, setCorrectingId] = useState(null)

  // all the spending categories for the correction dropdown
  const CATEGORIES = [
    "Groceries", "Dining and Cafes", "Shopping & Retail",
    "Fuel and Transport", "Housing and Utilities", "Telecom",
    "Medical and Health", "Education", "Entertainment and Leisure",
    "Travel and Hotels", "Bank Charges", "Insurance",
    "Savings and Investments", "Loan Payments", "Rent Payments",
    "Charity Donations", "Other / Uncategorized"
  ]

  // runs once when app loads
  // checks if user was already logged in from last session
  useEffect(() => {
    const token = localStorage.getItem("token")
    const email = localStorage.getItem("email")
    if (token && email) {
      // token found so restore their session
      setUser(email)
      loadTransactions()
    }
  }, [])

  // hits GET /transactions and loads the users history from db
  async function loadTransactions() {
    try {
      const res = await getTransactions()
      setTransactions(res.data)
    } catch (err) {
      console.error("Failed to load transactions", err)
    }
  }

  // auth component calls this after login/register succeeds
  function handleLogin(email) {
    setUser(email)
    loadTransactions()
  }

  // wipes token from localstorage and resets everything
  function handleLogout() {
    localStorage.removeItem("token")
    localStorage.removeItem("email")
    setUser(null)
    setTransactions([])
  }

  // groups transactions by category and adds up amounts
  // recharts needs [{name, value}] format
  function getChartData() {
    const totals = {}
    transactions.forEach(t => {
      totals[t.category] = (totals[t.category] || 0) + Math.abs(t.amount)
    })
    return Object.entries(totals).map(([name, value]) => ({
      name,
      value: parseFloat(value.toFixed(2))
    }))
  }

  // sends one transaction to POST /transactions
  // backend classifies it with the ml model and saves to db
  async function classifyTransaction() {
    if (!description || !amount) return
    try {
      setLoading(true)
      const res = await classifyAndSave(description, parseFloat(amount))
      // append new transaction to list using the id from db
      setTransactions(prev => [...prev, res.data])
      setDescription("")
      setAmount("")
    } catch (err) {
      setError("Error classifying transaction")
    } finally {
      setLoading(false)
    }
  }

  // reads csv file row by row and classifies each one
  async function handleCSVUpload(e) {
    const file = e.target.files[0]
    if (!file) return
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: async (results) => {
        for (const row of results.data) {
          // handle different column name capitalizations
          const desc = row.description || row.Description || row.DESCRIPTION
          const amt = row.amount || row.Amount || row.AMOUNT
          if (!desc || !amt || isNaN(parseFloat(amt))) continue
          try {
            const res = await classifyAndSave(desc, parseFloat(amt))
            setTransactions(prev => [...prev, res.data])
          } catch (err) {
            console.error("Failed to classify:", desc)
          }
        }
      }
    })
  }

  // sends correction to POST /feedback
  // updates the category in local state right away so ui feels instant
  async function handleCorrection(transactionId, newCategory) {
    try {
      await submitFeedback(transactionId, newCategory)
      setTransactions(prev => prev.map(t =>
        t.id === transactionId ? { ...t, category: newCategory } : t
      ))
      setCorrectingId(null)
    } catch (err) {
      console.error("Failed to submit correction", err)
    }
  }

  // show login/register screen if not logged in
  if (!user) {
    return <Auth onLogin={handleLogin} />
  }

  return (
    <div className="app">

      {/* header - shows email and logout button */}
      <div className="app-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1>Transaction Coach</h1>
          <p>Classify your spending. Understand your money.</p>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: "12px", color: "var(--text-dim)", marginBottom: "6px" }}>{user}</div>
          <button
            onClick={handleLogout}
            style={{ padding: "6px 14px", fontSize: "11px", background: "none", color: "var(--text-dim)", border: "1px solid var(--border2)", borderRadius: "4px", cursor: "pointer" }}
          >
            Logout
          </button>
        </div>
      </div>

      {/* description + amount + classify button */}
      <div className="input-row">
        <input
          type="text"
          placeholder="Transaction description"
          value={description}
          onChange={e => setDescription(e.target.value)}
        />
        <input
          type="number"
          placeholder="Amount"
          value={amount}
          onChange={e => setAmount(e.target.value)}
        />
        <button onClick={classifyTransaction}>
          {loading ? "Classifying..." : "Classify"}
        </button>
      </div>

      {/* csv upload - file input hidden behind the label */}
      <div style={{ margin: "0 0 24px", display: "flex", alignItems: "center", gap: "12px" }}>
        <label style={{ fontSize: "13px", color: "var(--text-dim)", cursor: "pointer", padding: "8px 16px", border: "1px dashed var(--border)", borderRadius: "6px" }}>
          Upload CSV
          <input type="file" accept=".csv" onChange={handleCSVUpload} style={{ display: "none" }} />
        </label>
        <span style={{ fontSize: "12px", color: "var(--text-pale)" }}>
          CSV needs "description" and "amount" columns
        </span>
      </div>

      {/* summary chips - only shows when there are transactions */}
      {transactions.length > 0 && (
        <div className="summary-bar">
          <div className="summary-chip">
            <strong>{transactions.length}</strong> transactions
          </div>
          <div className="summary-chip">
            {/* reduce loops thru all transactions and adds up amounts */}
            Total spent: <strong>
              ${transactions.reduce((sum, t) => sum + Math.abs(t.amount), 0).toFixed(2)}
            </strong>
          </div>
        </div>
      )}

      {/* donut chart - only shows when there are transactions */}
      {transactions.length > 0 && (
        <div style={{ margin: "28px 0" }}>
          <p className="section-label">Spending Breakdown</p>
          <div style={{ background: "var(--panel2)", border: "1px solid var(--border2)", borderRadius: "10px", padding: "24px", boxShadow: "0 1px 6px var(--shadow2)" }}>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={getChartData()} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={3} dataKey="value">
                  {/* one colored slice per category */}
                  {getChartData().map((entry, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                {/* tooltip shows dollar amount on hover */}
                <Tooltip formatter={(value) => `$${value}`} />
              </PieChart>
            </ResponsiveContainer>

            {/* custom legend below chart */}
            <div style={{ display: "flex", flexWrap: "wrap", gap: "10px", marginTop: "16px", justifyContent: "center" }}>
              {getChartData().map((entry, index) => (
                <div key={index} style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px", color: "var(--text-dim)" }}>
                  <div style={{ width: "10px", height: "10px", borderRadius: "50%", background: COLORS[index % COLORS.length], flexShrink: 0 }} />
                  {entry.name}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* section label */}
      {transactions.length > 0 && (
        <p className="section-label">Recent Transactions</p>
      )}

      {/* transaction list */}
      <div className="transaction-list">
        {transactions.length === 0 ? (
          <div className="empty-state">
            <p>Add your first transaction above</p>
          </div>
        ) : (
          transactions.map((t, i) => (
            <div key={t.id || i} className="transaction-card">
              <span className="t-desc">{t.description}</span>

              {/* if this transaction is being corrected show dropdown otherwise show badge */}
              {correctingId === t.id ? (
                <select
                  style={{ fontSize: "12px", padding: "4px 8px", border: "1px solid var(--blue)", borderRadius: "4px", background: "var(--panel2)", color: "var(--blue-dark)" }}
                  defaultValue={t.category}
                  onChange={e => handleCorrection(t.id, e.target.value)}
                >
                  {CATEGORIES.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              ) : (
                // click the badge to start correcting
                <span
                  className="t-category"
                  onClick={() => t.id && setCorrectingId(t.id)}
                  style={{ cursor: t.id ? "pointer" : "default" }}
                  title={t.id ? "Click to correct" : ""}
                >
                  {t.category}
                </span>
              )}

              <span className="t-amount">${Math.abs(t.amount).toFixed(2)}</span>
            </div>
          ))
        )}
      </div>

      {/* error msg if something went wrong */}
      {error && <p className="error">{error}</p>}

    </div>
  )
}

export default App