// src/services/recommendationService.js
import api from "./api";

export const getContentBasedRecommendations = (params = {}) => {
  const { k = 5, ...otherParams } = params;
  return api.get("/recommendations/content/", { 
    params: { k, ...otherParams } 
  });
};

export const getCollaborativeRecommendations = (params = {}) => {
  const { k = 5, ...otherParams } = params;
  return api.get("/recommendations/collaborative/", { 
    params: { k, ...otherParams } 
  });
};

export const getHybridRecommendations = (params = {}) => {
  const { k = 5, ...otherParams } = params;
  return api.get("/recommendations/hybrid/", { 
    params: { k, ...otherParams } 
  });
};

export const trackUserActivity = (activityData) => {
  return api.post("/users/activity/", activityData);
};

export const getUserActivity = (userId) => {
  return api.get(`/users/activity/${userId}/`);
};

export const updateUserPreferences = (preferences) => {
  return api.put("/users/preferences/", preferences);
};

export const getUserPreferences = () => {
  return api.get("/users/preferences/");
};
