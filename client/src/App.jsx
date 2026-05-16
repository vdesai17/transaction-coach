import { useState } from "react"
import Papa from "papaparse"
import "./App.css"
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts"


// colors for each slice of the pie chart
const COLORS = [
  "#4A7FA0", "#7BADC8", "#8B7355", "#5A8F7A",
  "#9B7EA0", "#7A8FA0", "#A07A5A", "#5A7A8F"
]

function App() {

  // what the user types in the description input
  const [description, setDescription] = useState("")

  // what the user types in the amount input
  const [amount, setAmount] = useState("")

  // list of all classified transactions, grows as user adds more
  const [transactions, setTransactions] = useState([])

  // true while waiting for API response, false otherwise
  const [loading, setLoading] = useState(false)

  // holds error message if something goes wrong, null if all good
  const [error, setError] = useState(null)

  // groups transactions by category and totals the amounts
  // recharts needs data in this format: [{ name: "Dining", value: 45.50 }]
  function getChartData() {
    const totals = {}

    // add each transaction's amount to its category total
    transactions.forEach(t => {
      totals[t.category] = (totals[t.category] || 0) + Math.abs(t.amount)
    })

    // convert object to array that recharts can read
    return Object.entries(totals).map(([name, value]) => ({
      name,
      value: parseFloat(value.toFixed(2))
    }))
  }

  // called when user clicks Classify
  // sends description + amount to FastAPI, gets category back
  async function classifyTransaction() {

    // do nothing if either field is empty
    if (!description || !amount) return

    try {
      // tell React we are waiting for the API
      setLoading(true)

      // send POST request to FastAPI with the transaction data as JSON
      const response = await fetch("http://127.0.0.1:8001/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description, amount: parseFloat(amount) })
      })

      // parse the JSON response — data = { category: "Dining and Cafes" }
      const data = await response.json()

      // add new transaction to the list
      // spread the previous array and append the new transaction
      setTransactions(prev => [...prev, {
        description,
        amount: parseFloat(amount),
        category: data.category
      }])

      // clear inputs so user can type next transaction
      setDescription("")
      setAmount("")

    } catch (error) {
      // show error message if API call fails
      setError("Error classifying transaction")

    } finally {
      // always stop loading when done, success or error
      setLoading(false)
    }
  }

  // called when user uploads a CSV file
  // parses each row and classifies it one by one
  async function handleCSVUpload(e) {
    const file = e.target.files[0]
    if (!file) return

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: async (results) => {
        for (const row of results.data) {
          const desc = row.description || row.Description || row.DESCRIPTION
          const amt = row.amount || row.Amount || row.AMOUNT

          // skip row if missing or invalid amount
          if (!desc || !amt) continue
          if (isNaN(parseFloat(amt))) continue

          try {
            const response = await fetch("http://127.0.0.1:8001/predict", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ description: desc, amount: parseFloat(amt) })
            })
            const data = await response.json()
            setTransactions(prev => [...prev, {
              description: desc,
              amount: parseFloat(amt),
              category: data.category
            }])
          } catch (err) {
            console.error("Failed to classify:", desc)
          }
        }
      }
    })
  }

  return (
    <div className="app">

      {/* app title and subtitle */}
      <div className="app-header">
        <h1>Transaction Coach</h1>
        <p>Classify your spending. Understand your money.</p>
      </div>

      {/* input row — description, amount, classify button */}
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
          {/* show different text while loading */}
          {loading ? "Classifying..." : "Classify"}
        </button>
      </div>

      {/* CSV upload button — hidden file input styled as a label */}
      <div style={{ margin: "0 0 24px", display: "flex", alignItems: "center", gap: "12px" }}>
        <label style={{
          fontSize: "13px",
          color: "var(--text-dim)",
          cursor: "pointer",
          padding: "8px 16px",
          border: "1px dashed var(--border)",
          borderRadius: "6px"
        }}>
          Upload CSV
          {/* file input is hidden, clicking the label triggers it */}
          <input
            type="file"
            accept=".csv"
            onChange={handleCSVUpload}
            style={{ display: "none" }}
          />
        </label>
        <span style={{ fontSize: "12px", color: "var(--text-pale)" }}>
          CSV needs "description" and "amount" columns
        </span>
      </div>

      {/* summary bar — only shows when there are transactions */}
      {transactions.length > 0 && (
        <div className="summary-bar">
          <div className="summary-chip">
            <strong>{transactions.length}</strong> transactions
          </div>
          <div className="summary-chip">
            {/* reduce adds up all amounts to get total spent */}
            Total spent: <strong>
              ${transactions.reduce((sum, t) => sum + Math.abs(t.amount), 0).toFixed(2)}
            </strong>
          </div>
        </div>
      )}

      {/* pie chart — only shows when there are transactions */}
{transactions.length > 0 && (
  <div style={{ margin: "28px 0" }}>
    <p className="section-label">Spending Breakdown</p>
    <div style={{ background: "var(--panel2)", border: "1px solid var(--border2)", borderRadius: "10px", padding: "24px", boxShadow: "0 1px 6px var(--shadow2)" }}>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={getChartData()}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
          >
            {getChartData().map((entry, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => `$${value}`} />
        </PieChart>
      </ResponsiveContainer>

      {/* legend sits below the chart, outside the ResponsiveContainer */}
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

      {/* section label — only shows when there are transactions */}
      {transactions.length > 0 && (
        <p className="section-label">Recent Transactions</p>
      )}

      {/* transaction list */}
      <div className="transaction-list">
        {transactions.length === 0 ? (
        <div className="empty-state">
            <p>Add your first transaction above</p>
        </div>  ) : (transactions.map((t, i) => (
            <div key={i} className="transaction-card">
              <span className="t-desc">{t.description}</span>
              <span className="t-category">{t.category}</span>
              <span className="t-amount">${Math.abs(t.amount).toFixed(2)}</span>
            </div>
          ))
        )}
      </div>

      {/* error message — only shows if something went wrong */}
      {error && <p className="error">{error}</p>}

    </div>
  )
}

export default App