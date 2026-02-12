'use client';

import { useQuery } from "@tanstack/react-query";
import { alertService } from "@/services/api";
import { KPICards } from "@/components/dashboard/KPICards";
import { FraudTrends } from "@/components/dashboard/FraudTrends";
import Link from "next/link";
import { cn } from "@/lib/utils";

export default function Home() {
  const { data: alerts, isLoading } = useQuery({
    queryKey: ['recent-alerts'],
    queryFn: () => alertService.getAlerts(),
    select: (data) => data.slice(0, 5).sort((a: any, b: any) => b.risk_score - a.risk_score)
  });

  const getRiskBadge = (score: number) => {
    if (score >= 90) return "bg-red-100 text-red-800 border-red-200";
    if (score >= 70) return "bg-orange-100 text-orange-800 border-orange-200";
    return "bg-yellow-100 text-yellow-800 border-yellow-200";
  };

  const { data: allAlerts } = useQuery({
    queryKey: ['all-alerts'],
    queryFn: () => alertService.getAlerts(),
  });

  const queues = [
    { name: 'High Profile Queue', count: allAlerts?.filter((a: any) => a.risk_score > 90).length || 0, color: 'bg-red-500' },
    { name: 'New Accounts', count: allAlerts?.filter((a: any) => a.transaction?.category === 'retail').length || 0, color: 'bg-blue-500' },
    { name: 'High Velocity', count: allAlerts?.filter((a: any) => a.risk_score > 70 && a.risk_score <= 90).length || 0, color: 'bg-amber-500' },
    { name: 'Merchant Anomalies', count: allAlerts?.filter((a: any) => a.transaction?.category === 'entertainment').length || 0, color: 'bg-indigo-500' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Fraud Dashboard</h1>
        <p className="text-slate-500 text-sm">Real-time fraud monitoring and analytics overview.</p>
      </div>

      <KPICards />
      <FraudTrends />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900">Recent High Risk Alerts</h3>
            <Link href="/alerts" className="text-sm text-blue-600 font-medium hover:underline">View all</Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-500 uppercase text-xs">
                <tr>
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Customer</th>
                  <th className="px-4 py-3">Amount</th>
                  <th className="px-4 py-3">Score</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {isLoading ? (
                  [1, 2, 3, 4, 5].map((i) => (
                    <tr key={i} className="animate-pulse">
                      <td colSpan={5} className="px-4 py-3"><div className="h-4 bg-slate-100 rounded w-full"></div></td>
                    </tr>
                  ))
                ) : alerts?.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-10 text-center text-slate-500 italic">No high risk alerts found.</td>
                  </tr>
                ) : alerts?.map((alert: any) => (
                  <tr key={alert.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-medium text-blue-600 underline decoration-blue-200 underline-offset-4">
                      <Link href="/alerts">AL-{alert.id}</Link>
                    </td>
                    <td className="px-4 py-3 font-medium text-slate-900">
                      {alert.transaction?.customer_id ? `CUST-${alert.transaction.customer_id}` : 'N/A'}
                    </td>
                    <td className="px-4 py-3 font-bold text-slate-700">
                      ${alert.transaction?.amount?.toFixed(2) || '0.00'}
                    </td>
                    <td className="px-4 py-3">
                      <span className={cn(
                        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-bold border",
                        getRiskBadge(alert.risk_score)
                      )}>
                        {alert.risk_score} - {alert.risk_level}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center rounded-full bg-amber-50 px-2 py-0.5 text-xs font-bold text-amber-700 border border-amber-100">
                        {alert.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Queue Distribution</h3>
          <div className="space-y-4">
            {queues.map((queue) => (
              <div key={queue.name} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className={cn("h-2 w-2 rounded-full mr-2", queue.color)} />
                  <span className="text-sm text-slate-600">{queue.name}</span>
                </div>
                <span className="text-sm font-semibold text-slate-900">{queue.count}</span>
              </div>
            ))}
          </div>
          <div className="mt-6 pt-6 border-t border-slate-100">
            <Link href="/alerts" className="block text-center text-sm font-bold text-blue-600 hover:text-blue-700 transition-colors">
              Manage All Queues
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
