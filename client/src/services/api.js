// axios is like fetch but cleaner - handles json, headers, errors better
import axios from "axios"

// create one axios instance with the backend url
// VITE_API_URL comes from .env file
// locally its http://127.0.0.1:8001
// in production it'll be the railway url
const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL
})

// interceptor runs before every single request
// checks if theres a token in localstorage and adds it to the header
// this is how protected routes know who u are
// format fastapi expects: Authorization: Bearer <token>
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// creates a new account
// returns { token, email } on success
export const register = (email, password) =>
  API.post("/register", { email, password })

// logs in with existing account
// returns { token, email } on success
export const login = (email, password) =>
  API.post("/login", { email, password })

// classifies a transaction with the ml model AND saves it to db
// requires auth token - tied to the logged in user
// returns { id, description, amount, category }
export const classifyAndSave = (description, amount) =>
  API.post("/transactions", { description, amount })

// loads all transactions for the logged in user from db
// returns array of { id, description, amount, category, created_at }
export const getTransactions = () =>
  API.get("/transactions")

// sends a category correction when user says model was wrong
// saves to corrections table for future model retraining
export const submitFeedback = (transaction_id, corrected_category) =>
  API.post("/feedback", { transaction_id, corrected_category })

// classifies without saving - no auth needed
// used for quick testing
export const predict = (description, amount) =>
  API.post("/predict", { description, amount })