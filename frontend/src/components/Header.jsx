import React, { useEffect, useState } from 'react';
import {
  Sparkles,
  RefreshCw,
  Info,
  Award,
  Activity,
  Clock,
  Layers,
} from 'lucide-react';

export default function Header({ onResetDemoData, isDemoData = true }) {
  const [backendHealth, setBackendHealth] = useState({
    status: 'checking',
    label: 'Checking API...',
  });

  const checkHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        setBackendHealth({
          status: 'online',
          label: 'API Connected',
        });
      } else {
        setBackendHealth({
          status: 'offline',
          label: 'API Unavailable',
        });
      }
    } catch (err) {
      setBackendHealth({
        status: 'offline',
        label: 'API Offline',
      });
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="vl-header-wrapper">
      {/* Top Navigation Bar */}
      <nav className="vl-navbar" aria-label="Main Navigation">
        <div className="vl-brand-lockup">
          <div className="vl-logo-mark" aria-hidden="true">
            {/* Custom geometric lens mark */}
            <svg
              width="22"
              height="22"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="9" />
              <circle cx="12" cy="12" r="4" />
              <line x1="12" y1="3" x2="12" y2="7" />
              <line x1="12" y1="17" x2="12" y2="21" />
              <line x1="3" y1="12" x2="7" y2="12" />
              <line x1="17" y1="12" x2="21" y2="12" />
            </svg>
          </div>
          <div className="vl-brand-text">
            <span className="vl-wordmark">
              Vocal<span>Lens</span>
            </span>
            <span className="vl-tagline">AI-Powered Speech Coaching</span>
          </div>
        </div>

        {/* Navigation Anchors */}
        <div className="vl-nav-center">
          <a href="#delivery-score" className="vl-nav-anchor">
            Delivery Score
          </a>
          <a href="#temporal-analysis" className="vl-nav-anchor">
            Temporal Analysis
          </a>
          <a href="#pitch-energy" className="vl-nav-anchor">
            Pitch & Energy
          </a>
        </div>

        {/* Status Indicators & Actions */}
        <div className="vl-nav-right">
          {/* Subtle Backend Connection Status */}
          <span
            className={`vl-pill ${
              backendHealth.status === 'online' ? 'status-online' : 'status-offline'
            }`}
            title="FastAPI Backend Health"
          >
            <span className="vl-status-dot" />
            {backendHealth.label}
          </span>

          {/* Discreet Demo Mode Badge */}
          {isDemoData && (
            <span className="vl-pill demo" title="Illustrative sample dataset loaded">
              Demo Mode
            </span>
          )}

          <button
            type="button"
            className="vl-btn-subtle"
            onClick={onResetDemoData}
            title="Reset dataset to default baseline"
          >
            <RefreshCw size={13} />
            <span>Reset Demo</span>
          </button>
        </div>
      </nav>

      {/* Hero Introduction */}
      <section className="vl-hero-section">
        <div className="vl-hero-header">
          <h1 className="vl-hero-title">
            Understand your delivery. Improve your impact.
          </h1>
          <p className="vl-hero-subtitle">
            Compare speech against a reference, identify delivery issues at precise timestamps,
            and discover actionable ways to improve.
          </p>

          <div className="vl-feature-pills-row">
            <span className="vl-feature-pill">
              <Award size={14} /> Delivery Score
            </span>
            <span className="vl-feature-pill">
              <Clock size={14} /> Temporal Analysis
            </span>
            <span className="vl-feature-pill">
              <Activity size={14} /> Pitch & Energy
            </span>
          </div>
        </div>

        {/* Required Honest Messaging Disclaimer */}
        <div className="vl-disclaimer-banner" role="status">
          <div className="vl-disclaimer-content">
            <Info size={16} style={{ color: 'var(--brand-primary)', flexShrink: 0 }} />
            <span className="vl-disclaimer-text">
              <strong>Notice:</strong> Demo results shown for illustration. Real analysis becomes
              available when the speech-analysis pipeline is integrated.
            </span>
          </div>
        </div>
      </section>
    </header>
  );
}
