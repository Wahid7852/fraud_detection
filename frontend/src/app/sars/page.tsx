'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FileText, Download, Search, Filter, Plus, MoreHorizontal, Clock, CheckCircle, AlertCircle, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { sarService } from '@/services/api';
import { caseService } from '@/services/api';

export default function SARsPage() {
  const queryClient = useQueryClient();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedCaseId, setSelectedCaseId] = useState('');
  const [sarAmount, setSarAmount] = useState('');
  const [sarDescription, setSarDescription] = useState('');

  const { data: sars, isLoading } = useQuery({
    queryKey: ['sars', statusFilter, searchQuery],
    queryFn: () => sarService.getSARs({ 
      status: statusFilter || undefined,
      search: searchQuery || undefined
    }),
  });

  const { data: stats } = useQuery({
    queryKey: ['sar-stats'],
    queryFn: sarService.getStats,
  });

  const { data: cases } = useQuery({
    queryKey: ['cases-for-sar'],
    queryFn: () => caseService.getCases({ status: 'Open' }),
  });

  const createSARMutation = useMutation({
    mutationFn: (data: any) => sarService.createSAR(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sars'] });
      queryClient.invalidateQueries({ queryKey: ['sar-stats'] });
      setShowCreateModal(false);
      setSelectedCaseId('');
      setSarAmount('');
      setSarDescription('');
      
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce';
      toast.innerText = '✅ SAR created successfully!';
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
    },
  });

  const fileSARMutation = useMutation({
    mutationFn: (sarId: string) => sarService.fileSAR(sarId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sars'] });
      queryClient.invalidateQueries({ queryKey: ['sar-stats'] });
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce';
      toast.innerText = '✅ SAR filed successfully!';
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
    },
  });

  const exportBatchMutation = useMutation({
    mutationFn: (params: any) => sarService.exportBatch(params),
    onSuccess: (data) => {
      if (data.csv) {
        const blob = new Blob([data.csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `sars_export_${new Date().toISOString().split('T')[0]}.csv`;
        link.click();
      } else if (data.data) {
        const blob = new Blob([JSON.stringify(data.data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `sars_export_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
      }
      
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-blue-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce';
      toast.innerText = '📥 SARs exported successfully!';
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
    },
  });

  const handleCreateSAR = () => {
    if (!selectedCaseId) {
      alert('Please select a case');
      return;
    }
    
    const selectedCase = cases?.find((c: any) => c.id === selectedCaseId);
    const transactionAmount = selectedCase?.alert?.transaction?.amount || 0;
    const amount = sarAmount ? parseFloat(sarAmount) : transactionAmount;
    
    if (amount <= 0) {
      alert('Please enter a valid amount or select a case with a transaction amount');
      return;
    }
    
    createSARMutation.mutate({
      case_id: selectedCaseId,
      amount: amount,
      description: sarDescription || 'Suspicious activity report'
    });
  };

  const handleExportBatch = () => {
    exportBatchMutation.mutate({ 
      status: statusFilter || undefined,
      format: 'csv'
    });
  };

  const filteredSARs = sars?.filter((sar: any) => 
    !searchQuery || 
    sar.sar_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    sar.case_id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    sar.customer_name?.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Suspicious Activity Reports (SAR)</h1>
          <p className="text-slate-500 text-sm">Regulatory filings for suspicious financial activity.</p>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={handleExportBatch}
            disabled={exportBatchMutation.isPending}
            className="flex items-center rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors disabled:opacity-50"
          >
            <Download className="mr-2 h-4 w-4" />
            {exportBatchMutation.isPending ? 'Exporting...' : 'Export Batch'}
          </button>
          <button 
            onClick={() => setShowCreateModal(true)}
            className="flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 shadow-sm transition-all"
          >
            <Plus className="mr-2 h-4 w-4" />
            New SAR Filing
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'Pending Filings', count: stats?.pending_filings || 0, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50' },
          { label: 'Successfully Filed', count: stats?.successfully_filed || 0, icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50' },
          { label: 'Drafts', count: stats?.drafts || 0, icon: AlertCircle, color: 'text-blue-600', bg: 'bg-blue-50' },
        ].map((stat) => (
          <div key={stat.label} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm flex items-center space-x-4">
            <div className={cn("p-3 rounded-lg", stat.bg)}>
              <stat.icon className={cn("h-6 w-6", stat.color)} />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-500">{stat.label}</p>
              <p className="text-2xl font-bold text-slate-900">{stat.count}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="border-b border-slate-100 bg-slate-50/50 p-4">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search filings, case IDs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-10 pr-4 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div className="relative">
              <button 
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                <Filter className="mr-2 h-4 w-4" />
                Status
                {statusFilter && (
                  <span className="ml-2 rounded-full bg-blue-600 text-white text-xs px-2 py-0.5">1</span>
                )}
              </button>
              {showFilters && (
                <div className="absolute right-0 mt-2 w-48 rounded-lg border border-slate-200 bg-white shadow-lg z-10 p-3">
                  <select
                    value={statusFilter || ''}
                    onChange={(e) => setStatusFilter(e.target.value || null)}
                    className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                  >
                    <option value="">All Statuses</option>
                    <option value="Draft">Draft</option>
                    <option value="Pending">Pending</option>
                    <option value="Filed">Filed</option>
                  </select>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 uppercase text-xs font-semibold">
              <tr>
                <th className="px-6 py-4">Filing ID</th>
                <th className="px-6 py-4">Case ID</th>
                <th className="px-6 py-4">Customer</th>
                <th className="px-6 py-4">Amount</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-10 text-center text-slate-500">
                    <div className="flex flex-col items-center justify-center space-y-2">
                      <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
                      <p>Loading SARs...</p>
                    </div>
                  </td>
                </tr>
              ) : filteredSARs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-10 text-center text-slate-500">
                    No SARs found.
                  </td>
                </tr>
              ) : (
                filteredSARs.map((sar: any) => (
                  <tr key={sar.id || sar.sar_id} className="hover:bg-slate-50 transition-colors group">
                    <td className="px-6 py-4 font-bold text-blue-600">{sar.sar_id}</td>
                    <td className="px-6 py-4 font-medium text-slate-600">{sar.case_id || 'N/A'}</td>
                    <td className="px-6 py-4 font-medium text-slate-900">{sar.customer_name || 'Unknown'}</td>
                    <td className="px-6 py-4 font-bold text-slate-900">${sar.amount?.toLocaleString() || '0.00'}</td>
                    <td className="px-6 py-4">
                      <span className={cn(
                        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-bold border",
                        sar.status === 'Filed' ? "bg-green-50 text-green-700 border-green-100" :
                        sar.status === 'Pending' ? "bg-amber-50 text-amber-700 border-amber-100" :
                        "bg-slate-50 text-slate-700 border-slate-100"
                      )}>
                        {sar.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-500 text-xs">
                      {sar.filing_date ? new Date(sar.filing_date).toLocaleDateString() : 
                       sar.created_at ? new Date(sar.created_at).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4">
                      {sar.status !== 'Filed' && (
                        <button
                          onClick={() => fileSARMutation.mutate(sar.sar_id || sar.id)}
                          disabled={fileSARMutation.isPending}
                          className="text-blue-600 hover:text-blue-800 text-xs font-medium disabled:opacity-50"
                        >
                          File
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create SAR Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-slate-900">Create New SAR</h2>
              <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-slate-700 mb-2 block">Case</label>
                <select
                  value={selectedCaseId}
                  onChange={(e) => setSelectedCaseId(e.target.value)}
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="">Select a case...</option>
                  {cases?.map((c: any) => (
                    <option key={c.id} value={c.id}>
                      CASE-{c.id} - {c.alert?.transaction?.amount ? `$${c.alert.transaction.amount.toFixed(2)}` : 'N/A'}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="text-sm font-medium text-slate-700 mb-2 block">Amount</label>
                <input
                  type="number"
                  value={sarAmount}
                  onChange={(e) => setSarAmount(e.target.value)}
                  placeholder={cases?.find((c: any) => c.id === selectedCaseId)?.alert?.transaction?.amount 
                    ? `Auto: $${cases.find((c: any) => c.id === selectedCaseId).alert.transaction.amount.toFixed(2)}`
                    : "Enter amount"}
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                {cases?.find((c: any) => c.id === selectedCaseId)?.alert?.transaction?.amount && (
                  <p className="mt-1 text-xs text-slate-500">
                    Transaction amount: ${cases.find((c: any) => c.id === selectedCaseId).alert.transaction.amount.toFixed(2)}
                  </p>
                )}
              </div>
              
              <div>
                <label className="text-sm font-medium text-slate-700 mb-2 block">Description</label>
                <textarea
                  value={sarDescription}
                  onChange={(e) => setSarDescription(e.target.value)}
                  placeholder="Enter description of suspicious activity"
                  rows={4}
                  className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex space-x-3 pt-4">
                <button
                  onClick={handleCreateSAR}
                  disabled={createSARMutation.isPending || !selectedCaseId}
                  className="flex-1 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {createSARMutation.isPending ? 'Creating...' : 'Create SAR'}
                </button>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
