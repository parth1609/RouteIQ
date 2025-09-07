import React, { createContext, useContext, useState, useEffect } from 'react'

/**
 * Authentication Context
 * Provides authentication state and methods throughout the application
 */
const AuthContext = createContext({
  user: null,
  isAuthenticated: false,
  login: () => {},
  logout: () => {},
  loading: false
})

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for existing authentication on mount
    checkAuthStatus()
  }, [])

  const checkAuthStatus = () => {
    try {
      const savedUser = localStorage.getItem('routeiq_user')
      const token = localStorage.getItem('routeiq_token')
      
      if (savedUser && token) {
        setUser(JSON.parse(savedUser))
      }
    } catch (error) {
      console.error('Failed to check auth status:', error)
      // Clear invalid data
      localStorage.removeItem('routeiq_user')
      localStorage.removeItem('routeiq_token')
    } finally {
      setLoading(false)
    }
  }

  const login = async (credentials) => {
    setLoading(true)
    try {
      // In a real app, this would call your authentication API
      // For demo purposes, we'll simulate authentication
      const { email, password } = credentials
      
      if (email && password) {
        const mockUser = {
          id: '1',
          email: email,
          name: email.split('@')[0],
          role: 'admin',
          avatar: `https://ui-avatars.com/api/?name=${email}&background=1976D2&color=fff`
        }
        
        const mockToken = 'mock-jwt-token-' + Date.now()
        
        // Save to localStorage
        localStorage.setItem('routeiq_user', JSON.stringify(mockUser))
        localStorage.setItem('routeiq_token', mockToken)
        
        setUser(mockUser)
        return { success: true, user: mockUser }
      } else {
        throw new Error('Invalid credentials')
      }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('routeiq_user')
    localStorage.removeItem('routeiq_token')
    setUser(null)
  }

  const value = {
    user,
    isAuthenticated: !!user,
    login,
    logout,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export default AuthContext
