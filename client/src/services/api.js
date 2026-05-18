import axios from "axios"

// base URL for all API calls
const API = axios.create({
  baseURL: "http://127.0.0.1:8001"
})

// automatically attach token to every request if it exists
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Auth ────────────────────────────────────────────────────────────

export const register = (email, password) =>
  API.post("/register", { email, password })

export const login = (email, password) =>
  API.post("/login", { email, password })

// ── Transactions ────────────────────────────────────────────────────

export const classifyAndSave = (description, amount) =>
  API.post("/transactions", { description, amount })

export const getTransactions = () =>
  API.get("/transactions")

export const submitFeedback = (transaction_id, corrected_category) =>
  API.post("/feedback", { transaction_id, corrected_category })

// ── Predict only (no save, no auth) ─────────────────────────────────

export const predict = (description, amount) =>
  API.post("/predict", { description, amount })