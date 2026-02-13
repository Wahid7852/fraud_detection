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
  getCases: (params?: any) => api.get('/cases', { params }).then(res => res.data),
  getCase: (id: string) => api.get(`/cases/${id}`).then(res => res.data),
  createCase: (data: any) => api.post('/cases', data).then(res => res.data),
  updateCase: (id: string, data: any) => api.put(`/cases/${id}`, data).then(res => res.data),
  addNote: (data: { case_id: string; note: string; analyst_id: number }) => api.post('/cases/notes', data).then(res => res.data),
  assignAnalyst: (id: string, analyst_id: number) => api.post(`/cases/${id}/assign`, analyst_id).then(res => res.data),
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

export const reportService = {
  getTemplates: () => api.get('/reports/templates').then(res => res.data),
  getReports: (params?: any) => api.get('/reports/list', { params }).then(res => res.data),
  generateReport: (data: any) => api.post('/reports/generate', data).then(res => res.data),
  getTrends: (params?: any) => api.get('/reports/trends', { params }).then(res => res.data),
  getStats: () => api.get('/reports/stats').then(res => res.data),
  exportReport: (params?: any) => api.get('/reports/export', { params }).then(res => res.data),
};

export const sarService = {
  getSARs: (params?: any) => api.get('/sars', { params }).then(res => res.data),
  getSAR: (id: string) => api.get(`/sars/${id}`).then(res => res.data),
  createSAR: (data: any) => api.post('/sars', data).then(res => res.data),
  updateSAR: (id: string, data: any) => api.put(`/sars/${id}`, data).then(res => res.data),
  fileSAR: (id: string) => api.post(`/sars/${id}/file`).then(res => res.data),
  getStats: () => api.get('/sars/stats').then(res => res.data),
  exportBatch: (params?: any) => api.get('/sars/export/batch', { params }).then(res => res.data),
};
