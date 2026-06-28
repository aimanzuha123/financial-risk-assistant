import React from 'react';
import { 
  LayoutDashboard, 
  UploadCloud, 
  BarChart3, 
  Brain, 
  FileText, 
  ShieldAlert, 
  MessageSquare, 
  Settings as SettingsIcon,
  Workflow
} from 'lucide-react';
import { useStore } from '../store/useStore';

export default function Sidebar({ activePage, setActivePage }) {
  const { selectedDatasetId, datasets } = useStore();
  const activeDataset = datasets.find(d => d.id === selectedDatasetId);

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload Dataset', icon: UploadCloud },
    { id: 'eda', label: 'EDA Engine', icon: BarChart3, requiresDataset: true },
    { id: 'predictions', label: 'Prediction Engine', icon: Brain, requiresDataset: true },
    { id: 'report', label: 'Business Report', icon: FileText, requiresDataset: true },
    { id: 'collections', label: 'Collections Strategy', icon: Workflow, requiresDataset: true },
    { id: 'chat', label: 'AI Assistant', icon: MessageSquare },
    { id: 'settings', label: 'Settings & Trust', icon: ShieldAlert },
  ];

  return (
    <aside className="w-64 bg-[#0f172a] border-r border-slate-800 flex flex-col h-screen sticky top-0">
      {/* Brand Logo */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 space-x-2.5">
        <span className="text-2xl">🛡️</span>
        <span className="font-extrabold text-lg tracking-wider text-white font-sans">
          GELDIUM <span className="text-indigo-400">RISK</span>
        </span>
      </div>

      {/* Dataset Picker Widget */}
      <div className="p-4 border-b border-slate-800 bg-[#1e293b]/20">
        <label className="block text-[10px] uppercase font-bold tracking-wider text-slate-500 mb-1">
          Active Workspace
        </label>
        {datasets.length === 0 ? (
          <div className="text-xs text-slate-400 italic">No datasets uploaded</div>
        ) : (
          <select
            value={selectedDatasetId || ''}
            onChange={(e) => useStore.getState().setDatasetId(Number(e.target.value) || null)}
            className="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1.5 text-xs text-slate-200 outline-none focus:border-indigo-500"
          >
            <option value="">-- Choose Dataset --</option>
            {datasets.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name} ({d.rows} rows)
              </option>
            ))}
          </select>
        )}
        {activeDataset && (
          <div className="mt-2 flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-indigo-400"></span>
            <span className="text-[10px] text-indigo-300 font-medium capitalize">
              Status: {activeDataset.status}
            </span>
          </div>
        )}
      </div>

      {/* Main Navigation Links */}
      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isDisabled = item.requiresDataset && !selectedDatasetId;
          const isActive = activePage === item.id;

          return (
            <button
              key={item.id}
              onClick={() => !isDisabled && setActivePage(item.id)}
              disabled={isDisabled}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-sm transition-all duration-200 ${
                isActive
                  ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-neon font-semibold'
                  : isDisabled
                  ? 'opacity-40 cursor-not-allowed text-slate-500'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
              }`}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800 text-[10px] text-slate-500 text-center">
        v1.0.0 • Responsible AI Compliant
      </div>
    </aside>
  );
}
