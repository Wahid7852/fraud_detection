'use client';

import React, { useState } from 'react';
import { Save, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function SettingsPage() {
  const [scoringType, setScoringType] = useState('hybrid');
  const [thresholds, setThresholds] = useState({
    veryHigh: { min: 91, max: 99, color: 'bg-red-500' },
    high: { min: 71, max: 90, color: 'bg-orange-500' },
    medium: { min: 51, max: 70, color: 'bg-yellow-500' },
    low: { min: 11, max: 50, color: 'bg-green-500' },
    veryLow: { min: 1, max: 10, color: 'bg-emerald-600' },
  });

  const updateThreshold = (key: string, field: 'min' | 'max', val: string) => {
    const num = parseInt(val) || 0;
    setThresholds(prev => ({
      ...prev,
      [key]: { ...prev[key as keyof typeof thresholds], [field]: num }
    }));
  };

  const handleSave = () => {
    alert(`Configuration saved successfully!\nEngine Mode: ${scoringType}\nThresholds: Updated`);
  };

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Score Settings</h1>
        <p className="text-slate-500 text-sm">Configure fraud scoring logic and risk thresholds.</p>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-8">
        <section className="space-y-4">
          <div className="flex items-center space-x-2">
            <h3 className="text-lg font-semibold text-slate-900">Scoring Engine Mode</h3>
            <Info className="h-4 w-4 text-slate-400" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { id: 'rules', name: 'Rule Based Only', desc: 'Deterministic results based on set rules.' },
              { id: 'model', name: 'Model Based Only', desc: 'Probability scores from ML models.' },
              { id: 'hybrid', name: 'Hybrid (Recommended)', desc: 'Weighted average of rules and ML.' },
            ].map((mode) => (
              <button
                key={mode.id}
                onClick={() => setScoringType(mode.id)}
                className={cn(
                  "flex flex-col items-start p-4 rounded-xl border text-left transition-all",
                  scoringType === mode.id 
                    ? "border-blue-600 bg-blue-50 ring-2 ring-blue-600/10" 
                    : "border-slate-200 hover:border-slate-300 bg-white"
                )}
              >
                <div className="flex items-center justify-between w-full mb-2">
                  <span className={cn(
                    "font-semibold text-sm",
                    scoringType === mode.id ? "text-blue-700" : "text-slate-900"
                  )}>{mode.name}</span>
                  <div className={cn(
                    "h-4 w-4 rounded-full border flex items-center justify-center",
                    scoringType === mode.id ? "border-blue-600" : "border-slate-300"
                  )}>
                    {scoringType === mode.id && <div className="h-2 w-2 rounded-full bg-blue-600" />}
                  </div>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">{mode.desc}</p>
              </button>
            ))}
          </div>
        </section>

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-semibold text-slate-900">Risk Group Thresholds</h3>
              <Info className="h-4 w-4 text-slate-400" />
            </div>
            <button className="text-sm text-blue-600 font-medium hover:underline">Reset to defaults</button>
          </div>
          
          <div className="space-y-3">
            <div className="grid grid-cols-12 gap-4 px-4 py-2 text-xs font-semibold text-slate-500 uppercase">
              <div className="col-span-5">Risk Range</div>
              <div className="col-span-4">Risk Group</div>
              <div className="col-span-3">Indicator</div>
            </div>
            {Object.entries(thresholds).map(([key, value]) => (
              <div key={key} className="grid grid-cols-12 gap-4 items-center p-4 rounded-lg border border-slate-100 bg-slate-50/50 hover:bg-slate-50 transition-colors">
                <div className="col-span-5 flex items-center space-x-3">
                  <input 
                    type="number" 
                    value={value.min} 
                    onChange={(e) => updateThreshold(key, 'min', e.target.value)}
                    className="w-16 rounded border border-slate-200 py-1 px-2 text-sm text-center focus:border-blue-500 focus:outline-none"
                  />
                  <span className="text-slate-400 text-sm">to</span>
                  <input 
                    type="number" 
                    value={value.max} 
                    onChange={(e) => updateThreshold(key, 'max', e.target.value)}
                    className="w-16 rounded border border-slate-200 py-1 px-2 text-sm text-center focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <div className="col-span-4 font-medium text-slate-700 text-sm capitalize">
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </div>
                <div className="col-span-3">
                  <div className={cn("h-4 w-1 rounded-full", value.color)} />
                </div>
              </div>
            ))}
          </div>
        </section>

        <div className="pt-6 border-t border-slate-100 flex justify-end">
          <button 
            onClick={handleSave}
            className="flex items-center rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 shadow-sm shadow-blue-200 transition-all active:scale-95"
          >
            <Save className="mr-2 h-4 w-4" />
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
}
