import api from "./client";
export const getEmergencies = (params = { page: 1, limit: 50 }) => api.get("/emergencies", { params }).then(r => r.data);
export const getEmergency = id => api.get(`/emergencies/${id}`).then(r => r.data);
export const createEmergency = data => api.post("/emergencies", data).then(r => r.data);
export const updateEmergency = (id, data) => api.put(`/emergencies/${id}`, data).then(r => r.data);
export const updateEmergencyStatus = (id, status) => api.patch(`/emergencies/${id}/status`, { status }).then(r => r.data);
export const updateEmergencySeverity = (id, severity) => api.patch(`/emergencies/${id}/severity`, { severity }).then(r => r.data);
export const closeEmergency = id => api.patch(`/emergencies/${id}/close`).then(r => r.data);
