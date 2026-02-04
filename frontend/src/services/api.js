// src/services/api.js
// Simple wrapper around your FastAPI backend
const BASE_URL = "http://localhost:8000";

export const chatAPI = {
  async healthCheck() {
    const res = await fetch(`${BASE_URL}/`);
    if (!res.ok) throw new Error("Health check failed");
    return res.json();
  },

  async predictImage(file) {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${BASE_URL}/predict-cnn`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      throw new Error("Image prediction failed");
    }

    return res.json(); // expected: { prediction: 0 or 1, ... }
  },

  async sendMessage(message, language, cnnPrediction) {
    const payload = {
      message,
      language, // e.g. "English", "Tamil", "Hindi"
      cnn_prediction: cnnPrediction, // null or 0/1
    };

    const res = await fetch(`${BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error("Chat request failed");
    }

    return res.json(); // expected: { response: "...", source_diseases: [...], language: "..." }
  },
};
