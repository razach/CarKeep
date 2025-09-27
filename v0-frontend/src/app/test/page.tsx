export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">CarKeep Frontend Test</h1>
        <p className="text-gray-600">Next.js is working correctly!</p>
        <div className="mt-8 p-4 bg-white rounded-lg shadow">
          <p className="text-sm text-gray-500">Environment: {process.env.NODE_ENV}</p>
          <p className="text-sm text-gray-500">API URL: {process.env.NEXT_PUBLIC_API_URL || 'not set'}</p>
        </div>
      </div>
    </div>
  )
}