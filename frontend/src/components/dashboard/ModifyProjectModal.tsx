'use client'

import React, { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Loader2, CheckCircle, AlertTriangle, XCircle, Zap, Code, Database, Globe, Wifi, WifiOff } from 'lucide-react'
import { useWebSocket } from '@/lib/websocket'
import { useToast } from '@/hooks/use-toast'

interface ModifyProjectModalProps {
  isOpen: boolean
  onClose: () => void
  projectId: string
}

interface ModificationResult {
  success: boolean
  filesModified: number
  testsRun: number
  testsPass: number
  warnings: number
  changes: Array<{
    type: 'added' | 'modified' | 'deleted'
    file: string
    lines: number
  }>
}

interface ProgressUpdate {
  step: string
  progress: number
  details?: string
  timestamp: number
}

export default function ModifyProjectModal({ isOpen, onClose, projectId }: ModifyProjectModalProps) {
  const [modifications, setModifications] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState('')
  const [results, setResults] = useState<ModificationResult | null>(null)
  const [taskId, setTaskId] = useState<string | null>(null)
  const { toast } = useToast()

  // WebSocket connection for real-time updates
  const {
    isConnected,
    isConnecting,
    send,
    subscribe,
    unsubscribe,
  } = useWebSocket(
    process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws',
    {
      onConnect: () => {
        toast({
          title: "Connected",
          description: "Real-time updates enabled",
          duration: 2000,
        })
      },
      onDisconnect: () => {
        toast({
          title: "Disconnected",
          description: "Real-time updates unavailable",
          variant: "destructive",
          duration: 3000,
        })
      },
      onError: (error) => {
        console.error('WebSocket error:', error)
        toast({
          title: "Connection Error",
          description: "Failed to connect to real-time updates",
          variant: "destructive",
        })
      },
    }
  )

  // Subscribe to real-time progress updates
  useEffect(() => {
    const handleProgressUpdate = (data: ProgressUpdate) => {
      if (taskId && data.timestamp) {
        setCurrentStep(data.step)
        setProgress(data.progress)
      }
    }

    const handleModificationComplete = (data: ModificationResult & { taskId: string }) => {
      if (data.taskId === taskId) {
        setResults(data)
        setIsProcessing(false)
        setTaskId(null)
        
        toast({
          title: data.success ? "Modification Complete" : "Modification Failed",
          description: data.success 
            ? `Successfully modified ${data.filesModified} files`
            : "Project modification failed. Check logs for details.",
          variant: data.success ? "default" : "destructive",
        })
      }
    }

    const handleModificationError = (data: { taskId: string; error: string; details?: string }) => {
      if (data.taskId === taskId) {
        setIsProcessing(false)
        setTaskId(null)
        
        toast({
          title: "Modification Failed",
          description: data.error,
          variant: "destructive",
        })
      }
    }

    if (isConnected) {
      subscribe('progress_update', handleProgressUpdate)
      subscribe('modification_complete', handleModificationComplete)
      subscribe('modification_error', handleModificationError)
    }

    return () => {
      if (isConnected) {
        unsubscribe('progress_update', handleProgressUpdate)
        unsubscribe('modification_complete', handleModificationComplete)
        unsubscribe('modification_error', handleModificationError)
      }
    }
  }, [isConnected, taskId, subscribe, unsubscribe, toast])

  const handleSubmit = async () => {
    if (!modifications.trim()) return

    if (!isConnected) {
      toast({
        title: "Connection Required",
        description: "Real-time connection required for project modifications",
        variant: "destructive",
      })
      return
    }

    setIsProcessing(true)
    setProgress(0)
    setCurrentStep('Initializing modification...')
    setResults(null)

    // Generate unique task ID for tracking
    const newTaskId = `modify_${projectId}_${Date.now()}`
    setTaskId(newTaskId)

    try {
      // Send modification request via WebSocket
      send('start_modification', {
        taskId: newTaskId,
        projectId,
        modifications: modifications.trim(),
        timestamp: Date.now(),
      })

      toast({
        title: "Modification Started",
        description: "Project modification is in progress...",
      })
    } catch (error) {
      console.error('Failed to start modification:', error)
      setIsProcessing(false)
      setTaskId(null)
      
      toast({
        title: "Failed to Start",
        description: "Could not initiate project modification",
        variant: "destructive",
      })
    }
  }

  const resetForm = () => {
    setModifications('')
    setProgress(0)
    setCurrentStep('')
    setResults(null)
    setTaskId(null)
    setIsProcessing(false)
  }

  const handleClose = () => {
    resetForm()
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-500" />
            Modify Project
            <div className="flex items-center gap-2 ml-auto">
              {isConnecting ? (
                <Badge variant="secondary" className="flex items-center gap-1">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  Connecting...
                </Badge>
              ) : isConnected ? (
                <Badge variant="default" className="flex items-center gap-1 bg-green-600">
                  <Wifi className="w-3 h-3" />
                  Live Updates
                </Badge>
              ) : (
                <Badge variant="destructive" className="flex items-center gap-1">
                  <WifiOff className="w-3 h-3" />
                  Offline
                </Badge>
              )}
            </div>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Input Section */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Describe Your Modifications</CardTitle>
              <CardDescription>
                Describe what you want to modify in your project. Be specific about features, components, or functionality.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                value={modifications}
                onChange={(e) => setModifications(e.target.value)}
                placeholder="e.g., Add a user authentication system with JWT tokens, Create a new dashboard component with charts, Optimize database queries..."
                rows={6}
                disabled={isProcessing}
                className="w-full"
              />
            </CardContent>
          </Card>

          {/* Progress Section */}
          {isProcessing && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                  Processing Modifications...
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>{currentStep}</span>
                    <span>{progress}%</span>
                  </div>
                  <Progress value={progress} className="w-full" />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Results Section */}
          {results && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {results.success ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-500" />
                  )}
                  Modification {results.success ? 'Completed' : 'Failed'}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {results.success && (
                  <>
                    {/* Summary Stats */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">{results.filesModified}</div>
                        <div className="text-sm text-blue-700 dark:text-blue-300">Files Modified</div>
                      </div>
                      <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">{results.testsPass}</div>
                        <div className="text-sm text-green-700 dark:text-green-300">Tests Passed</div>
                      </div>
                      <div className="text-center p-3 bg-gray-50 dark:bg-gray-900/20 rounded-lg">
                        <div className="text-2xl font-bold text-gray-600">{results.testsRun}</div>
                        <div className="text-sm text-gray-700 dark:text-gray-300">Tests Run</div>
                      </div>
                      <div className="text-center p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                        <div className="text-2xl font-bold text-amber-600">{results.warnings}</div>
                        <div className="text-sm text-amber-700 dark:text-amber-300">Warnings</div>
                      </div>
                    </div>

                    {/* File Changes */}
                    <div>
                      <h4 className="font-semibold mb-2">File Changes</h4>
                      <div className="space-y-2">
                        {results.changes.map((change, index) => (
                          <div key={index} className="flex items-center gap-2 p-2 border rounded-lg">
                            {change.type === 'added' && <Code className="w-4 h-4 text-green-500" />}
                            {change.type === 'modified' && <Database className="w-4 h-4 text-blue-500" />}
                            {change.type === 'deleted' && <XCircle className="w-4 h-4 text-red-500" />}
                            <span className="font-medium">{change.file}</span>
                            <Badge variant={change.type === 'added' ? 'default' : change.type === 'modified' ? 'secondary' : 'destructive'}>
                              {change.type}
                            </Badge>
                            <span className="text-sm text-muted-foreground ml-auto">
                              {change.lines} lines
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 justify-end">
            <Button
              variant="outline"
              onClick={handleClose}
              disabled={isProcessing}
            >
              {isProcessing ? 'Processing...' : 'Close'}
            </Button>
            {!isProcessing && !results && (
              <Button
                onClick={handleSubmit}
                disabled={!modifications.trim() || !isConnected}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                <Globe className="w-4 h-4 mr-2" />
                Start Modification
              </Button>
            )}
            {results && (
              <Button
                onClick={resetForm}
                className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
              >
                <Zap className="w-4 h-4 mr-2" />
                New Modification
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
