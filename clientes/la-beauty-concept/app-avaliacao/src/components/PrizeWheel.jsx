import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { PRIZES } from "@/lib/la";

function pickPrize() {
  const total = PRIZES.reduce((s, p) => s + p.weight, 0);
  let r = Math.random() * total;
  for (let i = 0; i < PRIZES.length; i++) {
    r -= PRIZES[i].weight;
    if (r <= 0) return i;
  }
  return 0;
}

const INK = "#f3efe8";
const PAPER = "#121110";

export default function PrizeWheel({ onFinish }) {
  const canvasRef = useRef(null);
  const [spinning, setSpinning] = useState(false);
  const [rotation, setRotation] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    drawWheel(0);
  }, []);

  function drawWheel(currentRotation) {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const size = canvas.width;
    const center = size / 2;
    const radius = center - 8;
    const sliceAngle = (2 * Math.PI) / PRIZES.length;

    ctx.clearRect(0, 0, size, size);
    ctx.save();
    ctx.translate(center, center);
    ctx.rotate((currentRotation * Math.PI) / 180);
    ctx.translate(-center, -center);

    PRIZES.forEach((prize, i) => {
      const startAngle = i * sliceAngle;
      const endAngle = startAngle + sliceAngle;
      ctx.beginPath();
      ctx.moveTo(center, center);
      ctx.arc(center, center, radius, startAngle, endAngle);
      ctx.closePath();
      ctx.fillStyle = prize.color;
      ctx.fill();
      ctx.strokeStyle = PAPER;
      ctx.lineWidth = 4;
      ctx.stroke();

      ctx.save();
      ctx.translate(center, center);
      ctx.rotate(startAngle + sliceAngle / 2);
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.font = `${size * 0.08}px sans-serif`;
      ctx.fillText(prize.emoji, radius * 0.78, 0);
      ctx.fillStyle = INK;
      ctx.font = `600 ${size * 0.042}px 'Hanken Grotesk', sans-serif`;
      ctx.fillText(prize.short, radius * 0.5, 0);
      ctx.restore();
    });
    ctx.restore();

    // outer ring
    ctx.beginPath();
    ctx.arc(center, center, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = INK;
    ctx.lineWidth = 2;
    ctx.stroke();

    // hub
    ctx.beginPath();
    ctx.arc(center, center, radius * 0.16, 0, 2 * Math.PI);
    ctx.fillStyle = PAPER;
    ctx.fill();
    ctx.strokeStyle = INK;
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = INK;
    ctx.font = `${size * 0.075}px 'Libre Bodoni', Georgia, serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("LA", center, center + 1);
  }

  function spin() {
    if (spinning || done) return;
    setSpinning(true);

    const winIndex = pickPrize();
    const sliceDeg = 360 / PRIZES.length;
    const sliceCenter = winIndex * sliceDeg + sliceDeg / 2;
    const targetAngle = (270 - sliceCenter + 360) % 360;
    const totalRotation = 360 * 7 + targetAngle;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const duration = reduce ? 1 : 5200;
    const startRot = rotation;
    let start = null;

    function animate(ts) {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 4);
      const currentRot = startRot + totalRotation * ease;
      drawWheel(currentRot);
      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setRotation(currentRot % 360);
        setSpinning(false);
        setDone(true);
        setTimeout(() => onFinish(PRIZES[winIndex]), 500);
      }
    }
    requestAnimationFrame(animate);
  }

  return (
    <div className="flex flex-col items-center gap-8">
      <div className="relative">
        <div
          className="absolute z-10 left-1/2 -translate-x-1/2"
          style={{ top: -14, width: 0, height: 0, borderLeft: "12px solid transparent", borderRight: "12px solid transparent", borderTop: `24px solid ${INK}` }}
          aria-hidden="true"
        />
        <canvas
          ref={canvasRef}
          width={640}
          height={640}
          onClick={spin}
          className={`w-[min(80vw,320px)] h-[min(80vw,320px)] rounded-full ${spinning || done ? "" : "cursor-pointer"}`}
          role="img"
          aria-label={`Roleta com ${PRIZES.length} prêmios: ${PRIZES.map((p) => p.name).join("; ")}`}
        />
      </div>

      <AnimatePresence>
        {!done && (
          <motion.button
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            onClick={spin}
            disabled={spinning}
            className="w-full max-w-xs min-h-[56px] rounded-md bg-primary text-primary-foreground font-semibold text-base transition-colors hover:bg-primary/90 disabled:opacity-60"
          >
            {spinning ? "Girando..." : "Girar a roleta"}
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
}
