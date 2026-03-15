import axios from "axios";

const BASE = "http://localhost:8000/api";

export const getBrands = () => axios.get(`${BASE}/brands`);
export const getModels = (brand) => axios.get(`${BASE}/models`, { params: brand ? { brand } : {} });
export const getSentiment = () => axios.get(`${BASE}/sentiment`);
export const getAspects = () => axios.get(`${BASE}/aspects`);
export const getOpportunities = () => axios.get(`${BASE}/opportunities`);
export const getModelAspects = (brand, model) =>
  axios.get(`${BASE}/model-aspects`, { params: { brand, model } });
export const getCompetitorAdvantages = (target) =>
  axios.get(`${BASE}/competitor-advantages`, { params: { target } });
export const getSpecPeers = (model) =>
  axios.get(`${BASE}/spec-peers`, { params: { model } });
export const getSummary = (target) =>
  axios.get(`${BASE}/summary`, { params: { target } });
export const getPriceModels = (brand) =>
  axios.get(`${BASE}/price-models`, { params: brand ? { brand } : {} });
export const getModelComparison = (asusModel) =>
  axios.get(`${BASE}/model-comparison`, { params: { asus_model: asusModel } });

export const sendChat = (query) =>
  axios.post(`${BASE}/chat`, { query });

export const getInsights = (asusModel) =>
  axios.get(`${BASE}/insights`, { params: { asus_model: asusModel } });
