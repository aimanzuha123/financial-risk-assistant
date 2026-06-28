import { create } from 'zustand';
import { api } from '../api/client';

export const useStore = create((set, get) => ({
  datasets: [],
  selectedDatasetId: null,
  activeDataset: null,
  activeEda: null,
  activePredictions: null,
  activeReport: null,
  activeActions: [],
  chatHistory: [
    { sender: 'assistant', text: 'Hello! I am your Financial Risk & Collections Assistant. Upload a credit dataset or select an existing one to begin analysis.' }
  ],
  loading: false,
  error: null,

  setDatasetId: (id) => {
    set({ selectedDatasetId: id });
    if (id) {
      get().fetchDatasetDetails(id);
    } else {
      set({ activeDataset: null, activeEda: null, activePredictions: null, activeReport: null, activeActions: [] });
    }
  },

  fetchDatasets: async () => {
    set({ loading: true, error: null });
    try {
      const data = await api.getDatasets();
      set({ datasets: data });
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Failed to fetch datasets' });
    } finally {
      set({ loading: false });
    }
  },

  fetchDatasetDetails: async (id) => {
    set({ loading: true, error: null });
    try {
      const details = await api.getDataset(id);
      set({ activeDataset: details });
      
      // Auto load other related data if already analyzed/predicted
      if (details.status === 'analyzed' || details.status === 'predicted') {
        get().loadEdaResults(id);
      }
      if (details.status === 'predicted') {
        get().loadPredictionResults(id);
        get().loadCollectionActions(id);
      }
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Failed to load dataset details' });
    } finally {
      set({ loading: false });
    }
  },

  loadEdaResults: async (id) => {
    try {
      const data = await api.runEDA(id);
      set({ activeEda: data });
    } catch (err) {
      console.error('Failed to run/load EDA', err);
    }
  },

  loadPredictionResults: async (id) => {
    try {
      const data = await api.getPredictions(id);
      set({ activePredictions: data });
    } catch (err) {
      console.error('Failed to load predictions', err);
    }
  },

  loadCollectionActions: async (id) => {
    try {
      const data = await api.getActions(id);
      set({ activeActions: data });
    } catch (err) {
      console.error('Failed to load collections', err);
    }
  },

  runFullPipeline: async (id) => {
    set({ loading: true, error: null });
    try {
      // 1. Run EDA
      const eda = await api.runEDA(id);
      set({ activeEda: eda });

      // 2. Train Models
      const pred = await api.trainModels(id);
      set({ activePredictions: pred });

      // 3. Generate Collections
      const actions = await api.generateCollections(id);
      set({ activeActions: actions });

      // Refresh dataset info
      await get().fetchDatasetDetails(id);
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Pipeline failure occurred' });
    } finally {
      set({ loading: false });
    }
  },

  sendMessage: async (text) => {
    const history = get().chatHistory;
    const activeId = get().selectedDatasetId;
    
    set({
      chatHistory: [...history, { sender: 'user', text }]
    });

    try {
      const res = await api.askAssistant(text, activeId);
      set({
        chatHistory: [...get().chatHistory, { sender: 'assistant', text: res.reply }]
      });
    } catch (err) {
      set({
        chatHistory: [...get().chatHistory, { sender: 'assistant', text: 'Error: Failed to fetch reply from assistant.' }]
      });
    }
  },

  clearError: () => set({ error: null })
}));
