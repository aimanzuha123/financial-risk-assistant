import React, { useEffect } from 'react';
import { useStore } from '../store/useStore';
import { 
  FileSpreadsheet, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle,
  HelpCircle,
  Database,
  ShieldCheck
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

export default function Dashboard({ setActivePage }) {
  const { 
    selectedDatasetId, 
    activeDataset, 
    activeEda, 
    activeActions, 
    fetchDatasets,
    datasets 
  } = useStore();

  useEffect(() => {
    fetchDatasets();
  }, []);

  // Summary figures
  const totalDatasets = datasets.length;
  const activeStatus = activeDataset?.status || 'No Active Dataset';
  const rowCount = activeDataset?.rows || 0;
  const colCount = activeDataset?.columns || 0;
  const targetCol = activeDataset?.target_column || 'Not configured';

  // Pie chart calculation for risk segments
  const getRiskData = () => {
    if (!activeActions || activeActions.length === 0) {
      return [
        { name: 'No Data', value: 1, color: '#475569' }
      ];
    }
    const counts = activeActions.reduce((acc, curr) => {
      acc[curr.risk_level] = (acc[curr.risk_level] || 0) + 1;
      return acc;
    }, {});

    return [
      { name: 'Critical', value: counts.critical || 0, color: '#ef4444' },
      { name: 'High Risk', value: counts.high || 0, color: '#fb923c' },
      { name: 'Medium Risk', value: counts.medium || 0, color: '#facc15' },
      { name: 'Low Risk', value: counts.low || 0, color: '#10b981' }
    ].filter(item => item.value > 0);
  };

  const riskData = getRiskData();

  return (
    <div className="space-y-8">
      {/* Title section */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Risk Analytics Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">
            Overview of portfolio exposure, machine learning validation, and active interventions.
          </p>
        </div>
        {!selectedDatasetId && (
          <button
            onClick={() => setActivePage('upload')}
            className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
          >
            <UploadCloud size={16} />
            <span>Upload Dataset</span>
          </button>
        )}
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass-panel p-6 rounded-xl flex items-center space-x-4">
          <div className="p-3 bg-indigo-500/10 rounded-lg text-indigo-400">
            <Database size={24} />
          </div>
          <div>
            <span className="block text-xs text-slate-400 uppercase font-bold tracking-wider">Total Records</span>
            <span className="text-2xl font-bold text-white mt-1 block">
              {rowCount > 0 ? rowCount.toLocaleString() : 'N/A'}
            </span>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl flex items-center space-x-4">
          <div className="p-3 bg-cyan-500/10 rounded-lg text-cyan-400">
            <FileSpreadsheet size={24} />
          </div>
          <div>
            <span className="block text-xs text-slate-400 uppercase font-bold tracking-wider">Features</span>
            <span className="text-2xl font-bold text-white mt-1 block">
              {colCount > 0 ? colCount : 'N/A'}
            </span>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl flex items-center space-x-4">
          <div className="p-3 bg-amber-500/10 rounded-lg text-amber-400">
            <TrendingUp size={24} />
          </div>
          <div>
            <span className="block text-xs text-slate-400 uppercase font-bold tracking-wider">Target Configured</span>
            <span className="text-sm font-bold text-white mt-1 block truncate max-w-[150px]">
              {targetCol}
            </span>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-xl flex items-center space-x-4">
          <div className="p-3 bg-emerald-500/10 rounded-lg text-emerald-400">
            <ShieldCheck size={24} />
          </div>
          <div>
            <span className="block text-xs text-slate-400 uppercase font-bold tracking-wider">Analysis Status</span>
            <span className="text-sm font-bold text-white mt-1 block capitalize">
              {activeStatus}
            </span>
          </div>
        </div>
      </div>

      {/* Main Workspace Panels */}
      {selectedDatasetId ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Risk Pie Chart */}
          <div className="glass-panel p-6 rounded-xl lg:col-span-2 flex flex-col justify-between">
            <div>
              <h2 className="text-lg font-bold text-white">Portfolio Risk Segments</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Proportion of active records mapped across credit risk levels.
              </p>
            </div>
            
            <div className="h-64 mt-4 relative">
              {activeActions.length === 0 ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500 text-xs italic">
                  <span>No strategy generated yet.</span>
                  <button 
                    onClick={() => setActivePage('collections')}
                    className="mt-2 text-indigo-400 hover:underline text-[11px] font-semibold"
                  >
                    Generate strategy &rarr;
                  </button>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={riskData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {riskData.map((entry, idx) => (
                        <Cell key={`cell-${idx}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#fff' }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Legend verticalAlign="bottom" height={36} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          {/* Quick-start checklist */}
          <div className="glass-panel p-6 rounded-xl flex flex-col justify-between">
            <div>
              <h2 className="text-lg font-bold text-white">Setup Checklist</h2>
              <p className="text-xs text-slate-400 mt-0.5">Required steps to complete full portfolio evaluation.</p>
            </div>

            <div className="space-y-4 my-6 flex-1">
              <div className="flex items-center space-x-3 text-xs">
                {selectedDatasetId ? <CheckCircle size={16} className="text-emerald-400 shrink-0" /> : <div className="w-4 h-4 rounded-full border border-slate-600 shrink-0"></div>}
                <span className={selectedDatasetId ? "text-slate-300 line-through" : "text-slate-200 font-semibold"}>Upload CSV & Config Target</span>
              </div>
              <div className="flex items-center space-x-3 text-xs">
                {activeEda ? <CheckCircle size={16} className="text-emerald-400 shrink-0" /> : <div className="w-4 h-4 rounded-full border border-slate-600 shrink-0"></div>}
                <span className={activeEda ? "text-slate-300 line-through" : "text-slate-200 font-semibold"}>Execute Exploratory Data Analysis</span>
              </div>
              <div className="flex items-center space-x-3 text-xs">
                {activeDataset?.status === 'predicted' ? <CheckCircle size={16} className="text-emerald-400 shrink-0" /> : <div className="w-4 h-4 rounded-full border border-slate-600 shrink-0"></div>}
                <span className={activeDataset?.status === 'predicted' ? "text-slate-300 line-through" : "text-slate-200 font-semibold"}>Train Delinquency Classifier Models</span>
              </div>
              <div className="flex items-center space-x-3 text-xs">
                {activeActions.length > 0 ? <CheckCircle size={16} className="text-emerald-400 shrink-0" /> : <div className="w-4 h-4 rounded-full border border-slate-600 shrink-0"></div>}
                <span className={activeActions.length > 0 ? "text-slate-300 line-through" : "text-slate-200 font-semibold"}>Formulate Action Intervention Triggers</span>
              </div>
            </div>

            <button
              onClick={() => {
                if (!activeEda) setActivePage('eda');
                else if (activeDataset?.status !== 'predicted') setActivePage('predictions');
                else setActivePage('collections');
              }}
              className="w-full bg-indigo-600 hover:bg-indigo-500 py-2.5 rounded-lg text-xs font-bold transition text-center block text-white"
            >
              Resume Strategy Setup
            </button>
          </div>
        </div>
      ) : (
        <div className="glass-panel p-12 rounded-xl text-center space-y-4">
          <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto text-indigo-400 border border-slate-700">
            <Database size={28} />
          </div>
          <div className="max-w-md mx-auto">
            <h2 className="text-xl font-bold text-white">No Dataset Active</h2>
            <p className="text-slate-400 text-sm mt-1.5">
              Select an uploaded dataset from the sidebar workspace picker, or upload a new credit CSV file to initialize analysis.
            </p>
          </div>
          <button
            onClick={() => setActivePage('upload')}
            className="inline-block bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-6 py-2.5 rounded-lg transition"
          >
            Go to Upload Settings
          </button>
        </div>
      )}
    </div>
  );
}

// Extra helper for inline icon import fallback
function UploadCloud(props) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={props.size || 24} height={props.size || 24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242" />
      <path d="M12 12v9" />
      <path d="m16 16-4-4-4 4" />
    </svg>
  );
}
