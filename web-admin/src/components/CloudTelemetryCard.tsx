import React from 'react';
import { Cloud, Layers, Database, Bell, Cpu, CheckCircle2, Radio } from 'lucide-react';
import type { CloudTelemetry } from '../type';

interface CloudTelemetryCardProps {
  telemetry: CloudTelemetry | null;
  isLoading: boolean;
}

export const CloudTelemetryCard: React.FC<CloudTelemetryCardProps> = ({ telemetry, isLoading }) => {
  if (isLoading || !telemetry) {
    return (
      <div className="bg-white rounded-3xl p-6 shadow-md border border-gray-100 mb-6 animate-pulse">
        <div className="h-5 w-48 bg-gray-200 rounded mb-4" />
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-24 bg-gray-100 rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-3xl p-6 shadow-md border border-slate-700/50 mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-blue-500/20 flex items-center justify-center text-blue-400">
            <Cloud className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide">AWS Cloud Infrastructure Telemetry</h3>
            <p className="text-[11px] text-slate-400">Region: <span className="font-mono text-blue-400 font-semibold">{telemetry.aws_region}</span> • Live SQS Event Decoupling</p>
          </div>
        </div>
        <div className="flex items-center gap-2 bg-emerald-500/15 border border-emerald-500/30 px-3 py-1 rounded-full">
          <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span className="text-[11px] font-bold text-emerald-400">All Cloud Services Nominal</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
        {/* Amazon SQS */}
        <div className="bg-slate-800/80 rounded-2xl p-3.5 border border-slate-700 hover:border-slate-600 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-amber-400 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5" /> Amazon SQS
            </span>
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
          </div>
          <div className="text-xl font-black text-white">{telemetry.sqs.messages_available}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Queued Messages</div>
          <div className="mt-2 pt-2 border-t border-slate-700/60 text-[10px] text-slate-400 flex justify-between">
            <span>In-Flight: <strong className="text-white">{telemetry.sqs.messages_in_flight}</strong></span>
            <span className="text-emerald-400">DLQ: {telemetry.sqs.dlq_status}</span>
          </div>
        </div>

        {/* AWS Lambda */}
        <div className="bg-slate-800/80 rounded-2xl p-3.5 border border-slate-700 hover:border-slate-600 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-orange-400 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5" /> AWS Lambda
            </span>
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
          </div>
          <div className="text-xs font-bold text-white truncate">{telemetry.lambda.function_name}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">{telemetry.lambda.runtime} Worker</div>
          <div className="mt-2 pt-2 border-t border-slate-700/60 text-[10px] text-slate-400 flex justify-between">
            <span>Trigger: <strong className="text-white">SQS Event</strong></span>
            <span className="text-orange-400">Batch: {telemetry.lambda.batch_size}</span>
          </div>
        </div>

        {/* Amazon S3 */}
        <div className="bg-slate-800/80 rounded-2xl p-3.5 border border-slate-700 hover:border-slate-600 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-blue-400 flex items-center gap-1.5">
              <Cloud className="w-3.5 h-3.5" /> Amazon S3
            </span>
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
          </div>
          <div className="text-xs font-bold text-white truncate" title={telemetry.s3.bucket_name}>
            {telemetry.s3.bucket_name.replace('roadsense-', '')}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">Zero-Bloat S3 CDN</div>
          <div className="mt-2 pt-2 border-t border-slate-700/60 text-[10px] text-slate-400 flex justify-between">
            <span>Class: <strong className="text-white">{telemetry.s3.storage_class}</strong></span>
            <span className="text-blue-400">{telemetry.s3.encryption}</span>
          </div>
        </div>

        {/* Amazon SNS */}
        <div className="bg-slate-800/80 rounded-2xl p-3.5 border border-slate-700 hover:border-slate-600 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-rose-400 flex items-center gap-1.5">
              <Bell className="w-3.5 h-3.5" /> Amazon SNS
            </span>
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
          </div>
          <div className="text-xs font-bold text-white">Critical Dispatch</div>
          <div className="text-[10px] text-slate-400 mt-0.5">{telemetry.sns.alert_routing}</div>
          <div className="mt-2 pt-2 border-t border-slate-700/60 text-[10px] text-slate-400 flex justify-between">
            <span>Status: <strong className="text-emerald-400">PUBLISHING</strong></span>
            <span className="text-rose-400">Fan-out</span>
          </div>
        </div>

        {/* Amazon RDS */}
        <div className="bg-slate-800/80 rounded-2xl p-3.5 border border-slate-700 hover:border-slate-600 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-emerald-400 flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5" /> Amazon RDS
            </span>
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
          </div>
          <div className="text-xs font-bold text-white">{telemetry.rds.engine}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">ACID Relational Storage</div>
          <div className="mt-2 pt-2 border-t border-slate-700/60 text-[10px] text-slate-400 flex justify-between">
            <span>Pool: <strong className="text-white">{telemetry.rds.pool_size} conns</strong></span>
            <span className="text-emerald-400 flex items-center gap-1">
              <CheckCircle2 className="w-2.5 h-2.5" /> {telemetry.rds.status}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
