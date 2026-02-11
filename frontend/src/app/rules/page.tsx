'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Edit2, Trash2, Power, MoreVertical, Search, X, Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ruleService } from '@/services/api';

interface RuleFormData {
  name: string;
  description: string;
  score_impact: number;
  action: string;
  priority: number;
  is_active: boolean;
  conditions: any;
}

const INITIAL_FORM_DATA: RuleFormData = {
  name: '',
  description: '',
  score_impact: 10,
  action: 'Review',
  priority: 1,
  is_active: true,
  conditions: { field: 'amount', operator: '>', value: 1000 }
};

export default function RulesPage() {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<any>(null);
  const [formData, setFormData] = useState<RuleFormData>(INITIAL_FORM_DATA);

  const { data: rules, isLoading } = useQuery({
    queryKey: ['rules'],
    queryFn: ruleService.getRules,
  });

  const createMutation = useMutation({
    mutationFn: ruleService.createRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] });
      closeModal();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => ruleService.updateRule(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] });
      closeModal();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: ruleService.deleteRule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rules'] });
    },
  });

  const openCreateModal = () => {
    setEditingRule(null);
    setFormData(INITIAL_FORM_DATA);
    setIsModalOpen(true);
  };

  const openEditModal = (rule: any) => {
    setEditingRule(rule);
    setFormData({
      name: rule.name,
      description: rule.description,
      score_impact: rule.score_impact,
      action: rule.action,
      priority: rule.priority,
      is_active: rule.is_active,
      conditions: rule.conditions,
    });
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingRule(null);
    setFormData(INITIAL_FORM_DATA);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingRule) {
      updateMutation.mutate({ id: editingRule.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete this rule?')) {
      deleteMutation.mutate(id);
    }
  };

  const toggleStatus = (rule: any) => {
    updateMutation.mutate({ 
      id: rule.id, 
      data: { ...rule, is_active: !rule.is_active } 
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Rule Management</h1>
          <p className="text-slate-500 text-sm">Create and configure deterministic fraud rules.</p>
        </div>
        <button 
          onClick={openCreateModal}
          className="flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 shadow-sm transition-all"
        >
          <Plus className="mr-2 h-4 w-4" />
          Create Rule
        </button>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div className="relative w-96">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search rules..."
              className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-10 pr-4 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <div className="text-sm text-slate-500">
            Total active rules: <span className="font-semibold text-slate-900">{rules?.filter((r: any) => r.is_active).length || 0}</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 uppercase text-xs font-semibold">
              <tr>
                <th className="px-6 py-4">Priority</th>
                <th className="px-6 py-4">Rule Name</th>
                <th className="px-6 py-4">Score Impact</th>
                <th className="px-6 py-4">Action</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-10 text-center text-slate-500">
                    <div className="flex flex-col items-center justify-center space-y-2">
                      <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
                      <p>Loading rules...</p>
                    </div>
                  </td>
                </tr>
              ) : rules?.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-10 text-center text-slate-500">No rules found. Create one to get started.</td>
                </tr>
              ) : rules?.map((rule: any) => (
                <tr key={rule.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 font-medium text-slate-400">#{rule.priority}</td>
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-semibold text-slate-900">{rule.name}</p>
                      <p className="text-xs text-slate-500 mt-0.5">{rule.description}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-bold text-slate-700">+{rule.score_impact}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={cn(
                      "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
                      rule.action === 'Deny' ? "bg-red-50 text-red-700" : 
                      rule.action === 'Review' ? "bg-amber-50 text-amber-700" : 
                      "bg-blue-50 text-blue-700"
                    )}>
                      {rule.action}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <button 
                      onClick={() => toggleStatus(rule)}
                      className={cn(
                        "flex items-center rounded-full px-2 py-1 text-xs font-medium transition-colors",
                        rule.is_active ? "bg-green-100 text-green-800 hover:bg-green-200" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                      )}
                    >
                      <Power className="mr-1.5 h-3 w-3" />
                      {rule.is_active ? 'Active' : 'Inactive'}
                    </button>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end space-x-2">
                      <button 
                        onClick={() => openEditModal(rule)}
                        className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                      <button 
                        onClick={() => handleDelete(rule.id)}
                        className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create/Edit Rule Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-900/50 backdrop-blur-sm p-4">
          <div className="w-full max-w-2xl rounded-2xl bg-white shadow-2xl overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4 bg-slate-50/50">
              <div>
                <h2 className="text-xl font-bold text-slate-900">
                  {editingRule ? 'Edit Rule' : 'Create New Rule'}
                </h2>
                <p className="text-sm text-slate-500">
                  Configure logic for fraud detection.
                </p>
              </div>
              <button onClick={closeModal} className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="col-span-2 space-y-1.5">
                  <label className="text-sm font-semibold text-slate-700">Rule Name</label>
                  <input
                      required
                      type="text"
                      value={formData.name || ''}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full rounded-lg border border-slate-200 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                      placeholder="e.g., High Amount Transaction"
                    />
                </div>

                <div className="col-span-2 space-y-1.5">
                  <label className="text-sm font-semibold text-slate-700">Description</label>
                  <textarea
                    rows={2}
                    value={formData.description || ''}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full rounded-lg border border-slate-200 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    placeholder="Describe what this rule detects..."
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-sm font-semibold text-slate-700">Score Impact</label>
                  <div className="relative">
                    <input
                      required
                      type="number"
                      value={formData.score_impact ?? 0}
                      onChange={(e) => setFormData({ ...formData, score_impact: parseInt(e.target.value) || 0 })}
                      className="w-full rounded-lg border border-slate-200 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                      <Info className="h-4 w-4 text-slate-300" />
                    </div>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-sm font-semibold text-slate-700">Action</label>
                  <select
                    value={formData.action || 'Review'}
                    onChange={(e) => setFormData({ ...formData, action: e.target.value })}
                    className="w-full rounded-lg border border-slate-200 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value="Approve">Approve</option>
                    <option value="Review">Review</option>
                    <option value="Deny">Deny</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-sm font-semibold text-slate-700">Priority</label>
                  <input
                    required
                    type="number"
                    value={formData.priority ?? 0}
                    onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 0 })}
                    className="w-full rounded-lg border border-slate-200 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                </div>

                <div className="flex items-center space-x-3 pt-8">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label htmlFor="is_active" className="text-sm font-semibold text-slate-700">Active</label>
                </div>

                <div className="col-span-2 pt-4">
                  <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                    <h3 className="text-sm font-bold text-slate-900 mb-3">Conditions (JSON)</h3>
                    <textarea
                      rows={3}
                      value={JSON.stringify(formData.conditions, null, 2)}
                      onChange={(e) => {
                        try {
                          const parsed = JSON.parse(e.target.value);
                          setFormData({ ...formData, conditions: parsed });
                        } catch (err) {
                          // Allow typing invalid JSON temporarily
                        }
                      }}
                      className="w-full font-mono text-xs rounded-lg border border-slate-200 px-4 py-2 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
                    />
                  </div>
                </div>
              </div>

              <div className="mt-8 flex items-center justify-end space-x-3 border-t border-slate-100 pt-6">
                <button
                  type="button"
                  onClick={closeModal}
                  className="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending || updateMutation.isPending}
                  className="rounded-lg bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-700 shadow-sm transition-all disabled:opacity-50"
                >
                  {createMutation.isPending || updateMutation.isPending ? 'Saving...' : editingRule ? 'Update Rule' : 'Create Rule'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
