// Simple frontend API client for Trading-AI
// Uses fetch and returns JSON. Handles auth tokens via localStorage.

const API_BASE = '/api'

function getToken() {
  return localStorage.getItem('ta_token') || null
}

function setToken(token) {
  if (token) localStorage.setItem('ta_token', token)
  else localStorage.removeItem('ta_token')
}

async function request(path, opts = {}){
  const headers = opts.headers || {}
  headers['Accept'] = 'application/json'
  if (!(opts.body instanceof FormData)) headers['Content-Type'] = 'application/json'
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${API_BASE}${path}`, {...opts, headers})
  if (res.status === 401){
    // token invalid - clear
    setToken(null)
    throw new Error('Unauthorized')
  }
  const text = await res.text()
  try{
    return JSON.parse(text)
  }catch(e){
    return text
  }
}

export async function marketOverview(tickers){
  const q = `?tickers=${encodeURIComponent(Array.isArray(tickers)?tickers.join(','):tickers)}`
  return request(`/market_overview${q}`)
}

export async function livePrice(ticker){
  return request(`/live_price?ticker=${encodeURIComponent(ticker)}`)
}

export async function analyze(tickers, interval='1d', period='1mo'){
  const body = { tickers, interval, period }
  return request('/analyze', { method: 'POST', body: JSON.stringify(body) })
}

export async function signals(tickers, interval='1d'){
  return request('/signals', { method: 'POST', body: JSON.stringify({ tickers, interval }) })
}

export async function predict(ticker, interval='1d'){
  return request('/predict', { method: 'POST', body: JSON.stringify({ ticker, interval }) })
}

export async function backtest(ticker, strategy='sma', period='6mo'){
  return request('/backtest', { method: 'POST', body: JSON.stringify({ ticker, strategy, period }) })
}

export async function register(username, email, password){
  return request('/auth/register', { method: 'POST', body: JSON.stringify({ username, email, password }) })
}

export async function login(identifier, password){
  // identifier can be username or email
  const payload = isEmail(identifier) ? { email: identifier, password } : { username: identifier, password }
  const res = await request('/auth/login', { method: 'POST', body: JSON.stringify(payload) })
  if (res && res.access_token){
    setToken(res.access_token)
  }
  return res
}

function isEmail(str){
  return /@/.test(str)
}

export function logout(){ setToken(null) }

export default { marketOverview, livePrice, analyze, predict, backtest, register, login, logout }
