# Frontend Kengaytmalari va Yaxshilashlar

## 1. Next.js Performance Optimizatsiyalari

### Bundle Size Optimizatsiya
```javascript
// next.config.js - Enhanced configuration
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    turbo: true,
    optimizePackageImports: ['@tanstack/react-query', 'framer-motion', 'reactflow'],
    swcMinify: true
  },
  
  // Bundle analyzer
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            chunks: 'all',
            priority: 1
          },
          common: {
            minChunks: 2,
            priority: 0,
            reuseExistingChunk: true
          }
        }
      }
    }
    return config
  },

  // Image optimization
  images: {
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 768, 1024, 1280, 1600],
    imageSizes: [16, 32, 48, 64, 96, 128, 256],
    remotePatterns: [
      {
        protocol: "https",
        hostname: "via.placeholder.com",
      },
      {
        protocol: "https",
        hostname: "*.githubusercontent.com",
      }
    ],
  },

  // Compression
  compress: true,
  poweredByHeader: false,

  // Static optimization
  trailingSlash: false,
  
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.BACKEND_URL}/api/:path*`,
      }
    ]
  }
};

export default nextConfig;
```

### Advanced Lazy Loading
```typescript
// components/LazyComponents.tsx
import dynamic from 'next/dynamic'
import { Suspense } from 'react'

// Enhanced lazy loading with proper types
export const LazyIdeationCanvas = dynamic(
  () => import('./features/IdeationCanvas'),
  {
    loading: () => <div className="animate-pulse">Loading Canvas...</div>,
    ssr: false
  }
)

export const LazyReactFlow = dynamic(
  () => import('reactflow'),
  { ssr: false }
)

export const LazyMonacoEditor = dynamic(
  () => import('@monaco-editor/react'),
  {
    loading: () => <div className="h-96 bg-gray-100 animate-pulse rounded"></div>,
    ssr: false
  }
)

// Route-based code splitting
export const LazyAdminDashboard = dynamic(
  () => import('./features/admin/AdminDashboard'),
  {
    loading: () => <AdminDashboardSkeleton />,
    ssr: false
  }
)

// Component with error boundary
interface LazyWrapperProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

export const LazyWrapper = ({ children, fallback }: LazyWrapperProps) => (
  <Suspense fallback={fallback || <div>Loading...</div>}>
    {children}
  </Suspense>
)
```

## 2. State Management Yaxshilashlar

### Enhanced React Query Configuration
```typescript
// lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query'
import { persistQueryClient } from '@tanstack/react-query-persist-client-core'
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister'

// Advanced query client configuration
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: (failureCount, error: any) => {
        if (error?.status === 404) return false
        return failureCount < 3
      },
      refetchOnWindowFocus: false,
      refetchOnReconnect: 'always',
    },
    mutations: {
      retry: 1,
      onError: (error: any) => {
        console.error('Mutation error:', error)
        // Global error handling
      }
    }
  }
})

// Persist queries to localStorage
const localStoragePersister = createSyncStoragePersister({
  storage: typeof window !== 'undefined' ? window.localStorage : undefined,
  key: 'REACT_QUERY_OFFLINE_CACHE',
})

if (typeof window !== 'undefined') {
  persistQueryClient({
    queryClient,
    persister: localStoragePersister,
    maxAge: 1000 * 60 * 60 * 24, // 24 hours
  })
}
```

### Global State Management with Zustand
```typescript
// stores/appStore.ts
import { create } from 'zustand'
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware'

interface AppState {
  // UI State
  theme: 'light' | 'dark' | 'system'
  sidebarCollapsed: boolean
  notifications: Notification[]
  
  // User State
  user: User | null
  preferences: UserPreferences
  
  // Project State
  activeProject: Project | null
  projectsFilter: ProjectFilter
  
  // Actions
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  toggleSidebar: () => void
  addNotification: (notification: Notification) => void
  removeNotification: (id: string) => void
  setUser: (user: User | null) => void
  updatePreferences: (preferences: Partial<UserPreferences>) => void
  setActiveProject: (project: Project | null) => void
  updateProjectsFilter: (filter: Partial<ProjectFilter>) => void
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      subscribeWithSelector((set, get) => ({
        // Initial state
        theme: 'system',
        sidebarCollapsed: false,
        notifications: [],
        user: null,
        preferences: {
          language: 'en',
          autoSave: true,
          showTips: true
        },
        activeProject: null,
        projectsFilter: {
          status: 'all',
          framework: 'all',
          sortBy: 'created_at',
          order: 'desc'
        },

        // Actions
        setTheme: (theme) => set({ theme }),
        toggleSidebar: () => set(state => ({ sidebarCollapsed: !state.sidebarCollapsed })),
        addNotification: (notification) => 
          set(state => ({ 
            notifications: [...state.notifications, { ...notification, id: crypto.randomUUID() }] 
          })),
        removeNotification: (id) => 
          set(state => ({ 
            notifications: state.notifications.filter(n => n.id !== id) 
          })),
        setUser: (user) => set({ user }),
        updatePreferences: (preferences) => 
          set(state => ({ 
            preferences: { ...state.preferences, ...preferences } 
          })),
        setActiveProject: (project) => set({ activeProject: project }),
        updateProjectsFilter: (filter) => 
          set(state => ({ 
            projectsFilter: { ...state.projectsFilter, ...filter } 
          }))
      })),
      {
        name: 'app-store',
        partialize: (state) => ({
          theme: state.theme,
          sidebarCollapsed: state.sidebarCollapsed,
          preferences: state.preferences,
          projectsFilter: state.projectsFilter
        })
      }
    ),
    { name: 'AppStore' }
  )
)

// Selectors for better performance
export const useTheme = () => useAppStore(state => state.theme)
export const useNotifications = () => useAppStore(state => state.notifications)
export const useUser = () => useAppStore(state => state.user)
```

## 3. Komponent Optimizatsiyalari

### Advanced Virtualization
```typescript
// components/VirtualizedList.tsx
import { FixedSizeList as List } from 'react-window'
import { FixedSizeGrid as Grid } from 'react-window'
import InfiniteLoader from 'react-window-infinite-loader'
import { memo, useMemo } from 'react'

interface VirtualizedProjectListProps {
  projects: Project[]
  hasNextPage: boolean
  isLoading: boolean
  loadMore: () => void
}

const ProjectCard = memo(({ index, style, data }: any) => {
  const project = data.projects[index]
  
  return (
    <div style={style}>
      <div className="p-4 m-2 border rounded-lg shadow">
        <h3 className="text-lg font-semibold">{project.name}</h3>
        <p className="text-gray-600">{project.description}</p>
        <div className="flex justify-between items-center mt-4">
          <span className="text-sm text-gray-500">
            {new Date(project.created_at).toLocaleDateString()}
          </span>
          <Link href={`/projects/${project.id}`}>
            <Button size="sm">View</Button>
          </Link>
        </div>
      </div>
    </div>
  )
})

export const VirtualizedProjectList = memo(({ 
  projects, 
  hasNextPage, 
  isLoading, 
  loadMore 
}: VirtualizedProjectListProps) => {
  const itemCount = hasNextPage ? projects.length + 1 : projects.length
  
  const isItemLoaded = useMemo(
    () => (index: number) => !!projects[index],
    [projects]
  )
  
  return (
    <InfiniteLoader
      isItemLoaded={isItemLoaded}
      itemCount={itemCount}
      loadMoreItems={loadMore}
    >
      {({ onItemsRendered, ref }) => (
        <List
          ref={ref}
          height={600}
          itemCount={itemCount}
          itemSize={150}
          itemData={{ projects, isLoading }}
          onItemsRendered={onItemsRendered}
          overscanCount={5}
        >
          {ProjectCard}
        </List>
      )}
    </InfiniteLoader>
  )
})
```

### Enhanced Form Management
```typescript
// hooks/useFormValidation.ts
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'

// Advanced form schemas
const projectSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  description: z.string().max(500, 'Description too long'),
  framework: z.enum(['Next.js', 'React', 'Vue', 'Angular']),
  features: z.array(z.string()).min(1, 'Select at least one feature'),
  deployment: z.enum(['Vercel', 'Netlify', 'AWS', 'Custom']),
  database: z.enum(['PostgreSQL', 'MySQL', 'MongoDB', 'None']).optional(),
  authentication: z.boolean(),
  styling: z.enum(['Tailwind', 'CSS Modules', 'Styled Components']),
})

export type ProjectFormData = z.infer<typeof projectSchema>

export const useProjectForm = (initialData?: Partial<ProjectFormData>) => {
  const queryClient = useQueryClient()
  
  const form = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      name: '',
      description: '',
      framework: 'Next.js',
      features: [],
      deployment: 'Vercel',
      authentication: false,
      styling: 'Tailwind',
      ...initialData
    }
  })

  const createProject = useMutation({
    mutationFn: async (data: ProjectFormData) => {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!response.ok) throw new Error('Failed to create project')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['projects'])
      form.reset()
    }
  })

  return {
    form,
    createProject: form.handleSubmit(createProject.mutate),
    isLoading: createProject.isLoading,
    error: createProject.error
  }
}

// Enhanced form component
const ProjectCreateForm = () => {
  const { form, createProject, isLoading } = useProjectForm()
  
  return (
    <form onSubmit={createProject} className="space-y-6">
      <FormField
        control={form.control}
        name="name"
        render={({ field, fieldState }) => (
          <FormItem>
            <FormLabel>Project Name</FormLabel>
            <FormControl>
              <Input {...field} />
            </FormControl>
            <FormMessage>{fieldState.error?.message}</FormMessage>
          </FormItem>
        )}
      />
      
      <FormField
        control={form.control}
        name="features"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Features</FormLabel>
            <div className="grid grid-cols-2 gap-2">
              {FEATURE_OPTIONS.map(feature => (
                <FormControl key={feature.value}>
                  <Checkbox
                    checked={field.value.includes(feature.value)}
                    onCheckedChange={(checked) => {
                      if (checked) {
                        field.onChange([...field.value, feature.value])
                      } else {
                        field.onChange(field.value.filter(v => v !== feature.value))
                      }
                    }}
                  />
                  <span className="ml-2">{feature.label}</span>
                </FormControl>
              ))}
            </div>
          </FormItem>
        )}
      />
      
      <Button type="submit" disabled={isLoading}>
        {isLoading ? 'Creating...' : 'Create Project'}
      </Button>
    </form>
  )
}
```

## 4. Real-time Kommunikatsiya

### WebSocket Integration
```typescript
// hooks/useWebSocket.ts
import { useCallback, useEffect, useRef, useState } from 'react'
import { useAppStore } from '@/stores/appStore'

interface WebSocketMessage {
  type: string
  payload: any
  timestamp: number
}

export const useWebSocket = (url: string) => {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const ws = useRef<WebSocket | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5
  const { addNotification } = useAppStore()

  const connect = useCallback(() => {
    try {
      ws.current = new WebSocket(url)
      
      ws.current.onopen = () => {
        setIsConnected(true)
        reconnectAttempts.current = 0
        console.log('WebSocket connected')
      }

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
          
          // Handle different message types
          switch (message.type) {
            case 'notification':
              addNotification({
                type: message.payload.type,
                message: message.payload.message,
                duration: 5000
              })
              break
            case 'project_update':
              // Invalidate project queries
              queryClient.invalidateQueries(['projects', message.payload.projectId])
              break
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.current.onclose = (event) => {
        setIsConnected(false)
        
        if (!event.wasClean && reconnectAttempts.current < maxReconnectAttempts) {
          setTimeout(() => {
            reconnectAttempts.current++
            connect()
          }, Math.pow(2, reconnectAttempts.current) * 1000) // Exponential backoff
        }
      }

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
    }
  }, [url, addNotification])

  const disconnect = useCallback(() => {
    if (ws.current) {
      ws.current.close()
      ws.current = null
    }
  }, [])

  const sendMessage = useCallback((message: Omit<WebSocketMessage, 'timestamp'>) => {
    if (ws.current && isConnected) {
      ws.current.send(JSON.stringify({
        ...message,
        timestamp: Date.now()
      }))
    }
  }, [isConnected])

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return {
    isConnected,
    lastMessage,
    sendMessage,
    reconnect: connect
  }
}

// Real-time project generation
export const useProjectGeneration = (projectId: string) => {
  const { sendMessage, lastMessage } = useWebSocket(`/ws/projects/${projectId}`)
  const [logs, setLogs] = useState<string[]>([])
  const [status, setStatus] = useState('idle')

  useEffect(() => {
    if (lastMessage?.type === 'generation_log') {
      setLogs(prev => [...prev, lastMessage.payload.message])
    } else if (lastMessage?.type === 'generation_status') {
      setStatus(lastMessage.payload.status)
    }
  }, [lastMessage])

  const startGeneration = useCallback((config: any) => {
    sendMessage({
      type: 'start_generation',
      payload: config
    })
  }, [sendMessage])

  return {
    logs,
    status,
    startGeneration
  }
}
```

## 5. Advanced UI Komponentlar

### Smart Data Table
```typescript
// components/ui/DataTable.tsx
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  ColumnDef,
  flexRender,
} from '@tanstack/react-table'
import { useState, useMemo } from 'react'

interface DataTableProps<T> {
  data: T[]
  columns: ColumnDef<T, any>[]
  searchKey?: keyof T
  pageSize?: number
}

export function DataTable<T>({ 
  data, 
  columns, 
  searchKey,
  pageSize = 10 
}: DataTableProps<T>) {
  const [sorting, setSorting] = useState([])
  const [columnFilters, setColumnFilters] = useState([])
  const [globalFilter, setGlobalFilter] = useState('')

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    state: {
      sorting,
      columnFilters,
      globalFilter,
    },
    initialState: {
      pagination: {
        pageSize,
      },
    },
  })

  return (
    <div className="space-y-4">
      {/* Search */}
      <Input
        placeholder={`Search ${searchKey ? String(searchKey) : 'all columns'}...`}
        value={globalFilter ?? ''}
        onChange={(event) => setGlobalFilter(event.target.value)}
        className="max-w-sm"
      />

      {/* Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between space-x-2 py-4">
        <div className="text-sm text-muted-foreground">
          {table.getFilteredRowModel().rows.length} row(s) total
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}

// Usage example
const ProjectsTable = () => {
  const { data: projects } = useQuery(['projects'], fetchProjects)

  const columns: ColumnDef<Project>[] = useMemo(() => [
    {
      accessorKey: 'name',
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        >
          Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
    },
    {
      accessorKey: 'framework',
      header: 'Framework',
      cell: ({ row }) => (
        <Badge variant="secondary">{row.getValue('framework')}</Badge>
      ),
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => (
        <StatusBadge status={row.getValue('status')} />
      ),
    },
    {
      id: 'actions',
      cell: ({ row }) => (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <Link href={`/projects/${row.original.id}`}>View</Link>
            </DropdownMenuItem>
            <DropdownMenuItem>Edit</DropdownMenuItem>
            <DropdownMenuItem className="text-red-600">Delete</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      ),
    },
  ], [])

  return (
    <DataTable
      data={projects || []}
      columns={columns}
      searchKey="name"
    />
  )
}
```

## 6. Testing va Quality Assurance

### Comprehensive Testing Setup
```typescript
// __tests__/setup.ts
import '@testing-library/jest-dom'
import { server } from '@/mocks/server'

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/',
}))

// Setup MSW
beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

// __tests__/utils/test-utils.tsx
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@/components/providers/ThemeProvider'

const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="light">
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  )
}

const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

export * from '@testing-library/react'
export { customRender as render }

// Component tests
// __tests__/components/ProjectCard.test.tsx
import { render, screen, fireEvent } from '@/utils/test-utils'
import ProjectCard from '@/components/ui/ProjectCard'

const mockProject = {
  id: '1',
  name: 'Test Project',
  description: 'A test project',
  framework: 'Next.js',
  status: 'active',
  created_at: '2023-01-01'
}

describe('ProjectCard', () => {
  it('renders project information correctly', () => {
    render(<ProjectCard project={mockProject} />)
    
    expect(screen.getByText('Test Project')).toBeInTheDocument()
    expect(screen.getByText('A test project')).toBeInTheDocument()
    expect(screen.getByText('Next.js')).toBeInTheDocument()
  })

  it('handles click events', () => {
    const mockOnClick = jest.fn()
    render(<ProjectCard project={mockProject} onClick={mockOnClick} />)
    
    fireEvent.click(screen.getByRole('button'))
    expect(mockOnClick).toHaveBeenCalledWith(mockProject.id)
  })
})

// Integration tests
// __tests__/pages/dashboard.test.tsx
import { render, screen, waitFor } from '@/utils/test-utils'
import DashboardPage from '@/pages/dashboard'
import { server } from '@/mocks/server'
import { rest } from 'msw'

describe('Dashboard Page', () => {
  it('displays projects after loading', async () => {
    server.use(
      rest.get('/api/projects', (req, res, ctx) => {
        return res(ctx.json([
          { id: '1', name: 'Project 1', description: 'Test' },
          { id: '2', name: 'Project 2', description: 'Test' }
        ]))
      })
    )

    render(<DashboardPage />)
    
    expect(screen.getByText('Loading...')).toBeInTheDocument()
    
    await waitFor(() => {
      expect(screen.getByText('Project 1')).toBeInTheDocument()
      expect(screen.getByText('Project 2')).toBeInTheDocument()
    })
  })
})
```

## 7. Performance Monitoring

### Advanced Analytics Integration
```typescript
// lib/analytics.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

interface AnalyticsEvent {
  name: string
  value: number
  id: string
  delta: number
  rating: 'good' | 'needs-improvement' | 'poor'
}

class Analytics {
  private queue: AnalyticsEvent[] = []
  private flushTimer: NodeJS.Timeout | null = null

  constructor() {
    this.initWebVitals()
  }

  private initWebVitals() {
    getCLS(this.handleVitalMetric.bind(this))
    getFID(this.handleVitalMetric.bind(this))
    getFCP(this.handleVitalMetric.bind(this))
    getLCP(this.handleVitalMetric.bind(this))
    getTTFB(this.handleVitalMetric.bind(this))
  }

  private handleVitalMetric(metric: AnalyticsEvent) {
    this.track('web-vital', {
      metric_name: metric.name,
      value: metric.value,
      rating: metric.rating
    })
  }

  track(event: string, properties?: Record<string, any>) {
    const eventData = {
      event,
      properties: {
        ...properties,
        timestamp: Date.now(),
        url: window.location.href,
        user_agent: navigator.userAgent
      }
    }

    this.queue.push(eventData)
    this.scheduleFlush()
  }

  private scheduleFlush() {
    if (this.flushTimer) return

    this.flushTimer = setTimeout(() => {
      this.flush()
      this.flushTimer = null
    }, 1000)
  }

  private async flush() {
    if (this.queue.length === 0) return

    const events = [...this.queue]
    this.queue = []

    try {
      await fetch('/api/analytics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ events })
      })
    } catch (error) {
      console.error('Failed to send analytics:', error)
      // Re-queue events for retry
      this.queue.unshift(...events)
    }
  }

  // Page view tracking
  pageView(path: string) {
    this.track('page_view', { path })
  }

  // User interactions
  click(element: string, properties?: Record<string, any>) {
    this.track('click', { element, ...properties })
  }

  // Custom events
  customEvent(name: string, properties?: Record<string, any>) {
    this.track(name, properties)
  }
}

export const analytics = new Analytics()

// Hook for component analytics
export const useAnalytics = () => {
  return {
    track: analytics.track.bind(analytics),
    pageView: analytics.pageView.bind(analytics),
    click: analytics.click.bind(analytics),
    customEvent: analytics.customEvent.bind(analytics)
  }
}

// Performance monitoring component
export const PerformanceMonitor = () => {
  useEffect(() => {
    // Monitor React render performance
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'measure' && entry.name.startsWith('⚛️')) {
          analytics.track('react-render', {
            component: entry.name,
            duration: entry.duration
          })
        }
      })
    })

    observer.observe({ entryTypes: ['measure'] })

    return () => observer.disconnect()
  }, [])

  return null
}
```

## Xulosa

Bu frontend kengaytmalari loyiha performansini sezilarli darajada yaxshilaydi:

### Asosiy Yaxshilashlar:
1. **Performance**: Bundle optimizatsiya, lazy loading, virtualization
2. **State Management**: Advanced React Query, Zustand integration
3. **Real-time**: WebSocket bilan live updates
4. **UI/UX**: Advanced komponentlar, better form handling
5. **Testing**: Comprehensive test setup
6. **Monitoring**: Performance va analytics tracking

### Implementatsiya Ketma-ketligi:
1. **Hafta 1-2**: Bundle optimizatsiya, lazy loading
2. **Hafta 3-4**: State management yaxshilash
3. **Hafta 5-6**: WebSocket integration
4. **Hafta 7-8**: Advanced UI komponentlar
5. **Hafta 9-10**: Testing va monitoring setup

### Kutilgan Natijalari:
- **Performance**: 40-60% tezroq sahifa yuklash
- **Bundle Size**: 30-50% kichikroq bundle
- **User Experience**: Real-time updates, better responsiveness
- **Code Quality**: 90%+ test coverage
- **Monitoring**: Real-time performance insights
