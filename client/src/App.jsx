import { useState } from "react"
import "./App.css"

function App() {
    const[description, setDescription] = useState("") //starts as empty string, updates as user types
    const[amount, setAmount] = useState("") //starts as empty string, updates as user types
    const[transactions, setTransactions] = useState([]) //starts as empty array, to store past transactions
    const[loading, setLoading] = useState(false) //for API has strated to load correctly or not
    const[error, setError] = useState(null) //for error handling

    async function classifyTransaction() {

        if (!description || !amount) return //if either description or amount is empty, do not proceed with classification

        try {

        //set loading to true when API call starts
        setLoading(true)

        //send POST request to backend with description and amount as JSON
        //wait for server to respond with classification result
        const response = await fetch("http://127.0.0.1:8001/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ description, amount: parseFloat(amount) })
        })
        
        //fetch the response from server
        const data = await response.json()

        setTransactions(prev => [...prev, {
            description,
            amount: parseFloat(amount),
            category: data.category
        }])
        setDescription("") //clear description input after classification
        setAmount("") //clear amount input after classification

        setLoading(false) //set loading to false when API call is done
    }
        catch (error) {
            setError("Error classifying transaction") //if error occurs during API call, set error message
        }
        
        finally {
            setLoading(false) //ensure loading is set to false after API call completes, regardless of success or error
        }
    }

    return (
  <div className="app">
    <div className="app-header">
      <h1>Transaction Coach</h1>
      <p>Classify your spending. Understand your money.</p>
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
      <button onClick={classifyTransaction}>
        {loading ? "Classifying..." : "Classify"}
      </button>
    </div>

    {transactions.length > 0 && (
      <div className="summary-bar">
        <div className="summary-chip">
          <strong>{transactions.length}</strong> transactions
        </div>
        <div className="summary-chip">
          Total spent: <strong>${transactions.reduce((sum, t) => sum + Math.abs(t.amount), 0).toFixed(2)}</strong>
        </div>
      </div>
    )}

    {transactions.length > 0 && (
      <p className="section-label">Recent Transactions</p>
    )}

    <div className="transaction-list">
      {transactions.length === 0 ? (
        <div className="empty-state">
          <p>Add your first transaction above</p>
        </div>
      ) : (
        transactions.map((t, i) => (
          <div key={i} className="transaction-card">
            <span className="t-desc">{t.description}</span>
            <span className="t-category">{t.category}</span>
            <span className="t-amount">${Math.abs(t.amount).toFixed(2)}</span>
          </div>
        ))
      )}
    </div>

    {error && <p className="error">{error}</p>}
  </div>
)
    
}
export default App
