import React, { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { api } from '../api/client';
import { 
  Check, 
  X, 
  MessageSquare, 
  CreditCard, 
  Loader2,
  AlertTriangle,
  Play,
  Mail,
  Phone,
  Scale,
  ShieldAlert,
  ChevronRight,
  ClipboardList
} from 'lucide-react';

export default function CollectionsPage() {
  const { 
    selectedDatasetId, 
    activeDataset, 
    activeActions, 
    loadCollectionActions 
  } = useStore();

  const [generating, setGenerating] = useState(false);
  const [selectedAction, setSelectedAction] = useState(null); // action selected for modal interaction feedback
  const [paymentAmt, setPaymentAmt] = useState('');
  const [promiseToPay, setPromiseToPay] = useState(false);
  const [notes, setNotes] = useState('');
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const [approving, setApproving] = useState(null); // ID of action currently approving

  useEffect(() => {
    if (selectedDatasetId && activeDataset?.status === 'predicted' && activeActions.length === 0) {
      handleGenerateStrategy();
    }
  }, [selectedDatasetId]);

  const handleGenerateStrategy = async () => {
    if (!selectedDatasetId) return;
    setGenerating(true);
    try {
      await api.generateCollections(selectedDatasetId);
      await loadCollectionActions(selectedDatasetId);
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const handleApprove = async (id) => {
    setApproving(id);
    try {
      await api.approveAction(id, 'analyst_user');
      await loadCollectionActions(selectedDatasetId);
    } catch (err) {
      console.error(err);
    } finally {
      setApproving(null);
    }
  };

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    if (!selectedAction) return;
    setSubmittingFeedback(true);
    try {
      await api.submitFeedback(selectedAction.id, {
        paymentAmount: parseFloat(paymentAmt) || 0.0,
        promiseToPay: promiseToPay,
        notes: notes
      });
      await loadCollectionActions(selectedDatasetId);
      setSelectedAction(null);
      setPaymentAmt('');
      setPromiseToPay(false);
      setNotes('');
    } catch (err) {
      console.error(err);
    } finally {
      setSubmittingFeedback(false);
    }
  };

  if (!selectedDatasetId) {
    return (
      <div className="text-center py-12 glass-panel p-8 rounded-xl max-w-md mx-auto">
        <h2 className="text-lg font-bold text-white mb-2">No Dataset Active</h2>
        <p className="text-slate-400 text-xs">Choose or upload a dataset in Workspace configuration to view collections strategy.</p>
      </div>
    );
  }

  // Calculate allocation channels
  const getAllocations = () => {
    if (activeActions.length === 0) return {};
    return activeActions.reduce((acc, curr) => {
      acc[curr.recommended_action] = (acc[curr.recommended_action] || 0) + 1;
      return acc;
    }, {});
  };

  const allocs = getAllocations();
  const totalActions = activeActions.length;

  const getChannelIcon = (ch) => {
    switch(ch) {
      case 'email': return <Mail size={14} className="text-indigo-400" />;
      case 'sms': return <MessageSquare size={14} className="text-cyan-400" />;
      case 'phone_call': return <Phone size={14} className="text-amber-400" />;
      case 'payment_plan': return <CreditCard size={14} className="text-emerald-400" />;
      case 'escalation': return <Scale size={14} className="text-red-400" />;
      default: return <ShieldAlert size={14} className="text-violet-400" />;
    }
  };

  return (
    <div className="space-y-8 animate-slide-up">
      {/* Title */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">AI Collections Strategy</h1>
          <p className="text-slate-400 text-sm mt-1">
            Automated recommendations across collections channels and Agentic AI dynamic feedback triggers.
          </p>
        </div>
        {activeDataset?.status === 'predicted' && (
          <button
            onClick={handleGenerateStrategy}
            disabled={generating}
            className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-4 py-2.5 rounded-lg text-xs font-bold transition shadow-neon"
          >
            {generating ? (
              <>
                <Loader2 className="animate-spin" size={14} />
                <span>Generating Actions...</span>
              </>
            ) : (
              <>
                <Play size={14} fill="currentColor" />
                <span>Re-run Collections Plan</span>
              </>
            )}
          </button>
        )}
      </div>

      {totalActions === 0 ? (
        <div className="text-center py-16 glass-panel p-8 rounded-xl max-w-lg mx-auto space-y-6">
          <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto text-indigo-400 border border-slate-700">
            <ClipboardList size={28} />
          </div>
          <div className="space-y-2">
            <h2 className="text-xl font-bold text-white">Generate Collections Strategy</h2>
            <p className="text-slate-400 text-xs max-w-sm mx-auto">
              You must train the prediction models before generating collections actions. If models are trained, click the button below to allocate outreach channels.
            </p>
          </div>
          <button
            onClick={handleGenerateStrategy}
            disabled={generating || activeDataset?.status !== 'predicted'}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold px-8 py-3 rounded-lg transition"
          >
            Generate Allocation Strategies
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Allocation Statistics Sidebar */}
          <div className="space-y-6 lg:col-span-1">
            <div className="glass-panel p-5 rounded-xl space-y-4">
              <h3 className="text-xs uppercase font-extrabold text-slate-400 tracking-wider">Channel Allocation</h3>
              <div className="space-y-3.5 text-xs">
                {Object.entries(allocs).map(([ch, count]) => {
                  const pct = ((count / totalActions) * 100).toFixed(1);
                  return (
                    <div key={ch} className="space-y-1">
                      <div className="flex justify-between items-center text-slate-300">
                        <div className="flex items-center space-x-1.5 capitalize font-medium">
                          {getChannelIcon(ch)}
                          <span>{ch.replace('_', ' ')}</span>
                        </div>
                        <span className="font-bold">{count} ({pct}%)</span>
                      </div>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div 
                          className="bg-indigo-500 h-full transition-all duration-500" 
                          style={{ width: `${pct}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Actions Queue Table */}
          <div className="glass-panel p-6 rounded-xl lg:col-span-3 space-y-6 overflow-hidden">
            <div>
              <h2 className="text-base font-bold text-white">Interventions Queue</h2>
              <p className="text-xs text-slate-400 mt-0.5">Approve critical actions, record payments, and trigger feedback updates.</p>
            </div>

            <div className="overflow-x-auto border border-slate-800 rounded-lg">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="bg-slate-850 text-slate-400 font-bold border-b border-slate-800">
                    <th className="p-3">Customer ID</th>
                    <th className="p-3">Risk Level</th>
                    <th className="p-3">Action Route</th>
                    <th className="p-3">Status</th>
                    <th className="p-3 text-right">Queue Operations</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {activeActions.map((a) => {
                    const isPendingApproval = a.requires_approval && a.status === 'pending';
                    const riskColors = {
                      critical: 'text-red-400 bg-red-500/10 border border-red-500/20',
                      high: 'text-orange-400 bg-orange-500/10 border border-orange-500/20',
                      medium: 'text-yellow-400 bg-yellow-500/10 border border-yellow-500/20',
                      low: 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20',
                    };

                    return (
                      <tr key={a.id} className="hover:bg-slate-800/20">
                        <td className="p-3 font-semibold text-white">{a.customer_id}</td>
                        <td className="p-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider ${
                            riskColors[a.risk_level] || 'text-slate-400 bg-slate-800'
                          }`}>
                            {a.risk_level}
                          </span>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center space-x-1.5 capitalize text-white">
                            {getChannelIcon(a.recommended_action)}
                            <span>{a.recommended_action.replace('_', ' ')}</span>
                          </div>
                        </td>
                        <td className="p-3">
                          <span className={`capitalize font-semibold text-[10px] ${
                            a.status === 'completed' ? 'text-emerald-400' : a.status === 'approved' ? 'text-indigo-400' : 'text-slate-400'
                          }`}>
                            {a.status}
                          </span>
                        </td>
                        <td className="p-3 text-right space-x-2">
                          {isPendingApproval ? (
                            <button
                              onClick={() => handleApprove(a.id)}
                              disabled={approving === a.id}
                              className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-3 py-1 rounded text-[10px] transition inline-flex items-center space-x-1"
                            >
                              {approving === a.id ? (
                                <Loader2 className="animate-spin" size={10} />
                              ) : (
                                <Check size={10} />
                              )}
                              <span>Approve</span>
                            </button>
                          ) : (
                            <button
                              onClick={() => setSelectedAction(a)}
                              className="bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 font-bold px-3 py-1 rounded text-[10px] transition inline-flex items-center space-x-1"
                            >
                              <ChevronRight size={10} />
                              <span>Log Activity</span>
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Dynamic Interaction Agentic Feedback Modal */}
      {selectedAction && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="glass-panel max-w-md w-full rounded-xl p-6 space-y-6 border border-slate-800">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-base font-bold text-white">Log Account Interaction</h3>
                <span className="text-[10px] text-indigo-400 block font-semibold">Customer: {selectedAction.customer_id}</span>
              </div>
              <button 
                onClick={() => setSelectedAction(null)}
                className="text-slate-500 hover:text-slate-200"
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleFeedbackSubmit} className="space-y-4 text-xs">
              <div className="space-y-1.5">
                <label className="text-slate-400 font-medium block">Direct Payment Received ($)</label>
                <input 
                  type="number" 
                  step="any"
                  value={paymentAmt}
                  onChange={(e) => setPaymentAmt(e.target.value)}
                  placeholder="0.00"
                  className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex items-center space-x-2 py-1">
                <input 
                  type="checkbox" 
                  id="promise"
                  checked={promiseToPay}
                  onChange={(e) => setPromiseToPay(e.target.checked)}
                  className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                />
                <label htmlFor="promise" className="text-slate-300 font-medium select-none cursor-pointer">
                  Customer made verbal agreement (Promise to pay)
                </label>
              </div>

              <div className="space-y-1.5">
                <label className="text-slate-400 font-medium block">Interaction notes & summary</label>
                <textarea
                  rows="3"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Record client responses, hardship claims, or workout details..."
                  className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-white outline-none focus:border-indigo-500 resize-none"
                ></textarea>
              </div>

              <div className="bg-indigo-500/10 p-3 rounded-lg border border-indigo-500/20 text-[10px] text-indigo-400 flex items-start space-x-2">
                <AlertTriangle size={14} className="shrink-0" />
                <span>
                  Agentic AI Loop: Submitting this log immediately recalibrates model risk values, computes updated severity thresholds, and changes recommended treatments.
                </span>
              </div>

              <button
                type="submit"
                disabled={submittingFeedback}
                className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold py-2.5 rounded-lg transition flex items-center justify-center space-x-2"
              >
                {submittingFeedback ? (
                  <>
                    <Loader2 className="animate-spin" size={14} />
                    <span>Recalculating Strategy...</span>
                  </>
                ) : (
                  <span>Submit Log & Re-score</span>
                )}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
