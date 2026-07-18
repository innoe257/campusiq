'use client';

import { useState, useEffect } from 'react';
import { Search, Filter, ChevronDown, AlertTriangle, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface Student {
  id: number;
  student_id: string;
  first_name: string;
  last_name: string;
  email: string;
  program: string;
  major: string;
  gpa: number;
  risk_score: number | null;
  risk_category: string | null;
}

const RISK_BADGES: Record<string, string> = {
  critical: 'bg-red-100 text-red-700 border-red-200',
  high: 'bg-orange-100 text-orange-700 border-orange-200',
  medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  low: 'bg-green-100 text-green-700 border-green-200',
};

export default function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterProgram, setFilterProgram] = useState('');

  useEffect(() => {
    // Simulated data - in production, this would fetch from /api/v1/students
    const mockStudents: Student[] = [
      { id: 1, student_id: 'STU-2024-001', first_name: 'Sarah', last_name: 'Johnson', email: 'sarah.j@uni.edu', program: 'Computer Science', major: 'Software Engineering', gpa: 3.8, risk_score: 0.15, risk_category: 'low' },
      { id: 2, student_id: 'STU-2024-002', first_name: 'Michael', last_name: 'Chen', email: 'm.chen@uni.edu', program: 'Business', major: 'Finance', gpa: 2.1, risk_score: 0.72, risk_category: 'high' },
      { id: 3, student_id: 'STU-2024-003', first_name: 'Emma', last_name: 'Wilson', email: 'emma.w@uni.edu', program: 'Psychology', major: 'Clinical Psychology', gpa: 2.3, risk_score: 0.65, risk_category: 'high' },
      { id: 4, student_id: 'STU-2024-004', first_name: 'James', last_name: 'Brown', email: 'james.b@uni.edu', program: 'Computer Science', major: 'Data Science', gpa: 3.5, risk_score: 0.25, risk_category: 'low' },
      { id: 5, student_id: 'STU-2024-005', first_name: 'Olivia', last_name: 'Davis', email: 'olivia.d@uni.edu', program: 'Engineering', major: 'Mechanical', gpa: 3.2, risk_score: 0.35, risk_category: 'medium' },
      { id: 6, student_id: 'STU-2024-006', first_name: 'William', last_name: 'Miller', email: 'will.m@uni.edu', program: 'Business', major: 'Marketing', gpa: 1.8, risk_score: 0.89, risk_category: 'critical' },
      { id: 7, student_id: 'STU-2024-007', first_name: 'Sophia', last_name: 'Garcia', email: 'sophia.g@uni.edu', program: 'Computer Science', major: 'AI/ML', gpa: 3.9, risk_score: 0.10, risk_category: 'low' },
      { id: 8, student_id: 'STU-2024-008', first_name: 'Daniel', last_name: 'Martinez', email: 'dan.m@uni.edu', program: 'Nursing', major: 'RN Program', gpa: 2.8, risk_score: 0.42, risk_category: 'medium' },
    ];
    
    setTimeout(() => {
      setStudents(mockStudents);
      setLoading(false);
    }, 600);
  }, []);

  const filteredStudents = students.filter((s) => {
    const matchesSearch = 
      s.first_name.toLowerCase().includes(search.toLowerCase()) ||
      s.last_name.toLowerCase().includes(search.toLowerCase()) ||
      s.student_id.toLowerCase().includes(search.toLowerCase()) ||
      s.email.toLowerCase().includes(search.toLowerCase());
    const matchesProgram = !filterProgram || s.program === filterProgram;
    return matchesSearch && matchesProgram;
  });

  const programs = [...new Set(students.map((s) => s.program))];

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
          <h1 className="text-3xl font-bold text-slate-900">Student Directory</h1>
          <p className="text-slate-600">View all students, risk scores, and academic standing</p>
        </div>

        {/* Filters */}
        <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search by name, ID, or email..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <select
                value={filterProgram}
                onChange={(e) => setFilterProgram(e.target.value)}
                className="pl-10 pr-8 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
              >
                <option value="">All Programs</option>
                {programs.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            </div>
          </div>
        </div>

        {/* Student Table */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-sm font-semibold text-slate-600">Student ID</th>
                  <th className="px-4 py-3 text-sm font-semibold text-slate-600">Name</th>
                  <th className="px-4 py-3 text-sm font-semibold text-slate-600">Program</th>
                  <th className="px-4 py-3 text-sm font-semibold text-slate-600">GPA</th>
                  <th className="px-4 py-3 text-sm font-semibold text-slate-600">Risk Score</th>
                  <th className="px-4 py-3 text-sm font-semibold text-slate-600">Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredStudents.map((student) => (
                  <tr key={student.id} className="border-t hover:bg-slate-50">
                    <td className="px-4 py-3 text-sm font-mono text-slate-600">{student.student_id}</td>
                    <td className="px-4 py-3">
                      <div>
                        <p className="text-sm font-medium">{student.first_name} {student.last_name}</p>
                        <p className="text-xs text-slate-500">{student.email}</p>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <p>{student.program}</p>
                      <p className="text-xs text-slate-500">{student.major}</p>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1">
                        <span className="text-sm font-medium">{student.gpa.toFixed(1)}</span>
                        {student.gpa >= 3.5 ? (
                          <TrendingUp className="w-4 h-4 text-green-500" />
                        ) : student.gpa < 2.5 ? (
                          <TrendingDown className="w-4 h-4 text-red-500" />
                        ) : (
                          <Minus className="w-4 h-4 text-slate-400" />
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-slate-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              (student.risk_score || 0) > 0.7 ? 'bg-red-500' :
                              (student.risk_score || 0) > 0.4 ? 'bg-orange-500' :
                              (student.risk_score || 0) > 0.2 ? 'bg-yellow-500' : 'bg-green-500'
                            }`}
                            style={{ width: `${(student.risk_score || 0) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{((student.risk_score || 0) * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${
                        RISK_BADGES[student.risk_category || 'low']
                      }`}>
                        {student.risk_category === 'critical' && <AlertTriangle className="w-3 h-3" />}
                        {student.risk_category?.toUpperCase() || 'LOW'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {filteredStudents.length === 0 && (
            <div className="text-center py-12 text-slate-500">
              No students found matching your criteria.
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
