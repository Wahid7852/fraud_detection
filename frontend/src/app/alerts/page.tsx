'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, Filter, ChevronDown, Download, MoreHorizontal, X, ExternalLink, ShieldAlert, Clock, User, DollarSign, Tag, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { alertService, caseService } from '@/services/api';

export default function AlertsPage() {
  const queryClient = useQueryClient();
  const [selectedQueue, setSelectedQueue] = useState('All Queues');
  const [selectedAlert, setSelectedAlert] = useState<any>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  const exportToCSV = () => {
    if (!filteredAlerts?.length) return;
    const headers = ['Alert ID', 'Risk Score', 'Risk Level', 'Customer ID', 'Amount', 'Status', 'Queue', 'Timestamp'];
    const rows = filteredAlerts.map((a: any) => [
      `AL-${a.id}`,
      a.risk_score,
      a.risk_level,
      a.transaction.customer_id,
      a.transaction.amount,
      a.status,
      a.assigned_queue,
      a.created_at
    ]);
    const csvContent = [headers, ...rows].map(e => e.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `fraud_alerts_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const assignAlerts = () => {
    if (selectedIds.length === 0) {
      alert('Please select at least one alert to assign.');
      return;
    }
    alert(`Assigned ${selectedIds.length} alerts to your queue.`);
    setSelectedIds([]);
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === filteredAlerts?.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filteredAlerts?.map((a: any) => a.id) || []);
    }
  };

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alertService.getAlerts(),
  });

  const createCaseMutation = useMutation({
    mutationFn: (alertId: string) => caseService.createCase({ alert_id: alertId, status: 'Open' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      setSelectedAlert(null);
      alert('Case created successfully');
    },
  });

  const dismissAlertMutation = useMutation({
    mutationFn: (alertId: string) => alertService.updateAlert(alertId, { status: 'Dismissed' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      setSelectedAlert(null);
    },
  });

  const filteredAlerts = alerts?.filter((alert: any) => {
    const matchesQueue = selectedQueue === 'All Queues' || alert.assigned_queue === selectedQueue;
    const matchesSearch = searchQuery === '' || 
      `AL-${alert.id}`.toLowerCase().includes(searchQuery.toLowerCase()) ||
      `Customer ${alert.transaction.customer_id}`.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesQueue && matchesSearch;
  });

  const getRiskColor = (score: number) => {
    if (score >= 90) return 'text-red-700 bg-red-50 border-red-100';
    if (score >= 70) return 'text-orange-700 bg-orange-50 border-orange-100';
    return 'text-amber-700 bg-amber-50 border-amber-100';
  };

  const getRiskBadge = (score: number) => {
    if (score >= 90) return 'bg-red-500';
    if (score >= 70) return 'bg-orange-500';
    return 'bg-amber-500';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Fraud Alerts</h1>
          <p className="text-slate-500 text-sm">Review and manage triggered fraud alerts.</p>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={exportToCSV}
            className="flex items-center rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
          >
            <Download className="mr-2 h-4 w-4" />
            Export CSV
          </button>
          <button 
            onClick={assignAlerts}
            className="flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 shadow-sm transition-all"
          >
            Assign Alerts
          </button>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="border-b border-slate-100 bg-slate-50/50 p-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="relative flex-1 min-w-[300px]">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search alerts, customers, IDs..."
                className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-10 pr-4 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-slate-600">Queue:</label>
              <div className="relative">
                <select 
                  className="appearance-none rounded-lg border border-slate-200 bg-white py-2 pl-3 pr-10 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  value={selectedQueue}
                  onChange={(e) => setSelectedQueue(e.target.value)}
                >
                  <option>All Queues</option>
                  <option>General</option>
                  <option>Fraud Queue</option>
                  <option>High Profile Queue</option>
                  <option>New Accounts</option>
                  <option>High Velocity</option>
                </select>
                <ChevronDown className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 pointer-events-none" />
              </div>
            </div>
            <button 
              onClick={() => alert('Filter options: Date Range, Risk Range, Amount Range')}
              className="flex items-center rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
            >
              <Filter className="mr-2 h-4 w-4" />
              Filters
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 uppercase text-xs font-semibold">
              <tr>
                <th className="px-6 py-4">
                  <input 
                    type="checkbox" 
                    className="rounded border-slate-300 text-blue-600 focus:ring-blue-500" 
                    checked={filteredAlerts?.length > 0 && selectedIds.length === filteredAlerts?.length}
                    onChange={toggleSelectAll}
                  />
                </th>
                <th className="px-6 py-4">Alert ID</th>
                <th className="px-6 py-4">Risk Score</th>
                <th className="px-6 py-4">Customer</th>
                <th className="px-6 py-4">Amount</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Assigned Queue</th>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td colSpan={9} className="px-6 py-10 text-center text-slate-500">
                    <div className="flex flex-col items-center justify-center space-y-2">
                      <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
                      <p>Loading alerts...</p>
                    </div>
                  </td>
                </tr>
              ) : filteredAlerts?.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-6 py-10 text-center text-slate-500">No alerts found in this queue.</td>
                </tr>
              ) : filteredAlerts?.map((alert: any) => (
                <tr key={alert.id} className="hover:bg-slate-50 transition-colors group cursor-pointer" onClick={() => setSelectedAlert(alert)}>
                  <td className="px-6 py-4" onClick={(e) => e.stopPropagation()}>
                    <input 
                      type="checkbox" 
                      className="rounded border-slate-300 text-blue-600 focus:ring-blue-500" 
                      checked={selectedIds.includes(alert.id)}
                      onChange={() => toggleSelect(alert.id)}
                    />
                  </td>
                  <td className="px-6 py-4 font-medium text-blue-600 hover:underline">
                    AL-{alert.id}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <div className={cn("h-2 w-2 rounded-full mr-2", getRiskBadge(alert.risk_score))} />
                      <span className={cn("font-semibold", getRiskColor(alert.risk_score).split(' ')[0])}>
                        {alert.risk_score} - {alert.risk_level}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-slate-900">Customer {alert.transaction.customer_id}</td>
                  <td className="px-6 py-4 font-medium text-slate-900">${alert.transaction.amount.toFixed(2)}</td>
                  <td className="px-6 py-4">
                    <span className={cn(
                      "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
                      alert.status === 'Pending' ? "bg-amber-100 text-amber-800" : 
                      alert.status === 'Reviewed' ? "bg-blue-100 text-blue-800" : 
                      "bg-slate-100 text-slate-800"
                    )}>
                      {alert.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-600">{alert.assigned_queue}</td>
                  <td className="px-6 py-4 text-slate-500">{new Date(alert.created_at).toLocaleString()}</td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-slate-400 hover:text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity">
                      <MoreHorizontal className="h-5 w-5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Alert Details Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-slate-900/40 backdrop-blur-sm">
          <div className="h-full w-full max-w-2xl bg-white shadow-2xl animate-in slide-in-from-right duration-300 overflow-y-auto">
            <div className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-100 bg-white/80 px-6 py-4 backdrop-blur-md">
              <div className="flex items-center space-x-3">
                <div className={cn("rounded-lg p-2", getRiskColor(selectedAlert.risk_score))}>
                  <ShieldAlert className="h-6 w-6" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-slate-900">Alert AL-{selectedAlert.id}</h2>
                  <div className="flex items-center text-xs text-slate-500 space-x-2">
                    <span className="flex items-center"><Clock className="mr-1 h-3 w-3" /> {new Date(selectedAlert.created_at).toLocaleString()}</span>
                    <span>•</span>
                    <span className="font-medium text-slate-700">{selectedAlert.assigned_queue}</span>
                  </div>
                </div>
              </div>
              <button onClick={() => setSelectedAlert(null)} className="rounded-lg p-2 text-slate-400 hover:bg-slate-100">
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="p-6 space-y-8">
              {/* Score Card */}
              <div className={cn("rounded-2xl border p-6 flex items-center justify-between", getRiskColor(selectedAlert.risk_score))}>
                <div className="space-y-1">
                  <p className="text-sm font-medium opacity-80">Fraud Probability Score</p>
                  <div className="flex items-baseline space-x-2">
                    <span className="text-4xl font-black">{selectedAlert.risk_score}</span>
                    <span className="text-lg font-bold opacity-80">/ 100</span>
                  </div>
                  <p className="text-sm font-bold uppercase tracking-wider">{selectedAlert.risk_level} RISK</p>
                </div>
                <div className="h-20 w-20 rounded-full border-4 border-current border-t-transparent animate-spin-slow flex items-center justify-center">
                  <span className="text-xl font-bold">ML</span>
                </div>
              </div>

              {/* Transaction Details */}
              <div className="space-y-4">
                <h3 className="flex items-center text-lg font-bold text-slate-900">
                  <FileText className="mr-2 h-5 w-5 text-blue-600" />
                  Transaction Information
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { label: 'Transaction ID', value: selectedAlert.transaction.transaction_id, icon: Tag },
                    { label: 'Amount', value: `$${selectedAlert.transaction.amount.toFixed(2)}`, icon: DollarSign },
                    { label: 'Customer ID', value: selectedAlert.transaction.customer_id, icon: User },
                    { label: 'Category', value: selectedAlert.transaction.category, icon: FileText },
                    { label: 'Type', value: selectedAlert.transaction.transaction_type, icon: Clock },
                    { label: 'Merchant ID', value: selectedAlert.transaction.merchant_id, icon: Tag },
                  ].map((item, i) => (
                    <div key={i} className="rounded-xl border border-slate-100 bg-slate-50/50 p-3">
                      <p className="text-xs font-medium text-slate-500 flex items-center mb-1">
                        <item.icon className="mr-1 h-3 w-3" />
                        {item.label}
                      </p>
                      <p className="text-sm font-bold text-slate-900">{item.value}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Section */}
              <div className="rounded-2xl border border-blue-100 bg-blue-50/50 p-6 space-y-4">
                <h3 className="text-lg font-bold text-slate-900 flex items-center">
                  <CheckCircle className="mr-2 h-5 w-5 text-blue-600" />
                  Resolution Actions
                </h3>
                <p className="text-sm text-slate-600">
                  Based on the high risk score, we recommend opening a full investigation case or dismissing if it's a known pattern.
                </p>
                <div className="flex space-x-3">
                  <button 
                    onClick={() => createCaseMutation.mutate(selectedAlert.id)}
                    disabled={createCaseMutation.isPending}
                    className="flex-1 rounded-xl bg-blue-600 py-3 text-sm font-bold text-white hover:bg-blue-700 shadow-lg shadow-blue-200 transition-all disabled:opacity-50"
                  >
                    {createCaseMutation.isPending ? 'Processing...' : 'Create Investigation Case'}
                  </button>
                  <button 
                    onClick={() => dismissAlertMutation.mutate(selectedAlert.id)}
                    disabled={dismissAlertMutation.isPending}
                    className="flex-1 rounded-xl bg-white border border-slate-200 py-3 text-sm font-bold text-slate-700 hover:bg-slate-50 transition-all disabled:opacity-50"
                  >
                    Dismiss Alert
                  </button>
                </div>
              </div>

              {/* Evidence Section (Mockup) */}
              <div className="space-y-4 pb-10">
                <h3 className="flex items-center text-lg font-bold text-slate-900">
                  <AlertCircle className="mr-2 h-5 w-5 text-orange-600" />
                  Fraud Indicators
                </h3>
                <div className="space-y-3">
                  <div className="rounded-xl border border-red-100 bg-red-50/30 p-4">
                    <p className="text-sm font-bold text-red-900 mb-1">High Velocity Pattern Detected</p>
                    <p className="text-xs text-red-700">This customer has made 5 transactions in the last 10 minutes, exceeding the normal threshold.</p>
                  </div>
                  <div className="rounded-xl border border-amber-100 bg-amber-50/30 p-4">
                    <p className="text-sm font-bold text-amber-900 mb-1">Unusual Location</p>
                    <p className="text-xs text-amber-700">Transaction originated from a high-risk jurisdiction not previously associated with this customer.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
