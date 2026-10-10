import React, { useState, useRef, useEffect } from 'react';
import {
  UploadCloud,
  Play,
  Pause,
  RotateCcw,
  Volume2,
  FileAudio,
  AlertCircle,
  Clock,
  FileText,
} from 'lucide-react';

const ALLOWED_TYPES = [
  'audio/wav',
  'audio/x-wav',
  'audio/wave',
  'audio/mp3',
  'audio/mpeg',
  'audio/ogg',
  'audio/m4a',
  'audio/x-m4a',
  'audio/flac',
  'audio/webm',
];
const MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024; // 25 MB

function formatSeconds(secs) {
  if (isNaN(secs) || secs < 0) return '0:00.0';
  const mins = Math.floor(secs / 60);
  const remainingSecs = (secs % 60).toFixed(1);
  const padSecs = remainingSecs < 10 ? `0${remainingSecs}` : remainingSecs;
  return `${mins}:${padSecs}`;
}

export default function AudioTranscriptSection({
  meta = {},
  words = [],
  currentTime = 0,
  onTimeUpdate = () => {},
  audioRef = null,
  onSeek = () => {},
}) {
  const [file, setFile] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(meta?.duration || 3.0);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [validationError, setValidationError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [transcriptText, setTranscriptText] = useState(
    words && words.length > 0 ? words.map((w) => w.w).join(' ') : 'we must act now'
  );

  const localAudioRef = useRef(null);
  const activeAudioRef = audioRef || localAudioRef;
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (meta?.duration && !audioUrl) {
      setDuration(meta.duration);
    }
  }, [meta, audioUrl]);

  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  const handleFileValidationAndLoad = (selectedFile) => {
    setValidationError(null);
    if (!selectedFile) return;

    const isAudioType =
      ALLOWED_TYPES.includes(selectedFile.type) ||
      /\.(wav|mp3|ogg|m4a|flac|webm)$/i.test(selectedFile.name);

    if (!isAudioType) {
      setValidationError(
        `Unsupported audio format "${selectedFile.name}". Please upload a WAV, MP3, OGG, FLAC, or M4A file.`
      );
      return;
    }

    if (selectedFile.size > MAX_FILE_SIZE_BYTES) {
      const sizeMB = (selectedFile.size / (1024 * 1024)).toFixed(1);
      setValidationError(
        `File exceeds maximum limit (${sizeMB} MB). Please choose a file under 25 MB.`
      );
      return;
    }

    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }

    const objectUrl = URL.createObjectURL(selectedFile);
    setFile(selectedFile);
    setAudioUrl(objectUrl);
    setIsPlaying(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileValidationAndLoad(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragActive(false);
  };

  const togglePlayPause = () => {
    if (!activeAudioRef.current) return;
    if (isPlaying) {
      activeAudioRef.current.pause();
      setIsPlaying(false);
    } else {
      activeAudioRef.current.play().catch((err) => {
        console.warn('Audio play error:', err);
      });
      setIsPlaying(true);
    }
  };

  const handleAudioTimeUpdate = () => {
    if (activeAudioRef.current) {
      onTimeUpdate(activeAudioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (activeAudioRef.current) {
      const dur = activeAudioRef.current.duration;
      if (!isNaN(dur) && dur > 0) {
        setDuration(dur);
      }
    }
  };

  const handleSpeedChange = (e) => {
    const rate = parseFloat(e.target.value);
    setPlaybackRate(rate);
    if (activeAudioRef.current) {
      activeAudioRef.current.playbackRate = rate;
    }
  };

  return (
    <section className="vl-card" aria-label="Audio Workspace and Transcript">
      <div className="vl-card-header">
        <div className="vl-card-title-group">
          <h2 className="vl-card-title">
            <Volume2 size={18} style={{ color: 'var(--brand-primary)' }} />
            Audio Workspace & Alignment
          </h2>
          <span className="vl-card-subtitle">
            Local browser playback • Synchronized with transcript grounding
          </span>
        </div>
      </div>

      {validationError && (
        <div className="vl-pill demo" style={{ width: '100%', marginBottom: '1rem', padding: '0.6rem 0.8rem' }} role="alert">
          <AlertCircle size={15} style={{ flexShrink: 0 }} />
          <span>{validationError}</span>
        </div>
      )}

      {/* Upload Dropzone */}
      <div
        className={`vl-dropzone ${dragActive ? 'drag-active' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
        role="button"
        tabIndex={0}
      >
        <input
          type="file"
          ref={fileInputRef}
          style={{ display: 'none' }}
          accept="audio/*,.wav,.mp3,.ogg,.m4a,.flac"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              handleFileValidationAndLoad(e.target.files[0]);
            }
          }}
        />
        <div className="vl-dropzone-icon">
          <UploadCloud size={20} />
        </div>
        <div className="vl-dropzone-title">
          {file ? `Loaded: ${file.name}` : 'Select audio file or drag & drop'}
        </div>
        <div className="vl-dropzone-guidance">
          Supported: WAV, MP3, OGG, FLAC up to 25 MB (Local playback)
        </div>
      </div>

      {file && (
        <div className="vl-file-chip">
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 500 }}>
            <FileAudio size={14} style={{ color: 'var(--brand-primary)' }} />
            {file.name} ({(file.size / (1024 * 1024)).toFixed(2)} MB)
          </span>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
            Sampling: {meta.sr ? `${meta.sr / 1000} kHz` : '16 kHz'}
          </span>
        </div>
      )}

      {/* Audio Playback Bar */}
      <div className="vl-audio-player-surface">
        {audioUrl ? (
          <audio
            ref={activeAudioRef}
            src={audioUrl}
            onTimeUpdate={handleAudioTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
            onEnded={() => setIsPlaying(false)}
          />
        ) : (
          <div
            style={{
              fontSize: '0.775rem',
              color: 'var(--text-muted)',
              marginBottom: '0.65rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
          >
            <Clock size={13} style={{ color: 'var(--brand-primary)' }} />
            <span>
              Target sample audio duration:{' '}
              <strong>{(meta.duration || 3.0).toFixed(1)}s</strong>. Load speech to sync
              playback.
            </span>
          </div>
        )}

        <div className="vl-player-controls-row">
          <button
            type="button"
            className="vl-btn-play"
            onClick={togglePlayPause}
            disabled={!audioUrl}
            style={{ opacity: audioUrl ? 1 : 0.6, cursor: audioUrl ? 'pointer' : 'not-allowed' }}
            title={audioUrl ? (isPlaying ? 'Pause' : 'Play') : 'Load an audio file first'}
          >
            {isPlaying ? <Pause size={18} /> : <Play size={18} style={{ marginLeft: 2 }} />}
          </button>

          <button
            type="button"
            className="vl-btn-icon"
            onClick={() => onSeek(0)}
            disabled={!audioUrl}
            style={{ opacity: audioUrl ? 1 : 0.6 }}
            title="Restart playback"
          >
            <RotateCcw size={15} />
          </button>

          <div className="vl-seeker-container">
            <input
              type="range"
              className="vl-range-slider"
              min="0"
              max={duration > 0 ? duration : 3.0}
              step="0.01"
              value={currentTime}
              onChange={(e) => onSeek(parseFloat(e.target.value))}
              disabled={!audioUrl}
            />
            <div className="vl-time-counter">
              <span>{formatSeconds(currentTime)}</span>
              <span>{formatSeconds(duration)}</span>
            </div>
          </div>

          <select
            className="vl-speed-select"
            value={playbackRate}
            onChange={handleSpeedChange}
            disabled={!audioUrl}
            title="Playback Speed"
          >
            <option value="0.5">0.5×</option>
            <option value="0.75">0.75×</option>
            <option value="1">1.0×</option>
            <option value="1.25">1.25×</option>
            <option value="1.5">1.5×</option>
          </select>
        </div>
      </div>

      {/* Aligned Words & Transcript Section */}
      <div>
        <div className="vl-aligned-words-label">
          <span>Aligned Word Tokens</span>
          <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
            Click token to jump timestamp
          </span>
        </div>

        {words && words.length > 0 ? (
          <div className="vl-aligned-words-track">
            {words.map((wObj, idx) => {
              const isCurrent = currentTime >= wObj.start && currentTime <= wObj.end;
              return (
                <button
                  type="button"
                  key={idx}
                  className={`vl-word-pill ${isCurrent ? 'active' : ''}`}
                  onClick={() => onSeek(wObj.start)}
                  title={`"${wObj.w}" (${wObj.start.toFixed(2)}s – ${wObj.end.toFixed(2)}s)`}
                >
                  <span className="vl-word-text">{wObj.w}</span>
                  <span className="vl-word-time">
                    {wObj.start.toFixed(2)}s – {wObj.end.toFixed(2)}s
                  </span>
                </button>
              );
            })}
          </div>
        ) : (
          <div className="vl-empty-state" style={{ padding: '1rem' }}>
            <p>No aligned words in dataset.</p>
          </div>
        )}

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.4rem' }}>
          <FileText size={14} style={{ color: 'var(--text-muted)' }} />
          <span style={{ fontSize: '0.775rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            Reference Transcript
          </span>
        </div>
        <textarea
          className="vl-transcript-textarea"
          value={transcriptText}
          onChange={(e) => setTranscriptText(e.target.value)}
          placeholder="Speech transcript reference..."
          title="Reference transcript text"
        />
      </div>
    </section>
  );
}
