import React, { useState } from 'react';
import { X, Server, CheckCircle2, AlertCircle, Save } from 'lucide-react';
import { getApiBaseUrl, setApiBaseUrl } from '../services/api';
import { toast } from 'sonner';

interface ApiConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaved: () => void;
}

export const ApiConfigModal: React.FC<ApiConfigModalProps> = ({
  isOpen,
  onClose,
  onSaved,
}) => {
  const [url, setUrl] = useState(getApiBaseUrl());
  const [isTesting, setIsTesting] = useState(false);

  if (!isOpen) return null;

  const handleTestConnection = async () => {
    try {
      setIsTesting(true);
      const res = await fetch(`${url.trim().replace(/\/+$/, '')}/api/health`, {
        method: 'GET',
      });
      if (res.ok) {
        toast.success('Connection successful! Backend is online.');
      } else {
        toast.error(`Backend returned status ${res.status}`);
      }
    } catch (e: any) {
      toast.error(`Could not reach backend: ${e.message}`);
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = () => {
    setApiBaseUrl(url);
    toast.success('API configuration updated');
    onSaved();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[1000] bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-md w-full shadow-2xl border border-gray-100 p-6 space-y-5">
        <div className="flex items-center justify-between pb-3 border-b border-gray-100">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-purple-50 text-purple-600">
              <Server className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900 text-base">Backend Cloud Settings</h3>
              <p className="text-xs text-gray-500">Configure target API host</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-3">
          <label className="text-xs font-bold text-gray-700 uppercase tracking-wider block">
            Backend API Base URL
          </label>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="http://127.0.0.1:6969"
            className="w-full px-4 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm font-mono"
          />
          <p className="text-xs text-gray-500">
            For local testing, use <code className="text-purple-600 bg-purple-50 px-1 py-0.5 rounded">http://127.0.0.1:6969</code>.
            When deployed to AWS EC2, set this to <code className="text-purple-600 bg-purple-50 px-1 py-0.5 rounded">http://&lt;EC2_PUBLIC_IP&gt;:6969</code>.
          </p>
        </div>

        <div className="flex items-center gap-2 pt-2">
          <button
            type="button"
            onClick={handleTestConnection}
            disabled={isTesting}
            className="flex-1 py-2.5 px-3 rounded-xl border border-gray-200 hover:bg-gray-50 text-xs font-bold text-gray-700 transition-colors disabled:opacity-50"
          >
            {isTesting ? 'Testing...' : 'Test Connection'}
          </button>

          <button
            type="button"
            onClick={handleSave}
            className="flex-1 py-2.5 px-3 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white text-xs font-bold shadow-md transition-all flex items-center justify-center gap-1.5"
          >
            <Save className="w-4 h-4" />
            <span>Save Settings</span>
          </button>
        </div>
      </div>
    </div>
  );
};
