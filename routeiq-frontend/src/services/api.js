import axios from 'axios'
import { API_CONFIG } from '@/lib/utils'

/**
 * API client configuration for RouteIQ backend
 * Handles authentication, error handling, and request/response interceptors
 */
const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth tokens
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('routeiq_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('routeiq_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

/**
 * Health Check API
 */
export const healthAPI = {
  // Check overall API health
  checkAPI: () => apiClient.get('/health'),
  
  // Check classifier health
  checkClassifier: () => apiClient.get('/classifier/health'),
  
  // Check Zendesk integration health
  checkZendesk: () => apiClient.get('/zendesk/health'),
  
  // Check Zammad integration health
  checkZammad: () => apiClient.get('/zammad/health'),
}

/**
 * Zammad API endpoints
 */
export const zammadAPI = {
  // Create a new ticket
  createTicket: (ticketData) => apiClient.post('/zammad/tickets', ticketData),
  
  // List tickets with optional filters
  listTickets: (params = {}) => apiClient.get('/zammad/tickets', { params }),
  
  // Get a specific ticket by ID
  getTicket: (ticketId) => apiClient.get(`/zammad/tickets/${ticketId}`),
  
  // Update a ticket
  updateTicket: (ticketId, updateData) => apiClient.patch(`/zammad/tickets/${ticketId}`, updateData),
  
  // Delete/close a ticket
  deleteTicket: (ticketId) => apiClient.delete(`/zammad/tickets/${ticketId}`),
}

/**
 * Zendesk API endpoints
 */
export const zendeskAPI = {
  // Create a new ticket
  createTicket: (ticketData) => apiClient.post('/zendesk/tickets', ticketData),
  
  // List tickets
  listTickets: (params = {}) => apiClient.get('/zendesk/tickets', { params }),
  
  // Get a specific ticket by ID
  getTicket: (ticketId) => apiClient.get(`/zendesk/tickets/${ticketId}`),
  
  // Update a ticket
  updateTicket: (ticketId, updateData) => apiClient.patch(`/zendesk/tickets/${ticketId}`, updateData),
  
  // Delete a ticket
  deleteTicket: (ticketId) => apiClient.delete(`/zendesk/tickets/${ticketId}`),
}

/**
 * AI Classifier API endpoints
 */
export const classifierAPI = {
  // Predict ticket classification
  predict: (ticketData) => apiClient.post('/classifier/predict', ticketData),
  
  // Get classifier metrics
  getMetrics: () => apiClient.get('/classifier/metrics'),
}

/**
 * Generic API error handler
 */
export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response
    return {
      message: data.message || data.detail || `HTTP ${status} Error`,
      status,
      details: data,
    }
  } else if (error.request) {
    // Request was made but no response received
    return {
      message: 'Network error - please check your connection',
      status: 0,
      details: error.request,
    }
  } else {
    // Something else happened
    return {
      message: error.message || 'An unexpected error occurred',
      status: -1,
      details: error,
    }
  }
}

export default apiClient
