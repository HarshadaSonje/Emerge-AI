const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(method, path, body, options = {}) {
  const token = localStorage.getItem("access_token");
  const headers = { ...(body !== undefined ? {"Content-Type":"application/json"}:{}), ...(options.headers||{}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${BASE_URL}${path}${options.params ? `?${new URLSearchParams(Object.entries(options.params).filter(([,v])=>v!==null&&v!==undefined&&v!==""))}` : ""}`, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  let data = null;
  try { data = await response.json(); } catch {}
  if (!response.ok) { const err = new Error(data?.detail || data?.message || `HTTP ${response.status}`); err.response = { status: response.status, data }; throw err; }
  return { data, status: response.status };
}
const api = { get:(p,o)=>request("GET",p,undefined,o), post:(p,b,o)=>request("POST",p,b,o), put:(p,b,o)=>request("PUT",p,b,o), patch:(p,b,o)=>request("PATCH",p,b,o), delete:(p,o)=>request("DELETE",p,undefined,o) };
export default api;
