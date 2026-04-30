/**
 * API Helper for Digital Twin Dashboard
 * Provides clean interface to backend APIs
 */

import axios from 'axios';

// Create axios instance with base configuration
const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor for logging
API.interceptors.request.use(
  (config) => {
    console.log(`🔗 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging
API.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// Machine API endpoints
export const machineAPI = {
  // Get all machines
  getMachines: () => API.get("/machines"),
  
  // Get machine details
  getMachine: (id) => API.get(`/machines/${id}`),
  
  // Get latest sensor data for machine
  getLatestData: (id, limit = 10) => API.get(`/machines/${id}/latest?limit=${limit}`),
  
  // Get prediction history for machine
  getPredictions: (id, limit = 50) => API.get(`/machines/${id}/predictions?limit=${limit}`),
  
  // Get anomalies for machine
  getAnomalies: (id, activeOnly = true) => 
    API.get(`/machines/${id}/anomalies${activeOnly ? '?active_only=true' : ''}`),
  
  // Get comprehensive machine status
  getMachineStatus: (id) => API.get(`/machines/${id}/status`),
};

// System API endpoints
export const systemAPI = {
  // Health check
  getHealth: () => API.get("/health"),
  
  // System health metrics
  getSystemHealth: () => API.get("/system/health"),
  
  // System metrics
  getMetrics: (metricName, hours = 24) => 
    API.get(`/system/metrics?metric_name=${metricName}&hours=${hours}`),
};

// Sensor data API endpoints
export const sensorAPI = {
  // Submit sensor data
  submitData: (data) => API.post("/sensor-data", data),
  
  // Submit full sensor data
  submitFullData: (data) => API.post("/sensor-data-full", data),
};

// Simulation API endpoints
export const simulationAPI = {
  // Run what-if simulation
  runSimulation: (params) => API.post("/simulate", params),
  
  // Run machine simulation
  runMachineSimulation: (machineId, cycles = 100) => 
    API.post(`/simulate/${machineId}?cycles=${cycles}`),
};

// Report API endpoints
export const reportAPI = {
  // Generate report
  generateReport: (config) => API.post("/generate-report", config),
};

// WebSocket connection helper
export class WebSocketManager {
  constructor(url = "ws://127.0.0.1:8000/ws") {
    this.url = url;
    this.ws = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        console.log("🔗 WebSocket connected");
        this.reconnectAttempts = 0;
        this.emit('connected');
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.emit('message', data);
        } catch (error) {
          console.error("❌ WebSocket message parse error:", error);
        }
      };

      this.ws.onclose = () => {
        console.log("🔌 WebSocket disconnected");
        this.emit('disconnected');
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error("❌ WebSocket error:", error);
        this.emit('error', error);
      };

    } catch (error) {
      console.error("❌ WebSocket connection failed:", error);
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`🔄 Reconnecting... Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error("❌ Max reconnect attempts reached");
      this.emit('maxReconnectAttemptsReached');
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn("⚠️ WebSocket not connected, message not sent");
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`❌ Error in ${event} listener:`, error);
        }
      });
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Create singleton WebSocket manager
export const wsManager = new WebSocketManager();

// Utility functions
export const apiUtils = {
  // Format timestamp
  formatTimestamp: (timestamp) => {
    return new Date(timestamp).toLocaleString();
  },

  // Get health status color
  getHealthColor: (health) => {
    const colors = {
      'HEALTHY': '#22c55e',
      'WARNING': '#f59e0b', 
      'CRITICAL': '#ef4444',
      'COLLECTING': '#6366f1'
    };
    return colors[health] || '#6b7280';
  },

  // Get RUL status
  getRULStatus: (rul) => {
    if (rul === null || rul === undefined) return 'COLLECTING';
    if (rul >= 50) return 'HEALTHY';
    if (rul >= 20) return 'WARNING';
    return 'CRITICAL';
  },

  // Format sensor value
  formatSensorValue: (value, decimals = 2) => {
    if (value === null || value === undefined) return '--';
    return Number(value).toFixed(decimals);
  },

  // Calculate health score
  calculateHealthScore: (rul) => {
    if (rul === null || rul === undefined) return 0;
    if (rul >= 50) return 100;
    if (rul >= 20) return 60 + (rul - 20) * 40 / 30;
    return Math.max(0, rul * 3);
  },

  // Get trend direction
  getTrend: (current, previous) => {
    if (previous === null || previous === undefined) return 'stable';
    const diff = current - previous;
    if (Math.abs(diff) < 0.1) return 'stable';
    return diff > 0 ? 'up' : 'down';
  },

  // Get trend icon
  getTrendIcon: (trend) => {
    const icons = {
      'up': '↗️',
      'down': '↘️',
      'stable': '→'
    };
    return icons[trend] || '→';
  }
};

export default API;
