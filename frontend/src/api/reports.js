import api from "./client";

export const getDailyReport = (reportDate) => api.get("/reports/daily", { params: { report_date: reportDate } }).then(r => r.data);
export const getAmbulanceUtilization = () => api.get("/reports/ambulance-utilization").then(r => r.data);
export const getDriverPerformance = () => api.get("/reports/driver-performance").then(r => r.data);
export const getHospitalWorkload = () => api.get("/reports/hospital-workload").then(r => r.data);
