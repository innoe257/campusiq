'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, BookOpen } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: { document_id: string; similarity: number }[];
}

export default function AdvisorPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I am CampusIQ, your AI academic advisor. I can help you with questions about courses, programs, academic policies, and career pathways. What would you like to know?',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulated API call - in production, this would call /api/v1/chat/message
    setTimeout(() => {
      const responses: Record<string, string> = {
        'course': 'I can help you find courses! Based on our catalog, popular options include CS101 (Intro to Programming), MATH201 (Calculus II), and PSYCH101 (Introduction to Psychology). Would you like details on any specific course?',
        'prerequisite': 'Prerequisites vary by course. For example, CS201 requires CS101, and MATH301 requires MATH201. You can check the full course catalog for detailed prerequisite chains.',
        'career': 'Our Career Services office offers resume reviews, mock interviews, and job placement assistance. Many Computer Science graduates find roles in software engineering, data science, and AI/ML engineering.',
        'gpa': 'Your GPA is calculated by dividing total grade points by total credits attempted. Most programs require a minimum 2.0 GPA for good standing. If you need help improving your GPA, consider academic coaching or tutoring services.',
        'financial aid': 'Financial aid options include scholarships, grants, work-study programs, and student loans. The Financial Aid office is located in Building C, Room 205. Deadlines for next semester are typically March 1st.',
      };

      const lowerInput = input.toLowerCase();
      let response = 'I apologize, but I need more information to help with that. Could you rephrase your question or ask about specific courses, programs, policies, or career services?';
      
      for (const [keyword, resp] of Object.entries(responses)) {
        if (lowerInput.includes(keyword)) {
          response = resp;
          break;
        }
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: response,
        sources: [{ document_id: 'course_catalog', similarity: 0.92 }],
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 flex flex-col">
      <div className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <Bot className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-xl font-bold">AI Academic Advisor</h1>
            <p className="text-sm text-slate-600">Powered by RAG + Local LLM (Ollama)</p>
          </div>
        </div>
      </div>

      <div className="flex-1 max-w-4xl w-full mx-auto p-6 overflow-y-auto">
        <div className="space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-blue-600" />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-slate-200 text-slate-800'
                }`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-slate-100">
                    <div className="flex items-center gap-1 text-xs text-slate-500">
                      <BookOpen className="w-3 h-3" />
                      <span>Sources: {message.sources.map((s) => s.document_id).join(', ')}</span>
                    </div>
                  </div>
                )}
              </div>
              {message.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-slate-600" />
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                <Bot className="w-5 h-5 text-blue-600" />
              </div>
              <div className="bg-white border border-slate-200 rounded-2xl px-4 py-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="bg-white border-t border-slate-200 px-6 py-4">
        <div className="max-w-4xl mx-auto flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Ask about courses, programs, policies, or career advice..."
            className="flex-1 resize-none rounded-lg border border-slate-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={2}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">Send</span>
          </button>
        </div>
        <p className="max-w-4xl mx-auto mt-2 text-xs text-slate-500">
          This advisor uses Retrieval-Augmented Generation (RAG) to answer from official university documents. For complex cases, consult your faculty advisor.
        </p>
      </div>
    </main>
  );
}
