/**
 * Global API Error Handler
 * Centralized error handling for API requests with retry logic
 */

'use client'

import React, { createContext, useContext, ReactNode } from 'react'
import { useToast } from '@/hooks/use-toast'

interface APIError {
  message: string
  status?: number
  code?: string
  details?: any
}

interface ErrorBoundaryContextType {
  handleError: (error: APIError | Error, context?: string) => void
  handleAPIError: (response: Response, context?: string) => Promise<void>
  retryableRequest: <T>(
    request: () => Promise<T>,
    options?: RetryOptions
  ) => Promise<T>
}

interface RetryOptions {
  maxRetries?: number
  retryDelay?: number
  context?: string
  onRetry?: (attempt: number) => void
}

const ErrorBoundaryContext = createContext<ErrorBoundaryContextType | null>(null)

export function useErrorHandler() {
  const context = useContext(ErrorBoundaryContext)
  if (!context) {
    throw new Error('useErrorHandler must be used within ErrorBoundaryProvider')
  }
  return context
}

interface ErrorBoundaryProviderProps {
  children: ReactNode
}

export function ErrorBoundaryProvider({ children }: ErrorBoundaryProviderProps) {
  const { toast } = useToast()

  const handleError = (error: APIError | Error, context = 'Operation') => {
    console.error(`Error in ${context}:`, error)

    let errorMessage = 'An unexpected error occurred'
    let title = `${context} Failed`

    if (error instanceof Error) {
      errorMessage = error.message
    } else if (error.message) {
      errorMessage = error.message
    }

    // Special handling for common HTTP errors
    if ('status' in error && error.status) {
      switch (error.status) {
        case 401:
          title = 'Authentication Required'
          errorMessage = 'Please log in to continue'
          // Redirect to login could be handled here
          break
        case 403:
          title = 'Access Denied'
          errorMessage = 'You do not have permission to perform this action'
          break
        case 404:
          title = 'Not Found'
          errorMessage = 'The requested resource was not found'
          break
        case 429:
          title = 'Rate Limited'
          errorMessage = 'Too many requests. Please try again later.'
          break
        case 500:
          title = 'Server Error'
          errorMessage = 'Internal server error. Please try again later.'
          break
        case 503:
          title = 'Service Unavailable'
          errorMessage = 'Service is temporarily unavailable'
          break
      }
    }

    toast({
      title,
      description: errorMessage,
      variant: 'destructive',
      duration: 5000,
    })
  }

  const handleAPIError = async (response: Response, context = 'API Request') => {
    let errorDetails: any = {}
    
    try {
      const contentType = response.headers.get('content-type')
      if (contentType?.includes('application/json')) {
        errorDetails = await response.json()
      } else {
        errorDetails = { message: await response.text() }
      }
    } catch {
      errorDetails = { message: 'Failed to parse error response' }
    }

    const apiError: APIError = {
      message: errorDetails.message || errorDetails.detail || `HTTP ${response.status} Error`,
      status: response.status,
      code: errorDetails.code,
      details: errorDetails,
    }

    handleError(apiError, context)
  }

  const retryableRequest = async function<T>(
    request: () => Promise<T>,
    options: RetryOptions = {}
  ): Promise<T> {
    const {
      maxRetries = 3,
      retryDelay = 1000,
      context = 'Request',
      onRetry,
    } = options

    let lastError: Error | null = null

    for (let attempt = 1; attempt <= maxRetries + 1; attempt++) {
      try {
        return await request()
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error))
        
        // Don't retry on the last attempt
        if (attempt > maxRetries) {
          break
        }

        // Don't retry on certain errors
        if (error instanceof Error && 'status' in error) {
          const status = (error as any).status
          // Don't retry on 4xx errors (except 408, 429)
          if (status >= 400 && status < 500 && status !== 408 && status !== 429) {
            break
          }
        }

        console.warn(`${context} failed (attempt ${attempt}/${maxRetries + 1}), retrying in ${retryDelay}ms...`)
        
        onRetry?.(attempt)
        
        // Wait before retrying with exponential backoff
        const delay = retryDelay * Math.pow(2, attempt - 1)
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }

    // All retries failed, handle the error
    if (lastError) {
      handleError(lastError, context)
      throw lastError
    }

    throw new Error(`${context} failed after ${maxRetries + 1} attempts`)
  }

  const contextValue: ErrorBoundaryContextType = {
    handleError,
    handleAPIError,
    retryableRequest,
  }

  return (
    <ErrorBoundaryContext.Provider value={contextValue}>
      {children}
    </ErrorBoundaryContext.Provider>
  )
}

/**
 * Higher-order component for API error handling
 */
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>
) {
  return function WithErrorBoundaryWrapper(props: P) {
    return (
      <ErrorBoundaryProvider>
        <Component {...props} />
      </ErrorBoundaryProvider>
    )
  }
}

/**
 * Utility function for handling fetch requests with error handling
 */
export async function apiRequest<T = any>(
  url: string,
  options: RequestInit = {},
  context = 'API Request'
): Promise<T> {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const contentType = response.headers.get('content-type')
    if (contentType?.includes('application/json')) {
      return await response.json()
    } else {
      return await response.text() as unknown as T
    }
  } catch (error) {
    console.error(`${context} failed:`, error)
    throw error
  }
}

/**
 * React Query error handler
 */
export function createQueryErrorHandler(context = 'Query') {
  return (error: unknown) => {
    console.error(`${context} error:`, error)
    
    // Handle the error based on type
    if (error instanceof Error) {
      // This would typically be handled by the ErrorBoundaryProvider
      // but for React Query we need to handle it here
    }
  }
}

/**
 * Global error boundary component
 */
interface GlobalErrorBoundaryState {
  hasError: boolean
  error?: Error
}

export class GlobalErrorBoundary extends React.Component<
  { children: ReactNode },
  GlobalErrorBoundaryState
> {
  constructor(props: { children: ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): GlobalErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Global error boundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
          <div className="text-center p-8">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Something went wrong
            </h1>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              We apologize for the inconvenience. Please try refreshing the page.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
            >
              Refresh Page
            </button>
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-4 text-left">
                <summary className="cursor-pointer text-sm text-gray-500">
                  Error Details (Development)
                </summary>
                <pre className="mt-2 text-xs text-red-600 bg-red-50 p-2 rounded">
                  {this.state.error.stack}
                </pre>
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
