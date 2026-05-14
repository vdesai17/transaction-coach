import { use, useState } from "react"
import "./App.css"

function App() {
    const[description, setDescription] = useState("") //starts as empty string, updates as user types
    const[amount, setAmount] = useState("") //starts as empty string, updates as user types
    const[result, setResult] = useState(null) //starts as null, for classification result
    const[loading, setLoading] = useState(false) //for API has strated to load correctly or not
    const[error, setError] = useState(null) //for error handling

    async function classifyTransaction() {

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

        //now data is { category: "some category" }
        setResult(data) //update result state with classification result from server
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
            <h1>Transaction Coach</h1>
            <input
                type="text"
                placeholder="transaction description"
                value={description}
                onChange={e => setDescription(e.target.value)}
            />
                
            <input
                type="number"
                placeholder="amount"
                value={amount}
                onChange={e => setAmount(e.target.value)}
            />

            <button onClick={classifyTransaction}> {/*on click call classifyTransaction function */}
                {loading ? "Classifying..." : "Classify"} {/*loading is true then show "Classifying..." otherwise show "Classify" */}
            </button>

            {/* on click call classifyTransaction function */}
            {result && <p>Category: {result.category}</p>} 
            {error && <p>{error}</p>}
        </div>

    )
    
}

export default App
