import api from "./client";
export const getHospitals = (params = {}) => api.get("/hospitals", { params }).then(r => r.data);
export const getHospital = id => api.get(`/hospitals/${id}`).then(r => r.data);
export const updateHospital = (id, data) => api.put(`/hospitals/${id}`, data).then(r => r.data);
export const activateHospital = id => api.patch(`/hospitals/${id}/activate`).then(r => r.data);
export const deactivateHospital = id => api.patch(`/hospitals/${id}/deactivate`).then(r => r.data);
