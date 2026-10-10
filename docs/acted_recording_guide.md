# Acted Recording Guide — Human Flaw Dataset (Track C)

This guide explains how teammates record and label naturalistic, acted speech recordings for held-out evaluation.

---

## 1. Clean Reference Recording (Ideal Take)

Before recording flawed versions, the speaker must record one clean, natural reference reading:

- **Environment**: Quiet room with minimal reverberation (no fan, AC noise, or background music).
- **Microphone**: Phone or dedicated microphone placed 15–20 cm from the mouth, slightly off-axis to avoid plosives.
- **Audio format**: 16 kHz or higher (e.g. 44.1 kHz / 48 kHz 16-bit PCM WAV or lossless format), mono or stereo.
- **Length**: One continuous take of 60 to 90 seconds, read naturally from the reference transcript.
- **Save path**: Save as `data/raw/spXX_ideal.wav` after running `src/dataset/prepare.py` on the raw capture.

---

## 2. Recording the Acted Flaw Set

For each speaker, record deliberate acted flaw takes of the **same transcript**.

### Flaw Takes (7 single + 1 combined):

Read the full text (or the relevant paragraph) once for each take, acting the flaw in a noticeable region:

1. **`too_fast`**: Speak noticeably rushed/hurried across one or two phrases.
2. **`too_slow`**: Speak noticeably sluggish, dragging out words across one or two phrases.
3. **`monotone`**: Speak with an unnaturally flat, robotic, expressionless pitch contour across a sentence.
4. **`erratic_pitch`**: Speak with an unsteady, wavering, erratic intonation across a sentence.
5. **`volume_drop`**: Noticeably drop voice volume/loudness to a quiet whisper-like level for a phrase.
6. **`long_pause`**: Insert an awkward, unnaturally long silence (1.5–2.5 s) between phrases.
7. **`missing_pause`**: Rapidly rush through a punctuation boundary where a natural breath pause belongs.
8. **`combined`**: Act two or three flaws in distinct sections of the same take.

### File Naming Convention

Save audio files directly in `data/acted/`:
- `data/acted/spXX_acted_<flaw>.wav`
  - Examples: `sp03_acted_too_fast.wav`, `sp03_acted_monotone.wav`, `sp03_acted_combined.wav`

---

## 3. Labelling Flaw Regions in Audacity

1. Open the recorded WAV file in **Audacity**.
2. Select the audio interval where the flaw was acted.
3. Add a label: **Edit > Labels > Add Label at Selection** (shortcut: `Ctrl + B`).
4. Set the label text to the **exact flaw name** in lowercase:
   - Allowed values: `too_fast`, `too_slow`, `monotone`, `erratic_pitch`, `volume_drop`, `long_pause`, `missing_pause`
5. Export labels: **File > Export > Export Labels...** and save as `labels.txt`.
   - Audacity exports a tab-delimited text file with format: `start_s<TAB>end_s<TAB>flaw_type`.

---

## 4. Converting Audacity Labels to Dataset JSON

Run the conversion utility `src/dataset/audacity_to_labels.py`:

```bash
python src/dataset/audacity_to_labels.py <txt> <wav> <speech_id> [--severity 3]
```

**Real arguments**:
- `txt`: Path to the exported Audacity label file (e.g. `labels.txt`).
- `wav`: Path to the acted audio file (e.g. `data/acted/sp03_acted_monotone.wav`).
- `speech_id`: Speaker identifier string (e.g. `sp03`).
- `--severity`: Perceived severity level integer 1–5 (default: `3`).

The script verifies flaw types against the approved set, measures duration and sample rate, and outputs the final label document to `data/acted/spXX_acted_<flaw>.json`.

---

## 5. Held-Out Evaluation Set Rule

> [!IMPORTANT]
> **The acted recordings form a strict held-out evaluation test set.**
> Teammates developing speech feature extractors, contrastive grounding models, or anomaly detectors
> **MUST NOT** use the `data/acted/` recordings to fit model parameters, tune detection thresholds,
> or adjust hyperparameters. These files are reserved exclusively for final benchmark testing.

---

## 6. Source Text Notes for Speech 3

- **Public-domain source text**: Swami Vivekananda's welcome address at the Parliament of the World's Religions, Chicago, 11 September 1893.
- **Text excerpt**:
  TODO: fetch the exact public-domain text from https://www.artic.edu/articles/710/sisters-and-brothers-of-america-swami-vivekananda-in-chicago and choose an excerpt of 150 to 220 words.
- **Audio authenticity note**:
  No authentic audio recording of Swami Vivekananda's voice exists; no audio claiming to be a recording of his voice exists or may be used. The speech must be read aloud by a project teammate.
