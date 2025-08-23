import React from 'react'
import Dashboard from './components/Dashboard'
import ErrorBoundary from './components/ErrorBoundary'

function App() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <Dashboard />
      </div>
    </ErrorBoundary>
  )
}

export default App
