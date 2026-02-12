'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { TrendingUp, DollarSign, Target, Search, CheckCircle, AlertCircle } from 'lucide-react';
import { dashboardService } from '@/services/api';

export const KPICards = () => {
  const { data: kpis, isLoading } = useQuery({
    queryKey: ['dashboard-kpis'],
    queryFn: dashboardService.getKPIs,
  });

  const kpiConfig = [
    { key: 'fraud_rate', name: 'Fraud Rate', unit: '%', icon: TrendingUp, color: 'text-red-600', bg: 'bg-red-100' },
    { key: 'fraud_sum', name: 'Fraud Sum', unit: '$', icon: DollarSign, color: 'text-blue-600', bg: 'bg-blue-100' },
    { key: 'detection_rate', name: 'Detection Rate', unit: '%', icon: Target, color: 'text-green-600', bg: 'bg-green-100' },
    { key: 'review_rate', name: 'Review Rate', unit: '%', icon: Search, color: 'text-amber-600', bg: 'bg-amber-100' },
    { key: 'approval_rate', name: 'Approval Rate', unit: '%', icon: CheckCircle, color: 'text-indigo-600', bg: 'bg-indigo-100' },
    { key: 'false_negative_rate', name: 'False Negative', unit: '%', icon: AlertCircle, color: 'text-orange-600', bg: 'bg-orange-100' },
  ];

  if (isLoading) {
    return <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="h-32 rounded-xl bg-white border border-slate-200 animate-pulse" />
      ))}
    </div>;
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      {kpiConfig.map((config) => {
        const val = kpis?.[config.key as keyof typeof kpis] || 0;
        let displayVal: string;
        
        if (config.unit === '$') {
          // Format currency with proper rounding
          const numVal = typeof val === 'number' ? val : parseFloat(String(val)) || 0;
          displayVal = `$${numVal.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        } else {
          // Format percentage with 2 decimal places, limit to 100%
          const numVal = typeof val === 'number' ? val : parseFloat(String(val)) || 0;
          const limitedVal = Math.min(Math.max(numVal, 0), 100);
          displayVal = `${limitedVal.toFixed(2)}${config.unit}`;
        }

        return (
          <div key={config.key} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div className={`rounded-lg ${config.bg} p-2`}>
                <config.icon className={`h-5 w-5 ${config.color}`} />
              </div>
            </div>
            <div className="mt-3">
              <p className="text-sm text-slate-500">{config.name}</p>
              <p className="text-2xl font-bold text-slate-900">{displayVal}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
};
