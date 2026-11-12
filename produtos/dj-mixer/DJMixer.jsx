import React, { useEffect, useReducer, useRef, useState } from "react";

/* ==========================================================================
   Mesa de mixagem de dois decks, feita com Web Audio API.
   Arquivo único e sem dependências além do React, para colar como página
   em um app Base44 (ou em qualquer projeto React).
   ========================================================================== */

const PPS = 150; // quadros de análise por segundo de áudio
const LOW_X = 250; // corte grave/médio do isolador (Hz)
const HIGH_X = 2500; // corte médio/agudo do isolador (Hz)
const BUTTER_DB = 20 * Math.log10(Math.SQRT1_2); // Q Butterworth em dB
const LOOP_SIZES = [0.5, 1, 2, 4, 8, 16];
const PITCH_RANGES = [0.08, 0.16, 0.5];

const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

function fmtTime(s) {
  if (!isFinite(s) || s < 0) s = 0;
  const m = Math.floor(s / 60);
  const r = s - m * 60;
  return `${String(m).padStart(2, "0")}:${r.toFixed(1).padStart(4, "0")}`;
}

/* ----------------------------- Análise ---------------------------------- */

// Extrai picos da forma de onda (geral e graves), BPM e posição da 1ª batida.
function analyzeBuffer(buffer) {
  const sr = buffer.sampleRate;
  const n = buffer.length;
  const c0 = buffer.getChannelData(0);
  const c1 = buffer.numberOfChannels > 1 ? buffer.getChannelData(1) : null;
  const hop = sr / PPS;
  const frames = Math.max(1, Math.ceil(n / hop));
  const peaks = new Float32Array(frames);
  const lows = new Float32Array(frames);
  const eLow = new Float32Array(frames);
  const eAll = new Float32Array(frames);
  const a = 1 - Math.exp((-2 * Math.PI * 160) / sr);
  let lp = 0;
  for (let f = 0; f < frames; f++) {
    const s0 = Math.floor(f * hop);
    const s1 = Math.min(n, Math.floor((f + 1) * hop));
    let pk = 0, lpk = 0, el = 0, ea = 0;
    for (let i = s0; i < s1; i++) {
      const x = c1 ? (c0[i] + c1[i]) * 0.5 : c0[i];
      lp += a * (x - lp);
      const ax = x < 0 ? -x : x;
      const al = lp < 0 ? -lp : lp;
      if (ax > pk) pk = ax;
      if (al > lpk) lpk = al;
      el += lp * lp;
      ea += x * x;
    }
    peaks[f] = pk;
    lows[f] = lpk;
    eLow[f] = el;
    eAll[f] = ea;
  }

  // Envelope de ataques: subida da energia (em log), com peso maior no grave.
  const onset = new Float32Array(frames);
  let mean = 0;
  for (let f = 1; f < frames; f++) {
    const dl = Math.log(1 + 200 * eLow[f]) - Math.log(1 + 200 * eLow[f - 1]);
    const da = Math.log(1 + 50 * eAll[f]) - Math.log(1 + 50 * eAll[f - 1]);
    const v = Math.max(0, dl) + 0.4 * Math.max(0, da);
    onset[f] = v;
    mean += v;
  }
  mean /= frames;

  let bpm = 0;
  let firstBeat = 0;
  if (frames > PPS * 8 && mean > 1e-6) {
    // 1) Autocorrelação para achar o período aproximado (85 a 175 BPM).
    const minLag = Math.floor((60 / 175) * PPS);
    const maxLag = Math.ceil((60 / 85) * PPS);
    const ac = new Float32Array(maxLag * 2 + 2);
    for (let lag = minLag; lag <= maxLag * 2 + 1; lag++) {
      let s = 0;
      for (let i = lag; i < frames; i++) s += onset[i] * onset[i - lag];
      ac[lag] = s / (frames - lag);
    }
    let bestLag = minLag, bestScore = -1;
    for (let lag = minLag; lag <= maxLag; lag++) {
      const sc = ac[lag] + 0.5 * ac[lag * 2];
      if (sc > bestScore) { bestScore = sc; bestLag = lag; }
    }
    // 2) Refino fino: histograma de fase ao longo da faixa inteira.
    const idx = [];
    for (let f = 0; f < frames; f++) if (onset[f] > mean * 1.5) idx.push(f);
    const BINS = 48;
    const hist = new Float32Array(BINS);
    const score = (period) => {
      hist.fill(0);
      for (let k = 0; k < idx.length; k++) {
        const f = idx[k];
        const ph = (f / period) % 1;
        hist[(ph * BINS) | 0] += onset[f];
      }
      let mx = 0, mi = 0;
      for (let b = 0; b < BINS; b++) {
        const v = hist[b] + 0.5 * (hist[(b + 1) % BINS] + hist[(b + BINS - 1) % BINS]);
        if (v > mx) { mx = v; mi = b; }
      }
      return [mx, mi];
    };
    const b0 = (60 * PPS) / bestLag;
    let bestBpm = b0, top = -1;
    for (let b = b0 * 0.975; b <= b0 * 1.025; b += 0.01) {
      const [sc] = score((60 * PPS) / b);
      if (sc > top) { top = sc; bestBpm = b; }
    }
    // Faixas de pista quase sempre têm BPM inteiro: arredonda se estiver colado.
    const rounded = Math.round(bestBpm);
    if (Math.abs(bestBpm - rounded) < 0.06) {
      const [sc] = score((60 * PPS) / rounded);
      if (sc > top * 0.97) bestBpm = rounded;
    }
    bpm = Math.round(bestBpm * 100) / 100;
    // 3) Fase: centro de massa dos ataques em volta do melhor ponto.
    const period = (60 * PPS) / bpm;
    const [, bin] = score(period);
    const center = (bin + 0.5) / BINS;
    let sw = 0, sp = 0;
    for (let k = 0; k < idx.length; k++) {
      const f = idx[k];
      let d = ((f / period) % 1) - center;
      if (d > 0.5) d -= 1;
      if (d < -0.5) d += 1;
      if (Math.abs(d) < 0.06) { sw += onset[f]; sp += onset[f] * d; }
    }
    let phase = center + (sw > 0 ? sp / sw : 0);
    phase = ((phase % 1) + 1) % 1;
    // O ataque é medido no quadro seguinte ao início do som.
    firstBeat = Math.max(0, ((phase * period - 0.5) / PPS));
    const beatLen = 60 / bpm;
    firstBeat = firstBeat % beatLen;
  }
  return { peaks, lows, bpm, firstBeat, duration: buffer.duration };
}

/* ----------------------------- Batida demo ------------------------------ */

function makeDemoBuffer(ctx, bpm, rootHz) {
  const sr = ctx.sampleRate;
  const beat = 60 / bpm;
  const patLen = Math.round(16 * beat * sr);
  const pat = new Float32Array(patLen);
  const add = (start, dur, fn) => {
    const s0 = Math.round(start * sr);
    const len = Math.round(dur * sr);
    for (let i = 0; i < len; i++) pat[(s0 + i) % patLen] += fn(i / sr, i);
  };
  let seed = Math.round(bpm * 1000 + rootHz);
  const rnd = () => {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    return seed / 2147483648 - 1;
  };
  const semis = [0, 0, 3, 5];
  for (let b = 0; b < 16; b++) {
    const t0 = b * beat;
    const bar = Math.floor(b / 4);
    const note = rootHz * Math.pow(2, semis[bar] / 12);
    // bumbo
    let ph = 0;
    add(t0, 0.32, (t) => {
      ph += (2 * Math.PI * (44 + 120 * Math.exp(-t * 32))) / sr;
      return Math.sin(ph) * Math.exp(-t * 8) * 0.95;
    });
    // chimbal no contratempo
    let prev = 0;
    add(t0 + beat / 2, 0.08, (t) => {
      const nz = rnd();
      const v = (nz - prev) * 0.5;
      prev = nz;
      return v * Math.exp(-t * 55) * 0.4;
    });
    // palma nos tempos 2 e 4
    if (b % 2 === 1) {
      let p2 = 0;
      add(t0, 0.16, (t) => {
        const nz = rnd();
        p2 += 0.35 * (nz - p2);
        return p2 * Math.exp(-t * 22) * 0.55;
      });
    }
    // baixo em colcheias fora do tempo
    for (const off of [0.5, 0.75]) {
      add(t0 + beat * off, beat * 0.22, (t) => {
        const env = Math.min(1, t * 200) * Math.exp(-t * 7);
        return (Math.sin(2 * Math.PI * note * t) + 0.4 * Math.sin(4 * Math.PI * note * t)) * env * 0.32;
      });
    }
    // acorde no início do compasso e na síncope
    if (b % 4 === 0 || b % 4 === 2) {
      const st = b % 4 === 0 ? t0 : t0 + beat * 0.5;
      add(st, 0.5, (t) => {
        const f = note * 8;
        const s = Math.sin(2 * Math.PI * f * t) + Math.sin(2 * Math.PI * f * 1.1892 * t) + Math.sin(2 * Math.PI * f * 1.4983 * t);
        return s * Math.exp(-t * 7) * 0.07;
      });
    }
  }
  const reps = 14;
  const buf = ctx.createBuffer(1, patLen * reps, sr);
  const out = buf.getChannelData(0);
  for (let r = 0; r < reps; r++) {
    const o = r * patLen;
    for (let i = 0; i < patLen; i++) out[o + i] = Math.tanh(pat[i] * 0.9);
  }
  return buf;
}

/* ----------------------------- Motor de áudio --------------------------- */

const eqGain = (v) => (v <= 0.5 ? Math.pow(v * 2, 2.2) : Math.pow(10, ((v - 0.5) * 2 * 6) / 20));

class DeckEngine {
  constructor(engine, id) {
    this.engine = engine;
    this.id = id;
    const ctx = (this.ctx = engine.ctx);
    this.listeners = new Set();

    this.buffer = null;
    this.analysis = null;
    this.title = "";
    this.loading = false;
    this.error = "";
    this.playing = false;
    this.anchorPos = 0;
    this.anchorTime = 0;
    this.pitch = 0;
    this.bend = 0;
    this.pitchRange = PITCH_RANGES[0];
    this.cuePoint = 0;
    this.cuePreview = false;
    this.hotCues = [null, null, null, null];
    this.loop = null;
    this.eq = { low: 0.5, mid: 0.5, high: 0.5 };
    this.kill = { low: false, mid: false, high: false };
    this.trim = 0;
    this.filter = 0;
    this.volume = 1;
    this.synced = false;

    const bq = (type, f) => {
      const n = ctx.createBiquadFilter();
      n.type = type;
      n.frequency.value = f;
      n.Q.value = BUTTER_DB;
      return n;
    };
    const chain = (...nodes) => {
      for (let i = 0; i < nodes.length - 1; i++) nodes[i].connect(nodes[i + 1]);
      return nodes[nodes.length - 1];
    };

    // Isolador de 3 bandas com cruzamentos Linkwitz-Riley de 4ª ordem:
    // as bandas somam plano e o kill realmente zera a banda.
    this.input = ctx.createGain();
    this.bandGain = { low: ctx.createGain(), mid: ctx.createGain(), high: ctx.createGain() };
    const sum = ctx.createGain();
    const lowPre = chain(this.input, bq("lowpass", LOW_X), bq("lowpass", LOW_X));
    chain(lowPre, bq("lowpass", HIGH_X), bq("lowpass", HIGH_X), this.bandGain.low);
    chain(lowPre, bq("highpass", HIGH_X), bq("highpass", HIGH_X), this.bandGain.low);
    const upper = chain(this.input, bq("highpass", LOW_X), bq("highpass", LOW_X));
    chain(upper, bq("lowpass", HIGH_X), bq("lowpass", HIGH_X), this.bandGain.mid);
    chain(upper, bq("highpass", HIGH_X), bq("highpass", HIGH_X), this.bandGain.high);
    this.bandGain.low.connect(sum);
    this.bandGain.mid.connect(sum);
    this.bandGain.high.connect(sum);

    this.fLow = ctx.createBiquadFilter();
    this.fLow.type = "lowpass";
    this.fLow.frequency.value = 22000;
    this.fLow.Q.value = 0;
    this.fHigh = ctx.createBiquadFilter();
    this.fHigh.type = "highpass";
    this.fHigh.frequency.value = 10;
    this.fHigh.Q.value = 0;
    this.fader = ctx.createGain();
    this.meter = ctx.createAnalyser();
    this.meter.fftSize = 1024;
    this.xfade = ctx.createGain();
    chain(sum, this.fLow, this.fHigh, this.fader, this.xfade, engine.bus);
    this.fader.connect(this.meter);
  }

  subscribe(fn) {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }
  emit() {
    this.listeners.forEach((fn) => fn());
  }

  get bpm() {
    return this.analysis ? this.analysis.bpm : 0;
  }
  get rate() {
    return (1 + this.pitch) * (1 + this.bend);
  }
  get liveBpm() {
    return this.bpm * (1 + this.pitch);
  }
  get duration() {
    return this.buffer ? this.buffer.duration : 0;
  }

  position() {
    if (!this.playing) return this.anchorPos;
    let p = this.anchorPos + (this.ctx.currentTime - this.anchorTime) * this.rate;
    const L = this.loop;
    if (L && p >= L.end) p = L.start + ((p - L.start) % (L.end - L.start));
    return Math.min(p, this.duration);
  }

  async loadFile(file, cached) {
    this.loading = true;
    this.error = "";
    this.emit();
    try {
      const ab = await file.arrayBuffer();
      const buf = await this.ctx.decodeAudioData(ab);
      await new Promise((r) => setTimeout(r, 0));
      const analysis = cached || analyzeBuffer(buf);
      this.setBuffer(buf, file.name.replace(/\.[^.]+$/, ""), analysis);
      return analysis;
    } catch (e) {
      this.loading = false;
      this.error = "Não consegui abrir esse arquivo. Tente MP3, WAV, M4A, OGG ou FLAC.";
      this.emit();
      return null;
    }
  }

  setBuffer(buf, title, analysis) {
    this._stopSource();
    this.playing = false;
    this.buffer = buf;
    this.analysis = analysis || analyzeBuffer(buf);
    this.title = title;
    this.loading = false;
    this.error = "";
    this.anchorPos = 0;
    this.cuePoint = 0;
    this.hotCues = [null, null, null, null];
    this.loop = null;
    this.pitch = 0;
    this.bend = 0;
    this.synced = false;
    this.emit();
  }

  _startSource(offset) {
    const ctx = this.ctx;
    const src = ctx.createBufferSource();
    src.buffer = this.buffer;
    src.playbackRate.value = this.rate;
    if (this.loop) {
      src.loop = true;
      src.loopStart = this.loop.start;
      src.loopEnd = this.loop.end;
    }
    const env = ctx.createGain();
    env.gain.setValueAtTime(0, ctx.currentTime);
    env.gain.linearRampToValueAtTime(1, ctx.currentTime + 0.004);
    src.connect(env).connect(this.input);
    src.onended = () => {
      if (this.source !== src) return;
      this.source = null;
      this.playing = false;
      this.anchorPos = 0;
      this.emit();
    };
    src.start(0, clamp(offset, 0, Math.max(0, this.duration - 0.01)));
    this.source = src;
    this.env = env;
    this.anchorPos = offset;
    this.anchorTime = ctx.currentTime;
  }

  _stopSource() {
    const src = this.source;
    if (!src) return;
    this.source = null;
    const t = this.ctx.currentTime;
    try {
      this.env.gain.cancelScheduledValues(t);
      this.env.gain.setValueAtTime(this.env.gain.value, t);
      this.env.gain.linearRampToValueAtTime(0, t + 0.006);
      src.stop(t + 0.01);
    } catch (e) {
      /* já parado */
    }
  }

  play() {
    if (!this.buffer || this.playing) return;
    this.engine.resume();
    this._startSource(this.anchorPos);
    this.playing = true;
    this.emit();
  }

  pause() {
    if (!this.playing) return;
    const p = this.position();
    this._stopSource();
    this.playing = false;
    this.anchorPos = p;
    this.emit();
  }

  toggle() {
    if (this.playing) this.pause();
    else this.play();
  }

  seek(pos) {
    if (!this.buffer) return;
    pos = clamp(pos, 0, Math.max(0, this.duration - 0.02));
    if (this.loop && (pos < this.loop.start || pos >= this.loop.end)) this.loop = null;
    if (this.playing) {
      this._stopSource();
      this._startSource(pos);
    } else {
      this.anchorPos = pos;
    }
    this.emit();
  }

  _applyRate() {
    if (this.playing && this.source) {
      this.anchorPos = this.position();
      this.anchorTime = this.ctx.currentTime;
      this.source.playbackRate.setValueAtTime(this.rate, this.ctx.currentTime);
    }
  }

  setPitch(p, keepSync) {
    this.pitch = clamp(p, -this.pitchRange, this.pitchRange);
    if (!keepSync) this.synced = false;
    this._applyRate();
    this.emit();
  }

  setBend(b) {
    this.bend = b;
    this._applyRate();
  }

  cyclePitchRange() {
    const i = PITCH_RANGES.indexOf(this.pitchRange);
    this.pitchRange = PITCH_RANGES[(i + 1) % PITCH_RANGES.length];
    this.setPitch(this.pitch, true);
  }

  // CUE no estilo dos CDJs.
  cueDown() {
    if (!this.buffer) return;
    if (this.playing && !this.cuePreview) {
      this.pause();
      this.seek(this.cuePoint);
    } else if (!this.playing) {
      if (Math.abs(this.position() - this.cuePoint) > 0.02) {
        this.cuePoint = this.position();
        this.emit();
      } else {
        this.cuePreview = true;
        this.play();
      }
    }
  }
  cueUp() {
    if (!this.cuePreview) return;
    this.cuePreview = false;
    this.pause();
    this.seek(this.cuePoint);
  }

  hotCue(i, erase) {
    if (!this.buffer) return;
    if (erase) this.hotCues[i] = null;
    else if (this.hotCues[i] == null) this.hotCues[i] = this.position();
    else {
      this.seek(this.hotCues[i]);
      return;
    }
    this.emit();
  }

  toggleLoop(beats) {
    if (!this.buffer) return;
    if (this.loop && this.loop.beats === beats) {
      this.exitLoop();
      return;
    }
    const beatLen = 60 / (this.bpm || 120);
    let start;
    if (this.loop) start = this.loop.start;
    else {
      const pos = this.position();
      start = this.bpm ? this.analysis.firstBeat + Math.round((pos - this.analysis.firstBeat) / beatLen) * beatLen : pos;
      start = Math.max(0, start);
    }
    const end = Math.min(this.duration, start + beats * beatLen);
    if (end - start < 0.03) return;
    if (this.playing) {
      this.anchorPos = this.position();
      this.anchorTime = this.ctx.currentTime;
    }
    this.loop = { start, end, beats };
    if (this.source) {
      this.source.loopStart = start;
      this.source.loopEnd = end;
      this.source.loop = true;
    }
    this.emit();
  }

  exitLoop() {
    if (!this.loop) return;
    if (this.playing) {
      this.anchorPos = this.position();
      this.anchorTime = this.ctx.currentTime;
    }
    this.loop = null;
    if (this.source) this.source.loop = false;
    this.emit();
  }

  _applyBand(band) {
    const g = this.kill[band] ? 0 : eqGain(this.eq[band]);
    this.bandGain[band].gain.setTargetAtTime(g, this.ctx.currentTime, 0.008);
  }
  setEq(band, v) {
    this.eq[band] = clamp(v, 0, 1);
    this._applyBand(band);
    this.emit();
  }
  setKill(band, on) {
    this.kill[band] = on;
    this._applyBand(band);
    this.emit();
  }
  setTrim(db) {
    this.trim = clamp(db, -12, 12);
    this.input.gain.setTargetAtTime(Math.pow(10, this.trim / 20), this.ctx.currentTime, 0.01);
    this.emit();
  }
  setVolume(v) {
    this.volume = clamp(v, 0, 1);
    this.fader.gain.setTargetAtTime(this.volume * this.volume, this.ctx.currentTime, 0.01);
    this.emit();
  }
  // Um botão só: para a esquerda fecha os agudos, para a direita corta os graves.
  setFilter(v) {
    this.filter = clamp(v, -1, 1);
    const t = this.ctx.currentTime;
    const amt = Math.abs(this.filter);
    const active = amt > 0.04;
    const lp = active && this.filter < 0 ? 20000 * Math.pow(120 / 20000, amt) : 22000;
    const hp = active && this.filter > 0 ? 20 * Math.pow(9000 / 20, amt) : 10;
    this.fLow.frequency.setTargetAtTime(lp, t, 0.015);
    this.fHigh.frequency.setTargetAtTime(hp, t, 0.015);
    this.fLow.Q.setTargetAtTime(active && this.filter < 0 ? 5 : 0, t, 0.015);
    this.fHigh.Q.setTargetAtTime(active && this.filter > 0 ? 5 : 0, t, 0.015);
    this.emit();
  }

  // Iguala o andamento ao outro deck e alinha a fase das batidas.
  syncTo(other) {
    if (!this.bpm || !other.bpm) return false;
    const target = other.liveBpm;
    let ratio = target / this.bpm;
    for (const r of [ratio * 2, ratio / 2]) if (Math.abs(r - 1) < Math.abs(ratio - 1)) ratio = r;
    const need = Math.abs(ratio - 1);
    const fit = PITCH_RANGES.find((r) => r >= need - 1e-9 && r >= this.pitchRange);
    if (!fit) return false;
    this.pitchRange = fit;
    this.setPitch(ratio - 1, true);
    this.synced = true;
    if (this.playing && other.playing) {
      const bl = 60 / this.bpm;
      const obl = 60 / other.bpm;
      const mine = (((this.position() - this.analysis.firstBeat) / bl) % 1 + 1) % 1;
      const theirs = (((other.position() - other.analysis.firstBeat) / obl) % 1 + 1) % 1;
      let d = theirs - mine;
      if (d > 0.5) d -= 1;
      if (d < -0.5) d += 1;
      if (Math.abs(d) > 0.004) this.seek(this.position() + d * bl);
    }
    this.emit();
    return true;
  }

  level() {
    const buf = this._lv || (this._lv = new Float32Array(this.meter.fftSize));
    this.meter.getFloatTimeDomainData(buf);
    let pk = 0;
    for (let i = 0; i < buf.length; i++) {
      const v = buf[i] < 0 ? -buf[i] : buf[i];
      if (v > pk) pk = v;
    }
    return pk;
  }
}

class Engine {
  constructor() {
    const AC = window.AudioContext || window.webkitAudioContext;
    const ctx = (this.ctx = new AC({ latencyHint: "interactive" }));
    this.bus = ctx.createGain();
    this.master = ctx.createGain();
    this.master.gain.value = 0.8 * 0.8;
    this.masterValue = 0.8;
    const lim = ctx.createDynamicsCompressor();
    lim.threshold.value = -2;
    lim.knee.value = 0;
    lim.ratio.value = 20;
    lim.attack.value = 0.002;
    lim.release.value = 0.12;
    this.meter = ctx.createAnalyser();
    this.meter.fftSize = 1024;
    this.bus.connect(this.master).connect(lim).connect(ctx.destination);
    lim.connect(this.meter);
    this.limiter = lim;
    this.decks = { A: new DeckEngine(this, "A"), B: new DeckEngine(this, "B") };
    this.crossfader = 0;
    this.setCrossfader(0);
  }
  resume() {
    if (this.ctx.state !== "running") this.ctx.resume();
  }
  other(id) {
    return this.decks[id === "A" ? "B" : "A"];
  }
  setCrossfader(x) {
    this.crossfader = clamp(x, -1, 1);
    const t = ((this.crossfader + 1) / 2) * (Math.PI / 2);
    const now = this.ctx.currentTime;
    this.decks.A.xfade.gain.setTargetAtTime(Math.cos(t), now, 0.008);
    this.decks.B.xfade.gain.setTargetAtTime(Math.sin(t), now, 0.008);
  }
  // Troca de grave: passa a linha de baixo de um deck para o outro de uma vez.
  swapBass() {
    const { A, B } = this.decks;
    let a = A.kill.low, b = B.kill.low;
    if (a === b) { a = this.crossfader > 0; b = !a; } else { a = !a; b = !b; }
    A.setKill("low", a);
    B.setKill("low", b);
  }
  setMaster(v) {
    this.masterValue = clamp(v, 0, 1);
    this.master.gain.setTargetAtTime(this.masterValue * this.masterValue, this.ctx.currentTime, 0.01);
  }
  level() {
    const buf = this._lv || (this._lv = new Float32Array(this.meter.fftSize));
    this.meter.getFloatTimeDomainData(buf);
    let pk = 0;
    for (let i = 0; i < buf.length; i++) {
      const v = buf[i] < 0 ? -buf[i] : buf[i];
      if (v > pk) pk = v;
    }
    return pk;
  }
  startRecording() {
    if (this.recorder || typeof MediaRecorder === "undefined") return false;
    if (!this.recDest) {
      this.recDest = this.ctx.createMediaStreamDestination();
      this.limiter.connect(this.recDest);
    }
    const types = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4"];
    const mime = types.find((t) => MediaRecorder.isTypeSupported(t));
    const rec = new MediaRecorder(this.recDest.stream, mime ? { mimeType: mime, audioBitsPerSecond: 256000 } : undefined);
    this.chunks = [];
    rec.ondataavailable = (e) => e.data.size && this.chunks.push(e.data);
    rec.start(1000);
    this.recorder = rec;
    return true;
  }
  stopRecording() {
    return new Promise((resolve) => {
      const rec = this.recorder;
      if (!rec) return resolve(null);
      rec.onstop = () => {
        this.recorder = null;
        resolve(new Blob(this.chunks, { type: rec.mimeType || "audio/webm" }));
      };
      rec.stop();
    });
  }
}

/* ----------------------------- Atalhos ---------------------------------- */

const DECK_ACTIONS = [
  ["play", "Tocar / pausar"],
  ["cue", "CUE"],
  ["sync", "SYNC"],
  ["killLow", "Kill grave"],
  ["killMid", "Kill médio"],
  ["killHigh", "Kill agudo"],
  ["cue1", "Hot cue 1"],
  ["cue2", "Hot cue 2"],
  ["cue3", "Hot cue 3"],
  ["cue4", "Hot cue 4"],
  ["loop4", "Loop de 4 batidas"],
  ["bendDown", "Atrasar (segurar)"],
  ["bendUp", "Adiantar (segurar)"],
];
const MIX_ACTIONS = [
  ["swap", "Troca de grave"],
  ["xfLeft", "Crossfader para A"],
  ["xfRight", "Crossfader para B"],
  ["xfCenter", "Crossfader no centro"],
];
const KEY_GROUPS = [
  ["Deck A", DECK_ACTIONS.map(([k, l]) => ["A." + k, l])],
  ["Deck B", DECK_ACTIONS.map(([k, l]) => ["B." + k, l])],
  ["Mixer", MIX_ACTIONS.map(([k, l]) => ["mix." + k, l])],
];
const DEFAULT_KEYS = {
  "A.play": "KeyQ", "A.cue": "KeyW", "A.sync": "KeyE",
  "A.killLow": "KeyA", "A.killMid": "KeyS", "A.killHigh": "KeyD",
  "A.cue1": "Digit1", "A.cue2": "Digit2", "A.cue3": "Digit3", "A.cue4": "Digit4",
  "A.loop4": "KeyR", "A.bendDown": "KeyZ", "A.bendUp": "KeyX",
  "B.play": "KeyP", "B.cue": "KeyO", "B.sync": "KeyI",
  "B.killLow": "KeyJ", "B.killMid": "KeyK", "B.killHigh": "KeyL",
  "B.cue1": "Digit7", "B.cue2": "Digit8", "B.cue3": "Digit9", "B.cue4": "Digit0",
  "B.loop4": "KeyU", "B.bendDown": "KeyN", "B.bendUp": "KeyM",
  "mix.swap": "Space", "mix.xfLeft": "ArrowLeft", "mix.xfRight": "ArrowRight", "mix.xfCenter": "ArrowDown",
};
const KEY_NAMES = {
  Space: "Espaço", ArrowLeft: "←", ArrowRight: "→", ArrowUp: "↑", ArrowDown: "↓", Enter: "Enter", Tab: "Tab",
  Comma: ",", Period: ".", Semicolon: ";", Slash: "/", Minus: "-", Equal: "=", Backquote: "`", Quote: "'",
  BracketLeft: "[", BracketRight: "]", Backslash: "\\", ShiftLeft: "Shift E", ShiftRight: "Shift D",
};
function keyLabel(code) {
  if (!code) return "";
  if (KEY_NAMES[code]) return KEY_NAMES[code];
  return code.replace(/^Key|^Digit/, "").replace(/^Numpad/, "Num ");
}
function loadStored(name, fallback) {
  try {
    const v = JSON.parse(window.localStorage.getItem(name));
    return v == null ? fallback : v;
  } catch (e) {
    return fallback;
  }
}
function store(name, value) {
  try {
    window.localStorage.setItem(name, JSON.stringify(value));
  } catch (e) {
    /* sem armazenamento: os atalhos valem só nesta sessão */
  }
}

const BANDS = { killLow: "low", killMid: "mid", killHigh: "high" };

// Executa uma ação de atalho. `up` indica que a tecla foi solta.
function runAction(engine, id, up, opt) {
  const [scope, name] = id.split(".");
  if (scope === "mix") {
    if (up) return;
    if (name === "swap") return engine.swapBass();
    const v = name === "xfCenter" ? 0 : clamp(engine.crossfader + (name === "xfLeft" ? -0.1 : 0.1), -1, 1);
    engine.setCrossfader(v);
    engine.onCrossfader && engine.onCrossfader(v);
    return;
  }
  const d = engine.decks[scope];
  if (name === "cue") return up ? d.cueUp() : d.cueDown();
  if (name === "bendDown" || name === "bendUp") return d.setBend(up ? 0 : name === "bendUp" ? 0.04 : -0.04);
  if (BANDS[name]) {
    const band = BANDS[name];
    if (opt.killHold) d.setKill(band, !up);
    else if (!up) d.setKill(band, !d.kill[band]);
    return;
  }
  if (up) return;
  if (name === "play") return d.toggle();
  if (name === "sync") return d.syncTo(engine.other(scope));
  if (name === "loop4") return d.toggleLoop(4);
  if (name.startsWith("cue")) return d.hotCue(Number(name.slice(3)) - 1, opt.shift);
}

const KeysContext = React.createContext(DEFAULT_KEYS);
function KeyHint({ action }) {
  const keys = React.useContext(KeysContext);
  const label = keyLabel(keys[action]);
  return label ? <kbd className="djx-kbd">{label}</kbd> : null;
}

/* ----------------------------- Controles -------------------------------- */

function useDeck(deck) {
  const [, force] = useReducer((x) => x + 1, 0);
  useEffect(() => deck.subscribe(force), [deck]);
}

function Knob({ value, min, max, onChange, reset, label, bipolar, size = 46 }) {
  const drag = useRef(null);
  const t = (value - min) / (max - min);
  const ang = -135 + t * 270;
  const R = 18;
  const arc = (a0, a1) => {
    const p = (a) => [24 + R * Math.sin((a * Math.PI) / 180), 24 - R * Math.cos((a * Math.PI) / 180)];
    const [x0, y0] = p(a0);
    const [x1, y1] = p(a1);
    return `M${x0} ${y0} A${R} ${R} 0 ${Math.abs(a1 - a0) > 180 ? 1 : 0} ${a1 > a0 ? 1 : 0} ${x1} ${y1}`;
  };
  const from = bipolar ? 0 : -135;
  return (
    <div className="djx-knob">
      <svg
        width={size}
        height={size}
        viewBox="0 0 48 48"
        role="slider"
        tabIndex={0}
        aria-label={label}
        aria-valuemin={min}
        aria-valuemax={max}
        aria-valuenow={Number(value.toFixed(2))}
        onPointerDown={(e) => {
          e.currentTarget.setPointerCapture(e.pointerId);
          drag.current = { y: e.clientY, v: value };
        }}
        onPointerMove={(e) => {
          if (!drag.current) return;
          const dv = ((drag.current.y - e.clientY) / 140) * (max - min);
          onChange(clamp(drag.current.v + dv, min, max));
        }}
        onPointerUp={() => (drag.current = null)}
        onPointerCancel={() => (drag.current = null)}
        onDoubleClick={() => onChange(reset)}
        onKeyDown={(e) => {
          const step = (max - min) / 40;
          if (e.key === "ArrowUp" || e.key === "ArrowRight") onChange(clamp(value + step, min, max));
          if (e.key === "ArrowDown" || e.key === "ArrowLeft") onChange(clamp(value - step, min, max));
        }}
      >
        <path d={arc(-135, 135)} className="djx-knob-track" />
        {Math.abs(ang - from) > 1 && <path d={ang > from ? arc(from, ang) : arc(ang, from)} className="djx-knob-fill" />}
        <circle cx="24" cy="24" r="12.5" className="djx-knob-cap" />
        <line x1="24" y1="24" x2="24" y2="13" className="djx-knob-tick" transform={`rotate(${ang} 24 24)`} />
      </svg>
      <span className="djx-label">{label}</span>
    </div>
  );
}

function Slider({ value, min, max, onChange, vertical, reset, label, className = "" }) {
  const ref = useRef(null);
  const down = useRef(false);
  const set = (e) => {
    const r = ref.current.getBoundingClientRect();
    const pad = 14;
    const t = vertical ? 1 - (e.clientY - r.top - pad) / (r.height - pad * 2) : (e.clientX - r.left - pad) / (r.width - pad * 2);
    onChange(min + clamp(t, 0, 1) * (max - min));
  };
  const t = (value - min) / (max - min);
  const style = vertical ? { bottom: `calc(14px + ${t} * (100% - 28px))` } : { left: `calc(14px + ${t} * (100% - 28px))` };
  return (
    <div
      ref={ref}
      className={`djx-slider ${vertical ? "djx-v" : "djx-h"} ${className}`}
      role="slider"
      tabIndex={0}
      aria-label={label}
      aria-orientation={vertical ? "vertical" : "horizontal"}
      aria-valuemin={min}
      aria-valuemax={max}
      aria-valuenow={Number(value.toFixed(3))}
      onPointerDown={(e) => {
        e.currentTarget.setPointerCapture(e.pointerId);
        down.current = true;
        set(e);
      }}
      onPointerMove={(e) => down.current && set(e)}
      onPointerUp={() => (down.current = false)}
      onPointerCancel={() => (down.current = false)}
      onDoubleClick={() => reset !== undefined && onChange(reset)}
      onKeyDown={(e) => {
        const step = (max - min) / 50;
        if (e.key === "ArrowUp" || e.key === "ArrowRight") { e.stopPropagation(); onChange(clamp(value + step, min, max)); }
        if (e.key === "ArrowDown" || e.key === "ArrowLeft") { e.stopPropagation(); onChange(clamp(value - step, min, max)); }
      }}
    >
      <div className="djx-slider-rail" />
      {reset !== undefined && <div className="djx-slider-mark" />}
      <div className="djx-slider-thumb" style={style} />
    </div>
  );
}

function Meter({ source }) {
  const ref = useRef(null);
  useEffect(() => {
    let raf, hold = 0;
    const tick = () => {
      const pk = source.level();
      hold = Math.max(pk, hold * 0.9);
      const db = 20 * Math.log10(hold + 1e-6);
      const t = clamp((db + 48) / 48, 0, 1);
      if (ref.current) ref.current.style.transform = `scaleY(${t})`;
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [source]);
  return (
    <div className="djx-meter" aria-hidden="true">
      <div className="djx-meter-fill" ref={ref} />
    </div>
  );
}

/* ----------------------------- Formas de onda --------------------------- */

const ZOOM_PXS = 105; // pixels por segundo na onda ampliada

function sizeCanvas(cv) {
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  const w = Math.round(cv.clientWidth * dpr);
  const h = Math.round(cv.clientHeight * dpr);
  if (cv.width !== w || cv.height !== h) {
    cv.width = w;
    cv.height = h;
  }
  return dpr;
}

function cssVar(el, name) {
  return getComputedStyle(el).getPropertyValue(name).trim();
}

function drawZoom(cv, deck, col) {
  const dpr = sizeCanvas(cv);
  const g = cv.getContext("2d");
  const w = cv.width, h = cv.height;
  g.clearRect(0, 0, w, h);
  const an = deck.analysis;
  const cx = Math.round(w / 2);
  if (an) {
    const pos = deck.position();
    const rate = 1 + deck.pitch;
    const pxs = ZOOM_PXS * dpr;
    const secPerPx = rate / pxs;
    const mid = h / 2;
    const L = deck.loop;
    if (L) {
      const x0 = cx + (L.start - pos) / secPerPx;
      const x1 = cx + (L.end - pos) / secPerPx;
      g.fillStyle = col.loop;
      g.fillRect(x0, 0, x1 - x0, h);
    }
    if (an.bpm) {
      const bl = 60 / an.bpm;
      const tL = pos - cx * secPerPx;
      const tR = pos + (w - cx) * secPerPx;
      let k = Math.ceil((tL - an.firstBeat) / bl);
      for (; an.firstBeat + k * bl <= tR; k++) {
        const t = an.firstBeat + k * bl;
        if (t < 0 || t > an.duration) continue;
        const x = Math.round(cx + (t - pos) / secPerPx);
        const bar = ((k % 4) + 4) % 4 === 0;
        g.fillStyle = bar ? col.grid2 : col.grid;
        g.fillRect(x, bar ? 0 : h * 0.18, dpr, bar ? h : h * 0.64);
      }
    }
    const spp = secPerPx * PPS;
    for (let pass = 0; pass < 2; pass++) {
      const arr = pass ? an.lows : an.peaks;
      g.fillStyle = pass ? col.wave : col.waveDim;
      for (let x = 0; x < w; x++) {
        const f0 = pos * PPS + (x - cx) * spp;
        const i0 = Math.floor(f0);
        if (i0 < 0 || i0 >= arr.length) continue;
        const i1 = Math.min(arr.length, Math.max(i0 + 1, Math.floor(f0 + spp)));
        let m = 0;
        for (let i = i0; i < i1; i++) if (arr[i] > m) m = arr[i];
        const bh = Math.max(dpr, m * (h - 6 * dpr) * (pass ? 1.25 : 1));
        g.fillRect(x, mid - bh / 2, 1, Math.min(bh, h));
      }
    }
    deck.hotCues.forEach((c, i) => {
      if (c == null) return;
      const x = cx + (c - pos) / secPerPx;
      if (x < -20 || x > w + 20) return;
      g.fillStyle = col.cue;
      g.fillRect(x, 0, 2 * dpr, h);
      g.font = `${10 * dpr}px ui-monospace, monospace`;
      g.fillText(String(i + 1), x + 4 * dpr, 11 * dpr);
    });
  }
  g.fillStyle = col.head;
  g.fillRect(cx - dpr, 0, 2 * dpr, h);
}

function drawOverview(cv, deck, col, cache) {
  const dpr = sizeCanvas(cv);
  const g = cv.getContext("2d");
  const w = cv.width, h = cv.height;
  g.clearRect(0, 0, w, h);
  const an = deck.analysis;
  if (!an) return;
  if (cache.an !== an || cache.w !== w || cache.h !== h) {
    const off = document.createElement("canvas");
    off.width = w;
    off.height = h;
    const o = off.getContext("2d");
    const per = an.peaks.length / w;
    for (let pass = 0; pass < 2; pass++) {
      const arr = pass ? an.lows : an.peaks;
      o.fillStyle = pass ? col.wave : col.waveDim;
      for (let x = 0; x < w; x++) {
        const i0 = Math.floor(x * per);
        const i1 = Math.max(i0 + 1, Math.floor((x + 1) * per));
        let m = 0;
        for (let i = i0; i < i1 && i < arr.length; i++) if (arr[i] > m) m = arr[i];
        const bh = Math.max(1, m * h * (pass ? 1.2 : 0.96));
        o.fillRect(x, (h - Math.min(bh, h)) / 2, 1, Math.min(bh, h));
      }
    }
    cache.an = an;
    cache.w = w;
    cache.h = h;
    cache.img = off;
  }
  g.drawImage(cache.img, 0, 0);
  const X = (t) => (t / an.duration) * w;
  const px = X(deck.position());
  g.fillStyle = col.played;
  g.fillRect(0, 0, px, h);
  if (deck.loop) {
    g.fillStyle = col.loop;
    g.fillRect(X(deck.loop.start), 0, Math.max(2, X(deck.loop.end) - X(deck.loop.start)), h);
  }
  g.fillStyle = col.cue;
  deck.hotCues.forEach((c) => c != null && g.fillRect(X(c), 0, 2 * dpr, h));
  g.fillStyle = col.head;
  g.fillRect(px - dpr, 0, 2 * dpr, h);
}

/* ----------------------------- Deck ------------------------------------- */

function DeckPanel({ engine, deck, onPickFile }) {
  useDeck(deck);
  const other = engine.other(deck.id);
  useDeck(other);
  const zoomRef = useRef(null);
  const overRef = useRef(null);
  const timeRef = useRef(null);
  const leftRef = useRef(null);
  const rootRef = useRef(null);
  const fileRef = useRef(null);
  const [erase, setErase] = useState(false);
  const [over, setOver] = useState(false);
  const scrub = useRef(null);

  useEffect(() => {
    let raf;
    const cache = {};
    const root = rootRef.current;
    const col = {
      wave: cssVar(root, "--deck"),
      waveDim: cssVar(root, "--deck-dim"),
      grid: cssVar(root, "--grid"),
      grid2: cssVar(root, "--grid-strong"),
      head: cssVar(root, "--ink"),
      cue: cssVar(root, "--cue"),
      loop: cssVar(root, "--loop"),
      played: cssVar(root, "--played"),
    };
    const tick = () => {
      if (zoomRef.current) drawZoom(zoomRef.current, deck, col);
      if (overRef.current) drawOverview(overRef.current, deck, col, cache);
      const p = deck.position();
      if (timeRef.current) timeRef.current.textContent = fmtTime(p);
      if (leftRef.current) leftRef.current.textContent = "-" + fmtTime(deck.duration - p);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [deck]);

  const loaded = !!deck.buffer;
  const pitchPct = deck.pitch * 100;
  const seekOverview = (e) => {
    const r = e.currentTarget.getBoundingClientRect();
    deck.seek(clamp((e.clientX - r.left) / r.width, 0, 1) * deck.duration);
  };

  return (
    <section
      ref={rootRef}
      className={`djx-deck djx-deck-${deck.id} ${over ? "djx-over" : ""}`}
      aria-label={`Deck ${deck.id}`}
      onDragOver={(e) => {
        e.preventDefault();
        setOver(true);
      }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setOver(false);
        const f = [...e.dataTransfer.files].find((x) => x.type.startsWith("audio") || /\.(mp3|wav|m4a|aac|ogg|flac)$/i.test(x.name));
        if (f) onPickFile(f);
      }}
    >
      <header className="djx-deck-head">
        <span className="djx-badge">{deck.id}</span>
        <div className="djx-title" title={deck.title}>
          {deck.loading ? "Analisando a faixa…" : deck.title || "Nenhuma faixa carregada"}
        </div>
        <button className="djx-btn djx-ghost" onClick={() => fileRef.current.click()}>
          Carregar
        </button>
        <input
          ref={fileRef}
          id={`djx-file-${deck.id}`}
          type="file"
          accept="audio/*,.mp3,.wav,.m4a,.aac,.ogg,.flac"
          hidden
          onChange={(e) => {
            if (e.target.files[0]) onPickFile(e.target.files[0]);
            e.target.value = "";
          }}
        />
      </header>

      <div className="djx-readout">
        <div>
          <span className="djx-label">BPM</span>
          <strong className="djx-num djx-bpm">{deck.bpm ? deck.liveBpm.toFixed(1) : "–"}</strong>
        </div>
        <div>
          <span className="djx-label">Pitch</span>
          <strong className="djx-num">{(pitchPct >= 0 ? "+" : "") + pitchPct.toFixed(1)}%</strong>
        </div>
        <div>
          <span className="djx-label">Tempo</span>
          <strong className="djx-num" ref={timeRef}>00:00.0</strong>
        </div>
        <div>
          <span className="djx-label">Resta</span>
          <strong className="djx-num" ref={leftRef}>-00:00.0</strong>
        </div>
      </div>

      <div className="djx-waves">
        <canvas
          ref={zoomRef}
          className="djx-zoom"
          onPointerDown={(e) => {
            if (!loaded) return;
            e.currentTarget.setPointerCapture(e.pointerId);
            scrub.current = { x: e.clientX, pos: deck.position() };
          }}
          onPointerMove={(e) => {
            if (!scrub.current) return;
            const dx = e.clientX - scrub.current.x;
            deck.seek(scrub.current.pos - (dx / ZOOM_PXS) * (1 + deck.pitch));
          }}
          onPointerUp={() => (scrub.current = null)}
          onPointerCancel={() => (scrub.current = null)}
        />
        <canvas
          ref={overRef}
          className="djx-overview"
          onPointerDown={(e) => {
            if (!loaded) return;
            e.currentTarget.setPointerCapture(e.pointerId);
            scrub.current = "ov";
            seekOverview(e);
          }}
          onPointerMove={(e) => scrub.current === "ov" && seekOverview(e)}
          onPointerUp={() => (scrub.current = null)}
          onPointerCancel={() => (scrub.current = null)}
        />
        {!loaded && !deck.loading && <div className="djx-empty">Arraste uma música para cá ou toque em Carregar</div>}
        {deck.error && <div className="djx-empty djx-error">{deck.error}</div>}
      </div>

      <div className="djx-deck-body">
        <div className="djx-controls">
          <div className="djx-transport">
            <button
              className="djx-btn djx-big djx-cue"
              disabled={!loaded}
              onPointerDown={() => deck.cueDown()}
              onPointerUp={() => deck.cueUp()}
              onPointerLeave={() => deck.cueUp()}
            >
              CUE
              <KeyHint action={`${deck.id}.cue`} />
            </button>
            <button
              className={`djx-btn djx-big djx-play ${deck.playing ? "djx-on" : ""}`}
              disabled={!loaded}
              onClick={() => deck.toggle()}
              aria-pressed={deck.playing}
            >
              {deck.playing ? "❚❚" : "▶"}
              <KeyHint action={`${deck.id}.play`} />
            </button>
            <button
              className={`djx-btn djx-big djx-sync ${deck.synced ? "djx-on" : ""}`}
              disabled={!loaded || !deck.bpm || !other.bpm}
              onClick={() => deck.syncTo(other)}
              title={`Iguala o BPM ao deck ${other.id}`}
            >
              SYNC
              <KeyHint action={`${deck.id}.sync`} />
            </button>
          </div>

          <div className="djx-row">
            <span className="djx-label djx-rowlabel">Hot cue</span>
            <div className="djx-pads">
              {deck.hotCues.map((c, i) => (
                <button
                  key={i}
                  className={`djx-btn djx-pad ${c != null ? "djx-set" : ""}`}
                  disabled={!loaded}
                  onClick={(e) => deck.hotCue(i, erase || e.shiftKey)}
                  onContextMenu={(e) => {
                    e.preventDefault();
                    deck.hotCue(i, true);
                  }}
                >
                  {i + 1}
                  <KeyHint action={`${deck.id}.cue${i + 1}`} />
                </button>
              ))}
              <button
                className={`djx-btn djx-pad djx-del ${erase ? "djx-on" : ""}`}
                onClick={() => setErase(!erase)}
                aria-pressed={erase}
                title="Ligado: tocar em um hot cue apaga o ponto"
              >
                Apagar
              </button>
            </div>
          </div>

          <div className="djx-row">
            <span className="djx-label djx-rowlabel">Loop</span>
            <div className="djx-pads">
              {LOOP_SIZES.map((b) => (
                <button
                  key={b}
                  className={`djx-btn djx-pad ${deck.loop && deck.loop.beats === b ? "djx-on" : ""}`}
                  disabled={!loaded}
                  onClick={() => deck.toggleLoop(b)}
                  title={`Loop de ${b === 0.5 ? "meia" : b} batida${b > 1 ? "s" : ""}`}
                >
                  {b === 0.5 ? "½" : b}
                  {b === 4 && <KeyHint action={`${deck.id}.loop4`} />}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="djx-pitch">
          <span className="djx-label">Pitch</span>
          <Slider
            vertical
            label={`Pitch do deck ${deck.id}`}
            value={-deck.pitch}
            min={-deck.pitchRange}
            max={deck.pitchRange}
            reset={0}
            onChange={(v) => deck.setPitch(-v)}
          />
          <button className="djx-btn djx-mini" onClick={() => deck.cyclePitchRange()} title="Alcance do pitch">
            ±{Math.round(deck.pitchRange * 100)}%
          </button>
          <div className="djx-bend">
            {[-1, 1].map((d) => (
              <button
                key={d}
                className="djx-btn djx-mini"
                disabled={!loaded}
                onPointerDown={() => deck.setBend(d * 0.04)}
                onPointerUp={() => deck.setBend(0)}
                onPointerLeave={() => deck.setBend(0)}
                title={d < 0 ? "Segura para atrasar" : "Segura para adiantar"}
              >
                {d < 0 ? "−" : "+"}
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

/* ----------------------------- Mixer ------------------------------------ */

function Channel({ deck }) {
  useDeck(deck);
  const bands = [
    ["high", "Agudo", "killHigh"],
    ["mid", "Médio", "killMid"],
    ["low", "Grave", "killLow"],
  ];
  return (
    <div className={`djx-channel djx-deck-${deck.id}`}>
      <span className="djx-badge djx-small">{deck.id}</span>
      <Knob label="Ganho" value={deck.trim} min={-12} max={12} reset={0} bipolar onChange={(v) => deck.setTrim(v)} />
      {bands.map(([band, name, action]) => (
        <div className="djx-band" key={band}>
          <Knob label={name} value={deck.eq[band]} min={0} max={1} reset={0.5} onChange={(v) => deck.setEq(band, v)} />
          <button
            className={`djx-btn djx-kill ${deck.kill[band] ? "djx-on" : ""}`}
            aria-pressed={deck.kill[band]}
            aria-label={`Kill ${name} do deck ${deck.id}`}
            onClick={() => deck.setKill(band, !deck.kill[band])}
          >
            KILL
            <KeyHint action={`${deck.id}.${action}`} />
          </button>
        </div>
      ))}
      <Knob label="Filtro" value={deck.filter} min={-1} max={1} reset={0} bipolar onChange={(v) => deck.setFilter(v)} />
      <div className="djx-faderwrap">
        <Slider vertical label={`Volume do deck ${deck.id}`} value={deck.volume} min={0} max={1} onChange={(v) => deck.setVolume(v)} />
        <Meter source={deck} />
      </div>
    </div>
  );
}

function MixerPanel({ engine }) {
  const [xf, setXf] = useState(0);
  const [master, setMaster] = useState(engine.masterValue);
  const [rec, setRec] = useState(null);
  const [recTime, setRecTime] = useState(0);
  const [take, setTake] = useState(null);

  useEffect(() => {
    engine.onCrossfader = setXf;
    return () => (engine.onCrossfader = null);
  }, [engine]);
  useEffect(() => {
    if (!rec) return;
    const id = setInterval(() => setRecTime((Date.now() - rec) / 1000), 250);
    return () => clearInterval(id);
  }, [rec]);

  const toggleRec = async () => {
    if (rec) {
      const blob = await engine.stopRecording();
      setRec(null);
      if (blob) {
        if (take) URL.revokeObjectURL(take.url);
        const ext = blob.type.includes("mp4") ? "m4a" : "webm";
        setTake({ url: URL.createObjectURL(blob), name: `set-${new Date().toISOString().slice(0, 16).replace(/[:T]/g, "-")}.${ext}` });
      }
    } else {
      engine.resume();
      if (engine.startRecording()) {
        setRecTime(0);
        setRec(Date.now());
      }
    }
  };

  return (
    <section className="djx-mixer" aria-label="Mixer">
      <div className="djx-channels">
        <Channel deck={engine.decks.A} />
        <div className="djx-master">
          <span className="djx-label">Master</span>
          <Meter source={engine} />
          <Knob
            label="Volume"
            value={master}
            min={0}
            max={1}
            reset={0.8}
            onChange={(v) => {
              setMaster(v);
              engine.setMaster(v);
            }}
          />
          <button className={`djx-btn djx-rec ${rec ? "djx-on" : ""}`} onClick={toggleRec} aria-pressed={!!rec}>
            {rec ? `■ ${fmtTime(recTime).slice(0, 5)}` : "● REC"}
          </button>
          {take && !rec && (
            <a className="djx-take" href={take.url} download={take.name}>
              Baixar set
            </a>
          )}
        </div>
        <Channel deck={engine.decks.B} />
      </div>
      <button
        className="djx-btn djx-swap"
        onClick={() => engine.swapBass()}
        title="Mata o grave de um deck e devolve o do outro no mesmo instante"
      >
        Troca de grave
        <KeyHint action="mix.swap" />
      </button>
      <div className="djx-xfade">
        <span className="djx-badge djx-small djx-deck-A">A</span>
        <Slider
          label="Crossfader"
          value={xf}
          min={-1}
          max={1}
          reset={0}
          onChange={(v) => {
            setXf(v);
            engine.setCrossfader(v);
          }}
        />
        <span className="djx-badge djx-small djx-deck-B">B</span>
      </div>
    </section>
  );
}

/* ----------------------------- Página ----------------------------------- */

export default function DJMixer() {
  const [engine] = useState(() => (typeof window === "undefined" ? null : new Engine()));
  const [library, setLibrary] = useState([]);
  const [help, setHelp] = useState(false);
  const libRef = useRef(null);
  const libraryRef = useRef(library);
  libraryRef.current = library;

  const [keys, setKeys] = useState(() => ({ ...DEFAULT_KEYS, ...loadStored("cabine.keys", {}) }));
  const [killHold, setKillHold] = useState(() => loadStored("cabine.killHold", false));
  const [capture, setCapture] = useState(null);
  const live = useRef({});
  live.current = { keys, killHold, capture };

  const bind = (action, code) => {
    setKeys((prev) => {
      const next = { ...prev };
      if (code) for (const k in next) if (next[k] === code) next[k] = null;
      next[action] = code;
      store("cabine.keys", next);
      return next;
    });
  };

  useEffect(() => {
    if (!engine) return;
    const wake = () => engine.resume();
    window.addEventListener("pointerdown", wake);
    const held = new Map();
    const onKey = (e) => {
      const up = e.type === "keyup";
      const { keys, killHold, capture } = live.current;
      if (capture) {
        if (up) return;
        e.preventDefault();
        if (e.code === "Escape") setCapture(null);
        else if (e.code === "Backspace" || e.code === "Delete") { bind(capture, null); setCapture(null); }
        else if (!/^(Shift|Control|Alt|Meta)/.test(e.code)) { bind(capture, e.code); setCapture(null); }
        return;
      }
      const tag = (e.target.tagName || "").toLowerCase();
      const typing = tag === "textarea" || (tag === "input" && !/checkbox|radio|file|button/.test(e.target.type));
      if (typing || e.metaKey || e.ctrlKey || e.altKey) return;
      if (up) {
        // Solta a ação que a tecla disparou, mesmo que o atalho tenha mudado no meio.
        const id = held.get(e.code);
        if (!id) return;
        held.delete(e.code);
        e.preventDefault();
        runAction(engine, id, true, { killHold, shift: e.shiftKey });
        return;
      }
      const id = Object.keys(keys).find((k) => keys[k] === e.code);
      if (!id) return;
      e.preventDefault();
      const repeatable = id.startsWith("mix.xf");
      if (held.has(e.code) && !repeatable) return;
      held.set(e.code, id);
      engine.resume();
      runAction(engine, id, false, { killHold, shift: e.shiftKey });
    };
    const releaseAll = () => {
      const { killHold } = live.current;
      held.forEach((id) => runAction(engine, id, true, { killHold, shift: false }));
      held.clear();
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("keyup", onKey);
    window.addEventListener("blur", releaseAll);
    return () => {
      window.removeEventListener("pointerdown", wake);
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("keyup", onKey);
      window.removeEventListener("blur", releaseAll);
    };
  }, [engine]);

  if (!engine) return null;

  const addFiles = (files) => {
    const items = [...files]
      .filter((f) => f.type.startsWith("audio") || /\.(mp3|wav|m4a|aac|ogg|flac)$/i.test(f.name))
      .map((f) => ({ id: `${f.name}-${f.size}-${f.lastModified}`, name: f.name.replace(/\.[^.]+$/, ""), file: f, analysis: null }));
    setLibrary((lib) => [...lib, ...items.filter((it) => !lib.some((x) => x.id === it.id))]);
    return items;
  };

  const loadItem = async (deckId, item) => {
    const known = libraryRef.current.find((x) => x.id === item.id);
    const an = await engine.decks[deckId].loadFile(item.file, known && known.analysis);
    if (an) setLibrary((lib) => lib.map((x) => (x.id === item.id ? { ...x, analysis: an } : x)));
  };

  const pickFile = (deckId) => (file) => {
    const [item] = addFiles([file]);
    if (item) loadItem(deckId, item);
  };

  const loadDemo = () => {
    engine.resume();
    engine.decks.A.setBuffer(makeDemoBuffer(engine.ctx, 124, 55), "Batida demo · 124 BPM");
    engine.decks.B.setBuffer(makeDemoBuffer(engine.ctx, 128, 49), "Batida demo · 128 BPM");
  };

  return (
    <KeysContext.Provider value={keys}>
    <div className="djx-app">
      <style>{CSS}</style>
      <header className="djx-top">
        <h1>
          Cabine<span>2 decks</span>
        </h1>
        <div className="djx-top-actions">
          <button className="djx-btn djx-ghost" onClick={loadDemo}>
            Carregar batidas demo
          </button>
          <button className="djx-btn djx-ghost" onClick={() => setHelp(!help)} aria-expanded={help}>
            Atalhos
          </button>
        </div>
      </header>

      {help && (
        <section className="djx-help" aria-label="Atalhos de teclado">
          <div className="djx-help-head">
            <p>
              Clique em um atalho e aperte a tecla nova. Esc cancela, Backspace deixa a função sem tecla. Dois cliques em qualquer
              botão giratório ou fader voltam ao centro. Shift com hot cue apaga o ponto.
            </p>
            <div className="djx-help-opts">
              <label className="djx-check">
                <input
                  id="djx-killhold"
                  type="checkbox"
                  checked={killHold}
                  onChange={(e) => {
                    setKillHold(e.target.checked);
                    store("cabine.killHold", e.target.checked);
                  }}
                />
                Kill só enquanto seguro a tecla
              </label>
              <button
                className="djx-btn djx-ghost"
                onClick={() => {
                  setKeys({ ...DEFAULT_KEYS });
                  store("cabine.keys", DEFAULT_KEYS);
                  setCapture(null);
                }}
              >
                Restaurar padrão
              </button>
            </div>
          </div>
          <div className="djx-keys">
            {KEY_GROUPS.map(([group, actions]) => (
              <div key={group} className={`djx-keygroup ${group === "Deck A" ? "djx-deck-A" : group === "Deck B" ? "djx-deck-B" : ""}`}>
                <h3>{group}</h3>
                {actions.map(([id, label]) => (
                  <div className="djx-keyrow" key={id}>
                    <span>{label}</span>
                    <button
                      className={`djx-btn djx-keybtn ${capture === id ? "djx-on" : ""}`}
                      onClick={(e) => {
                        e.currentTarget.blur();
                        setCapture(capture === id ? null : id);
                      }}
                    >
                      {capture === id ? "aperte…" : keyLabel(keys[id]) || "sem tecla"}
                    </button>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </section>
      )}

      <main className="djx-grid">
        <DeckPanel engine={engine} deck={engine.decks.A} onPickFile={pickFile("A")} />
        <MixerPanel engine={engine} />
        <DeckPanel engine={engine} deck={engine.decks.B} onPickFile={pickFile("B")} />
      </main>

      <section
        className="djx-library"
        aria-label="Biblioteca"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          addFiles(e.dataTransfer.files);
        }}
      >
        <div className="djx-lib-head">
          <h2>Biblioteca</h2>
          <button className="djx-btn djx-ghost" onClick={() => libRef.current.click()}>
            Adicionar músicas
          </button>
          <input
            ref={libRef}
            id="djx-file-lib"
            type="file"
            multiple
            accept="audio/*,.mp3,.wav,.m4a,.aac,.ogg,.flac"
            hidden
            onChange={(e) => {
              addFiles(e.target.files);
              e.target.value = "";
            }}
          />
        </div>
        {library.length === 0 ? (
          <p className="djx-lib-empty">
            Adicione arquivos do seu computador (MP3, WAV, M4A, OGG, FLAC). Eles ficam só neste navegador, nada é enviado para a internet.
          </p>
        ) : (
          <ul className="djx-lib-list">
            {library.map((it) => (
              <li key={it.id}>
                <span className="djx-lib-name" title={it.name}>{it.name}</span>
                <span className="djx-num djx-lib-meta">{it.analysis && it.analysis.bpm ? it.analysis.bpm.toFixed(1) + " BPM" : "–"}</span>
                <span className="djx-num djx-lib-meta">{it.analysis ? fmtTime(it.analysis.duration).slice(0, 5) : ""}</span>
                <button className="djx-btn djx-mini djx-deck-A djx-to" onClick={() => loadItem("A", it)}>Deck A</button>
                <button className="djx-btn djx-mini djx-deck-B djx-to" onClick={() => loadItem("B", it)}>Deck B</button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
    </KeysContext.Provider>
  );
}

/* ----------------------------- Estilos ---------------------------------- */

const CSS = `
/* Layout: deck | mixer | deck em telas largas; empilha deck, mixer, deck no celular. */
.djx-app{
  --bg:#0e1116; --panel:#171b22; --panel-2:#1f242d; --line:#2b323d; --ink:#eef1f5; --muted:#8892a0;
  --a:#35d0c4; --a-dim:#1c6f6a; --b:#ff9b3d; --b-dim:#8a5220;
  --danger:#ff4d5e; --cue:#ffe14d; --loop:rgba(120,220,140,.22); --played:rgba(8,10,14,.55);
  --grid:rgba(255,255,255,.13); --grid-strong:rgba(255,255,255,.34);
  --display:"Space Grotesk","Inter",system-ui,sans-serif;
  --mono:"JetBrains Mono",ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  color-scheme:dark; background:var(--bg); color:var(--ink); min-height:100%;
  font-family:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif; font-size:14px; line-height:1.4;
  padding-block:14px 28px; padding-left:max(16px,env(safe-area-inset-left,0px)); padding-right:max(16px,env(safe-area-inset-right,0px));
  box-sizing:border-box; -webkit-user-select:none; user-select:none;
}
.djx-app *{box-sizing:border-box}
.djx-deck-A{--deck:var(--a); --deck-dim:var(--a-dim)}
.djx-deck-B{--deck:var(--b); --deck-dim:var(--b-dim)}
.djx-top{display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; margin-bottom:12px}
.djx-top h1{font-family:var(--display); font-size:20px; font-weight:700; letter-spacing:-.01em; margin:0; display:flex; align-items:baseline; gap:10px}
.djx-top h1 span{font-family:var(--mono); font-size:11px; font-weight:400; color:var(--muted); letter-spacing:.08em; text-transform:uppercase}
.djx-top-actions{display:flex; gap:8px; flex-wrap:wrap}
.djx-help{background:var(--panel); border:1px solid var(--line); border-radius:6px; padding:12px 14px; margin-bottom:12px; -webkit-user-select:none; user-select:none}
.djx-help-head{display:flex; gap:16px; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; margin-bottom:10px}
.djx-help-head p{margin:0; color:var(--muted); max-width:62ch; flex:1 1 280px}
.djx-help-opts{display:flex; gap:12px; align-items:center; flex-wrap:wrap}
.djx-check{display:flex; gap:7px; align-items:center; cursor:pointer}
.djx-check input{width:16px; height:16px; accent-color:var(--a)}
.djx-keys{display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:10px 28px}
.djx-keygroup h3{font-family:var(--display); font-size:13px; font-weight:600; margin:0 0 4px; color:var(--deck,var(--ink))}
.djx-keyrow{display:flex; justify-content:space-between; align-items:center; gap:10px; padding:3px 0; border-top:1px solid var(--line)}
.djx-keybtn{min-width:76px; padding:3px 8px; font-family:var(--mono); font-size:12px}
.djx-keybtn.djx-on{background:var(--cue); border-color:var(--cue); color:#0b0d11}
.djx-kbd{font-family:var(--mono); font-size:9.5px; font-weight:400; letter-spacing:0; line-height:1; padding:2px 4px; margin-left:6px; border:1px solid currentColor; border-radius:3px; opacity:.6; vertical-align:middle}
.djx-pad .djx-kbd{border:0; padding:0; margin-left:4px}
.djx-kill .djx-kbd{border:0; padding:0; margin-left:3px}
.djx-swap{font-size:12.5px; width:100%}
.djx-grid{display:grid; grid-template-columns:minmax(0,1fr) auto minmax(0,1fr); gap:12px; align-items:stretch}
.djx-label{font-size:10px; letter-spacing:.09em; text-transform:uppercase; color:var(--muted); white-space:nowrap}
.djx-num{font-family:var(--mono); font-variant-numeric:tabular-nums; font-weight:500}

.djx-btn{font:inherit; color:var(--ink); background:var(--panel-2); border:1px solid var(--line); border-radius:5px; padding:7px 10px; cursor:pointer; touch-action:manipulation; transition:background .08s,border-color .08s}
.djx-btn:hover:not(:disabled){border-color:var(--muted)}
.djx-btn:active:not(:disabled){transform:translateY(1px)}
.djx-btn:disabled{opacity:.38; cursor:default}
.djx-btn:focus-visible,.djx-slider:focus-visible,.djx-knob svg:focus-visible{outline:2px solid var(--ink); outline-offset:2px}
.djx-ghost{background:transparent; font-size:12.5px}
.djx-mini{padding:4px 7px; font-size:11.5px; font-family:var(--mono)}
.djx-badge{display:inline-grid; place-items:center; width:26px; height:26px; flex:none; border-radius:4px; background:var(--deck); color:#0b0d11; font-family:var(--display); font-weight:700; font-size:15px}
.djx-badge.djx-small{width:20px; height:20px; font-size:12px}

.djx-deck{background:var(--panel); border:1px solid var(--line); border-top:3px solid var(--deck); border-radius:8px; padding:12px; display:flex; flex-direction:column; gap:10px; min-width:0}
.djx-deck.djx-over{border-color:var(--deck); background:var(--panel-2)}
.djx-deck-head{display:flex; align-items:center; gap:10px; min-width:0}
.djx-title{flex:1; min-width:0; font-family:var(--display); font-weight:600; font-size:15px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.djx-readout{display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px}
.djx-readout>div{display:flex; flex-direction:column; gap:1px; min-width:0}
.djx-readout strong{font-size:15px}
.djx-readout .djx-bpm{font-size:22px; line-height:1.1; color:var(--deck)}
.djx-waves{position:relative; display:flex; flex-direction:column; gap:6px}
.djx-zoom,.djx-overview{display:block; width:100%; background:#0a0c10; border-radius:4px; touch-action:none; cursor:ew-resize}
.djx-zoom{height:96px} .djx-overview{height:34px; cursor:pointer}
.djx-empty{position:absolute; inset:0; display:grid; place-items:center; text-align:center; padding:8px; color:var(--muted); pointer-events:none; font-size:13px}
.djx-error{color:var(--danger); background:rgba(10,12,16,.85)}
.djx-deck-body{display:flex; gap:12px; align-items:stretch}
.djx-controls{flex:1; min-width:0; display:flex; flex-direction:column; gap:10px}
.djx-transport{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px}
.djx-big{height:52px; font-family:var(--display); font-weight:700; font-size:14px; letter-spacing:.04em}
.djx-play{font-size:18px}
.djx-play.djx-on{background:var(--deck); border-color:var(--deck); color:#0b0d11}
.djx-sync.djx-on{border-color:var(--deck); color:var(--deck)}
.djx-cue{color:var(--cue)}
.djx-row{display:flex; flex-direction:column; gap:4px}
.djx-pads{display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:6px}
.djx-pad{padding:9px 0; font-family:var(--mono); font-size:13px}
.djx-pad.djx-set{border-color:var(--cue); color:var(--cue)}
.djx-pad.djx-on{background:var(--deck); border-color:var(--deck); color:#0b0d11}
.djx-del{grid-column:span 2; font-family:inherit; font-size:11.5px}
.djx-del.djx-on{background:var(--danger); border-color:var(--danger); color:#fff}
.djx-pitch{display:flex; flex-direction:column; align-items:center; gap:6px; width:58px; flex:none}
.djx-pitch .djx-slider{flex:1; min-height:120px}
.djx-bend{display:flex; gap:4px}

.djx-slider{position:relative; touch-action:none; cursor:pointer}
.djx-slider.djx-v{width:34px; height:150px}
.djx-slider.djx-h{height:34px; width:100%}
.djx-slider-rail{position:absolute; background:#0a0c10; border:1px solid var(--line); border-radius:3px}
.djx-v .djx-slider-rail{left:50%; top:8px; bottom:8px; width:6px; transform:translateX(-50%)}
.djx-h .djx-slider-rail{top:50%; left:8px; right:8px; height:6px; transform:translateY(-50%)}
.djx-slider-mark{position:absolute; background:var(--muted)}
.djx-v .djx-slider-mark{left:3px; right:3px; top:50%; height:1px}
.djx-h .djx-slider-mark{top:3px; bottom:3px; left:50%; width:1px}
.djx-slider-thumb{position:absolute; background:linear-gradient(#f4f6f9,#b9c0cb); border-radius:3px; box-shadow:0 1px 4px rgba(0,0,0,.6)}
.djx-v .djx-slider-thumb{left:3px; right:3px; height:20px; transform:translateY(50%); border-top:0}
.djx-h .djx-slider-thumb{top:3px; bottom:3px; width:20px; transform:translateX(-50%)}
.djx-v .djx-slider-thumb::after,.djx-h .djx-slider-thumb::after{content:""; position:absolute; background:#20242c}
.djx-v .djx-slider-thumb::after{left:2px; right:2px; top:9px; height:2px}
.djx-h .djx-slider-thumb::after{top:2px; bottom:2px; left:9px; width:2px}

.djx-knob{display:flex; flex-direction:column; align-items:center; gap:1px}
.djx-knob svg{touch-action:none; cursor:ns-resize; border-radius:50%}
.djx-knob-track{fill:none; stroke:#0a0c10; stroke-width:4; stroke-linecap:round}
.djx-knob-fill{fill:none; stroke:var(--deck,var(--ink)); stroke-width:4; stroke-linecap:round}
.djx-knob-cap{fill:var(--panel-2); stroke:var(--line)}
.djx-knob-tick{stroke:var(--ink); stroke-width:2.5; stroke-linecap:round}

.djx-mixer{background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:12px; display:flex; flex-direction:column; gap:12px}
.djx-channels{display:flex; gap:10px; justify-content:center; flex:1}
.djx-channel{display:flex; flex-direction:column; align-items:center; gap:8px; width:64px}
.djx-band{display:flex; flex-direction:column; align-items:center; gap:3px}
.djx-kill{padding:3px 0; width:52px; font-family:var(--mono); font-size:10.5px; letter-spacing:.08em; color:var(--muted)}
.djx-kill.djx-on{background:var(--danger); border-color:var(--danger); color:#fff}
.djx-faderwrap{display:flex; gap:5px; align-items:stretch; flex:1; min-height:130px}
.djx-faderwrap .djx-slider{height:auto}
.djx-meter{width:6px; background:#0a0c10; border-radius:2px; overflow:hidden; display:flex; align-items:flex-end; min-height:60px}
.djx-meter-fill{width:100%; height:100%; transform-origin:bottom; transform:scaleY(0); background:linear-gradient(to top,#3ecf6e 0%,#3ecf6e 68%,#ffd23d 86%,#ff4d5e 100%)}
.djx-master{display:flex; flex-direction:column; align-items:center; gap:8px; width:74px; padding-inline:6px; border-inline:1px solid var(--line)}
.djx-master .djx-meter{flex:1; width:10px}
.djx-rec{font-family:var(--mono); font-size:11.5px; padding:6px 0; width:100%; color:var(--danger)}
.djx-rec.djx-on{background:var(--danger); border-color:var(--danger); color:#fff}
.djx-take{font-size:11.5px; color:var(--ink); text-align:center}
.djx-xfade{display:flex; align-items:center; gap:8px}

.djx-library{margin-top:12px; background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:12px}
.djx-lib-head{display:flex; align-items:center; justify-content:space-between; gap:10px; margin-bottom:8px}
.djx-lib-head h2{font-family:var(--display); font-size:15px; font-weight:600; margin:0}
.djx-lib-empty{color:var(--muted); margin:4px 0; max-width:70ch}
.djx-lib-list{list-style:none; margin:0; padding:0; display:flex; flex-direction:column}
.djx-lib-list li{display:grid; grid-template-columns:minmax(0,1fr) 84px 50px auto auto; gap:10px; align-items:center; padding:6px 2px; border-top:1px solid var(--line)}
.djx-lib-name{overflow:hidden; text-overflow:ellipsis; white-space:nowrap}
.djx-lib-meta{color:var(--muted); font-size:12.5px; text-align:right}
.djx-to{color:var(--deck); border-color:var(--deck-dim); font-family:inherit}

@media (max-width:1080px){
  .djx-grid{grid-template-columns:minmax(0,1fr)}
  .djx-mixer{order:0}
  .djx-channels{justify-content:space-around}
}
@media (max-width:480px){
  .djx-readout{grid-template-columns:repeat(2,minmax(0,1fr))}
  .djx-pads{grid-template-columns:repeat(6,minmax(0,1fr)); gap:4px}
  .djx-lib-list li{grid-template-columns:minmax(0,1fr) auto auto; row-gap:2px}
  .djx-lib-meta{display:none}
  .djx-channels{gap:4px}
}
@media (prefers-reduced-motion:reduce){ .djx-btn{transition:none} }
`;
