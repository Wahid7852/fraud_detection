import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
});

export const dashboardService = {
  getKPIs: () => api.get('/dashboard/kpis').then(res => res.data),
  getAlertsTrend: () => api.get('/dashboard/alerts-over-time').then(res => res.data),
};

export const alertService = {
  getAlerts: (params?: any) => api.get('/alerts', { params }).then(res => res.data),
  getAlert: (id: string) => api.get(`/alerts/${id}`).then(res => res.data),
  updateAlert: (id: string, data: any) => api.put(`/alerts/${id}`, data).then(res => res.data),
  takeAction: (id: string, action: string) => api.post(`/alerts/${id}/action`, { action }).then(res => res.data),
};

export const caseService = {
  getCases: () => api.get('/cases').then(res => res.data),
  getCase: (id: number) => api.get(`/cases/${id}`).then(res => res.data),
  createCase: (data: any) => api.post('/cases', data).then(res => res.data),
  updateCase: (id: number, data: any) => api.put(`/cases/${id}`, data).then(res => res.data),
  addNote: (data: { case_id: number; note: string; analyst_id: number }) => api.post('/cases/notes', data).then(res => res.data),
};

export const ruleService = {
  getRules: () => api.get('/rules').then(res => res.data),
  createRule: (rule: any) => api.post('/rules', rule).then(res => res.data),
  updateRule: (id: string, rule: any) => api.put(`/rules/${id}`, rule).then(res => res.data),
  deleteRule: (id: string) => api.delete(`/rules/${id}`).then(res => res.data),
};

export const analysisService = {
  getResults: () => api.get('/analysis/results').then(res => res.data),
  getTrends: () => api.get('/analysis/trends').then(res => res.data),
};
