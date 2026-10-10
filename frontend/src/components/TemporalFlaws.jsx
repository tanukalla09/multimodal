import React from 'react';
import { Clock, AlertTriangle, AlertOctagon, ChevronRight } from 'lucide-react';

function getSeverityClass(severity) {
  if (typeof severity !== 'number') return 'severity-medium';
  if (severity >= 0.7) return 'severity-high';
  if (severity >= 0.4) return 'severity-medium';
  return 'severity-low';
}

function getSeverityLabel(severity) {
  if (typeof severity !== 'number') return 'Moderate';
  if (severity >= 0.7) return 'High Severity';
  if (severity >= 0.4) return 'Moderate Flaw';
  return 'Mild Divergence';
}

export default function TemporalFlaws({
  flaws = [],
  meta = {},
  selectedFlaw = null,
  onSelectFlaw = () => {},
  currentTime = 0,
}) {
  const duration = meta?.duration || 3.0;

  // Validation: preserve truth and avoid silently clamping invalid timestamps
  const processedFlaws = flaws.map((flaw, idx) => {
    const isStartValid = typeof flaw.start === 'number' && flaw.start >= 0;
    const isEndValid =
      typeof flaw.end === 'number' &&
      flaw.end >= (flaw.start || 0) &&
      flaw.end <= duration;
    const isValid = isStartValid && isEndValid && flaw.end > flaw.start;

    return {
      ...flaw,
      id: idx,
      isValid,
      invalidReason: !isStartValid
        ? 'Start time is negative or invalid'
        : flaw.start >= flaw.end
        ? 'Start time exceeds or equals end time'
        : flaw.end > duration
        ? `End time (${flaw.end}s) exceeds audio duration (${duration}s)`
        : null,
    };
  });

  const playheadPercent =
    duration > 0 ? Math.min(Math.max((currentTime / duration) * 100, 0), 100) : 0;

  // Step marks along the ruler
  const tickStep = duration <= 5 ? 0.5 : 1.0;
  const numTicks = Math.floor(duration / tickStep) + 1;
  const ticks = Array.from({ length: numTicks }, (_, i) => i * tickStep);

  return (
    <section id="temporal-analysis" className="vl-card" aria-label="Temporal Flaw Analysis">
      <div className="vl-card-header">
        <div className="vl-card-title-group">
          <h2 className="vl-card-title">
            <Clock size={18} style={{ color: 'var(--brand-primary)' }} />
            Temporal Flaw Analysis
          </h2>
          <span className="vl-card-subtitle">
            Millisecond-grounded flaw intervals on total audio duration ({duration.toFixed(2)}s)
          </span>
        </div>
      </div>

      <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
        Interactive timeline highlighting localized delivery irregularities. Click any marked
        interval to inspect acoustic divergence and synchronize audio playback.
      </p>

      {/* Signature Timeline Track */}
      <div className="vl-timeline-canvas" role="region" aria-label="Speech Flaw Timeline Canvas">
        {/* Ruler ticks */}
        <div className="vl-timeline-ruler-ticks" aria-hidden="true">
          {ticks.map((t) => {
            const pct = (t / duration) * 100;
            return (
              <div key={t} className="vl-ruler-tick" style={{ left: `${pct}%` }}>
                <span className="vl-ruler-label">{t.toFixed(1)}s</span>
              </div>
            );
          })}
        </div>

        {/* Live Audio Playhead */}
        <div
          className="vl-timeline-playhead"
          style={{ left: `${playheadPercent}%` }}
          aria-label={`Playback playhead at ${currentTime.toFixed(2)}s`}
        >
          <div className="vl-playhead-cap" />
        </div>

        {/* Flaw Interval Highlights */}
        {processedFlaws.map((flaw) => {
          if (!flaw.isValid) return null;

          const leftPercent = (flaw.start / duration) * 100;
          const widthPercent = ((flaw.end - flaw.start) / duration) * 100;
          const isSelected = selectedFlaw && selectedFlaw.id === flaw.id;
          const severityClass = getSeverityClass(flaw.severity);

          return (
            <div
              key={flaw.id}
              className={`vl-flaw-segment ${severityClass} ${isSelected ? 'selected' : ''}`}
              style={{
                left: `${leftPercent}%`,
                width: `${Math.max(widthPercent, 2.0)}%`,
              }}
              onClick={() => onSelectFlaw(flaw)}
              role="button"
              tabIndex={0}
              title={`${flaw.type.toUpperCase()}: ${flaw.start.toFixed(2)}s – ${flaw.end.toFixed(
                2
              )}s (Severity: ${flaw.severity})`}
            >
              <span className="vl-flaw-segment-title">
                {flaw.type} • {flaw.severity}
              </span>
            </div>
          );
        })}
      </div>

      {/* Diagnostic Warning for Invalid Timestamps if present */}
      {processedFlaws.some((f) => !f.isValid) && (
        <div className="vl-pill demo" style={{ width: '100%', marginBottom: '1rem' }} role="alert">
          <AlertOctagon size={16} />
          <span>
            Timeline warning: Unclamped irregular flaw intervals detected outside audio bounds.
          </span>
        </div>
      )}

      {/* Flaw Quick-Select Cards */}
      <div>
        <div
          style={{
            fontSize: '0.8rem',
            fontWeight: 600,
            color: 'var(--text-muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            marginBottom: '0.5rem',
          }}
        >
          Identified Flaw Segments ({flaws.length})
        </div>

        {flaws.length === 0 ? (
          <div className="vl-empty-state" style={{ padding: '1.5rem' }}>
            <p>No delivery flaws detected in this audio segment.</p>
          </div>
        ) : (
          <div className="vl-flaw-cards-grid">
            {processedFlaws.map((flaw) => {
              const isSelected = selectedFlaw && selectedFlaw.id === flaw.id;
              const sevClass = getSeverityClass(flaw.severity);
              const sevBadgeText =
                flaw.severity >= 0.7 ? 'high' : flaw.severity >= 0.4 ? 'medium' : 'low';

              return (
                <div
                  key={flaw.id}
                  className={`vl-flaw-chip-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => onSelectFlaw(flaw)}
                  role="button"
                  tabIndex={0}
                >
                  <div className="vl-flaw-chip-header">
                    <span className="vl-flaw-chip-type">{flaw.type}</span>
                    <span className={`vl-flaw-severity-badge ${sevBadgeText}`}>
                      {getSeverityLabel(flaw.severity)} ({flaw.severity})
                    </span>
                  </div>

                  <div className="vl-flaw-chip-time">
                    <span>
                      Window: <strong>{flaw.start.toFixed(2)}s – {flaw.end.toFixed(2)}s</strong>
                    </span>
                    <span style={{ color: 'var(--text-muted)' }}>
                      Duration: {(flaw.end - flaw.start).toFixed(2)}s
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}
