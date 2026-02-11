'use client';

import React from 'react';
import { FileText, Download, Search, Filter, Plus, MoreHorizontal, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

const mockSARs = [
  { id: 'SAR-2026-001', caseId: 'CASE-1', customer: 'Alice Johnson', amount: 5420.50, status: 'Filed', date: '2026-02-01' },
  { id: 'SAR-2026-002', caseId: 'CASE-4', customer: 'Bob Smith', amount: 12400.00, status: 'Pending', date: '2026-02-05' },
  { id: 'SAR-2026-003', caseId: 'CASE-7', customer: 'Charlie Davis', amount: 8900.25, status: 'Draft', date: '2026-02-09' },
];

export default function SARsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Suspicious Activity Reports (SAR)</h1>
          <p className="text-slate-500 text-sm">Regulatory filings for suspicious financial activity.</p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors">
            <Download className="mr-2 h-4 w-4" />
            Export Batch
          </button>
          <button className="flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 shadow-sm transition-all">
            <Plus className="mr-2 h-4 w-4" />
            New SAR Filing
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: 'Pending Filings', count: 12, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50' },
          { label: 'Successfully Filed', count: 145, icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50' },
          { label: 'Drafts', count: 5, icon: AlertCircle, color: 'text-blue-600', bg: 'bg-blue-50' },
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
                className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-10 pr-4 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <button className="flex items-center rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
              <Filter className="mr-2 h-4 w-4" />
              Status
            </button>
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
                <th className="px-6 py-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {mockSARs.map((sar) => (
                <tr key={sar.id} className="hover:bg-slate-50 transition-colors group cursor-pointer">
                  <td className="px-6 py-4 font-bold text-blue-600">{sar.id}</td>
                  <td className="px-6 py-4 font-medium text-slate-600">{sar.caseId}</td>
                  <td className="px-6 py-4 font-medium text-slate-900">{sar.customer}</td>
                  <td className="px-6 py-4 font-bold text-slate-900">${sar.amount.toLocaleString()}</td>
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
                  <td className="px-6 py-4 text-slate-500 text-xs">{sar.date}</td>
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
    </div>
  );
}
