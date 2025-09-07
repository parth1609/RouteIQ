import React from 'react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'

/**
 * Error Boundary Component
 * Catches JavaScript errors anywhere in the child component tree and displays a fallback UI
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    // Log error details for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    })

    // In a real app, you would send this to an error reporting service
    // Example: Sentry.captureException(error, { extra: errorInfo })
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null })
  }

  render() {
    if (this.state.hasError) {
      const { fallback: Fallback } = this.props

      // If a custom fallback component is provided, use it
      if (Fallback) {
        return <Fallback error={this.state.error} resetError={this.handleReset} />
      }

      // Default error UI
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <Card className="max-w-lg w-full">
            <CardHeader className="text-center">
              <div className="h-12 w-12 rounded-lg bg-gradient-to-r from-red-500 to-red-600 mx-auto mb-4 flex items-center justify-center">
                <span className="text-white text-2xl">⚠️</span>
              </div>
              <CardTitle className="text-red-600">Something went wrong</CardTitle>
              <CardDescription>
                An unexpected error occurred. Our team has been notified.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-red-800 mb-2">Error Details:</h4>
                <p className="text-sm text-red-700 font-mono">
                  {this.state.error?.message || 'Unknown error'}
                </p>
              </div>
              
              <div className="flex space-x-3">
                <Button onClick={this.handleReset} className="flex-1">
                  Try Again
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => window.location.href = '/'}
                  className="flex-1"
                >
                  Go Home
                </Button>
              </div>
              
              {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                <details className="mt-4">
                  <summary className="text-sm font-medium text-gray-700 cursor-pointer">
                    Stack Trace (Development)
                  </summary>
                  <pre className="mt-2 text-xs text-gray-600 bg-gray-100 p-3 rounded overflow-auto max-h-40">
                    {this.state.errorInfo.componentStack}
                  </pre>
                </details>
              )}
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

/**
 * Hook-based error boundary for functional components
 */
export const useErrorHandler = () => {
  const [error, setError] = React.useState(null)

  const resetError = React.useCallback(() => {
    setError(null)
  }, [])

  const captureError = React.useCallback((error) => {
    console.error('Error captured:', error)
    setError(error)
  }, [])

  React.useEffect(() => {
    if (error) {
      throw error
    }
  }, [error])

  return { captureError, resetError }
}

/**
 * Loading Error Component
 * Specialized error component for loading states
 */
export const LoadingError = ({ error, onRetry, message }) => (
  <div className="text-center py-12">
    <div className="text-4xl mb-4">😵</div>
    <h3 className="text-lg font-medium text-gray-900 mb-2">
      {message || 'Failed to load data'}
    </h3>
    <p className="text-gray-500 mb-4">
      {error?.message || 'An error occurred while loading'}
    </p>
    {onRetry && (
      <Button onClick={onRetry} variant="outline">
        Try Again
      </Button>
    )}
  </div>
)

/**
 * Network Error Component
 * Specialized error component for network issues
 */
export const NetworkError = ({ onRetry }) => (
  <div className="text-center py-12">
    <div className="text-4xl mb-4">📡</div>
    <h3 className="text-lg font-medium text-gray-900 mb-2">
      Connection Problem
    </h3>
    <p className="text-gray-500 mb-4">
      Unable to connect to the server. Please check your internet connection.
    </p>
    {onRetry && (
      <Button onClick={onRetry} variant="outline">
        Retry Connection
      </Button>
    )}
  </div>
)

export { ErrorBoundary }
