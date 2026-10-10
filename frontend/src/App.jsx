import React, { useState, useRef, useEffect } from 'react';
import Header from './components/Header';
import ScoreCards from './components/ScoreCards';
import AudioTranscriptSection from './components/AudioTranscriptSection';
import TemporalFlaws from './components/TemporalFlaws';
import FlawDetailsPanel from './components/FlawDetailsPanel';
import FeatureVisualizations from './components/FeatureVisualizations';
import demoOutput from './data/sample_output.json';
import './App.css';

export default function App() {
  const [data, setData] = useState(demoOutput);
  const [selectedFlaw, setSelectedFlaw] = useState(
    demoOutput.flaws && demoOutput.flaws.length > 0
      ? { ...demoOutput.flaws[0], id: 0 }
      : null
  );
  const [currentTime, setCurrentTime] = useState(0);
  const audioRef = useRef(null);

  // Synchronize with FastAPI backend if online, otherwise preserve bundled contract
  useEffect(() => {
    async function fetchBackendData() {
      try {
        const response = await fetch('http://localhost:8000/sample-output');
        if (response.ok) {
          const remoteData = await response.json();
          setData(remoteData);
          if (remoteData.flaws && remoteData.flaws.length > 0) {
            setSelectedFlaw({ ...remoteData.flaws[0], id: 0 });
          }
        }
      } catch (err) {
        // Backend offline; fallback to bundled sample_output.json
      }
    }
    fetchBackendData();
  }, []);

  const handleSelectFlaw = (flaw) => {
    setSelectedFlaw(flaw);
    if (flaw && typeof flaw.start === 'number') {
      handleSeek(flaw.start);
    }
  };

  const handleSeek = (timeSec) => {
    setCurrentTime(timeSec);
    if (audioRef.current) {
      audioRef.current.currentTime = timeSec;
    }
  };

  const handleResetDemoData = () => {
    setData(demoOutput);
    if (demoOutput.flaws && demoOutput.flaws.length > 0) {
      setSelectedFlaw({ ...demoOutput.flaws[0], id: 0 });
    } else {
      setSelectedFlaw(null);
    }
    handleSeek(0);
  };

  return (
    <div className="vl-app-container">
      {/* Product Branding, Navigation, Hero, and Honest Messaging */}
      <Header
        onResetDemoData={handleResetDemoData}
        isDemoData={true}
      />

      <main className="vl-dashboard-grid">
        {/* Delivery Overview: Overall Hero Score + 4-Metric Grid */}
        <ScoreCards scores={data.scores} />

        {/* Audio Workspace & Flaw Diagnostic Inspector */}
        <div className="vl-two-column-grid">
          <AudioTranscriptSection
            meta={data.meta}
            words={data.words}
            currentTime={currentTime}
            onTimeUpdate={setCurrentTime}
            audioRef={audioRef}
            onSeek={handleSeek}
          />

          <FlawDetailsPanel
            selectedFlaw={selectedFlaw}
            onSeek={handleSeek}
          />
        </div>

        {/* Signature Temporal Flaw Analysis Timeline */}
        <TemporalFlaws
          flaws={data.flaws || []}
          meta={data.meta || {}}
          selectedFlaw={selectedFlaw}
          onSelectFlaw={handleSelectFlaw}
          currentTime={currentTime}
        />

        {/* Contrastive Feature Time-Series Contours */}
        <FeatureVisualizations
          features={data.features || {}}
          baselineFeatures={data.baseline_features || {}}
        />
      </main>

      {/* Minimal Product Footer */}
      <footer className="vl-footer">
        <div>
          <span className="vl-footer-brand">VocalLens</span> — AI-powered speech coaching.
        </div>
        <div>
          Understand your delivery. Improve your impact.
        </div>
      </footer>
    </div>
  );
}
