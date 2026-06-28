import axios from 'axios';

const API_BASE = '/api';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Datasets
  uploadDataset: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await client.post('/datasets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  getDatasets: async () => {
    const response = await client.get('/datasets');
    return response.data;
  },
  
  getDataset: async (id) => {
    const response = await client.get(`/datasets/${id}`);
    return response.data;
  },
  
  getPreview: async (id, rows = 20) => {
    const response = await client.get(`/datasets/${id}/preview?rows=${rows}`);
    return response.data;
  },
  
  setTargetColumn: async (id, targetColumn) => {
    const response = await client.put(`/datasets/${id}/target?target_column=${encodeURIComponent(targetColumn)}`);
    return response.data;
  },
  
  deleteDataset: async (id) => {
    const response = await client.delete(`/datasets/${id}`);
    return response.data;
  },

  // EDA
  runEDA: async (id) => {
    const response = await client.post(`/eda/${id}`);
    return response.data;
  },

  // Predictions
  trainModels: async (id) => {
    const response = await client.post(`/predictions/${id}/train`);
    return response.data;
  },
  
  getPredictions: async (id) => {
    const response = await client.get(`/predictions/${id}/results`);
    return response.data;
  },

  // Reports
  generateReport: async (id) => {
    const response = await client.post(`/reports/${id}/generate`);
    return response.data;
  },

  // Collections
  generateCollections: async (id) => {
    const response = await client.post(`/collections/${id}/generate`);
    return response.data;
  },
  
  getActions: async (id) => {
    const response = await client.get(`/collections/${id}/actions`);
    return response.data;
  },
  
  approveAction: async (actionId, approvedBy = 'agent') => {
    const response = await client.post(`/collections/actions/${actionId}/approve?approved_by=${encodeURIComponent(approvedBy)}`);
    return response.data;
  },
  
  submitFeedback: async (actionId, { paymentAmount, promiseToPay, notes }) => {
    const response = await client.post(`/collections/actions/${actionId}/feedback`, {
      payment_amount: paymentAmount,
      promise_to_pay: promiseToPay,
      notes: notes
    });
    return response.data;
  },

  // Chat
  askAssistant: async (message, datasetId = null) => {
    const response = await client.post('/chat', {
      message,
      dataset_id: datasetId
    });
    return response.data;
  },

  // Settings & Bias
  getSensitiveAttributes: async (id) => {
    const response = await client.get(`/settings/sensitive-attributes/${id}`);
    return response.data;
  },
  
  checkBias: async (id, { sensitiveColumn, privilegedGroup, unprivilegedGroup }) => {
    const response = await client.post(`/settings/bias-check/${id}?sensitive_column=${encodeURIComponent(sensitiveColumn)}&privileged_group=${encodeURIComponent(privilegedGroup)}&unprivileged_group=${encodeURIComponent(unprivilegedGroup)}`);
    return response.data;
  },
  
  getAuditLogs: async (datasetId = null) => {
    const url = datasetId ? `/settings/audit-logs?dataset_id=${datasetId}` : '/settings/audit-logs';
    const response = await client.get(url);
    return response.data;
  }
};
export default client;
