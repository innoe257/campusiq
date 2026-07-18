'use client';

import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { AlertTriangle, Users, TrendingUp, BookOpen } from 'lucide-react';
import { api, DashboardStats, Student } from '../../lib/api';

const RISK_COLORS: Record<string, string> = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#22c55e',
};

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [useMock, setUseMock] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        // Try to fetch from API
        const [statsData, studentsData] = await Promise.all([
          api.getDashboardStats(),
          api.getStudents(),
        ]);
        setStats(statsData);
        setStudents(studentsData);
        setError(null);
      } catch (err) {
        console.warn('API unavailable, using mock data:', err);
        setUseMock(true);
        // Fallback mock data
        setStats({
          total_students: 1247,
          active_students: 1189,
          risk_distribution: { low: 856, medium: 234, high: 112, critical: 45 },
          average_gpa: 3.2,
        });
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const riskData = stats ? Object.entries(stats.risk_distribution).map(([category, count]) => ({
    name: category.charAt(0).toUpperCase() + category.slice(1),
    value: count,
    color: RISK_COLORS[category] || '#94a3b8',
  })) : [];

  const gpaData = [
    { range: '< 2.0', count: 45 },
    { range: '2.0 - 2.5', count: 123 },
    { range: '2.5 - 3.0', count: 289 },
    { range: '3.0 - 3.5', count: 456 },
    { range: '3.5+', count: 334 },
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Faculty Dashboard</h1>
          <p className="text-slate-600">Student success analytics and intervention insights</p>
          {useMock && (
            <p className="text-xs text-amber-600 mt-1">Using demo data (API connection unavailable)</p>
          )}
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <StatCard 
            icon={<Users className="w-6 h-6 text-blue-600" />}
            title="Total Students"
            value={stats?.total_students.toLocaleString() || '0'}
            trend="+2.4%"
          />
          <StatCard 
            icon={<AlertTriangle className="w-6 h-6 text-red-600" />}
            title="At Risk"
            value={String((stats?.risk_distribution.high || 0) + (stats?.risk_distribution.critical || 0))}
            trend="-5.1%"
          />
          <StatCard 
            icon={<TrendingUp className="w-6 h-6 text-green-600" />}
            title="Avg GPA"
            value={stats?.average_gpa.toFixed(2) || '0'}
            trend="+0.1"
          />
          <StatCard 
            icon={<BookOpen className="w-6 h-6 text-purple-600" />}
            title="Active Programs"
            value="18"
            trend="+1"
          />
        </div>

        {/* Charts */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h2 className="text-lg font-bold mb-4">Risk Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={riskData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={5} dataKey="value">
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-4 mt-4 flex-wrap">
              {riskData.map((entry) => (
                <div key={entry.name} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color }}></div>
                  <span className="text-sm text-slate-600">{entry.name} ({entry.value})</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h2 className="text-lg font-bold mb-4">GPA Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={gpaData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="range" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Intervention Queue */}
        <div className="mt-8 bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <h2 className="text-lg font-bold mb-4">Priority Intervention Queue</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-sm font-semibold text-slate-600">Student</th>
                  <th className="px-4 py-3 text-sm font-semibold text-slate-600">Program</th>
                  <th className="px-4 py-3 text-sm font-semibold text-slate-600">Risk</th>
                  <th className="px-4 py-3 text-sm font-semibold text-slate-600">GPA</th>
                  <th className="px-4 py-3 text-sm font-semibold text-slate-600">Top Factor</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-t">
                  <td className="px-4 py-3">Sarah Johnson</td>
                  <td className="px-4 py-3">Computer Science</td>
                  <td className="px-4 py-3"><span className="bg-red-100 text-red-700 px-2 py-1 rounded text-xs font-medium">Critical</span></td>
                  <td className="px-4 py-3">1.8</td>
                  <td className="px-4 py-3 text-sm">Low GPA</td>
                </tr>
                <tr className="border-t">
                  <td className="px-4 py-3">Michael Chen</td>
                  <td className="px-4 py-3">Business</td>
                  <td className="px-4 py-3"><span className="bg-orange-100 text-orange-700 px-2 py-1 rounded text-xs font-medium">High</span></td>
                  <td className="px-4 py-3">2.1</td>
                  <td className="px-4 py-3 text-sm">Low Attendance</td>
                </tr>
                <tr className="border-t">
                  <td className="px-4 py-3">Emma Wilson</td>
                  <td className="px-4 py-3">Psychology</td>
                  <td className="px-4 py-3"><span className="bg-orange-100 text-orange-700 px-2 py-1 rounded text-xs font-medium">High</span></td>
                  <td className="px-4 py-3">2.3</td>
                  <td className="px-4 py-3 text-sm">Low Engagement</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  );
}

function StatCard({ icon, title, value, trend }: { icon: React.ReactNode, title: string, value: string, trend: string }) {
  const isPositive = trend.startsWith('+');
  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200">
      <div className="flex justify-between items-start mb-2">
        <div className="p-2 bg-slate-50 rounded-lg">{icon}</div>
        <span className={`text-xs font-medium px-2 py-1 rounded ${isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          {trend}
        </span>
      </div>
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-sm text-slate-600">{title}</p>
    </div>
  );
}
