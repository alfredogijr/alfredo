import { useEffect } from "react";
import { motion } from "framer-motion";
import confetti from "canvas-confetti";

const TONES = ["#c89b62", "#8f7458", "#a8502c", "#f3efe8", "#5c4433"];

export default function PrizeReveal({ prize, onContinue }) {
  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    confetti({ particleCount: 90, spread: 70, origin: { y: 0.6 }, colors: TONES, disableForReducedMotion: true });
    setTimeout(() => {
      confetti({ particleCount: 50, angle: 60, spread: 55, origin: { x: 0, y: 0.7 }, colors: TONES, disableForReducedMotion: true });
      confetti({ particleCount: 50, angle: 120, spread: 55, origin: { x: 1, y: 0.7 }, colors: TONES, disableForReducedMotion: true });
    }, 350);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-background/85 backdrop-blur-sm px-6"
      role="dialog"
      aria-modal="true"
      aria-labelledby="premio-titulo"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="bg-card rounded-md p-8 text-center max-w-xs w-full border border-border"
        style={{ borderTop: `6px solid ${prize.color}` }}
      >
        <div className="text-6xl leading-none py-3" aria-hidden="true">{prize.emoji}</div>
        <p className="text-sm text-muted-foreground mb-2">Você ganhou</p>
        <h2 id="premio-titulo" className="text-2xl leading-tight text-foreground mb-7">{prize.name}</h2>
        <button
          onClick={onContinue}
          className="w-full min-h-[52px] bg-primary text-primary-foreground font-semibold rounded-md hover:bg-primary/90 transition-colors"
          autoFocus
        >
          Ver meu cupom
        </button>
      </motion.div>
    </motion.div>
  );
}
