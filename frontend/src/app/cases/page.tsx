'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, Filter, ChevronDown, Download, MoreHorizontal, Briefcase, Clock, User, AlertTriangle, CheckCircle, FileText, Send, X, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { caseService } from '@/services/api';

export default function CasesPage() {
  const queryClient = useQueryClient();
  const [selectedCase, setSelectedCase] = useState<any>(null);
  const [newNote, setNewNote] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [analystFilter, setAnalystFilter] = useState<number | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  const exportCasesToCSV = () => {
    if (!filteredCases?.length) return;
    const headers = ['Case ID', 'Status', 'Alert ID', 'Risk Level', 'Amount', 'Analyst ID', 'Created At'];
    const rows = filteredCases.map((c: any) => [
      `CASE-${c.id}`,
      c.status,
      c.alert?.id ? `AL-${c.alert.id}` : 'N/A',
      c.alert?.risk_level || 'N/A',
      c.alert?.transaction?.amount || 0,
      c.analyst_id || 'Unassigned',
      c.created_at
    ]);
    const csvContent = [headers, ...rows].map(e => e.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `cases_export_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const { data: cases, isLoading } = useQuery({
    queryKey: ['cases', statusFilter, analystFilter, searchQuery],
    queryFn: () => caseService.getCases({ 
      status: statusFilter || undefined,
      analyst_id: analystFilter || undefined,
      search: searchQuery || undefined
    }),
  });

  const updateCaseStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => 
      caseService.updateCase(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      if (selectedCase) {
        queryClient.invalidateQueries({ queryKey: ['cases', selectedCase.id] });
      }
    },
  });

  const addNoteMutation = useMutation({
    mutationFn: (data: { case_id: string; note: string; analyst_id: number }) => 
      caseService.addNote(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      setNewNote('');
      if (selectedCase) {
        queryClient.invalidateQueries({ queryKey: ['cases', selectedCase.id] });
      }
    },
  });

  const assignAnalystMutation = useMutation({
    mutationFn: ({ caseId, analystId }: { caseId: string; analystId: number }) =>
      caseService.assignAnalyst(caseId, analystId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      if (selectedCase) {
        queryClient.invalidateQueries({ queryKey: ['cases', selectedCase.id] });
      }
    },
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Open': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'In Progress': return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'Closed': return 'bg-green-100 text-green-800 border-green-200';
      case 'SAR Filed': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  const filteredCases = cases; // Already filtered by API

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Case Management</h1>
          <p className="text-slate-500 text-sm">Investigate and resolve fraud cases.</p>
        </div>
        <div className="flex items-center space-x-3">
          <button 
            onClick={exportCasesToCSV}
            className="flex items-center rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
          >
            <Download className="mr-2 h-4 w-4" />
            Export Cases
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
                placeholder="Search cases, analysts, IDs..."
                className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-10 pr-4 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="relative">
              <button 
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                <Filter className="mr-2 h-4 w-4" />
                Filters
                {(statusFilter || analystFilter) && (
                  <span className="ml-2 rounded-full bg-blue-600 text-white text-xs px-2 py-0.5">
                    {(statusFilter ? 1 : 0) + (analystFilter ? 1 : 0)}
                  </span>
                )}
              </button>
              {showFilters && (
                <div className="absolute right-0 mt-2 w-64 rounded-lg border border-slate-200 bg-white shadow-lg z-10 p-4">
                  <div className="space-y-4">
                    <div>
                      <label className="text-xs font-bold text-slate-700 mb-2 block">Status</label>
                      <select
                        value={statusFilter || ''}
                        onChange={(e) => setStatusFilter(e.target.value || null)}
                        className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                      >
                        <option value="">All Statuses</option>
                        <option value="Open">Open</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Closed">Closed</option>
                        <option value="SAR Filed">SAR Filed</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-xs font-bold text-slate-700 mb-2 block">Analyst</label>
                      <select
                        value={analystFilter || ''}
                        onChange={(e) => setAnalystFilter(e.target.value ? parseInt(e.target.value) : null)}
                        className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                      >
                        <option value="">All Analysts</option>
                        <option value="1">Analyst 1</option>
                        <option value="2">Analyst 2</option>
                        <option value="3">Analyst 3</option>
                      </select>
                    </div>
                    <button
                      onClick={() => {
                        setStatusFilter(null);
                        setAnalystFilter(null);
                      }}
                      className="w-full text-xs text-slate-600 hover:text-slate-900"
                    >
                      Clear Filters
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 uppercase text-xs font-semibold">
              <tr>
                <th className="px-6 py-4">Case ID</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Alert ID</th>
                <th className="px-6 py-4">Risk Level</th>
                <th className="px-6 py-4">Amount</th>
                <th className="px-6 py-4">Analyst</th>
                <th className="px-6 py-4">Updated</th>
                <th className="px-6 py-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-10 text-center text-slate-500">
                    <div className="flex flex-col items-center justify-center space-y-2">
                      <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
                      <p>Loading cases...</p>
                    </div>
                  </td>
                </tr>
              ) : filteredCases?.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-10 text-center text-slate-500">
                    No cases found.
                  </td>
                </tr>
              ) : (
                filteredCases?.map((c: any) => (
                  <tr 
                    key={c.id} 
                    className="hover:bg-slate-50 transition-colors group cursor-pointer"
                    onClick={() => setSelectedCase(c)}
                  >
                    <td className="px-6 py-4 font-bold text-blue-600">CASE-{c.id}</td>
                    <td className="px-6 py-4">
                      <span className={cn(
                        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-bold border",
                        getStatusColor(c.status)
                      )}>
                        {c.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-600">AL-{c.alert_id}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className={cn(
                          "h-2 w-2 rounded-full mr-2",
                          c.alert.risk_score >= 90 ? "bg-red-500" : c.alert.risk_score >= 70 ? "bg-orange-500" : "bg-amber-500"
                        )} />
                        <span className="font-medium text-slate-700">{c.alert?.risk_level || 'N/A'}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 font-bold text-slate-900">${c.alert?.transaction?.amount?.toFixed(2) || '0.00'}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center text-slate-600">
                        <User className="mr-2 h-4 w-4 text-slate-400" />
                        {c.analyst_id ? `Analyst ${c.analyst_id}` : 'Unassigned'}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-500 text-xs">
                      {new Date(c.updated_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="text-slate-400 hover:text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity">
                        <MoreHorizontal className="h-5 w-5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Case Details Sidebar/Modal */}
      {selectedCase && (
        <div className="fixed inset-0 z-50 flex items-center justify-end bg-slate-900/40 backdrop-blur-sm">
          <div className="h-full w-full max-w-2xl bg-white shadow-2xl animate-in slide-in-from-right duration-300 flex flex-col">
            <div className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-100 bg-white/80 px-6 py-4 backdrop-blur-md">
              <div className="flex items-center space-x-3">
                <div className="rounded-lg bg-blue-600 p-2 text-white">
                  <Briefcase className="h-6 w-6" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-slate-900">Case CASE-{selectedCase.id}</h2>
                  <p className="text-xs text-slate-500">
                    {selectedCase.alert?.id ? `Alert AL-${selectedCase.alert.id}` : 'No Alert'} • 
                    {selectedCase.alert?.transaction?.transaction_id ? ` Transaction ${selectedCase.alert.transaction.transaction_id}` : ' No Transaction'}
                  </p>
                </div>
              </div>
              <button onClick={() => setSelectedCase(null)} className="rounded-lg p-2 text-slate-400 hover:bg-slate-100">
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-8">
              {/* Status Management */}
              <div className="rounded-2xl border border-slate-200 p-6 space-y-4">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Update Status</h3>
                <div className="flex flex-wrap gap-2">
                  {['Open', 'In Progress', 'Closed', 'SAR Filed'].map((status) => (
                    <button
                      key={status}
                      onClick={() => updateCaseStatusMutation.mutate({ id: String(selectedCase.id), status })}
                      disabled={updateCaseStatusMutation.isPending}
                      className={cn(
                        "px-4 py-2 rounded-lg text-sm font-bold transition-all border",
                        selectedCase.status === status 
                          ? "bg-slate-900 text-white border-slate-900" 
                          : "bg-white text-slate-600 border-slate-200 hover:border-slate-300 hover:bg-slate-50",
                        updateCaseStatusMutation.isPending && "opacity-50 cursor-not-allowed"
                      )}
                    >
                      {status}
                    </button>
                  ))}
                </div>
              </div>

              {/* Assign Analyst */}
              <div className="rounded-2xl border border-slate-200 p-6 space-y-4">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Assign Analyst</h3>
                <div className="flex items-center gap-3">
                  <select
                    value={selectedCase.analyst_id || ''}
                    onChange={(e) => {
                      const analystId = e.target.value ? parseInt(e.target.value) : null;
                      if (analystId) {
                        assignAnalystMutation.mutate({ caseId: String(selectedCase.id), analystId });
                      }
                    }}
                    disabled={assignAnalystMutation.isPending}
                    className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
                  >
                    <option value="">Unassigned</option>
                    <option value="1">Analyst 1</option>
                    <option value="2">Analyst 2</option>
                    <option value="3">Analyst 3</option>
                  </select>
                </div>
              </div>

              {/* Investigation Notes */}
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-slate-900 flex items-center">
                  <FileText className="mr-2 h-5 w-5 text-blue-600" />
                  Investigation Notes
                </h3>
                
                <div className="space-y-4">
                  {/* Notes List */}
                  <div className="space-y-4">
                    {selectedCase.notes?.map((note: any) => (
                      <div key={note.id} className="rounded-xl border border-slate-100 bg-slate-50/50 p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-bold text-slate-900">Analyst {note.analyst_id}</span>
                          <span className="text-[10px] text-slate-400">{new Date(note.created_at).toLocaleString()}</span>
                        </div>
                        <p className="text-sm text-slate-700 leading-relaxed">{note.note}</p>
                      </div>
                    ))}
                    {(!selectedCase.notes || selectedCase.notes.length === 0) && (
                      <div className="text-center py-6 text-slate-400 italic text-sm">
                        No notes yet. Start your investigation.
                      </div>
                    )}
                  </div>

                  {/* Add Note Form */}
                  <div className="relative">
                    <textarea
                      value={newNote || ''}
                      onChange={(e) => setNewNote(e.target.value)}
                      placeholder="Add an investigation note..."
                      className="w-full rounded-2xl border border-slate-200 p-4 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 pr-12 min-h-[100px]"
                    />
                    <button 
                      onClick={() => addNoteMutation.mutate({ case_id: String(selectedCase.id), note: newNote, analyst_id: 1 })}
                      disabled={!newNote.trim() || addNoteMutation.isPending}
                      className="absolute bottom-4 right-4 rounded-xl bg-blue-600 p-2 text-white hover:bg-blue-700 disabled:opacity-50 transition-all shadow-lg shadow-blue-200"
                    >
                      <Send className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Related Alert Info */}
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-slate-900 flex items-center">
                  <AlertTriangle className="mr-2 h-5 w-5 text-orange-600" />
                  Source Alert Details
                </h3>
                <div className="rounded-2xl border border-slate-100 p-4 space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-500">Risk Score</span>
                    <span className="text-sm font-bold text-red-600">{selectedCase.alert.risk_score} - {selectedCase.alert.risk_level}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-500">Transaction Amount</span>
                    <span className="text-sm font-bold text-slate-900">
                      ${selectedCase.alert?.transaction?.amount?.toFixed(2) || '0.00'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-500">Merchant Category</span>
                    <span className="text-sm font-bold text-slate-900">
                      {selectedCase.alert?.transaction?.category || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-slate-100 bg-slate-50/50">
              <button 
                onClick={() => setSelectedCase(null)}
                className="w-full rounded-xl bg-white border border-slate-200 py-3 text-sm font-bold text-slate-700 hover:bg-slate-50 transition-all"
              >
                Close Investigation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
