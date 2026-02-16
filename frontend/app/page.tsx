export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 text-white">
      <div className="max-w-5xl mx-auto px-4 py-20">
        <h1 className="text-5xl font-bold mb-6">
          Cloud IDE with AI Integration
        </h1>
        
        <p className="text-xl text-blue-100 mb-8">
          Zero installation friction. Instant provisioning. Isolated per-user environments.
        </p>

        <div className="space-x-4 mb-12">
          <a href="/signup" className="inline-block bg-white text-blue-600 px-8 py-3 rounded-lg font-bold hover:bg-blue-50">
            Get Started Free
          </a>
          <a href="/login" className="inline-block bg-blue-500 text-white px-8 py-3 rounded-lg font-bold hover:bg-blue-400">
            Sign In
          </a>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
          <div className="bg-blue-500 bg-opacity-50 p-6 rounded-lg backdrop-blur-sm">
            <h3 className="text-2xl font-bold mb-2">⚡ Instant Setup</h3>
            <p>Get a fully configured cloud environment in seconds. No setup required.</p>
          </div>

          <div className="bg-blue-500 bg-opacity-50 p-6 rounded-lg backdrop-blur-sm">
            <h3 className="text-2xl font-bold mb-2">🔒 Isolated</h3>
            <p>Each user gets their own isolated environment with full resource control.</p>
          </div>

          <div className="bg-blue-500 bg-opacity-50 p-6 rounded-lg backdrop-blur-sm">
            <h3 className="text-2xl font-bold mb-2">🤖 AI-Ready</h3>
            <p>Pre-configured with AI agents and tools for productive development.</p>
          </div>
        </div>
      </div>
    </main>
  );
}
