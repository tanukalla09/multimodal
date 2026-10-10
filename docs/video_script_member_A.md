# Video Script — Member A: Dataset Sources, Flaw Injection, and A/B Demo

## Slide / Screen Notes

**[0:00–0:10] — SHOW: repo root / data/ folder tree in file explorer or terminal**

> "Hi, I am Member A and I built the speech dataset for Track C.
> Let me walk you through where the audio comes from, how we inject flaws,
> and what it actually sounds like."

---

**[0:10–0:25] — SHOW: LibriVox webpage (https://librivox.org/the-gettysburg-address-150th-anniversary-by-abraham-lincoln/)**

> "We use two LibriVox readings of the Gettysburg Address — both public domain,
> so we can modify and redistribute them freely.
> Speaker 1 is Ernst Pattynama; speaker 2 is Julia Niedermaier.
> Each recording is trimmed, resampled to 16 kilohertz mono, and
> RMS-normalised to minus 20 dBFS using our prepare.py script."

---

**[0:25–0:45] — SHOW: src/dataset/flaws.py, SEVERITY table highlighted, then configs/sp01_regions.yaml**

> "We have seven flaw types.
> For example, 'volume drop' multiplies the audio by a gain factor — minus 3 dB
> at level 1, minus 18 dB at level 5.
> 'Too fast' uses WSOLA time-stretching: the pitch stays the same but the words
> arrive faster.
> Each flaw is injected into a hand-chosen region defined in a YAML config —
> you can see the start and end times here, aligned to natural pause gaps in the speech."

---

**[0:45–1:05] — SHOW: data/ab/ folder; play sp01_volume_drop_s4_AB.wav in a media player (or Audacity showing the waveform with the two halves)**

> "To make it easy to hear the difference, I generated A/B clips.
> Each clip plays the ideal region first, then 0.8 seconds of silence,
> then the same region with the flaw injected.
> [PAUSE — let the ideal play]
> That was the ideal.
> [PAUSE — let the flawed play]
> And that is volume drop at severity 4 — 12 dB quieter.
> Even without knowing the label, the difference is clear."

---

**[1:05–1:20] — SHOW: data/qc_report.md in a markdown viewer, Summary line highlighted**

> "Every injected flaw passes an objective QC check:
> 49 out of 49 testable instances PASS — duration ratios match the expected
> tempo factor, RMS changes match the expected gain, and silence share confirms
> real pauses were shortened or inserted.
> The only MEASURED entries are erratic_pitch — that flaw wobbles the pitch
> contour, and the expected direction of spread change is ambiguous,
> so I report numbers but flag it for manual listening."

---

**[1:20–1:30] — SHOW: git log --oneline -5 or git status on feature/sp01**

> "All of this is reproducible from the configs: run generate.py with the YAML
> and you get byte-identical labels, and near-identical audio on the same machine.
> Thank you."

---

## Notes for Recording

- Total target: 60 to 90 seconds of speaking.
- The A/B clip to play: `data/ab/sp01_volume_drop_s4_AB.wav`
  (ideal: -19.8 dBFS, flawed: -31.8 dBFS — clearly audible difference).
- Alternatively use `sp01_too_fast_s4_AB.wav` if tempo is more visual on a waveform.
- Confirm speaker sex for sp01 and sp02 before recording; fill the TODO in
  `data/README.md` first.
- Keep the camera on screen for the Audacity waveform demo.
