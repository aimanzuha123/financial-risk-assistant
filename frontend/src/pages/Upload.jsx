import React, { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { api } from '../api/client';
import { 
  Upload, 
  Trash2, 
  Settings, 
  Eye, 
  Check, 
  Loader2,
  Table as TableIcon
} from 'lucide-react';

export default function UploadPage() {
  const { 
    datasets, 
    selectedDatasetId, 
    fetchDatasets, 
    setDatasetId 
  } = useStore();

  const [uploading, setUploading] = useState(false);
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [updatingTarget, setUpdatingTarget] = useState(false);

  useEffect(() => {
    fetchDatasets();
  }, []);

  // Handle preview change when active dataset shifts
  useEffect(() => {
    if (selectedDatasetId) {
      handleLoadPreview(selectedDatasetId);
    } else {
      setPreview(null);
    }
  }, [selectedDatasetId]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError(null);

    try {
      const data = await api.uploadDataset(file);
      await fetchDatasets();
      setDatasetId(data.id);
      setFile(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload CSV. Ensure it is a valid formatted table.');
    } finally {
      setUploading(false);
    }
  };

  const handleLoadPreview = async (id) => {
    setLoadingPreview(true);
    try {
      const data = await api.getPreview(id, 10); // get top 10 preview rows
      setPreview(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingPreview(false);
    }
  };

  const handleSetTarget = async (id, col) => {
    setUpdatingTarget(true);
    try {
      await api.setTargetColumn(id, col);
      await fetchDatasets();
      // reload details
      useStore.getState().fetchDatasetDetails(id);
    } catch (err) {
      console.error(err);
    } finally {
      setUpdatingTarget(false);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this dataset? This will clear all calculations, models, and actions.')) return;
    try {
      await api.deleteDataset(id);
      if (selectedDatasetId === id) {
        setDatasetId(null);
      }
      fetchDatasets();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8 animate-slide-up">
      {/* Title */}
      <div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Upload & Workspace Configuration</h1>
        <p className="text-slate-400 text-sm mt-1">
          Upload credit portfolio CSV files, declare targets, and review structure schema mapping.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload Column */}
        <div className="glass-panel p-6 rounded-xl space-y-6">
          <div>
            <h2 className="text-lg font-bold text-white">Upload New CSV</h2>
            <p className="text-xs text-slate-400 mt-0.5">Supports standard financial and collections formats.</p>
          </div>

          <form onSubmit={handleUpload} className="space-y-4">
            <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500/50 rounded-xl p-8 text-center cursor-pointer transition relative">
              <input 
                type="file" 
                accept=".csv" 
                onChange={handleFileChange}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
              <Upload className="mx-auto text-slate-500 mb-3" size={32} />
              {file ? (
                <div>
                  <span className="text-xs text-indigo-400 font-semibold block truncate max-w-[200px] mx-auto">{file.name}</span>
                  <span className="text-[10px] text-slate-500">{(file.size / 1024).toFixed(1)} KB</span>
                </div>
              ) : (
                <div>
                  <span className="text-xs font-medium text-slate-300 block">Drag & drop CSV or click to select</span>
                  <span className="text-[10px] text-slate-500 mt-1 block">Maximum upload file size: 50MB</span>
                </div>
              )}
            </div>

            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-lg">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={!file || uploading}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 py-2.5 rounded-lg text-xs font-bold text-white transition flex items-center justify-center space-x-2"
            >
              {uploading ? (
                <>
                  <Loader2 className="animate-spin" size={16} />
                  <span>Processing File...</span>
                </>
              ) : (
                <span>Upload & Analyze</span>
              )}
            </button>
          </form>
        </div>

        {/* Existing Datasets List */}
        <div className="glass-panel p-6 rounded-xl lg:col-span-2 space-y-6">
          <div>
            <h2 className="text-lg font-bold text-white">Stored Portfolio Datasets</h2>
            <p className="text-xs text-slate-400 mt-0.5">Manage active database schema and target definitions.</p>
          </div>

          {datasets.length === 0 ? (
            <div className="text-center py-12 text-slate-500 text-xs italic">
              No datasets uploaded yet. Use the upload panel to import data.
            </div>
          ) : (
            <div className="overflow-x-auto border border-slate-800 rounded-lg">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-800/40 text-[10px] uppercase font-bold tracking-wider text-slate-400 border-b border-slate-800">
                    <th className="p-3.5">Dataset Name</th>
                    <th className="p-3.5">Metrics</th>
                    <th className="p-3.5">Delinquency Target</th>
                    <th className="p-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-xs">
                  {datasets.map((d) => {
                    const isSelected = selectedDatasetId === d.id;
                    const candidates = d.summary?.columns || [];

                    return (
                      <tr 
                        key={d.id} 
                        onClick={() => setDatasetId(d.id)}
                        className={`cursor-pointer transition-colors ${
                          isSelected ? 'bg-indigo-600/10 text-white' : 'hover:bg-slate-800/30 text-slate-300'
                        }`}
                      >
                        <td className="p-3.5 font-semibold">
                          <div className="flex items-center space-x-2">
                            {isSelected && <Check size={14} className="text-indigo-400" />}
                            <span className="truncate max-w-[150px]">{d.name}</span>
                          </div>
                        </td>
                        <td className="p-3.5">
                          <span className="text-[10px] text-slate-400">
                            {d.rows.toLocaleString()} rows • {d.columns} cols
                          </span>
                        </td>
                        <td className="p-3.5" onClick={(e) => e.stopPropagation()}>
                          <select
                            value={d.target_column || ''}
                            onChange={(e) => handleSetTarget(d.id, e.target.value)}
                            disabled={updatingTarget}
                            className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-[11px] text-slate-300 focus:outline-none focus:border-indigo-500"
                          >
                            <option value="">-- Choose Target --</option>
                            {candidates.map((col) => (
                              <option key={col} value={col}>{col}</option>
                            ))}
                          </select>
                        </td>
                        <td className="p-3.5 text-right" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={(e) => handleDelete(d.id, e)}
                            className="text-slate-500 hover:text-red-400 p-1 rounded transition"
                            title="Delete dataset"
                          >
                            <Trash2 size={15} />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Dataset Preview Section */}
      {preview && (
        <div className="glass-panel p-6 rounded-xl space-y-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <TableIcon size={18} className="text-indigo-400" />
              <h2 className="text-lg font-bold text-white">Schema Preview</h2>
            </div>
            <span className="text-[10px] text-slate-400">Showing first 10 accounts</span>
          </div>

          <div className="overflow-x-auto border border-slate-800 rounded-lg">
            <table className="w-full text-left border-collapse text-[11px]">
              <thead>
                <tr className="bg-slate-800/40 text-slate-400 font-bold border-b border-slate-800">
                  {preview.columns.map((col) => (
                    <th key={col} className="p-3 border-r border-slate-800/60 last:border-0">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {preview.data.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/20">
                    {preview.columns.map((col) => (
                      <td key={col} className="p-3 border-r border-slate-800/60 last:border-0 truncate max-w-[120px]">
                        {row[col] !== null ? String(row[col]) : <span className="text-slate-600 italic">null</span>}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
