'use client';

import React from 'react';
import { BarChart3, Download, Calendar, Filter, PieChart, TrendingUp, Users, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

const mockData = [
  { month: 'Jan', fraud: 45, legit: 1200 },
  { month: 'Feb', fraud: 52, legit: 1100 },
  { month: 'Mar', fraud: 38, legit: 1350 },
  { month: 'Apr', fraud: 65, legit: 1400 },
  { month: 'May', fraud: 48, legit: 1250 },
  { month: 'Jun', fraud: 55, legit: 1500 },
];

export default function ReportsPage() {
  const [isMounted, setIsMounted] = React.useState(false);

  React.useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleGenerateReport = () => {
    alert('Generating custom report based on current filters...');
  };

  const handleTemplateClick = (title: string) => {
    alert(`Downloading template: ${title}`);
  };

  const handleAddWidget = () => {
    alert('Opening visualization builder...');
  };

  const reports = [
    { title: 'Monthly Fraud Summary', desc: 'Comprehensive overview of fraud trends and metrics for the current month.', icon: TrendingUp, color: 'text-blue-600', bg: 'bg-blue-50' },
    { title: 'Analyst Performance', desc: 'Metrics on case resolution time and accuracy across the investigation team.', icon: Users, color: 'text-purple-600', bg: 'bg-purple-50' },
    { title: 'Rule Effectiveness', desc: 'Analysis of false positive and true positive rates for all active detection rules.', icon: BarChart3, color: 'text-green-600', bg: 'bg-green-50' },
    { title: 'Regional Risk Heatmap', desc: 'Geographical distribution of fraud attempts and successful preventions.', icon: PieChart, color: 'text-orange-600', bg: 'bg-orange-50' },
  ];

  return (
    <div className="space-y-6 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Advanced Reports</h1>
          <p className="text-slate-500 text-sm">Deep dive analytics and regulatory reporting tools.</p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors shadow-sm">
            <Calendar className="mr-2 h-4 w-4" />
            Last 6 Months
          </button>
          <button 
            onClick={handleGenerateReport}
            className="flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 shadow-sm transition-all"
          >
            <Download className="mr-2 h-4 w-4" />
            Generate Custom Report
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Avg Fraud Score', value: '42.5', trend: '+2.1%', up: true },
          { label: 'False Positive Rate', value: '18.2%', trend: '-4.5%', up: false },
          { label: 'Detection Rate', value: '94.8%', trend: '+1.2%', up: true },
          { label: 'Avg Resolution Time', value: '4.2h', trend: '-12m', up: false },
        ].map((stat) => (
          <div key={stat.label} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">{stat.label}</p>
            <div className="mt-2 flex items-baseline justify-between">
              <p className="text-2xl font-bold text-slate-900">{stat.value}</p>
              <span className={cn(
                "flex items-center text-xs font-bold",
                stat.up ? "text-red-600" : "text-green-600"
              )}>
                {stat.up ? <ArrowUpRight className="h-3 w-3 mr-0.5" /> : <ArrowDownRight className="h-3 w-3 mr-0.5" />}
                {stat.trend}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 mb-6">Fraud vs Legit Volume Trend</h3>
          <div className="h-[300px]">
            {isMounted ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={mockData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} />
                  <Tooltip 
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                  />
                  <Line type="monotone" dataKey="legit" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: '#3b82f6', strokeWidth: 2, stroke: '#fff' }} />
                  <Line type="monotone" dataKey="fraud" stroke="#ef4444" strokeWidth={3} dot={{ r: 4, fill: '#ef4444', strokeWidth: 2, stroke: '#fff' }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full w-full flex items-center justify-center bg-slate-50 rounded-xl">
                <p className="text-slate-400 text-sm">Loading chart data...</p>
              </div>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 mb-6">Available Templates</h3>
          <div className="space-y-3">
            {reports.map((report, i) => (
              <div 
                key={i} 
                onClick={() => handleTemplateClick(report.title)}
                className="group flex items-center p-3 rounded-xl border border-slate-100 hover:border-blue-200 hover:bg-blue-50/50 transition-all cursor-pointer"
              >
                <div className={cn("rounded-lg p-2 mr-3", report.bg)}>
                  <report.icon className={cn("h-5 w-5", report.color)} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-bold text-slate-900 truncate">{report.title}</p>
                  <p className="text-xs text-slate-500 truncate">CSV, PDF, XLSX</p>
                </div>
                <Download className="h-4 w-4 text-slate-400 group-hover:text-blue-600 transition-colors" />
              </div>
            ))}
          </div>
          <button 
            onClick={() => alert('Redirecting to templates gallery...')}
            className="w-full mt-6 py-2.5 rounded-xl bg-slate-900 text-white text-sm font-bold hover:bg-slate-800 transition-all"
          >
            Browse All Templates
          </button>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center bg-gradient-to-b from-white to-slate-50/50">
        <div className="mx-auto w-16 h-16 rounded-full bg-blue-50 flex items-center justify-center mb-4">
          <BarChart3 className="h-8 w-8 text-blue-500" />
        </div>
        <h3 className="text-xl font-bold text-slate-900">Custom Analytics Builder</h3>
        <p className="text-slate-500 max-w-lg mx-auto mt-2">
          Drag and drop fields to create custom visualizations. Export data in PDF, XLSX, or JSON formats for external analysis.
        </p>
        <button 
          onClick={handleAddWidget}
          className="mt-6 rounded-xl border-2 border-dashed border-slate-300 px-8 py-3 text-sm font-bold text-slate-400 hover:border-blue-400 hover:text-blue-500 transition-all group"
        >
          <Plus className="inline-block mr-2 h-4 w-4 group-hover:scale-110 transition-transform" />
          Add New Visualization Widget
        </button>
      </div>
    </div>
  );
}

function Plus({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
    </svg>
  );
}
