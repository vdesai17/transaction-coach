import { useState } from "react"
import "./App.css"

function App() {
  const [description, setDescription] = useState("")
  const [amount, setAmount] = useState("")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  async function classifyTransaction() {
    setLoading(true)
    const response = await fetch("http://127.0.0.1:8001/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description, amount: parseFloat(amount) })
    })
    const data = await response.json()
    setResult(data)
    setLoading(false)
  }

  return (
    <div className="app">
      <h1>Transaction Coach</h1>
      
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

      {result && <p>Category: {result.category}</p>}
    </div>
  )
}

export default App