import api from "./client";
export const getDispatches = (params = {}) => api.get("/dispatches", { params }).then(r => r.data);
export const getDispatch = id => api.get(`/dispatches/${id}`).then(r => r.data);
export const createDispatch = data => api.post("/dispatches", data).then(r => r.data);
export const updateDispatch = (id, data) => api.put(`/dispatches/${id}`, data).then(r => r.data);
export const updateDispatchStatus = (id, status) => api.patch(`/dispatches/${id}/status`, { status }).then(r => r.data);
export const cancelDispatch = id => api.patch(`/dispatches/${id}/cancel`).then(r => r.data);
