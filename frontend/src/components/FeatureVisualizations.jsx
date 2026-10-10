import React, { useState, useMemo } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { Activity, Zap, TrendingUp, Info } from 'lucide-react';

const METRIC_TABS = [
  { id: 'f0', label: 'Pitch Contour (F0 Semitone)', icon: Activity, unit: 'st' },
  { id: 'energy', label: 'Energy Dynamics (Z-Score)', icon: Zap, unit: 'z' },
  { id: 'rate', label: 'Speech Rate (Syllables/s)', icon: TrendingUp, unit: 'syl/s' },
];

function EditorialTooltip({ active, payload, label, unit = '' }) {
  if (active && payload && payload.length) {
    return (
      <div
        style={{
          background: '#ffffff',
          border: '1px solid #e4e4e7',
          borderRadius: 8,
          padding: '0.65rem 0.85rem',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
          fontSize: '0.8rem',
        }}
      >
        <div
          style={{
            color: '#71717a',
            fontWeight: 600,
            marginBottom: '0.35rem',
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          Timestamp: {typeof label === 'number' ? `${label.toFixed(3)}s` : label}
        </div>
        {payload.map((item, index) => (
          <div
            key={index}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '1.25rem',
              color: item.color,
              fontWeight: 600,
              padding: '0.15rem 0',
            }}
          >
            <span>{item.name}:</span>
            <span style={{ fontVariantNumeric: 'tabular-nums' }}>
              {typeof item.value === 'number' ? item.value.toFixed(3) : item.value} {unit}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
}

export default function FeatureVisualizations({
  features = {},
  baselineFeatures = {},
}) {
  const [activeTab, setActiveTab] = useState('f0');

  const chartData = useMemo(() => {
    const timeArray = features?.time || baselineFeatures?.time || [];
    if (!Array.isArray(timeArray) || timeArray.length === 0) {
      return [];
    }

    return timeArray.map((t, idx) => {
      const point = {
        time: typeof t === 'number' ? t : idx,
      };

      if (features?.f0_semitone && features.f0_semitone[idx] !== undefined) {
        point.participant_f0 = features.f0_semitone[idx];
      }
      if (
        baselineFeatures?.f0_semitone &&
        baselineFeatures.f0_semitone[idx] !== undefined
      ) {
        point.baseline_f0 = baselineFeatures.f0_semitone[idx];
      }

      if (features?.energy_z && features.energy_z[idx] !== undefined) {
        point.participant_energy = features.energy_z[idx];
      }
      if (
        baselineFeatures?.energy_z &&
        baselineFeatures.energy_z[idx] !== undefined
      ) {
        point.baseline_energy = baselineFeatures.energy_z[idx];
      }

      if (features?.speech_rate && features.speech_rate[idx] !== undefined) {
        point.participant_rate = features.speech_rate[idx];
      }
      if (
        baselineFeatures?.speech_rate &&
        baselineFeatures.speech_rate[idx] !== undefined
      ) {
        point.baseline_rate = baselineFeatures.speech_rate[idx];
      }

      return point;
    });
  }, [features, baselineFeatures]);

  const hasData = chartData.length > 0;
  const currentTabConfig = METRIC_TABS.find((t) => t.id === activeTab) || METRIC_TABS[0];

  const renderActiveChart = () => {
    if (!hasData) {
      return (
        <div className="vl-empty-state">
          <Activity size={32} style={{ color: 'var(--text-subtle)' }} />
          <p>
            No acoustic feature contours available. Ensure feature arrays and time coordinates
            are populated.
          </p>
        </div>
      );
    }

    if (activeTab === 'f0') {
      const hasParticipant = chartData.some((d) => d.participant_f0 !== undefined);
      const hasBaseline = chartData.some((d) => d.baseline_f0 !== undefined);

      if (!hasParticipant && !hasBaseline) {
        return (
          <div className="vl-empty-state">
            <p>Pitch contour data (f0_semitone) is unavailable in current output.</p>
          </div>
        );
      }

      return (
        <div className="vl-chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" strokeOpacity={0.8} />
              <XAxis
                dataKey="time"
                stroke="#71717a"
                tickFormatter={(val) => `${val.toFixed(2)}s`}
                tick={{ fontSize: 12 }}
                label={{
                  value: 'Time (seconds)',
                  position: 'insideBottom',
                  offset: -12,
                  fill: '#71717a',
                  fontSize: 12,
                }}
              />
              <YAxis
                stroke="#71717a"
                tick={{ fontSize: 12 }}
                label={{
                  value: 'Pitch (semitones)',
                  angle: -90,
                  position: 'insideLeft',
                  fill: '#71717a',
                  fontSize: 12,
                }}
              />
              <Tooltip content={<EditorialTooltip unit="st" />} />
              <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '0.8rem' }} />
              <Line
                type="monotone"
                dataKey="participant_f0"
                name="Participant Delivery"
                stroke="#4f46e5"
                strokeWidth={2.5}
                dot={{ r: 4, fill: '#4f46e5' }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="baseline_f0"
                name="Reference Baseline"
                stroke="#0d9488"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={{ r: 3, fill: '#0d9488' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      );
    }

    if (activeTab === 'energy') {
      const hasParticipant = chartData.some((d) => d.participant_energy !== undefined);
      const hasBaseline = chartData.some((d) => d.baseline_energy !== undefined);

      if (!hasParticipant && !hasBaseline) {
        return (
          <div className="vl-empty-state">
            <p>Energy contour data (energy_z) is unavailable in current output.</p>
          </div>
        );
      }

      return (
        <div className="vl-chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" strokeOpacity={0.8} />
              <XAxis
                dataKey="time"
                stroke="#71717a"
                tickFormatter={(val) => `${val.toFixed(2)}s`}
                tick={{ fontSize: 12 }}
                label={{
                  value: 'Time (seconds)',
                  position: 'insideBottom',
                  offset: -12,
                  fill: '#71717a',
                  fontSize: 12,
                }}
              />
              <YAxis
                stroke="#71717a"
                tick={{ fontSize: 12 }}
                label={{
                  value: 'Energy (Z-Score)',
                  angle: -90,
                  position: 'insideLeft',
                  fill: '#71717a',
                  fontSize: 12,
                }}
              />
              <Tooltip content={<EditorialTooltip unit="z" />} />
              <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '0.8rem' }} />
              <Line
                type="monotone"
                dataKey="participant_energy"
                name="Participant Energy"
                stroke="#4f46e5"
                strokeWidth={2.5}
                dot={{ r: 4, fill: '#4f46e5' }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="baseline_energy"
                name="Reference Energy"
                stroke="#0d9488"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={{ r: 3, fill: '#0d9488' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      );
    }

    if (activeTab === 'rate') {
      return (
        <div className="vl-chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" strokeOpacity={0.8} />
              <XAxis
                dataKey="time"
                stroke="#71717a"
                tickFormatter={(val) => `${val.toFixed(2)}s`}
                tick={{ fontSize: 12 }}
                label={{
                  value: 'Time (seconds)',
                  position: 'insideBottom',
                  offset: -12,
                  fill: '#71717a',
                  fontSize: 12,
                }}
              />
              <YAxis
                stroke="#71717a"
                tick={{ fontSize: 12 }}
                label={{
                  value: 'Rate (syllables/s)',
                  angle: -90,
                  position: 'insideLeft',
                  fill: '#71717a',
                  fontSize: 12,
                }}
              />
              <Tooltip content={<EditorialTooltip unit="syl/s" />} />
              <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '0.8rem' }} />
              <Line
                type="monotone"
                dataKey="participant_rate"
                name="Participant Rate"
                stroke="#4f46e5"
                strokeWidth={2.5}
                dot={{ r: 4, fill: '#4f46e5' }}
              />
              <Line
                type="monotone"
                dataKey="baseline_rate"
                name="Reference Rate"
                stroke="#0d9488"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={{ r: 3, fill: '#0d9488' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      );
    }

    return null;
  };

  return (
    <section id="pitch-energy" className="vl-card" aria-label="Contrastive Feature Visualizations">
      <div className="vl-card-header">
        <div className="vl-card-title-group">
          <h2 className="vl-card-title">
            <Activity size={18} style={{ color: 'var(--brand-primary)' }} />
            Pitch & Energy Contours
          </h2>
          <span className="vl-card-subtitle">
            Synchronized acoustic comparison: Participant vs Target Baseline
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="vl-tabs-row" role="tablist">
        {METRIC_TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              type="button"
              key={tab.id}
              role="tab"
              aria-selected={isActive}
              className={`vl-tab-btn ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <Icon size={14} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {renderActiveChart()}

      <div
        style={{
          marginTop: '0.85rem',
          fontSize: '0.775rem',
          color: 'var(--text-muted)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem',
        }}
      >
        <Info size={13} />
        <span>
          Solid indigo line represents participant delivery; dashed teal line denotes reference
          baseline norm.
        </span>
      </div>
    </section>
  );
}
