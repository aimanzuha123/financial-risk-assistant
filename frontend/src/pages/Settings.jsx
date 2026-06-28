import React, { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { api } from '../api/client';
import { 
  ShieldCheck, 
  RefreshCw, 
  AlertTriangle, 
  HelpCircle,
  FileCheck,
  Activity,
  UserCheck,
  Sliders,
  Scale
} from 'lucide-react';

export default function SettingsPage() {
  const { selectedDatasetId, activeDataset } = useStore();
  
  // Bias Check form inputs
  const [sensitiveColumns, setSensitiveColumns] = useState([]);
  const [selectedCol, setSelectedCol] = useState('');
  const [privilegedGroup, setPrivilegedGroup] = useState('');
  const [unprivilegedGroup, setUnprivilegedGroup] = useState('');
  const [checkingBias, setCheckingBias] = useState(false);
  const [biasResult, setBiasResult] = useState(null);
  const [biasError, setBiasError] = useState(null);

  // Audit Logs inputs
  const [auditLogs, setAuditLogs] = useState([]);
  const [loadingLogs, setLoadingLogs] = useState(false);

  const loadSensitiveColumns = async () => {
    if (!selectedDatasetId) return;
    try {
      const data = await api.getSensitiveAttributes(selectedDatasetId);
      setSensitiveColumns(data);
      if (data.length > 0) {
        setSelectedCol(data[0].column);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const loadAuditLogs = async () => {
    setLoadingLogs(true);
    try {
      const logs = await api.getAuditLogs(selectedDatasetId);
      setAuditLogs(logs);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingLogs(false);
    }
  };

  // Run initial loading on select dataset change
  useEffect(() => {
    if (selectedDatasetId) {
      loadSensitiveColumns();
      loadAuditLogs();
      setBiasResult(null);
      setBiasError(null);
    }
  }, [selectedDatasetId]);

  const handleBiasCheck = async (e) => {
    e.preventDefault();
    if (!selectedDatasetId || !selectedCol || !privilegedGroup || !unprivilegedGroup) return;
    setCheckingBias(true);
    setBiasResult(null);
    setBiasError(null);

    try {
      const res = await api.checkBias(selectedDatasetId, {
        sensitiveColumn: selectedCol,
        privilegedGroup,
        unprivilegedGroup
      });
      if (res.error) {
        setBiasError(res.error);
      } else {
        setBiasResult(res);
        loadAuditLogs(); // Refresh logs to show the check
      }
    } catch (err) {
      setBiasError(err.response?.data?.detail || 'Failed to complete bias assessment. Ensure models are trained first.');
    } finally {
      setCheckingBias(false);
    }
  };

  return (
    <div className="space-y-8 animate-slide-up">
      {/* Title */}
      <div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Settings & Compliance Auditing</h1>
        <p className="text-slate-400 text-sm mt-1">
          Responsible AI bias checkers, data safety policies, and system-wide immutable audit trail logs.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Bias Assessment Column */}
        <div className="glass-panel p-6 rounded-xl space-y-6 lg:col-span-1 h-fit">
          <div>
            <h2 className="text-sm font-bold text-white flex items-center space-x-2">
              <Scale size={16} className="text-indigo-400" />
              <span>Bias & Fairness Assessment</span>
            </h2>
            <p className="text-[11px] text-slate-400 mt-0.5">Quantify disparities across protected groups.</p>
          </div>

          {!selectedDatasetId ? (
            <div className="text-slate-500 text-xs italic">Select a dataset to enable fairness evaluation.</div>
          ) : (
            <form onSubmit={handleBiasCheck} className="space-y-4 text-xs">
              <div className="space-y-1.5">
                <label className="text-slate-400 font-medium block">Sensitive Attribute Column</label>
                <select
                  value={selectedCol}
                  onChange={(e) => setSelectedCol(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-slate-200 outline-none focus:border-indigo-500"
                >
                  <option value="">-- Choose Column --</option>
                  {sensitiveColumns.map((c) => (
                    <option key={c.column} value={c.column}>{c.column}</option>
                  ))}
                  {/* Fallback all columns if none detected */}
                  {sensitiveColumns.length === 0 && activeDataset?.numerical_columns?.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-slate-400 font-medium block">Privileged Value</label>
                <input 
                  type="text"
                  value={privilegedGroup}
                  onChange={(e) => setPrivilegedGroup(e.target.value)}
                  placeholder="e.g. 1, Male, Young"
                  className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-slate-400 font-medium block">Unprivileged Value</label>
                <input 
                  type="text"
                  value={unprivilegedGroup}
                  onChange={(e) => setUnprivilegedGroup(e.target.value)}
                  placeholder="e.g. 0, Female, Senior"
                  className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-white outline-none focus:border-indigo-500"
                />
              </div>

              <button
                type="submit"
                disabled={checkingBias || !selectedCol || !privilegedGroup || !unprivilegedGroup}
                className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold py-2.5 rounded-lg transition flex items-center justify-center space-x-2"
              >
                {checkingBias ? (
                  <>
                    <RefreshCw className="animate-spin" size={14} />
                    <span>Analyzing Fairness...</span>
                  </>
                ) : (
                  <span>Evaluate Parity Metrics</span>
                )}
              </button>
            </form>
          )}

          {biasError && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-[11px] rounded-lg">
              {biasError}
            </div>
          )}

          {biasResult && (
            <div className="p-4 bg-slate-900/40 rounded-lg border border-slate-850 space-y-3 text-[11px]">
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Disparate Impact Ratio (DIR)</span>
                <span className={`font-bold ${biasResult.has_bias ? 'text-red-400' : 'text-emerald-400'}`}>
                  {biasResult.disparate_impact_ratio}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Statistical Parity Diff (SPD)</span>
                <span className="text-white font-bold">{biasResult.statistical_parity_difference}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Equal Opportunity Diff (EOD)</span>
                <span className="text-white font-bold">{biasResult.equal_opportunity_difference}</span>
              </div>
              <div className={`p-2 rounded text-[10px] ${biasResult.has_bias ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'}`}>
                {biasResult.interpretation}
              </div>
            </div>
          )}
        </div>

        {/* Audit Log timeline */}
        <div className="glass-panel p-6 rounded-xl lg:col-span-2 space-y-6 flex flex-col min-h-[400px]">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-base font-bold text-white flex items-center space-x-2">
                <Activity size={16} className="text-indigo-400" />
                <span>Compliance Audit Trail</span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">Immutable record logs of user and AI operations.</p>
            </div>
            <button 
              onClick={loadAuditLogs}
              disabled={loadingLogs}
              className="text-slate-500 hover:text-slate-200 transition"
            >
              <RefreshCw size={14} className={loadingLogs ? 'animate-spin' : ''} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-4 max-h-[450px] pr-2 text-xs">
            {auditLogs.length === 0 ? (
              <div className="text-center py-16 text-slate-500 italic">
                No logs recorded yet. Perform dataset operations or model predictions.
              </div>
            ) : (
              auditLogs.map((log) => {
                const badgeColors = {
                  fairness: 'border-indigo-500/30 bg-indigo-500/10 text-indigo-400',
                  collections: 'border-cyan-500/30 bg-cyan-500/10 text-cyan-400',
                  approval: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
                  security: 'border-red-500/30 bg-red-500/10 text-red-400',
                  explainability: 'border-violet-500/30 bg-violet-500/10 text-violet-400',
                };
                
                return (
                  <div key={log.id} className="p-3.5 bg-slate-800/40 border border-slate-800 rounded-lg flex items-start space-x-4">
                    <span className={`px-2 py-0.5 rounded text-[9px] uppercase font-bold tracking-wider border shrink-0 ${
                      badgeColors[log.category] || 'border-slate-700 bg-slate-800 text-slate-400'
                    }`}>
                      {log.category}
                    </span>

                    <div className="flex-1 space-y-1">
                      <div className="flex justify-between items-start">
                        <span className="font-semibold text-slate-200">{log.action}</span>
                        <span className="text-[10px] text-slate-500">
                          {new Date(log.timestamp).toLocaleString()}
                        </span>
                      </div>
                      {log.details && (
                        <div className="bg-slate-900/30 p-2 rounded text-[10px] text-slate-400 leading-normal max-h-32 overflow-y-auto font-mono">
                          {JSON.stringify(log.details, null, 2)}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
