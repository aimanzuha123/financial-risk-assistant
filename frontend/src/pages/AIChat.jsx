import React, { useState, useRef, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { 
  MessageSquare, 
  Send, 
  Sparkles, 
  Bot, 
  User, 
  HelpCircle,
  Loader2
} from 'lucide-react';

export default function AIChatPage() {
  const { chatHistory, sendMessage, selectedDatasetId } = useStore();
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const scrollRef = useRef(null);

  const presets = [
    'Summarize this dataset.',
    'Why is this customer high risk?',
    'Generate recommendations.',
    'Tell me about model bias metrics.',
    'Explain the feature importance graph.'
  ];

  const handleSend = async (textToSend) => {
    const text = textToSend || input;
    if (!text.trim()) return;

    setSending(true);
    if (!textToSend) setInput('');

    try {
      await sendMessage(text);
    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  // Scroll chat to bottom on new message
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory]);

  return (
    <div className="space-y-6 h-[calc(100vh-8rem)] flex flex-col animate-slide-up">
      {/* Title */}
      <div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">AI Chat Assistant</h1>
        <p className="text-slate-400 text-sm mt-1">
          Chat with the localized collections agent to inspect variables, explain predictions, and query accounts.
        </p>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-8 min-h-0">
        {/* Presets Sidebar */}
        <div className="glass-panel p-5 rounded-xl space-y-4 h-fit lg:col-span-1">
          <h3 className="text-xs uppercase font-extrabold text-slate-400 tracking-wider flex items-center space-x-1.5">
            <HelpCircle size={14} className="text-indigo-400" />
            <span>Suggested Prompts</span>
          </h3>
          <div className="space-y-2 text-xs">
            {presets.map((p, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(p)}
                disabled={sending}
                className="w-full text-left bg-slate-800/40 hover:bg-slate-800 text-slate-300 border border-slate-700/60 p-2.5 rounded-lg transition text-[11px] leading-snug"
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Chat Window */}
        <div className="glass-panel rounded-xl lg:col-span-3 flex flex-col min-h-0 border border-slate-800/80">
          {/* Chat Messages */}
          <div className="flex-1 p-6 overflow-y-auto space-y-4 min-h-0">
            {chatHistory.map((msg, idx) => {
              const isAssistant = msg.sender === 'assistant';

              return (
                <div 
                  key={idx}
                  className={`flex ${isAssistant ? 'justify-start' : 'justify-end'} space-x-3 max-w-full`}
                >
                  {isAssistant && (
                    <div className="w-8 h-8 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 shrink-0">
                      <Bot size={16} />
                    </div>
                  )}
                  
                  <div className={`p-4 rounded-xl text-xs max-w-[80%] whitespace-pre-line leading-relaxed ${
                    isAssistant 
                      ? 'bg-slate-800/60 text-slate-200 border border-slate-700/40' 
                      : 'bg-indigo-600 text-white font-medium shadow-neon'
                  }`}>
                    {msg.text}
                  </div>

                  {!isAssistant && (
                    <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-750 flex items-center justify-center text-slate-400 shrink-0">
                      <User size={16} />
                    </div>
                  )}
                </div>
              );
            })}
            <div ref={scrollRef}></div>
          </div>

          {/* Form input */}
          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
            className="p-4 border-t border-slate-800 bg-[#1e293b]/20 flex items-center space-x-3"
          >
            <input 
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={selectedDatasetId ? "Ask about high risk accounts, model accuracy, default traits..." : "Upload a dataset to chat with full data insights context..."}
              className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-xs text-white outline-none focus:border-indigo-500 placeholder-slate-500"
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white p-2.5 rounded-lg transition shrink-0 shadow-neon"
            >
              {sending ? (
                <Loader2 className="animate-spin" size={16} />
              ) : (
                <Send size={16} />
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
