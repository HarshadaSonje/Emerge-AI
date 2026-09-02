import api from "./client";

export const getTriageAssessment = (id) => api.post(`/ai/triage/${id}`).then(r => r.data);
export const getRecommendation = (id) => api.get(`/recommendation/${id}`).then(r => r.data);
export const autoDispatch = (id) => api.post(`/auto-dispatch/${id}`).then(r => r.data);
