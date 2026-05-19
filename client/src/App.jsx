import { useState, useEffect } from "react"
import Papa from "papaparse"
import "./App.css"
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts"
import Auth from "./pages/Auth"
import { classifyAndSave, getTransactions, submitFeedback, deleteTransaction } from "./services/api"

const COLORS = [
  "#4A7FA0", "#7BADC8", "#8B7355", "#5A8F7A",
  "#9B7EA0", "#7A8FA0", "#A07A5A", "#5A7A8F"
]

function App() {

  const [user, setUser] = useState(null)
  const [description, setDescription] = useState("")
  const [amount, setAmount] = useState("")
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [correctingId, setCorrectingId] = useState(null)
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7))

  // filters transactions to only show selected month
  const filteredTransactions = transactions.filter(t => {
    if (!t.date) return true
    return t.date.slice(0, 7) === selectedMonth
  })

  const CATEGORIES = [
    "Groceries", "Dining and Cafes", "Shopping & Retail",
    "Fuel and Transport", "Housing and Utilities", "Telecom",
    "Medical and Health", "Education", "Entertainment and Leisure",
    "Travel and Hotels", "Bank Charges", "Insurance",
    "Savings and Investments", "Loan Payments", "Rent Payments",
    "Charity Donations", "Other / Uncategorized"
  ]

  useEffect(() => {
    const token = localStorage.getItem("token")
    const email = localStorage.getItem("email")
    if (token && email) {
      setUser(email)
      loadTransactions()
    }
  }, [])

  async function loadTransactions() {
    try {
      const res = await getTransactions()
      setTransactions(res.data)
    } catch (err) {
      console.error("Failed to load transactions", err)
    }
  }

  function handleLogin(email) {
    setUser(email)
    loadTransactions()
  }

  function handleLogout() {
    localStorage.removeItem("token")
    localStorage.removeItem("email")
    setUser(null)
    setTransactions([])
  }

  // uses filteredTransactions so chart reflects selected month
  function getChartData() {
    const totals = {}
    filteredTransactions.forEach(t => {
      totals[t.category] = (totals[t.category] || 0) + Math.abs(t.amount)
    })
    return Object.entries(totals).map(([name, value]) => ({
      name,
      value: parseFloat(value.toFixed(2))
    }))
  }

  async function classifyTransaction() {
    if (!description || !amount) return
    try {
      setLoading(true)
      const res = await classifyAndSave(description, parseFloat(amount), date)
      setTransactions(prev => [...prev, res.data])
      setDescription("")
      setAmount("")
    } catch (err) {
      setError("Error classifying transaction")
    } finally {
      setLoading(false)
    }
  }

  async function handleCSVUpload(e) {
    const file = e.target.files[0]
    if (!file) return
    const today = new Date().toISOString().split('T')[0]
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: async (results) => {
        for (const row of results.data) {
          const desc = row.description || row.Description || row.DESCRIPTION
          const amt = row.amount || row.Amount || row.AMOUNT
          const rowDate = row.date || row.Date || today
          if (!desc || !amt || isNaN(parseFloat(amt))) continue
          try {
            const res = await classifyAndSave(desc, parseFloat(amt), rowDate)
            setTransactions(prev => [...prev, res.data])
          } catch (err) {
            console.error("Failed to classify:", desc)
          }
        }
      }
    })
  }

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

  async function handleDelete(transactionId) {
    try {
      await deleteTransaction(transactionId)
      setTransactions(prev => prev.filter(t => t.id !== transactionId))
    } catch (err) {
      console.error("Failed to delete", err)
    }
  }

  if (!user) {
    return <Auth onLogin={handleLogin} />
  }

  return (
    <div className="app">

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
        <input
          type="date"
          value={date}
          onChange={e => setDate(e.target.value)}
          style={{ flex: "0 0 auto" }}
        />
        <button onClick={classifyTransaction}>
          {loading ? "Classifying..." : "Classify"}
        </button>
      </div>

      <div style={{ margin: "0 0 24px", display: "flex", alignItems: "center", gap: "12px" }}>
        <label style={{ fontSize: "13px", color: "var(--text-dim)", cursor: "pointer", padding: "8px 16px", border: "1px dashed var(--border)", borderRadius: "6px" }}>
          Upload CSV
          <input type="file" accept=".csv" onChange={handleCSVUpload} style={{ display: "none" }} />
        </label>
        <span style={{ fontSize: "12px", color: "var(--text-pale)" }}>
          CSV needs "description" and "amount" columns
        </span>
      </div>

      {/* month filter */}
      {transactions.length > 0 && (
        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "16px" }}>
          <span style={{ fontSize: "11px", color: "var(--text-pale)", letterSpacing: "1.5px", textTransform: "uppercase" }}>Month</span>
          <input
            type="month"
            value={selectedMonth}
            onChange={e => setSelectedMonth(e.target.value)}
            style={{ fontSize: "13px", padding: "6px 12px", border: "1px solid var(--border2)", borderRadius: "6px", background: "var(--panel2)", color: "var(--text)", outline: "none" }}
          />
          <span style={{ fontSize: "12px", color: "var(--text-pale)" }}>
            {filteredTransactions.length} transactions
          </span>
        </div>
      )}

      {/* summary bar - uses filteredTransactions */}
      {filteredTransactions.length > 0 && (
        <div className="summary-bar">
          <div className="summary-chip">
            <strong>{filteredTransactions.length}</strong> transactions
          </div>
          <div className="summary-chip">
            Total spent: <strong>
              ${filteredTransactions.reduce((sum, t) => sum + Math.abs(t.amount), 0).toFixed(2)}
            </strong>
          </div>
        </div>
      )}

      {/* donut chart - uses filteredTransactions via getChartData */}
      {filteredTransactions.length > 0 && (
        <div style={{ margin: "28px 0" }}>
          <p className="section-label">Spending Breakdown</p>
          <div style={{ background: "var(--panel2)", border: "1px solid var(--border2)", borderRadius: "10px", padding: "24px", boxShadow: "0 1px 6px var(--shadow2)" }}>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={getChartData()} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={3} dataKey="value">
                  {getChartData().map((entry, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `$${value}`} />
              </PieChart>
            </ResponsiveContainer>
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

      {filteredTransactions.length > 0 && (
        <p className="section-label">Recent Transactions</p>
      )}

      <div className="transaction-list">
        {filteredTransactions.length === 0 ? (
          <div className="empty-state">
            <p>{transactions.length === 0 ? "Add your first transaction above" : "No transactions for this month"}</p>
          </div>
        ) : (
          filteredTransactions.map((t, i) => (
            <div key={t.id || i} className="transaction-card">
              <span className="t-desc">{t.description}</span>

              <span style={{ fontSize: "11px", color: "var(--text-pale)", minWidth: "80px" }}>
                {t.date ? new Date(t.date).toLocaleDateString("en-CA") : ""}
              </span>

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

              {t.id && (
                <button
                  onClick={() => handleDelete(t.id)}
                  style={{
                    padding: "3px 10px",
                    fontSize: "11px",
                    background: "none",
                    color: "var(--text-pale)",
                    border: "1px solid var(--border2)",
                    borderRadius: "4px",
                    cursor: "pointer"
                  }}
                >
                  ×
                </button>
              )}
            </div>
          ))
        )}
      </div>

      {error && <p className="error">{error}</p>}

    </div>
  )
}

export default App