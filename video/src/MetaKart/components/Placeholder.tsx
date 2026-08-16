import React from "react";
import { AbsoluteFill } from "remotion";
import { theme } from "../theme";
import type { Shot } from "../shots";

/**
 * Cartela de storyboard exibida enquanto o take ainda não foi escolhido
 * (`src: null`). Serve para aprovar a estrutura do filme antes da edição.
 */
export const Placeholder: React.FC<{
  shot: Shot;
  index: number;
  /** Nos takes com cartela por cima, o briefing recua para não competir. */
  dimmed?: boolean;
}> = ({ shot, index, dimmed }) => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#101012",
        backgroundImage: `repeating-linear-gradient(135deg, rgba(255,255,255,0.03) 0px, rgba(255,255,255,0.03) 2px, transparent 2px, transparent 14px)`,
        justifyContent: "center",
        padding: 140,
        opacity: dimmed ? 0.22 : 1,
      }}
    >
      <div
        style={{
          fontFamily: theme.fontFamily,
          color: theme.accent,
          fontSize: 26,
          fontWeight: 700,
          letterSpacing: 4,
          textTransform: "uppercase",
        }}
      >
        Take {String(index + 1).padStart(2, "0")} · {shot.durationInSeconds}s
      </div>
      <div
        style={{
          marginTop: 28,
          fontFamily: theme.fontFamily,
          color: theme.text,
          fontSize: 46,
          lineHeight: 1.32,
          fontWeight: 600,
          maxWidth: 1350,
        }}
      >
        {shot.slot}
      </div>
      <div
        style={{
          marginTop: 40,
          fontFamily: theme.fontFamily,
          color: theme.textMuted,
          fontSize: 24,
        }}
      >
        Coloque o arquivo em public/ e preencha `src` em src/MetaKart/shots.ts
      </div>
    </AbsoluteFill>
  );
};
