'use client';

import { useState } from 'react';
import { GraduationCap, Bot, BarChart3 } from 'lucide-react';

export default function HomePage() {
  const [demoClicked, setDemoClicked] = useState(false);

  const handleDemo = () => {
    setDemoClicked(true);
    // Scroll to features
    document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-slate-900 text-white py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold mb-6">CampusIQ</h1>
          <p className="text-xl text-slate-300 mb-8">
            AI-Powered Student Success Platform for Higher Education
          </p>
          <div className="flex justify-center gap-4 flex-wrap">
            <a href="/dashboard/" className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition-colors">
              View Dashboard
            </a>
            <a href="/advisor/" className="bg-slate-700 hover:bg-slate-600 px-6 py-3 rounded-lg font-semibold transition-colors">
              Try AI Advisor
            </a>
            <button onClick={handleDemo} className="bg-green-600 hover:bg-green-700 px-6 py-3 rounded-lg font-semibold transition-colors">
              {demoClicked ? 'Scroll down 👇' : 'Live Demo'}
            </button>
          </div>
          <p className="mt-6 text-sm text-slate-400">
            Deployed on Render • Open Source • MIT License
          </p>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-16 px-4 max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">Platform Capabilities</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard 
            icon={<Bot className="w-10 h-10 text-blue-600" />}
            title="Predictive Analytics"
            description="Machine learning models identify at-risk students early, enabling proactive intervention using XGBoost and MLflow."
          />
          <FeatureCard 
            icon={<GraduationCap className="w-10 h-10 text-green-600" />}
            title="AI Academic Advisor"
            description="RAG-powered chatbot answers course, policy, and career questions from official university documents using LangChain."
          />
          <FeatureCard 
            icon={<BarChart3 className="w-10 h-10 text-purple-600" />}
            title="Faculty Dashboard"
            description="Real-time cohort analytics, risk distribution, and intervention priority queue with interactive visualizations."
          />
        </div>
      </section>

      {/* Tech Stack */}
      <section className="bg-slate-50 py-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-8">Built With Modern Open Source</h2>
          <div className="flex flex-wrap justify-center gap-3">
            {['Python', 'FastAPI', 'PostgreSQL', 'pgvector', 'Next.js', 'LangChain', 'Ollama', 'XGBoost', 'MLflow', 'Airflow', 'Docker', 'Terraform'].map((tech) => (
              <span key={tech} className="bg-white border border-slate-200 px-4 py-2 rounded-full text-sm font-medium">
                {tech}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture Preview */}
      <section className="py-16 px-4 max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-8">Architecture Overview</h2>
        <div className="bg-slate-900 text-slate-300 p-6 rounded-xl font-mono text-sm overflow-x-auto">
          <pre>{`┌─────────────────────────────────────────────┐
│  Next.js Frontend  ←──→  FastAPI Backend   │
│  (Dashboard/Chat)       (Auth/ML/RAG)      │
└─────────────────────────────────────────────┘
            │                    │
            ▼                    ▼
    ┌──────────┐        ┌──────────────┐
    │PostgreSQL│        │   MLflow     │
    │+pgvector │        │ (Tracking)   │
    └──────────┘        └──────────────┘
`}</pre>
        </div>
        <p className="text-center mt-4 text-slate-600">
          See the full architecture in <a href="https://github.com/innoe257/campusiq/blob/main/docs/architecture.md" className="text-blue-600 underline">docs/architecture.md</a>
        </p>
      </section>

      {/* CTA */}
      <section className="bg-blue-600 text-white py-16 px-4 text-center">
        <h2 className="text-3xl font-bold mb-4">View the Code</h2>
        <p className="text-blue-100 mb-8 max-w-xl mx-auto">
          This is an open-source portfolio project demonstrating full-stack AI/ML engineering skills for the New Zealand tech market.
        </p>
        <a 
          href="https://github.com/innoe257/campusiq" 
          target="_blank" 
          rel="noopener noreferrer"
          className="bg-white text-blue-600 px-8 py-3 rounded-lg font-bold hover:bg-blue-50 transition-colors"
        >
          GitHub Repository →
        </a>
      </section>
    </main>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-md border border-slate-100">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-slate-600">{description}</p>
    </div>
  );
}
