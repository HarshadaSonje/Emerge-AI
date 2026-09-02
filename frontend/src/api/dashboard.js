import api from "./client";

export const getDashboardOverview = async () => {
  const response = await api.get("/dashboard/overview");
  return response.data;
};

export const getRecentEmergencies = async () => {
  const response = await api.get("/dashboard/recent-emergencies");
  return response.data;
};

export const getAmbulanceStatus = async () => {
  const response = await api.get("/dashboard/ambulance-status");
  return response.data;
};

export const getEmergencyTrends = async () => {
  const response = await api.get("/dashboard/emergency-trends");
  return response.data;
};