import React from 'react';
import { Award, Zap, Activity, Volume2, PauseCircle, CheckCircle2 } from 'lucide-react';

const METRIC_CONFIG = {
  pacing: {
    label: 'Pacing & Tempo',
    icon: Zap,
    description: 'Syllabic timing and cadence alignment',
    benchmark: 'Target: 70–85',
  },
  pitch: {
    label: 'Pitch Dynamics',
    icon: Activity,
    description: 'Intonation contour and inflection range',
    benchmark: 'Target: 65–85',
  },
  volume: {
    label: 'Volume & Energy',
    icon: Volume2,
    description: 'Dynamic intensity and loudness stability',
    benchmark: 'Target: 75–90',
  },
  pauses: {
    label: 'Pause Structure',
    icon: PauseCircle,
    description: 'Silent duration and natural phrasing pauses',
    benchmark: 'Target: 70–80',
  },
};

function getScoreTier(score) {
  if (typeof score !== 'number' || isNaN(score)) return 'unknown';
  if (score >= 75) return 'high';
  if (score >= 60) return 'medium';
  return 'low';
}

function getTierLabel(score) {
  if (typeof score !== 'number' || isNaN(score)) return 'N/A';
  if (score >= 80) return 'Optimal Delivery';
  if (score >= 70) return 'Strong Baseline';
  if (score >= 60) return 'Moderate Flaw';
  return 'Requires Focus';
}

export default function ScoreCards({ scores = {} }) {
  if (!scores || Object.keys(scores).length === 0) {
    return (
      <section id="delivery-score" className="vl-card">
        <div className="vl-card-header">
          <div className="vl-card-title-group">
            <h2 className="vl-card-title">Delivery Score Overview</h2>
            <span className="vl-card-subtitle">AI-grounded performance rubrics</span>
          </div>
        </div>
        <div className="vl-empty-state">
          <p>No evaluation scores available in dataset.</p>
        </div>
      </section>
    );
  }

  const rawOverall = scores.overall;
  const overallNum = typeof rawOverall === 'number' ? Math.round(rawOverall) : 0;
  const overallTier = getScoreTier(overallNum);

  // Remaining metric keys in order
  const subMetricKeys = ['pacing', 'pitch', 'volume', 'pauses'].filter(
    (key) => key in scores
  );

  return (
    <section id="delivery-score" aria-label="Delivery Overview">
      <div className="vl-delivery-overview">
        {/* Primary Hero Overall Score Card */}
        <div className="vl-hero-score-card">
          <div className="vl-hero-score-header">
            <span className="vl-hero-score-label">Overall Delivery</span>
            <Award size={20} style={{ color: 'var(--brand-primary)' }} />
          </div>

          <div>
            <div className="vl-hero-score-body">
              <span className="vl-hero-score-number">{overallNum}</span>
              <span className="vl-hero-score-max">/ 100</span>
            </div>

            <span className={`vl-hero-score-badge ${overallTier}`}>
              <CheckCircle2 size={13} />
              {getTierLabel(overallNum)}
            </span>

            <div className="vl-hero-progress-track" aria-hidden="true">
              <div
                className="vl-hero-progress-fill"
                style={{ width: `${Math.min(Math.max(overallNum, 0), 100)}%` }}
              />
            </div>
          </div>

          <div className="vl-hero-score-meta">
            Target reference: <strong>80+</strong>. Composite score computed by contrastive
            alignment of acoustic contours and temporal pause grounding.
          </div>
        </div>

        {/* Secondary Compact 4-Metric Grid */}
        <div className="vl-metrics-grid">
          {subMetricKeys.map((key) => {
            const val = scores[key];
            const numVal = typeof val === 'number' ? Math.round(val) : 0;
            const tier = getScoreTier(numVal);
            const cfg = METRIC_CONFIG[key] || {
              label: key.replace(/_/g, ' '),
              icon: Activity,
              description: 'Speech metric',
              benchmark: 'Dynamic benchmark',
            };
            const Icon = cfg.icon;

            return (
              <div key={key} className="vl-metric-subcard">
                <div>
                  <div className="vl-metric-header">
                    <span className="vl-metric-label">{cfg.label}</span>
                    <Icon
                      size={16}
                      style={{
                        color:
                          tier === 'high'
                            ? 'var(--status-success)'
                            : tier === 'medium'
                            ? 'var(--status-warning)'
                            : 'var(--status-danger)',
                      }}
                    />
                  </div>

                  <div className="vl-metric-value-row">
                    <span className="vl-metric-number">{numVal}</span>
                    <span className={`vl-metric-status ${tier}`}>
                      {getTierLabel(numVal)}
                    </span>
                  </div>

                  <div className="vl-meter-track" aria-hidden="true">
                    <div
                      className={`vl-meter-fill ${tier}`}
                      style={{ width: `${Math.min(Math.max(numVal, 0), 100)}%` }}
                    />
                  </div>
                </div>

                <div className="vl-metric-desc">
                  {cfg.description} • {cfg.benchmark}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
