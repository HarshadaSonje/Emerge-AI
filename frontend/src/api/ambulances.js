import api from "./client";
export const getAmbulances = (params = {}) => api.get("/ambulances", { params }).then(r => r.data);
export const getAmbulance = id => api.get(`/ambulances/${id}`).then(r => r.data);
export const updateAmbulanceStatus = (id, status) => api.patch(`/ambulances/${id}/status`, { status }).then(r => r.data);
export const activateAmbulance = id => api.patch(`/ambulances/${id}/activate`).then(r => r.data);
export const deactivateAmbulance = id => api.patch(`/ambulances/${id}/deactivate`).then(r => r.data);
export const updateAmbulanceLocation = (id, current_latitude, current_longitude) => api.patch(`/ambulances/${id}/location`, { current_latitude, current_longitude }).then(r => r.data);
