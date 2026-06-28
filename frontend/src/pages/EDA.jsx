import React, { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { api } from '../api/client';
import { 
  BarChart, 
  RefreshCw, 
  AlertTriangle, 
  HelpCircle,
  FileSpreadsheet,
  Layers,
  Image as ImageIcon
} from 'lucide-react';

export default function EDAPage() {
  const { 
    selectedDatasetId, 
    activeEda, 
    loadEdaResults 
  } = useStore();

  const [calculating, setCalculating] = useState(false);
  const [activeTab, setActiveTab] = useState('summary'); // summary, quality, correlation, charts
  const [chartType, setChartType] = useState('target_distribution'); // which chart to show

  const runAnalysis = async () => {
    if (!selectedDatasetId) return;
    setCalculating(true);
    try {
      await loadEdaResults(selectedDatasetId);
    } catch (err) {
      console.error(err);
    } finally {
      setCalculating(false);
    }
  };

  // Trigger analysis if select dataset changed and results not present
  useEffect(() => {
    if (selectedDatasetId && !activeEda) {
      runAnalysis();
    }
  }, [selectedDatasetId]);

  if (!selectedDatasetId) {
    return (
      <div className="text-center py-12 glass-panel p-8 rounded-xl max-w-md mx-auto">
        <h2 className="text-lg font-bold text-white mb-2">No Dataset Active</h2>
        <p className="text-slate-400 text-xs">Choose or upload a dataset in Workspace configuration to view EDA metrics.</p>
      </div>
    );
  }

  // Load state
  if (calculating || (!activeEda && selectedDatasetId)) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-4">
        <RefreshCw className="animate-spin text-indigo-400" size={32} />
        <span className="text-sm font-semibold text-slate-300">Executing Automated EDA Engine...</span>
        <span className="text-xs text-slate-500 max-w-xs text-center">
          Analyzing missing values, calculating correlations, detecting outliers, and rendering distribution charts.
        </span>
      </div>
    );
  }

  const {
    summary = {},
    missing_values = {},
    duplicates = {},
    outliers = {},
    correlation = {},
    distributions = {},
    risk_profile = {},
    charts = {},
    business_insights = []
  } = activeEda || {};

  return (
    <div className="space-y-8 animate-slide-up">
      {/* Title block */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">AI EDA Engine</h1>
          <p className="text-slate-400 text-sm mt-1">
            Automated Exploratory Data Analysis, missing values metrics, distributions, and correlation.
          </p>
        </div>
        <button
          onClick={runAnalysis}
          className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 px-4 py-2 rounded-lg text-xs font-bold transition"
        >
          <RefreshCw size={14} />
          <span>Re-run Analysis</span>
        </button>
      </div>

      {/* Tabs Menu */}
      <div className="flex border-b border-slate-800 space-x-6 text-sm">
        {['summary', 'quality', 'correlation', 'charts'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-3 capitalize font-semibold transition-all relative ${
              activeTab === tab ? 'text-indigo-400 border-b-2 border-indigo-400' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab: Summary */}
      {activeTab === 'summary' && (
        <div className="space-y-8">
          {/* Insights checklist */}
          {business_insights.length > 0 && (
            <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-xl p-5 space-y-3">
              <h3 className="text-xs uppercase font-extrabold text-indigo-400 tracking-wider flex items-center space-x-2">
                <Layers size={14} />
                <span>Automated Business Insights</span>
              </h3>
              <ul className="space-y-2 text-xs text-slate-300">
                {business_insights.map((insight, idx) => (
                  <li key={idx} className="flex items-start space-x-2">
                    <span className="text-indigo-400 select-none font-bold mt-0.5">•</span>
                    <span>{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Counts metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass-panel p-5 rounded-xl space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Memory Footprint</span>
              <span className="text-xl font-bold text-white block">{summary.memory_mb} MB</span>
            </div>
            <div className="glass-panel p-5 rounded-xl space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Duplication Ratio</span>
              <span className="text-xl font-bold text-white block">
                {duplicates.duplicate_percentage}% ({duplicates.total_duplicates} records)
              </span>
            </div>
            <div className="glass-panel p-5 rounded-xl space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Total Null Fields</span>
              <span className="text-xl font-bold text-white block">{summary.total_missing} cells</span>
            </div>
          </div>

          {/* Stats breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="glass-panel p-6 rounded-xl space-y-4">
              <h2 className="text-sm font-bold text-white">Target Distribution Metrics</h2>
              {risk_profile.target_distribution ? (
                <div className="space-y-3 text-xs">
                  {Object.entries(risk_profile.target_distribution).map(([cls, info]) => (
                    <div key={cls} className="flex justify-between items-center border-b border-slate-800/60 pb-2">
                      <span className="text-slate-400 font-semibold">Class {cls}</span>
                      <span className="text-white font-bold">{info.count.toLocaleString()} rows ({info.percentage}%)</span>
                    </div>
                  ))}
                  {risk_profile.is_imbalanced && (
                    <div className="flex items-center space-x-2 text-[10px] bg-amber-500/10 border border-amber-500/20 text-amber-400 p-2.5 rounded-lg mt-2">
                      <AlertTriangle size={14} className="shrink-0" />
                      <span>Warning: Detected class imbalance ratio {risk_profile.risk_ratio}. SMOTE/balancing enabled.</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-slate-500 text-xs italic">Set target column in Workspace to show risk breakdown.</div>
              )}
            </div>

            <div className="glass-panel p-6 rounded-xl space-y-4">
              <h2 className="text-sm font-bold text-white">Features DataType Count</h2>
              <div className="space-y-3 text-xs">
                <div className="flex justify-between items-center border-b border-slate-800/60 pb-2">
                  <span className="text-slate-400">Numerical Columns</span>
                  <span className="text-white font-bold">{summary.column_count?.numerical || 0}</span>
                </div>
                <div className="flex justify-between items-center border-b border-slate-800/60 pb-2">
                  <span className="text-slate-400">Categorical Columns</span>
                  <span className="text-white font-bold">{summary.column_count?.categorical || 0}</span>
                </div>
                <div className="flex justify-between items-center font-bold">
                  <span className="text-slate-400">Total Columns</span>
                  <span className="text-indigo-400">{summary.column_count?.total || 0}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab: Quality & Outliers */}
      {activeTab === 'quality' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Missing Values details */}
          <div className="glass-panel p-6 rounded-xl space-y-4">
            <h2 className="text-sm font-bold text-white">Missing Values by Column</h2>
            {missing_values.details && Object.keys(missing_values.details).length > 0 ? (
              <div className="space-y-3 text-xs overflow-y-auto max-h-96 pr-2">
                {Object.entries(missing_values.details).map(([col, info]) => (
                  <div key={col} className="flex justify-between items-center border-b border-slate-800/60 pb-2">
                    <span className="text-slate-400 truncate max-w-[150px] font-semibold">{col}</span>
                    <span className="text-white font-bold">{info.count} ({info.percentage}%)</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6 text-slate-500 text-xs italic">
                Clean dataset: No missing values found in columns.
              </div>
            )}
          </div>

          {/* Outliers details */}
          <div className="glass-panel p-6 rounded-xl space-y-4">
            <h2 className="text-sm font-bold text-white">IQR Outliers Detected</h2>
            {outliers.details && Object.keys(outliers.details).length > 0 ? (
              <div className="space-y-3 text-xs overflow-y-auto max-h-96 pr-2">
                {Object.entries(outliers.details).map(([col, info]) => (
                  <div key={col} className="flex justify-between items-center border-b border-slate-800/60 pb-2">
                    <span className="text-slate-400 truncate max-w-[150px] font-semibold">{col}</span>
                    <span className="text-white font-bold">{info.iqr_outliers} ({info.iqr_percentage}%)</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-6 text-slate-500 text-xs italic">
                No outliers found in numerical columns.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab: Correlation */}
      {activeTab === 'correlation' && (
        <div className="glass-panel p-6 rounded-xl space-y-6">
          <div>
            <h2 className="text-sm font-bold text-white">Strong Multi-collinearity Warning</h2>
            <p className="text-xs text-slate-400 mt-0.5">Identified correlations above 0.50 absolute threshold.</p>
          </div>

          {correlation.strong_correlations && correlation.strong_correlations.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {correlation.strong_correlations.map((c, idx) => (
                <div key={idx} className="p-4 bg-slate-800/40 border border-slate-800 rounded-lg flex justify-between items-center text-xs">
                  <div>
                    <span className="block text-slate-400 font-semibold">{c.feature_1} ↔ {c.feature_2}</span>
                    <span className="text-[10px] text-indigo-400 capitalize font-medium">{c.strength} {c.direction}</span>
                  </div>
                  <span className="text-white font-bold">{c.correlation.toFixed(3)}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500 text-xs italic">
              No strong correlation matches found. Features are well distributed.
            </div>
          )}
        </div>
      )}

      {/* Tab: Charts Gallery */}
      {activeTab === 'charts' && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Chart menu picker */}
          <div className="glass-panel p-4 rounded-xl flex flex-col space-y-1.5 h-fit">
            <label className="text-[10px] uppercase font-bold tracking-wider text-slate-500 mb-2 block">Available Plots</label>
            {Object.keys(charts).map((key) => (
              <button
                key={key}
                onClick={() => setChartType(key)}
                className={`w-full text-left px-3 py-2 rounded text-xs transition ${
                  chartType === key ? 'bg-indigo-600 text-white font-bold' : 'text-slate-400 hover:bg-slate-800/60'
                }`}
              >
                {key.replace('_', ' ')}
              </button>
            ))}
          </div>

          {/* Chart previewer */}
          <div className="glass-panel p-6 rounded-xl lg:col-span-3 flex flex-col items-center justify-center">
            {charts[chartType] ? (
              <div className="w-full">
                <img 
                  src={`data:image/png;base64,${charts[chartType]}`} 
                  alt={chartType} 
                  className="mx-auto rounded-lg max-w-full h-auto max-h-[500px]"
                />
                <div className="text-center text-[10px] text-slate-400 mt-4 capitalize font-semibold">
                  Visual: {chartType.replace('_', ' ')}
                </div>
              </div>
            ) : (
              <div className="text-center py-20 text-slate-500 text-xs flex flex-col items-center space-y-2">
                <ImageIcon size={28} />
                <span>Select a chart category to render the graphics canvas.</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
