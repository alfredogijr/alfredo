import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { theme } from "../theme";
import type { Overlay as OverlayType } from "../shots";

const Kicker: React.FC<{ children: string }> = ({ children }) => (
  <div
    style={{
      display: "flex",
      alignItems: "center",
      gap: 16,
      marginBottom: 18,
    }}
  >
    <div style={{ width: 54, height: 5, backgroundColor: theme.accent }} />
    <span
      style={{
        fontFamily: theme.fontFamily,
        color: theme.text,
        fontSize: 26,
        fontWeight: 700,
        letterSpacing: 5,
        textTransform: "uppercase",
      }}
    >
      {children}
    </span>
  </div>
);

const Wordmark: React.FC<{ height: number }> = ({ height }) => {
  if (theme.logo) {
    return (
      <Img
        src={staticFile(theme.logo)}
        style={{ height, objectFit: "contain" }}
      />
    );
  }

  return (
    <span
      style={{
        fontFamily: theme.fontFamilyDisplay,
        // Garante peso mesmo se a máquina cair numa fonte de fallback.
        fontWeight: 900,
        color: theme.text,
        fontSize: height,
        lineHeight: 1,
        letterSpacing: -1,
        textTransform: "uppercase",
      }}
    >
      Meta<span style={{ color: theme.accent }}>Kart</span>
    </span>
  );
};

export const Overlay: React.FC<{
  overlay: OverlayType;
  durationInFrames: number;
  /** Usado apenas na variante "cta". */
  contato: string;
}> = ({ overlay, durationInFrames, contato }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame: frame - 6,
    fps,
    config: { damping: 200 },
    durationInFrames: 26,
  });

  // Some junto com o corte, para não brigar com o texto do próximo take.
  const exit = interpolate(
    frame,
    [durationInFrames - 16, durationInFrames - 4],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const opacity = entrance * exit;
  const translateY = interpolate(entrance, [0, 1], [34, 0]);

  if (overlay.kind === "center" || overlay.kind === "cta") {
    const isCta = overlay.kind === "cta";
    return (
      <AbsoluteFill
        style={{
          backgroundColor: isCta ? "rgba(5,5,5,0.7)" : "rgba(5,5,5,0.62)",
          justifyContent: "center",
          alignItems: "center",
          textAlign: "center",
          padding: 120,
          opacity,
        }}
      >
        <div style={{ transform: `translateY(${translateY}px)` }}>
          <Wordmark height={isCta ? 118 : 96} />
          {overlay.kicker ? (
            <div
              style={{
                marginTop: 26,
                fontFamily: theme.fontFamily,
                color: theme.accent,
                fontSize: 26,
                fontWeight: 700,
                letterSpacing: 6,
                textTransform: "uppercase",
              }}
            >
              {overlay.kicker}
            </div>
          ) : null}
          <div
            style={{
              marginTop: 22,
              fontFamily: theme.fontFamily,
              color: theme.text,
              fontSize: isCta ? 62 : 52,
              fontWeight: 600,
              lineHeight: 1.22,
              maxWidth: 1250,
            }}
          >
            {overlay.headline}
          </div>
          {isCta ? (
            <div
              style={{
                marginTop: 34,
                fontFamily: theme.fontFamily,
                color: theme.textMuted,
                fontSize: 36,
                lineHeight: 1.4,
              }}
            >
              {contato}
            </div>
          ) : null}
        </div>
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        padding: "0 120px 108px",
        opacity,
      }}
    >
      <div style={{ transform: `translateY(${translateY}px)`, maxWidth: 1280 }}>
        {overlay.kicker ? <Kicker>{overlay.kicker}</Kicker> : null}
        <div
          style={{
            fontFamily: theme.fontFamily,
            color: theme.text,
            fontSize: 60,
            fontWeight: 700,
            lineHeight: 1.16,
            textShadow: "0 4px 30px rgba(0,0,0,0.6)",
          }}
        >
          {overlay.headline}
        </div>
        {overlay.sub ? (
          <div
            style={{
              marginTop: 16,
              fontFamily: theme.fontFamily,
              color: theme.textMuted,
              fontSize: 34,
              lineHeight: 1.35,
              textShadow: "0 2px 20px rgba(0,0,0,0.6)",
            }}
          >
            {overlay.sub}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
