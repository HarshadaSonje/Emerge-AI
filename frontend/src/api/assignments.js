import api from "./client";
export const getAssignments = (params = {}) => api.get("/dispatch-assignments", { params }).then(r => r.data);
export const updateAssignmentStatus = (id, status) => api.patch(`/dispatch-assignments/${id}/status`, { status }).then(r => r.data);
