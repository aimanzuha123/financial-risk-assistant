import React, { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { api } from '../api/client';
import { 
  Brain, 
  RefreshCw, 
  CheckCircle2, 
  HelpCircle,
  Cpu, 
  Play, 
  ShieldCheck,
  Search
} from 'lucide-react';

export default function PredictionsPage() {
  const { 
    selectedDatasetId, 
    activeDataset, 
    activePredictions, 
    loadPredictionResults,
    loadCollectionActions 
  } = useStore();

  const [training, setTraining] = useState(false);
  const [activeModel, setActiveModel] = useState(null); // which model's metrics/charts to inspect
  const [formInputs, setFormInputs] = useState({});
  const [singleResult, setSingleResult] = useState(null);
  const [runningSingle, setRunningSingle] = useState(false);

  const runTraining = async () => {
    if (!selectedDatasetId) return;
    setTraining(true);
    try {
      await api.trainModels(selectedDatasetId);
      await loadPredictionResults(selectedDatasetId);
      await loadCollectionActions(selectedDatasetId);
      // Reload dataset info
      useStore.getState().fetchDatasetDetails(selectedDatasetId);
    } catch (err) {
      console.error(err);
    } finally {
      setTraining(false);
    }
  };

  // Set default active model when predictions load
  useEffect(() => {
    if (activePredictions) {
      setActiveModel(activePredictions.best_model);
      // Populate single predict form inputs based on feature names
      const initial = {};
      activePredictions.feature_names?.forEach(f => {
        initial[f] = 0.0;
      });
      setFormInputs(initial);
    }
  }, [activePredictions]);

  // Load predictions if not present
  useEffect(() => {
    if (selectedDatasetId && activeDataset?.status === 'predicted' && !activePredictions) {
      loadPredictionResults(selectedDatasetId);
    }
  }, [selectedDatasetId, activeDataset]);

  const handleInputChange = (field, value) => {
    setFormInputs({
      ...formInputs,
      [field]: parseFloat(value) || 0.0
    });
  };

  const handlePredictSingle = async (e) => {
    e.preventDefault();
    if (!activePredictions?.model_path) return;
    setRunningSingle(true);
    setSingleResult(null);
    try {
      // Create endpoint mock or call real python script predict
      const res = await api.askAssistant(`Predict risk for customer with features: ${JSON.stringify(formInputs)}`, selectedDatasetId);
      setSingleResult(res.reply);
    } catch (err) {
      console.error(err);
    } finally {
      setRunningSingle(false);
    }
  };

  if (!selectedDatasetId) {
    return (
      <div className="text-center py-12 glass-panel p-8 rounded-xl max-w-md mx-auto">
        <h2 className="text-lg font-bold text-white mb-2">No Dataset Active</h2>
        <p className="text-slate-400 text-xs">Choose or upload a dataset in Workspace configuration to train prediction models.</p>
      </div>
    );
  }

  // If models have never been trained
  if (activeDataset?.status !== 'predicted' && !training) {
    return (
      <div className="text-center py-16 glass-panel p-8 rounded-xl max-w-lg mx-auto space-y-6">
        <div className="w-16 h-16 bg-indigo-500/10 rounded-full flex items-center justify-center mx-auto text-indigo-400 border border-indigo-500/20 animate-pulse">
          <Brain size={32} />
        </div>
        <div className="space-y-2">
          <h2 className="text-xl font-bold text-white">Train Predictions Engine</h2>
          <p className="text-slate-400 text-xs max-w-sm mx-auto">
            Train Logistic Regression, Decision Tree, and Random Forest models. The engine automatically evaluates accuracy, F1, AUC, and selects the champion model.
          </p>
        </div>
        <button
          onClick={runTraining}
          className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-8 py-3 rounded-lg transition inline-flex items-center space-x-2"
        >
          <Play size={14} fill="currentColor" />
          <span>Launch Training Pipeline</span>
        </button>
      </div>
    );
  }

  if (training || !activePredictions) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-4">
        <RefreshCw className="animate-spin text-indigo-400" size={32} />
        <span className="text-sm font-semibold text-slate-300">Training ML Models...</span>
        <span className="text-xs text-slate-500 max-w-xs text-center">
          Building and evaluating Logistic Regression, Decision Tree, and Random Forest. Calculating SHAP values.
        </span>
      </div>
    );
  }

  const currentModelData = activePredictions.models[activeModel];
  const championModelName = activePredictions.best_model_name;

  return (
    <div className="space-y-8 animate-slide-up">
      {/* Title */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Predictions Engine</h1>
          <p className="text-slate-400 text-sm mt-1">
            Validate classifier performance metrics and generate explainable credit risk predictions.
          </p>
        </div>
        <button
          onClick={runTraining}
          className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 px-4 py-2 rounded-lg text-xs font-bold transition"
        >
          <RefreshCw size={14} />
          <span>Re-train Models</span>
        </button>
      </div>

      {/* Model Selector Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {Object.entries(activePredictions.models).map(([key, item]) => {
          const isBest = item.is_best;
          const isActive = activeModel === key;

          return (
            <div 
              key={key}
              onClick={() => setActiveModel(key)}
              className={`glass-panel p-5 rounded-xl cursor-pointer border transition-all ${
                isActive ? 'border-indigo-500 shadow-neon' : 'border-slate-800/80 hover:border-slate-700'
              }`}
            >
              <div className="flex justify-between items-start">
                <span className="text-xs text-slate-400 font-bold tracking-wider">{item.model_name}</span>
                {isBest && (
                  <span className="bg-indigo-500/20 text-indigo-400 text-[9px] uppercase font-extrabold tracking-wider px-2 py-0.5 rounded-full border border-indigo-500/30 flex items-center space-x-1">
                    <CheckCircle2 size={10} />
                    <span>Champion</span>
                  </span>
                )}
              </div>
              
              <div className="grid grid-cols-2 gap-4 mt-4 text-xs">
                <div>
                  <span className="block text-slate-500 text-[10px]">F1 Score</span>
                  <span className="text-lg font-extrabold text-white">{item.metrics?.f1?.toFixed(4)}</span>
                </div>
                <div>
                  <span className="block text-slate-500 text-[10px]">Accuracy</span>
                  <span className="text-lg font-extrabold text-white">{item.metrics?.accuracy?.toFixed(4)}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Champion details & Charts */}
      {currentModelData && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Charts Panel */}
          <div className="glass-panel p-6 rounded-xl lg:col-span-2 space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-base font-bold text-white capitalize">{currentModelData.model_name} Performance</h2>
                <p className="text-xs text-slate-400">Detailed metric analytics, curves, and confusion heatmaps.</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {currentModelData.charts?.confusion_matrix && (
                <div className="p-4 bg-slate-900/40 rounded-lg border border-slate-850">
                  <h3 className="text-xs font-bold text-slate-400 mb-3 uppercase tracking-wider">Confusion Matrix</h3>
                  <img 
                    src={`data:image/png;base64,${currentModelData.charts.confusion_matrix}`} 
                    alt="Confusion Matrix" 
                    className="mx-auto rounded-lg max-h-56 h-auto"
                  />
                </div>
              )}
              {currentModelData.charts?.roc_curve && (
                <div className="p-4 bg-slate-900/40 rounded-lg border border-slate-850">
                  <h3 className="text-xs font-bold text-slate-400 mb-3 uppercase tracking-wider">ROC Curve Analysis</h3>
                  <img 
                    src={`data:image/png;base64,${currentModelData.charts.roc_curve}`} 
                    alt="ROC Curve" 
                    className="mx-auto rounded-lg max-h-56 h-auto"
                  />
                </div>
              )}
            </div>

            {currentModelData.charts?.feature_importance && (
              <div className="p-4 bg-slate-900/40 rounded-lg border border-slate-850">
                <h3 className="text-xs font-bold text-slate-400 mb-3 uppercase tracking-wider">Feature Importance Mapping</h3>
                <img 
                  src={`data:image/png;base64,${currentModelData.charts.feature_importance}`} 
                  alt="Feature Importance" 
                  className="mx-auto rounded-lg max-h-64 h-auto w-full object-contain"
                />
              </div>
            )}
          </div>

          {/* Predict Single and Explanations tab */}
          <div className="space-y-6">
            {/* Predict single Account Widget */}
            <div className="glass-panel p-6 rounded-xl space-y-4">
              <div>
                <h2 className="text-sm font-bold text-white flex items-center space-x-2">
                  <Cpu size={16} className="text-indigo-400" />
                  <span>Real-time Risk Assessor</span>
                </h2>
                <p className="text-[11px] text-slate-400">Score individual cases instantly through the champion model.</p>
              </div>

              <form onSubmit={handlePredictSingle} className="space-y-4">
                <div className="space-y-2.5 max-h-52 overflow-y-auto pr-1 text-xs">
                  {activePredictions.feature_names?.map((f) => (
                    <div key={f} className="flex justify-between items-center">
                      <label className="text-slate-400 truncate max-w-[150px]">{f}</label>
                      <input 
                        type="number" 
                        step="any"
                        value={formInputs[f] !== undefined ? formInputs[f] : ''}
                        onChange={(e) => handleInputChange(f, e.target.value)}
                        placeholder="0.0"
                        className="w-20 bg-slate-800 border border-slate-700 rounded px-1.5 py-1 text-right text-white outline-none focus:border-indigo-500"
                      />
                    </div>
                  ))}
                </div>

                <button
                  type="submit"
                  disabled={runningSingle}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white py-2 rounded-lg text-xs font-bold transition flex items-center justify-center space-x-2"
                >
                  {runningSingle ? (
                    <>
                      <RefreshCw className="animate-spin" size={12} />
                      <span>Scoring Case...</span>
                    </>
                  ) : (
                    <span>Evaluate Account</span>
                  )}
                </button>
              </form>

              {singleResult && (
                <div className="p-3.5 bg-slate-850 rounded-lg border border-slate-800 text-[11px] text-slate-300 whitespace-pre-line leading-relaxed max-h-48 overflow-y-auto">
                  {singleResult}
                </div>
              )}
            </div>

            {/* Prediction narrative overview */}
            {activeModel === activePredictions.best_model && activePredictions.explanations && (
              <div className="glass-panel p-6 rounded-xl space-y-4">
                <div>
                  <h2 className="text-sm font-bold text-white flex items-center space-x-2">
                    <ShieldCheck size={16} className="text-indigo-400" />
                    <span>Explainable Predictions</span>
                  </h2>
                  <p className="text-[11px] text-slate-400">SHAP-based global explanation metrics for samples.</p>
                </div>

                <div className="space-y-3 max-h-48 overflow-y-auto text-xs pr-1">
                  {activePredictions.explanations.slice(0, 5).map((exp, idx) => (
                    <div key={idx} className="p-2.5 bg-slate-800/40 border border-slate-800 rounded-lg">
                      <span className="block text-[10px] text-slate-400 font-bold uppercase mb-1">
                        Account index {exp.sample_index} ({exp.predicted_class === 1 ? 'High Risk' : 'Low Risk'})
                      </span>
                      <p className="text-[10px] text-slate-300 leading-relaxed italic">{exp.narrative}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
