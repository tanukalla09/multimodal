import React from 'react';
import { HelpCircle, Play, Info, Activity, ShieldAlert, Sparkles } from 'lucide-react';

export default function FlawDetailsPanel({
  selectedFlaw = null,
  onSeek = () => {},
}) {
  if (!selectedFlaw) {
    return (
      <section className="vl-card" aria-label="Flaw Diagnostic Details">
        <div className="vl-card-header">
          <div className="vl-card-title-group">
            <h2 className="vl-card-title">
              <Activity size={18} style={{ color: 'var(--brand-primary)' }} />
              Flaw Diagnostic Inspector
            </h2>
            <span className="vl-card-subtitle">Select a timeline segment to inspect</span>
          </div>
        </div>

        <div className="vl-empty-state">
          <HelpCircle size={32} style={{ color: 'var(--text-subtle)', marginBottom: '0.65rem' }} />
          <p>
            Click any marked flaw on the timeline to inspect grounded acoustic deviations
            and coaching recommendations.
          </p>
        </div>
      </section>
    );
  }

  const durationSec = (selectedFlaw.end - selectedFlaw.start).toFixed(2);
  const severityVal = typeof selectedFlaw.severity === 'number' ? selectedFlaw.severity : 0;
  const severityPercent = Math.min(Math.max(severityVal * 100, 0), 100);

  return (
    <section className="vl-card" aria-label="Flaw Diagnostic Details">
      <div className="vl-card-header">
        <div className="vl-card-title-group">
          <h2 className="vl-card-title" style={{ textTransform: 'capitalize' }}>
            <ShieldAlert size={18} style={{ color: 'var(--status-warning)' }} />
            Diagnostic: {selectedFlaw.type}
          </h2>
          <span className="vl-card-subtitle">Timestamp-grounded delivery issue</span>
        </div>

        <button
          type="button"
          className="vl-btn-action"
          onClick={() => onSeek(selectedFlaw.start)}
          title={`Seek audio to ${selectedFlaw.start}s`}
        >
          <Play size={13} fill="#ffffff" />
          <span>Seek to Flaw ({selectedFlaw.start.toFixed(2)}s)</span>
        </button>
      </div>

      <div className="vl-diagnostics-panel">
        {/* Core Metadata Grid */}
        <div className="vl-diag-meta-grid">
          <div className="vl-diag-meta-box">
            <div className="vl-diag-meta-label">Temporal Window</div>
            <div className="vl-diag-meta-value">
              {selectedFlaw.start.toFixed(2)}s – {selectedFlaw.end.toFixed(2)}s
            </div>
          </div>

          <div className="vl-diag-meta-box">
            <div className="vl-diag-meta-label">Duration Impact</div>
            <div className="vl-diag-meta-value">{durationSec}s</div>
          </div>
        </div>

        {/* Severity Bar */}
        <div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'baseline',
              fontSize: '0.8rem',
              fontWeight: 600,
              color: 'var(--text-secondary)',
              marginBottom: '0.35rem',
            }}
          >
            <span>Severity Rating</span>
            <span style={{ color: 'var(--text-primary)', fontVariantNumeric: 'tabular-nums' }}>
              {severityVal.toFixed(2)} / 1.00
            </span>
          </div>

          <div className="vl-meter-track" style={{ height: 6 }}>
            <div
              className={`vl-meter-fill ${
                severityVal >= 0.7 ? 'low' : severityVal >= 0.4 ? 'medium' : 'high'
              }`}
              style={{ width: `${severityPercent}%` }}
            />
          </div>
        </div>

        {/* Acoustic Differences Section */}
        {selectedFlaw.metrics && Object.keys(selectedFlaw.metrics).length > 0 && (
          <div>
            <div
              style={{
                fontSize: '0.75rem',
                fontWeight: 700,
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
                marginBottom: '0.4rem',
              }}
            >
              Acoustic Feature Deviations
            </div>

            <div className="vl-metric-delta-box">
              {Object.entries(selectedFlaw.metrics).map(([metricKey, metricVal]) => (
                <div key={metricKey} className="vl-delta-row">
                  <span style={{ color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
                    {metricKey}
                  </span>
                  <span
                    style={{
                      fontWeight: 700,
                      fontFamily: 'monospace',
                      color:
                        typeof metricVal === 'number' && metricVal < 0
                          ? 'var(--status-danger)'
                          : 'var(--status-success)',
                    }}
                  >
                    {typeof metricVal === 'number'
                      ? metricVal > 0
                        ? `+${metricVal.toFixed(2)} st`
                        : `${metricVal.toFixed(2)} st`
                      : String(metricVal)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* User-facing Coaching Explanation */}
        <div className="vl-explanation-card">
          <div className="vl-explanation-label">Coaching Guidance</div>
          <p>{selectedFlaw.explanation || 'No explanation provided in dataset.'}</p>
        </div>
      </div>
    </section>
  );
}
