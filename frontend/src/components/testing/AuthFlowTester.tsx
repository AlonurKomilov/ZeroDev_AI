/**
 * Authentication Flow Testing Component
 * Comprehensive testing of JWT authentication system
 */

'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Loader2, 
  Shield, 
  Key, 
  User, 
  Clock,
  Zap
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface AuthTestResult {
  test: string
  status: 'pending' | 'success' | 'failure' | 'warning'
  message: string
  duration?: number
  details?: any
}

interface AuthTokens {
  access_token?: string
  refresh_token?: string
  expires_in?: number
}

export default function AuthFlowTester() {
  const [isRunning, setIsRunning] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentTest, setCurrentTest] = useState('')
  const [results, setResults] = useState<AuthTestResult[]>([])
  const [tokens, setTokens] = useState<AuthTokens>({})
  const [testCredentials, setTestCredentials] = useState({
    email: 'test@example.com',
    password: 'testpassword123'
  })
  const { toast } = useToast()

  const authTests = [
    {
      name: 'User Registration',
      test: 'registration',
      description: 'Test user account creation'
    },
    {
      name: 'Login Authentication', 
      test: 'login',
      description: 'Test JWT token generation'
    },
    {
      name: 'Token Validation',
      test: 'tokenValidation', 
      description: 'Test access token validation'
    },
    {
      name: 'Protected Route Access',
      test: 'protectedRoute',
      description: 'Test authenticated API access'
    },
    {
      name: 'Token Refresh',
      test: 'tokenRefresh',
      description: 'Test refresh token functionality'
    },
    {
      name: 'Logout Process',
      test: 'logout',
      description: 'Test token invalidation'
    },
    {
      name: 'Expired Token Handling',
      test: 'expiredToken',
      description: 'Test expired token behavior'
    },
    {
      name: 'Invalid Credentials',
      test: 'invalidCredentials',
      description: 'Test authentication failure handling'
    }
  ]

  const runAuthTests = async () => {
    setIsRunning(true)
    setProgress(0)
    setResults([])
    
    const totalTests = authTests.length
    
    for (let i = 0; i < authTests.length; i++) {
      const testCase = authTests[i]
      setCurrentTest(testCase.name)
      setProgress(((i + 1) / totalTests) * 100)
      
      const startTime = Date.now()
      let result: AuthTestResult
      
      try {
        result = await executeAuthTest(testCase.test)
      } catch (error) {
        result = {
          test: testCase.name,
          status: 'failure',
          message: error instanceof Error ? error.message : 'Unknown error',
          duration: Date.now() - startTime
        }
      }
      
      result.duration = Date.now() - startTime
      setResults(prev => [...prev, result])
      
      // Delay between tests for visibility
      await new Promise(resolve => setTimeout(resolve, 500))
    }
    
    setIsRunning(false)
    setCurrentTest('')
    
    const successCount = results.filter(r => r.status === 'success').length
    const failureCount = results.filter(r => r.status === 'failure').length
    
    toast({
      title: "Authentication Testing Complete",
      description: `${successCount} passed, ${failureCount} failed`,
      variant: failureCount > 0 ? 'destructive' : 'default',
    })
  }

  const executeAuthTest = async (testType: string): Promise<AuthTestResult> => {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    switch (testType) {
      case 'registration':
        return await testRegistration(baseUrl)
      case 'login':
        return await testLogin(baseUrl)
      case 'tokenValidation':
        return await testTokenValidation(baseUrl)
      case 'protectedRoute':
        return await testProtectedRoute(baseUrl)
      case 'tokenRefresh':
        return await testTokenRefresh(baseUrl)
      case 'logout':
        return await testLogout(baseUrl)
      case 'expiredToken':
        return await testExpiredToken(baseUrl)
      case 'invalidCredentials':
        return await testInvalidCredentials(baseUrl)
      default:
        throw new Error(`Unknown test type: ${testType}`)
    }
  }

  const testRegistration = async (baseUrl: string): Promise<AuthTestResult> => {
    const response = await fetch(`${baseUrl}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: `test_${Date.now()}@example.com`,
        password: testCredentials.password,
        name: 'Test User'
      })
    })
    
    if (response.ok) {
      const data = await response.json()
      return {
        test: 'User Registration',
        status: 'success',
        message: 'User registration successful',
        details: data
      }
    } else if (response.status === 409) {
      return {
        test: 'User Registration',
        status: 'warning',
        message: 'User already exists (expected for repeated tests)',
      }
    } else {
      throw new Error(`Registration failed: ${response.status}`)
    }
  }

  const testLogin = async (baseUrl: string): Promise<AuthTestResult> => {
    const response = await fetch(`${baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testCredentials)
    })
    
    if (response.ok) {
      const data = await response.json()
      setTokens({
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        expires_in: data.expires_in
      })
      
      return {
        test: 'Login Authentication',
        status: 'success',
        message: 'Login successful, tokens received',
        details: { 
          hasAccessToken: !!data.access_token,
          hasRefreshToken: !!data.refresh_token,
          expiresIn: data.expires_in
        }
      }
    } else {
      throw new Error(`Login failed: ${response.status}`)
    }
  }

  const testTokenValidation = async (baseUrl: string): Promise<AuthTestResult> => {
    if (!tokens.access_token) {
      throw new Error('No access token available')
    }
    
    const response = await fetch(`${baseUrl}/auth/validate`, {
      method: 'GET',
      headers: { 
        'Authorization': `Bearer ${tokens.access_token}` 
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      return {
        test: 'Token Validation',
        status: 'success',
        message: 'Token validation successful',
        details: data
      }
    } else {
      throw new Error(`Token validation failed: ${response.status}`)
    }
  }

  const testProtectedRoute = async (baseUrl: string): Promise<AuthTestResult> => {
    if (!tokens.access_token) {
      throw new Error('No access token available')
    }
    
    const response = await fetch(`${baseUrl}/api/dashboard/stats`, {
      method: 'GET',
      headers: { 
        'Authorization': `Bearer ${tokens.access_token}` 
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      return {
        test: 'Protected Route Access',
        status: 'success',
        message: 'Protected route access successful',
        details: data
      }
    } else {
      throw new Error(`Protected route access failed: ${response.status}`)
    }
  }

  const testTokenRefresh = async (baseUrl: string): Promise<AuthTestResult> => {
    if (!tokens.refresh_token) {
      throw new Error('No refresh token available')
    }
    
    const response = await fetch(`${baseUrl}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: tokens.refresh_token })
    })
    
    if (response.ok) {
      const data = await response.json()
      setTokens(prev => ({
        ...prev,
        access_token: data.access_token,
        expires_in: data.expires_in
      }))
      
      return {
        test: 'Token Refresh',
        status: 'success',
        message: 'Token refresh successful',
        details: data
      }
    } else {
      throw new Error(`Token refresh failed: ${response.status}`)
    }
  }

  const testLogout = async (baseUrl: string): Promise<AuthTestResult> => {
    if (!tokens.access_token) {
      throw new Error('No access token available')
    }
    
    const response = await fetch(`${baseUrl}/auth/logout`, {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${tokens.access_token}` 
      }
    })
    
    if (response.ok) {
      return {
        test: 'Logout Process',
        status: 'success',
        message: 'Logout successful'
      }
    } else {
      throw new Error(`Logout failed: ${response.status}`)
    }
  }

  const testExpiredToken = async (baseUrl: string): Promise<AuthTestResult> => {
    // Use a clearly expired token
    const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.invalid'
    
    const response = await fetch(`${baseUrl}/auth/validate`, {
      method: 'GET',
      headers: { 
        'Authorization': `Bearer ${expiredToken}` 
      }
    })
    
    if (response.status === 401) {
      return {
        test: 'Expired Token Handling',
        status: 'success',
        message: 'Expired token correctly rejected',
        details: { expectedStatus: 401, actualStatus: response.status }
      }
    } else {
      throw new Error(`Expected 401 for expired token, got ${response.status}`)
    }
  }

  const testInvalidCredentials = async (baseUrl: string): Promise<AuthTestResult> => {
    const response = await fetch(`${baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'nonexistent@example.com',
        password: 'wrongpassword'
      })
    })
    
    if (response.status === 401 || response.status === 422) {
      return {
        test: 'Invalid Credentials',
        status: 'success',
        message: 'Invalid credentials correctly rejected',
        details: { expectedStatus: '401 or 422', actualStatus: response.status }
      }
    } else {
      throw new Error(`Expected 401/422 for invalid credentials, got ${response.status}`)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failure':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      default:
        return <Clock className="w-5 h-5 text-gray-400" />
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-6 h-6 text-blue-500" />
            Authentication Flow Tester
          </CardTitle>
          <CardDescription>
            Comprehensive testing of JWT authentication system with real backend integration
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Test Credentials */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Test Email</label>
              <Input
                value={testCredentials.email}
                onChange={(e) => setTestCredentials(prev => ({
                  ...prev,
                  email: e.target.value
                }))}
                disabled={isRunning}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Test Password</label>
              <Input
                type="password"
                value={testCredentials.password}
                onChange={(e) => setTestCredentials(prev => ({
                  ...prev,
                  password: e.target.value
                }))}
                disabled={isRunning}
              />
            </div>
          </div>

          {/* Progress */}
          {isRunning && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>{currentTest}</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <Progress value={progress} className="w-full" />
            </div>
          )}

          {/* Control Button */}
          <Button
            onClick={runAuthTests}
            disabled={isRunning}
            className="w-full"
          >
            {isRunning ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Running Tests...
              </>
            ) : (
              <>
                <Zap className="w-4 h-4 mr-2" />
                Run Authentication Tests
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Test Results */}
      {results.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Test Results
              <div className="flex gap-2">
                <Badge variant="default" className="bg-green-100 text-green-800">
                  {results.filter(r => r.status === 'success').length} Passed
                </Badge>
                <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                  {results.filter(r => r.status === 'warning').length} Warnings
                </Badge>
                <Badge variant="destructive">
                  {results.filter(r => r.status === 'failure').length} Failed
                </Badge>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {results.map((result, index) => (
                <div key={index} className="flex items-center gap-3 p-3 border rounded-lg">
                  {getStatusIcon(result.status)}
                  <div className="flex-1">
                    <div className="font-medium">{result.test}</div>
                    <div className="text-sm text-muted-foreground">{result.message}</div>
                    {result.duration && (
                      <div className="text-xs text-gray-500 mt-1">
                        Duration: {result.duration}ms
                      </div>
                    )}
                  </div>
                  {result.details && (
                    <details className="text-xs">
                      <summary className="cursor-pointer">Details</summary>
                      <pre className="mt-1 p-2 bg-gray-100 rounded text-xs overflow-x-auto">
                        {JSON.stringify(result.details, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Current Token Status */}
      {tokens.access_token && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="w-5 h-5 text-amber-500" />
              Current Authentication State
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm font-medium">Access Token</div>
                <div className="text-xs text-gray-500 font-mono break-all">
                  {tokens.access_token?.substring(0, 50)}...
                </div>
              </div>
              <div>
                <div className="text-sm font-medium">Expires In</div>
                <div className="text-sm text-gray-600">
                  {tokens.expires_in ? `${tokens.expires_in} seconds` : 'Unknown'}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
