import Link from 'next/link'
import { GraduationCap, Brain, BarChart3, Users } from 'lucide-react'

export default function HomePage() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-slate-900 text-white py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold mb-6">CampusIQ</h1>
          <p className="text-xl text-slate-300 mb-8">
            AI-Powered Student Success Platform for Higher Education
          </p>
          <div className="flex justify-center gap-4">
            <Link href="/dashboard" className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold">
              View Dashboard
            </Link>
            <Link href="/advisor" className="bg-slate-700 hover:bg-slate-600 px-6 py-3 rounded-lg font-semibold">
              Try AI Advisor
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4 max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">Platform Capabilities</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard 
            icon={<Brain className="w-10 h-10 text-blue-600" />}
            title="Predictive Analytics"
            description="Machine learning models identify at-risk students early, enabling proactive intervention."
          />
          <FeatureCard 
            icon={<GraduationCap className="w-10 h-10 text-green-600" />}
            title="AI Academic Advisor"
            description="RAG-powered chatbot answers course, policy, and career questions from official documents."
          />
          <FeatureCard 
            icon={<BarChart3 className="w-10 h-10 text-purple-600" />}
            title="Faculty Dashboard"
            description="Real-time cohort analytics, risk distribution, and intervention priority queue."
          />
        </div>
      </section>

      {/* Tech Stack */}
      <section className="bg-slate-50 py-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-8">Built With Modern Open Source</h2>
          <div className="flex flex-wrap justify-center gap-3">
            {['Python', 'FastAPI', 'PostgreSQL', 'pgvector', 'Next.js', 'LangChain', 'Ollama', 'XGBoost', 'MLflow', 'Airflow', 'Docker'].map((tech) => (
              <span key={tech} className="bg-white border border-slate-200 px-4 py-2 rounded-full text-sm font-medium">
                {tech}
              </span>
            ))}
          </div>
        </div>
      </section>
    </main>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-md border border-slate-100">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-slate-600">{description}</p>
    </div>
  )
}
