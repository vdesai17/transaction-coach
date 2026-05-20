import { useState, useEffect } from "react"
import Papa from "papaparse"
import "./App.css"
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts"
import Auth from "./pages/Auth"
import { classifyAndSave, getTransactions, submitFeedback, deleteTransaction, retrainModel } from "./services/api"

const COLORS = [
  "#3B82F6", "#8B5CF6", "#10B981", "#F59E0B", "#EF4444", "#06B6D4",
  "#EC4899", "#6366F1", "#F97316", "#14B8A6", "#A855F7", "#84CC16",
  "#F43F5E", "#0EA5E9", "#D97706", "#7C3AED", "#059669", "#DC2626",
  "#0891B2", "#9333EA", "#65A30D", "#B45309", "#E11D48"
]

function App() {

  const [user, setUser] = useState(null)
  const [description, setDescription] = useState("")
  const [amount, setAmount] = useState("")
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [correctingId, setCorrectingId] = useState(null)
  const [pendingCategory, setPendingCategory] = useState("")
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7))
  const [isDark, setIsDark] = useState(() => (localStorage.getItem("theme") || "dark") === "dark")
  const [csvProgress, setCsvProgress] = useState(null) // null | { done, total }
  const [retraining, setRetraining] = useState(false)
  const [retrainMsg, setRetrainMsg] = useState(null)

  useEffect(() => {
    const theme = isDark ? "dark" : "light"
    document.documentElement.setAttribute("data-theme", theme)
    localStorage.setItem("theme", theme)
  }, [isDark])

  // filters transactions to only show selected month
  const filteredTransactions = transactions.filter(t => {
  if (!t.date) return false  // hide transactions with no date
  return t.date.slice(0, 7) === selectedMonth
})

  const CATEGORIES = [
    "Bank Charges", "Business or Freelance Income", "Charity Donations",
    "Dining and Cafes", "Education", "Entertainment and Leisure",
    "Fuel and Transport", "Government Services", "Government Support and Pensions",
    "Groceries", "Home Goods and Furniture", "Housing and Utilities",
    "Insurance", "Loan Payments", "Medical and Health",
    "Other / Uncategorized", "Rent Payments", "Salary / Payroll",
    "Savings and Investments", "Shopping & Retail", "Telecom",
    "Travel and Hotels", "Vehicle Loans and Fines"
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

 function getTrendData() {
  const monthTotals = {}
  transactions.forEach(t => {
    if (!t.date) return
    const month = t.date.slice(0, 7)
    monthTotals[month] = (monthTotals[month] || 0) + Math.abs(t.amount)
  })
  return Object.entries(monthTotals)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([month, total]) => ({
      month,
      total: parseFloat(total.toFixed(2))
    }))
}

 async function classifyTransaction() {
  if (!description || !amount) return
  try {
    setLoading(true)
    console.log("sending date:", date)
    const res = await classifyAndSave(description, parseFloat(amount), date)
    console.log("response:", res.data)
    setTransactions(prev => [...prev, res.data])
    setDescription("")
    setAmount("")
  } catch (err) {
    setError("Error classifying transaction")
  } finally {
    setLoading(false)
  }
}

  function normalizeDate(raw) {
    if (!raw) return new Date().toISOString().split('T')[0]
    const s = String(raw).trim()
    if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s
    if (/^\d{4}\/\d{2}\/\d{2}$/.test(s)) return s.replace(/\//g, '-')
    const d = new Date(s)
    if (!isNaN(d)) return d.toISOString().split('T')[0]
    return new Date().toISOString().split('T')[0]
  }

  function parseBankRow(row) {
    // ── Description ──
    // RBC has two description columns — combine them
    const desc1 = row["Description 1"] || row["description 1"] || ""
    const desc2 = row["Description 2"] || row["description 2"] || ""
    const rbcDesc = [desc1, desc2].filter(Boolean).join(" ").trim()

    const desc =
      rbcDesc ||
      row.Description || row.description || row.DESCRIPTION ||
      row.Payee        || row.payee       ||
      row.Name         || row.name        ||
      row.Merchant     || row.merchant    ||
      row.Transaction  || row.transaction ||
      row.Memo         || row.memo        ||
      ""

    if (!desc) return null

    // ── Amount ──
    // Single-column banks (BMO, Tangerine, Wealthsimple, generic)
    const singleRaw =
      row.Amount || row.amount || row.AMOUNT ||
      row["CAD$"] || row["USD$"] ||
      ""

    // Split-column banks: withdrawals/debits are negative, deposits/credits positive
    const debitRaw  = row.Debit       || row.debit       || row.Withdrawals || row.withdrawals || ""
    const creditRaw = row.Credit      || row.credit      || row.Deposits    || row.deposits    || ""

    let amount = null

    if (singleRaw !== "") {
      const v = parseFloat(String(singleRaw).replace(/[,$]/g, ""))
      if (!isNaN(v)) amount = v
    } else if (debitRaw !== "" || creditRaw !== "") {
      const debit  = parseFloat(String(debitRaw ).replace(/[,$]/g, "")) || 0
      const credit = parseFloat(String(creditRaw).replace(/[,$]/g, "")) || 0
      // debit = money leaving → negative; credit = money arriving → positive
      if (debit  > 0) amount = -debit
      else if (credit > 0) amount = credit
    }

    if (amount === null) return null

    // ── Date ──
    const rawDate =
      row.Date || row.date || row.DATE ||
      row["Transaction Date"] || row["transaction date"] ||
      ""

    return { desc, amount, date: normalizeDate(rawDate) }
  }

  async function handleCSVUpload(e) {
    const file = e.target.files[0]
    if (!file) return
    e.target.value = ""

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const validRows = results.data
          .map(parseBankRow)
          .filter(Boolean)

        if (validRows.length === 0) {
          setError("No valid rows found. Supported banks: RBC, TD, Scotiabank, BMO, CIBC, Tangerine, Wealthsimple, or any CSV with description + amount columns.")
          return
        }

        setCsvProgress({ done: 0, total: validRows.length })

        ;(async () => {
          let done = 0
          for (const { desc, amount, date } of validRows) {
            try {
              const res = await classifyAndSave(desc, amount, date)
              setTransactions(prev => [...prev, res.data])
            } catch (err) {
              console.error("Failed to classify row:", desc, err?.response?.data || err.message)
            }
            done++
            setCsvProgress({ done, total: validRows.length })
          }
          setCsvProgress(null)
        })()
      },
      error: (err) => {
        setError(`CSV parse error: ${err.message}`)
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
      setPendingCategory("")
    } catch (err) {
      setError("Failed to save correction")
    }
  }

  async function handleRetrain() {
    try {
      setRetraining(true)
      setRetrainMsg(null)
      const res = await retrainModel()
      setRetrainMsg(`Retraining started with ${res.data.corrections} correction${res.data.corrections !== 1 ? "s" : ""}. Takes ~2 min, new classifications will use the updated model.`)
    } catch (err) {
      setRetrainMsg("Failed to start retraining.")
    } finally {
      setRetraining(false)
    }
  }

  async function handleDelete(transactionId) {
    try {
      await deleteTransaction(transactionId)
    } catch (err) {
      if (err?.response?.status !== 404) {
        console.error("Failed to delete", err)
        return
      }
    }
    setTransactions(prev => prev.filter(t => t.id !== transactionId))
  }

  if (!user) {
    return <Auth onLogin={handleLogin} />
  }

  return (
    <div className="app">

      <div className="app-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1>Finsnap</h1>
          <p>Understand your money in one page.</p>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: "12px", color: "var(--text-dim)", marginBottom: "6px" }}>{user}</div>
          <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end" }}>
            <button
              onClick={() => setIsDark(d => !d)}
              style={{ padding: "6px 12px", fontSize: "11px", background: "none", color: "var(--text-dim)", border: "1px solid var(--border2)", borderRadius: "4px", cursor: "pointer" }}
            >
              {isDark ? "Light" : "Dark"}
            </button>
            <button
              onClick={handleRetrain}
              disabled={retraining}
              style={{ padding: "6px 12px", fontSize: "11px", background: "none", color: "var(--text-dim)", border: "1px solid var(--border2)", borderRadius: "4px", cursor: retraining ? "not-allowed" : "pointer", opacity: retraining ? 0.5 : 1 }}
            >
              {retraining ? "Starting..." : "Retrain Model"}
            </button>
            <button
              onClick={handleLogout}
              style={{ padding: "6px 14px", fontSize: "11px", background: "none", color: "var(--text-dim)", border: "1px solid var(--border2)", borderRadius: "4px", cursor: "pointer" }}
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      {retrainMsg && (
        <div style={{ marginBottom: "16px", padding: "10px 14px", background: "var(--panel2)", border: "1px solid var(--border2)", borderRadius: "6px", fontSize: "13px", color: "var(--text-dim)" }}>
          {retrainMsg}
        </div>
      )}

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

      <div style={{ margin: "0 0 24px", display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
        <label style={{ fontSize: "13px", color: "var(--text-dim)", cursor: csvProgress ? "not-allowed" : "pointer", padding: "8px 16px", border: "1px dashed var(--border)", borderRadius: "6px", opacity: csvProgress ? 0.5 : 1 }}>
          Upload CSV
          <input type="file" accept=".csv" onChange={handleCSVUpload} style={{ display: "none" }} disabled={!!csvProgress} />
        </label>
        {csvProgress ? (
          <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>
            Classifying {csvProgress.done} / {csvProgress.total}...
          </span>
        ) : (
          <span style={{ fontSize: "12px", color: "var(--text-pale)" }}>
            CSV needs "description" and "amount" columns
          </span>
        )}
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

      {getTrendData().length > 0 && (
        <div style={{ margin: "28px 0" }}>
          <p className="section-label">Monthly Spending Trend</p>
          <div style={{ background: "var(--panel2)", border: "1px solid var(--border2)", borderRadius: "10px", padding: "24px", boxShadow: "0 1px 6px var(--shadow2)" }}>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={getTrendData()} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border2)" />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: "var(--text-dim)" }} />
                <YAxis tick={{ fontSize: 11, fill: "var(--text-dim)" }} />
                <Tooltip formatter={(value) => `$${value}`} />
                <Bar dataKey="total" fill="var(--accent)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
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
                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <select
                    style={{ fontSize: "12px", padding: "4px 8px", border: "1px solid var(--accent)", borderRadius: "4px", background: "var(--panel2)", color: "var(--accent-lt)" }}
                    value={pendingCategory}
                    onChange={e => setPendingCategory(e.target.value)}
                  >
                    {CATEGORIES.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => handleCorrection(t.id, pendingCategory)}
                    style={{ padding: "3px 8px", fontSize: "11px", background: "var(--accent)", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
                  >Save</button>
                  <button
                    onClick={() => { setCorrectingId(null); setPendingCategory("") }}
                    style={{ padding: "3px 8px", fontSize: "11px", background: "none", color: "var(--text-pale)", border: "1px solid var(--border2)", borderRadius: "4px", cursor: "pointer" }}
                  >×</button>
                </div>
              ) : (
                <span
                  className="t-category"
                  onClick={() => { if (t.id) { setCorrectingId(t.id); setPendingCategory(t.category) } }}
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
                >Delete
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