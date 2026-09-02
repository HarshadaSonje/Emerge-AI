import api from "./client";
export const getDrivers = (params = {}) => api.get("/drivers", { params }).then(r => r.data);
export const getDriver = id => api.get(`/drivers/${id}`).then(r => r.data);
export const updateDriverAvailability = (id, is_available) => api.patch(`/drivers/${id}/availability`, { is_available }).then(r => r.data);
export const activateDriver = id => api.patch(`/drivers/${id}/activate`).then(r => r.data);
export const deactivateDriver = id => api.patch(`/drivers/${id}/deactivate`).then(r => r.data);
