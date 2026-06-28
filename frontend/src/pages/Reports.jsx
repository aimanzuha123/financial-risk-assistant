import React, { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { api } from '../api/client';
import { 
  FileText, 
  Download, 
  RefreshCw, 
  DollarSign, 
  Sparkles,
  TrendingDown,
  Briefcase
} from 'lucide-react';

export default function ReportsPage() {
  const { 
    selectedDatasetId, 
    activeDataset, 
    activeEda, 
    activePredictions 
  } = useStore();

  const [generating, setGenerating] = useState(false);
  const [report, setReport] = useState(null);

  const handleGenerateReport = async () => {
    if (!selectedDatasetId) return;
    setGenerating(true);
    try {
      const res = await api.generateReport(selectedDatasetId);
      setReport(res);
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!report?.pdf_path) return;
    const url = `/api/reports/${selectedDatasetId}/download?pdf_path=${encodeURIComponent(report.pdf_path)}`;
    window.open(url, '_blank');
  };

  if (!selectedDatasetId) {
    return (
      <div className="text-center py-12 glass-panel p-8 rounded-xl max-w-md mx-auto">
        <h2 className="text-lg font-bold text-white mb-2">No Dataset Active</h2>
        <p className="text-slate-400 text-xs">Choose or upload a dataset in Workspace configuration to generate executive reports.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-slide-up">
      {/* Title */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Executive Business Report</h1>
          <p className="text-slate-400 text-sm mt-1">
            Generate, review, and export PDF executive-ready reports combining risk modeling and collections strategy.
          </p>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={handleGenerateReport}
            disabled={generating}
            className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white px-4 py-2.5 rounded-lg text-xs font-bold transition shadow-neon"
          >
            {generating ? (
              <>
                <RefreshCw className="animate-spin" size={14} />
                <span>Compiling Report...</span>
              </>
            ) : (
              <>
                <Sparkles size={14} />
                <span>Compile Report</span>
              </>
            )}
          </button>

          {report?.pdf_path && (
            <button
              onClick={handleDownload}
              className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 px-4 py-2.5 rounded-lg text-xs font-bold transition"
            >
              <Download size={14} />
              <span>Export PDF</span>
            </button>
          )}
        </div>
      </div>

      {report ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Document Preview */}
          <div className="glass-panel p-8 rounded-xl lg:col-span-2 space-y-8 border border-slate-800 text-slate-350">
            {/* Header branding */}
            <div className="flex justify-between items-start border-b border-slate-800 pb-6">
              <div>
                <span className="text-xs uppercase font-extrabold text-indigo-400 tracking-widest block">Executive Risk Assessment</span>
                <h2 className="text-xl font-bold text-white mt-1">Geldium Analytics Portal</h2>
              </div>
              <span className="text-[10px] text-slate-500 font-medium">CONFIDENTIAL</span>
            </div>

            {/* Executive Summary */}
            <section className="space-y-3">
              <h3 className="text-xs font-extrabold text-white uppercase tracking-wider">Executive Summary</h3>
              <p className="text-xs leading-relaxed whitespace-pre-line text-slate-300">
                {report.executive_summary}
              </p>
            </section>

            {/* Financial Impact */}
            <section className="space-y-3 p-4 bg-slate-900/40 rounded-lg border border-slate-850">
              <h3 className="text-xs font-extrabold text-white uppercase tracking-wider flex items-center space-x-1.5">
                <DollarSign size={14} className="text-emerald-400" />
                <span>Estimated Financial Impact</span>
              </h3>
              <p className="text-xs leading-relaxed whitespace-pre-line text-slate-300">
                {report.financial_impact}
              </p>
            </section>

            {/* Customer Segmentation */}
            {report.customer_segmentation && report.customer_segmentation.length > 0 && (
              <section className="space-y-4">
                <h3 className="text-xs font-extrabold text-white uppercase tracking-wider">Portfolio Customer Segments</h3>
                <div className="overflow-x-auto border border-slate-800 rounded-lg">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="bg-slate-850 text-slate-400 font-bold border-b border-slate-800">
                        <th className="p-3">Segment Name</th>
                        <th className="p-3">Allocation</th>
                        <th className="p-3 text-right">Average Exposure</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 text-slate-300">
                      {report.customer_segmentation.map((s, idx) => (
                        <tr key={idx}>
                          <td className="p-3 font-semibold text-white">{s.segment}</td>
                          <td className="p-3">{s.count} accounts ({s.percentage}%)</td>
                          <td className="p-3 text-right font-bold">${(s.avg_value || 0).toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}
          </div>

          {/* Sidebar recommendations */}
          <div className="space-y-6">
            {/* Recommendations */}
            {report.recommendations && (
              <div className="glass-panel p-6 rounded-xl space-y-4">
                <h3 className="text-xs uppercase font-extrabold text-indigo-400 tracking-wider flex items-center space-x-2">
                  <Briefcase size={14} />
                  <span>Strategic Recommendations</span>
                </h3>
                <ul className="space-y-3 text-xs">
                  {report.recommendations.map((rec, idx) => (
                    <li key={idx} className="bg-slate-800/30 p-2.5 rounded-lg border border-slate-800 text-slate-300">
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Next Steps */}
            {report.next_steps && (
              <div className="glass-panel p-6 rounded-xl space-y-4">
                <h3 className="text-xs uppercase font-extrabold text-amber-400 tracking-wider flex items-center space-x-2">
                  <TrendingDown size={14} />
                  <span>Stakeholder Next Steps</span>
                </h3>
                <ul className="space-y-2 text-xs">
                  {report.next_steps.map((step, idx) => (
                    <li key={idx} className="flex items-start space-x-2 text-slate-300">
                      <span className="text-amber-400 select-none font-bold mt-0.5">•</span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="glass-panel p-16 rounded-xl text-center space-y-4 max-w-xl mx-auto">
          <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto text-indigo-400 border border-slate-700">
            <FileText size={28} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Generate Executive Summary</h2>
            <p className="text-slate-400 text-xs mt-1.5">
              Click the compile button to run the financial impact formulas, customer segmentation metrics, and compile a PDF document.
            </p>
          </div>
          <button
            onClick={handleGenerateReport}
            disabled={generating}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold px-6 py-2.5 rounded-lg transition"
          >
            Compile Report Now
          </button>
        </div>
      )}
    </div>
  );
}
