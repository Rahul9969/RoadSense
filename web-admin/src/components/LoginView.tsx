import React, { useState } from 'react';
import { ShieldCheck, Mail, Lock, ArrowRight, Sparkles } from 'lucide-react';
import { loginAdmin } from '../services/api';
import { toast } from 'sonner';
import type { UserAuth } from '../type';

interface LoginViewProps {
  onLoginSuccess: (auth: UserAuth) => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('admin@roadsense.gov');
  const [password, setPassword] = useState('12345678');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('Please enter both email and password');
      return;
    }

    try {
      setIsLoading(true);
      const auth = await loginAdmin(email, password);
      toast.success(`Welcome back, ${auth.username}!`);
      onLoginSuccess(auth);
    } catch (err: any) {
      toast.error(err.message || 'Login failed. Please verify admin credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const fillDemoCredentials = () => {
    setEmail('admin@roadsense.gov');
    setPassword('12345678');
    toast.info('Loaded seeded Administrator credentials');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[#F8F9FA]">
      <div className="w-full max-w-md">
        {/* Card Header Branding */}
        <div className="text-center mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-gradient-to-tr from-[#9333EA] to-[#2563EB] text-white shadow-md mb-4">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">
            RoadSense Admin
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Municipality Road Hazard Management Portal
          </p>
        </div>

        {/* Login Box */}
        <div className="bg-white rounded-3xl p-8 shadow-md border border-gray-100">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">
                Administrator Email
              </label>
              <div className="relative">
                <Mail className="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@municipality.gov"
                  className="w-full pl-11 pr-4 py-3 rounded-2xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm font-medium"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-11 pr-4 py-3 rounded-2xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm font-medium"
                  required
                />
              </div>
            </div>

            {/* Quick Demo Fill Button */}
            <div className="flex justify-end">
              <button
                type="button"
                onClick={fillDemoCredentials}
                className="text-xs text-purple-600 hover:text-purple-700 font-semibold flex items-center gap-1"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Fill Default Credentials</span>
              </button>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-[#9333EA] to-[#2563EB] hover:from-purple-700 hover:to-blue-700 active:scale-95 text-white font-bold text-sm shadow-md transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <span>{isLoading ? 'Verifying...' : 'Sign In as Administrator'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Footer note */}
          <div className="mt-6 pt-5 border-t border-gray-100 text-center">
            <p className="text-xs text-gray-500">
              Only authorized municipal personnel with admin privileges can access this dashboard.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
