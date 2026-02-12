'use client';

import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { BarChart3, Download, Calendar, Filter, PieChart, TrendingUp, Users, ArrowUpRight, ArrowDownRight, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { reportService } from '@/services/api';

export default function ReportsPage() {
  const [isMounted, setIsMounted] = React.useState(false);
  const [dateRange, setDateRange] = useState('6months');
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);

  React.useEffect(() => {
    setIsMounted(true);
  }, []);

  const { data: templates } = useQuery({
    queryKey: ['report-templates'],
    queryFn: reportService.getTemplates,
  });

  const { data: stats } = useQuery({
    queryKey: ['report-stats'],
    queryFn: reportService.getStats,
  });

  const { data: trends } = useQuery({
    queryKey: ['report-trends', dateRange],
    queryFn: () => {
      const days = dateRange === '1month' ? 30 : dateRange === '3months' ? 90 : dateRange === '6months' ? 180 : 365;
      return reportService.getTrends({ days, group_by: 'day' });
    },
  });

  const generateReportMutation = useMutation({
    mutationFn: (data: any) => reportService.generateReport(data),
    onSuccess: (data) => {
      // Download report
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `fraud_report_${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      
      // Show success toast
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce';
      toast.innerText = `✅ Report generated successfully!`;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
    },
  });

  const handleGenerateReport = () => {
    const endDate = new Date();
    const startDate = new Date();
    if (dateRange === '1month') startDate.setMonth(startDate.getMonth() - 1);
    else if (dateRange === '3months') startDate.setMonth(startDate.getMonth() - 3);
    else if (dateRange === '6months') startDate.setMonth(startDate.getMonth() - 6);
    else startDate.setFullYear(startDate.getFullYear() - 1);

    generateReportMutation.mutate({
      start_date: startDate.toISOString(),
      end_date: endDate.toISOString(),
      report_type: 'summary'
    });
  };

  const handleTemplateClick = async (template: any) => {
    setSelectedTemplate(template.id);
    try {
      const data = await reportService.generateReport({
        start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        end_date: new Date().toISOString(),
        report_type: template.id
      });
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${template.id}_${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-blue-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce';
      toast.innerText = `📥 Downloading ${template.title}...`;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
    } catch (error) {
      console.error('Error generating template:', error);
    }
  };

  const handleAddWidget = () => {
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 right-4 bg-slate-800 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce';
    toast.innerText = `🛠️ Custom visualization builder - Coming soon!`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
  };

  const chartData = React.useMemo(() => {
    if (!trends || !Array.isArray(trends) || trends.length === 0) {
      return [];
    }
    return trends.map((t: any) => ({
      month: t.date ? new Date(t.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : t.date,
      fraud: t.fraud || 0,
      legit: t.legit || (t.total || 0) - (t.fraud || 0)
    }));
  }, [trends]);

  const reports = templates || [
    { id: 'monthly_summary', title: 'Monthly Fraud Summary', desc: 'Comprehensive overview of fraud trends and metrics for the current month.', icon: TrendingUp, color: 'text-blue-600', bg: 'bg-blue-50' },
    { id: 'analyst_performance', title: 'Analyst Performance', desc: 'Metrics on case resolution time and accuracy across the investigation team.', icon: Users, color: 'text-purple-600', bg: 'bg-purple-50' },
    { id: 'rule_effectiveness', title: 'Rule Effectiveness', desc: 'Analysis of false positive and true positive rates for all active detection rules.', icon: BarChart3, color: 'text-green-600', bg: 'bg-green-50' },
    { id: 'regional_risk', title: 'Regional Risk Heatmap', desc: 'Geographical distribution of fraud attempts and successful preventions.', icon: PieChart, color: 'text-orange-600', bg: 'bg-orange-50' },
  ];

  return (
    <div className="space-y-6 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Advanced Reports</h1>
          <p className="text-slate-500 text-sm">Deep dive analytics and regulatory reporting tools.</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="flex items-center rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors shadow-sm"
          >
            <option value="1month">Last Month</option>
            <option value="3months">Last 3 Months</option>
            <option value="6months">Last 6 Months</option>
            <option value="1year">Last Year</option>
          </select>
          <button 
            onClick={handleGenerateReport}
            disabled={generateReportMutation.isPending}
            className="flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 shadow-sm transition-all disabled:opacity-50"
          >
            <Download className="mr-2 h-4 w-4" />
            {generateReportMutation.isPending ? 'Generating...' : 'Generate Custom Report'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Avg Fraud Score', value: stats?.avg_fraud_score?.toFixed(1) || '42.5', trend: '+2.1%', up: true },
          { label: 'False Positive Rate', value: `${stats?.false_positive_rate?.toFixed(1) || '18.2'}%`, trend: '-4.5%', up: false },
          { label: 'Detection Rate', value: `${stats?.detection_rate?.toFixed(1) || '94.8'}%`, trend: '+1.2%', up: true },
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
            {isMounted && chartData && chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
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
            ) : trends === undefined ? (
              <div className="h-full w-full flex items-center justify-center bg-slate-50 rounded-xl">
                <p className="text-slate-400 text-sm">Loading chart data...</p>
              </div>
            ) : (
              <div className="h-full w-full flex items-center justify-center bg-slate-50 rounded-xl">
                <p className="text-slate-400 text-sm">No trend data available. Data ingestion may still be in progress.</p>
              </div>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 mb-6">Available Templates</h3>
          <div className="space-y-3">
            {reports.map((report: any, i: number) => {
              const Icon = report.icon || TrendingUp;
              return (
                <div 
                  key={report.id || i} 
                  onClick={() => handleTemplateClick(report)}
                  className="group flex items-center p-3 rounded-xl border border-slate-100 hover:border-blue-200 hover:bg-blue-50/50 transition-all cursor-pointer"
                >
                  <div className={cn("rounded-lg p-2 mr-3", report.bg || 'bg-blue-50')}>
                    <Icon className={cn("h-5 w-5", report.color || 'text-blue-600')} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-bold text-slate-900 truncate">{report.title}</p>
                    <p className="text-xs text-slate-500 truncate">{report.format?.join(', ') || 'CSV, PDF, XLSX'}</p>
                  </div>
                  <Download className="h-4 w-4 text-slate-400 group-hover:text-blue-600 transition-colors" />
                </div>
              );
            })}
          </div>
          <button 
            onClick={() => {
              const toast = document.createElement('div');
              toast.className = 'fixed bottom-4 right-4 bg-slate-900 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce';
              toast.innerText = `📂 Opening Template Gallery...`;
              document.body.appendChild(toast);
              setTimeout(() => toast.remove(), 3000);
            }}
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
