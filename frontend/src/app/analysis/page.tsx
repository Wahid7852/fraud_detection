'use client';

import React, { useEffect, useState } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell,
  LineChart, Line, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import { 
  Brain, 
  TrendingUp, 
  ShieldAlert, 
  Target,
  BarChart3
} from 'lucide-react';
import { analysisService } from '@/services/api';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

export default function AnalysisPage() {
  const [mlResults, setMlResults] = useState<any>(null);
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [resResults, resTrends] = await Promise.all([
          analysisService.getResults(),
          analysisService.getTrends()
        ]);
        setMlResults(resResults);
        setTrends(resTrends);
      } catch (error) {
        console.error("Error fetching analysis data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
      </div>
    );
  }

  // Extract model data from results
  const getModelData = () => {
    if (mlResults?.status === 'success' && mlResults.data) {
      const data = mlResults.data;
      const models = [];
      
      if (data.decision_tree) {
        models.push({
          name: 'Decision Tree',
          type: 'ML',
          accuracy: (data.decision_tree.accuracy || 0) * 100,
          f1_score: (data.decision_tree.f1_score || 0) * 100,
          precision: (data.decision_tree.precision || 0) * 100,
          recall: (data.decision_tree.recall || 0) * 100,
          auc_roc: (data.decision_tree.auc_roc || 0) * 100,
        });
      }
      
      if (data.naive_bayes) {
        models.push({
          name: 'Naive Bayes',
          type: 'ML',
          accuracy: (data.naive_bayes.accuracy || 0) * 100,
          f1_score: (data.naive_bayes.f1_score || 0) * 100,
          precision: (data.naive_bayes.precision || 0) * 100,
          recall: (data.naive_bayes.recall || 0) * 100,
          auc_roc: (data.naive_bayes.auc_roc || 0) * 100,
        });
      }
      
      if (data.knn) {
        models.push({
          name: 'KNN',
          type: 'ML',
          accuracy: (data.knn.accuracy || 0) * 100,
          f1_score: (data.knn.f1_score || 0) * 100,
          precision: (data.knn.precision || 0) * 100,
          recall: (data.knn.recall || 0) * 100,
          auc_roc: (data.knn.auc_roc || 0) * 100,
        });
      }
      
      if (data.ann) {
        models.push({
          name: 'ANN',
          type: 'DL',
          accuracy: (data.ann.accuracy || 0) * 100,
          f1_score: (data.ann.f1_score || 0) * 100,
          precision: (data.ann.precision || 0) * 100,
          recall: (data.ann.recall || 0) * 100,
          auc_roc: (data.ann.auc_roc || 0) * 100,
        });
      }
      
      return models;
    }
    
    // Fallback if no data
    return [];
  };

  const modelData = getModelData();
  const hasData = modelData.length > 0;

  // Prepare comparison data for different metrics
  const accuracyData = modelData.map(m => ({ name: m.name, value: m.accuracy, type: m.type }));
  const f1Data = modelData.map(m => ({ name: m.name, value: m.f1_score, type: m.type }));
  const precisionData = modelData.map(m => ({ name: m.name, value: m.precision, type: m.type }));
  const recallData = modelData.map(m => ({ name: m.name, value: m.recall, type: m.type }));
  const aucData = modelData.map(m => ({ name: m.name, value: m.auc_roc, type: m.type }));

  // Radar chart data - structure for Recharts (each model as a separate data point)
  const radarData = [
    { metric: 'Accuracy', ...Object.fromEntries(modelData.map(m => [m.name, m.accuracy])) },
    { metric: 'F1-Score', ...Object.fromEntries(modelData.map(m => [m.name, m.f1_score])) },
    { metric: 'Precision', ...Object.fromEntries(modelData.map(m => [m.name, m.precision])) },
    { metric: 'Recall', ...Object.fromEntries(modelData.map(m => [m.name, m.recall])) },
    { metric: 'AUC-ROC', ...Object.fromEntries(modelData.map(m => [m.name, m.auc_roc])) },
  ];

  const fraudByCategory = trends?.fraud_by_category?.map((rate: number, idx: number) => ({
    category: trends.categories[idx],
    rate: rate * 100
  })) || [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Machine Learning Analysis</h1>
        <p className="text-slate-500">IEEE-CIS Fraud Detection Dataset Insights</p>
      </div>

      {!hasData && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-6">
          <p className="text-amber-800">
            ⚠️ Models have not been trained yet. Please run <code className="bg-amber-100 px-2 py-1 rounded">python backend/app/train_models.py</code> to generate model results.
          </p>
        </div>
      )}

      {hasData && (
        <>
          {/* Model Performance Comparison - Multiple Metrics */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-slate-800">Accuracy Comparison</h2>
                <Target className="h-5 w-5 text-blue-500" />
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={accuracyData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                    <YAxis domain={[0, 100]} axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                    <Tooltip 
                      contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                      formatter={(value: number) => `${value.toFixed(2)}%`}
                    />
                    <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40}>
                      {accuracyData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.type === 'DL' ? '#8b5cf6' : COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-slate-800">F1-Score Comparison</h2>
                <TrendingUp className="h-5 w-5 text-emerald-500" />
              </div>
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={f1Data}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                    <YAxis domain={[0, 100]} axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                    <Tooltip 
                      contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                      formatter={(value: number) => `${value.toFixed(2)}%`}
                    />
                    <Bar dataKey="value" fill="#10b981" radius={[4, 4, 0, 0]} barSize={40}>
                      {f1Data.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.type === 'DL' ? '#8b5cf6' : COLORS[index % COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Multi-Metric Comparison */}
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-800">Comprehensive Model Comparison</h2>
              <BarChart3 className="h-5 w-5 text-purple-500" />
            </div>
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={modelData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                  <YAxis domain={[0, 100]} axisLine={false} tickLine={false} tick={{fill: '#64748b'}} />
                  <Tooltip 
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    formatter={(value: number) => `${value.toFixed(2)}%`}
                  />
                  <Legend />
                  <Bar dataKey="accuracy" fill="#3b82f6" name="Accuracy" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="f1_score" fill="#10b981" name="F1-Score" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="precision" fill="#f59e0b" name="Precision" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="recall" fill="#ef4444" name="Recall" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="auc_roc" fill="#8b5cf6" name="AUC-ROC" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Radar Chart for Multi-Dimensional Comparison */}
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-800">Multi-Dimensional Performance Radar</h2>
              <Brain className="h-5 w-5 text-purple-500" />
            </div>
            <div className="h-96 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="metric" tick={{fill: '#64748b', fontSize: 12}} />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{fill: '#64748b', fontSize: 10}} />
                  {modelData.map((m, idx) => (
                    <Radar 
                      key={m.name}
                      name={m.name} 
                      dataKey={m.name}
                      stroke={m.type === 'DL' ? '#8b5cf6' : COLORS[idx % COLORS.length]}
                      fill={m.type === 'DL' ? '#8b5cf6' : COLORS[idx % COLORS.length]}
                      fillOpacity={0.6} 
                    />
                  ))}
                  <Legend />
                  <Tooltip formatter={(value: number) => `${value.toFixed(2)}%`} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Model Rationale */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-slate-800">Model Rationale</h2>
                <Brain className="h-5 w-5 text-purple-500" />
              </div>
              <div className="space-y-4">
                <div className="rounded-lg bg-slate-50 p-3">
                  <h3 className="text-sm font-bold text-slate-700">Decision Tree (ML)</h3>
                  <p className="text-xs text-slate-500">Captures non-linear interactions; high interpretability via rule splitting.</p>
                </div>
                <div className="rounded-lg bg-slate-50 p-3">
                  <h3 className="text-sm font-bold text-slate-700">Naive Bayes (ML)</h3>
                  <p className="text-xs text-slate-500">Fast probabilistic benchmark assuming feature independence.</p>
                </div>
                <div className="rounded-lg bg-slate-50 p-3">
                  <h3 className="text-sm font-bold text-slate-700">KNN (ML)</h3>
                  <p className="text-xs text-slate-500">Distance-based detection with PCA dimensionality reduction.</p>
                </div>
                <div className="rounded-lg bg-purple-50 p-3">
                  <h3 className="text-sm font-bold text-purple-700">ANN (Deep Learning)</h3>
                  <p className="text-xs text-purple-500">Feed-forward neural network for complex feature representation.</p>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-slate-800">Feature Importance</h2>
                <TrendingUp className="h-5 w-5 text-emerald-500" />
              </div>
              <div className="space-y-4 pt-2">
                {trends?.top_features?.slice(0, 4).map((feature: any, idx: number) => (
                  <div key={feature.name || idx} className="group">
                    <div className="mb-1 flex justify-between text-sm">
                      <span className="font-medium text-slate-700">{feature.name}</span>
                      <span className="text-slate-500">{((feature.importance || 0) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-2 w-full rounded-full bg-slate-100">
                      <div 
                        className="h-2 rounded-full bg-emerald-500" 
                        style={{ width: `${(feature.importance || 0) * 100}%` }}
                      ></div>
                    </div>
                    {feature.reason && (
                      <p className="mt-1 text-[11px] text-slate-400 group-hover:text-slate-600 transition-colors">
                        {feature.reason}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Best Model Insights */}
          {trends?.logic_insights && trends.logic_insights.length > 0 && (
            <div className="space-y-4">
              {trends.logic_insights.map((insight: any, idx: number) => (
                <div key={idx} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                  <h3 className="mb-2 font-bold text-slate-800">{insight.title}</h3>
                  <p className="mb-3 text-sm text-slate-600">{insight.content}</p>
                  <div className="flex gap-4">
                    <div className="flex-1">
                      <span className="text-[10px] font-bold uppercase text-emerald-600">Pros</span>
                      <ul className="mt-1 space-y-1">
                        {insight.pros?.map((p: string, i: number) => (
                          <li key={i} className="text-xs text-slate-500 flex items-center">
                            <div className="mr-1.5 h-1 w-1 rounded-full bg-emerald-500" /> {p}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="flex-1">
                      <span className="text-[10px] font-bold uppercase text-rose-600">Cons</span>
                      <ul className="mt-1 space-y-1">
                        {insight.cons?.map((c: string, i: number) => (
                          <li key={i} className="text-xs text-slate-500 flex items-center">
                            <div className="mr-1.5 h-1 w-1 rounded-full bg-rose-500" /> {c}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
