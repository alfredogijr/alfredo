import React from "react";
import {
  AbsoluteFill,
  interpolate,
  OffthreadVideo,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { Shot } from "../shots";
import { Placeholder } from "./Placeholder";
import { Overlay } from "./Overlay";

export const ShotClip: React.FC<{
  shot: Shot;
  index: number;
  durationInFrames: number;
  /** 0 no primeiro take; nos demais é o cross-dissolve com o take anterior. */
  fadeInFrames: number;
  contato: string;
}> = ({ shot, index, durationInFrames, fadeInFrames, contato }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity =
    fadeInFrames === 0
      ? 1
      : interpolate(frame, [0, fadeInFrames], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

  const scale =
    shot.kenBurns === false
      ? 1
      : interpolate(frame, [0, durationInFrames], [1.05, 1.13], {
          extrapolateRight: "clamp",
        });

  return (
    <AbsoluteFill style={{ opacity }}>
      <AbsoluteFill style={{ overflow: "hidden" }}>
        {shot.src ? (
          <OffthreadVideo
            src={staticFile(shot.src)}
            trimBefore={Math.round(shot.trimBeforeInSeconds * fps)}
            muted={!shot.keepAudio}
            volume={shot.keepAudio ? 0.5 : 0}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: `scale(${scale})`,
            }}
          />
        ) : (
          <Placeholder
            shot={shot}
            index={index}
            dimmed={
              shot.overlay?.kind === "center" || shot.overlay?.kind === "cta"
            }
          />
        )}
      </AbsoluteFill>

      {/* Scrim: garante leitura do texto sobre qualquer imagem. */}
      {shot.overlay?.kind === "lower" ? (
        <AbsoluteFill
          style={{
            background:
              "linear-gradient(to top, rgba(0,0,0,0.82) 0%, rgba(0,0,0,0.45) 26%, rgba(0,0,0,0) 55%)",
          }}
        />
      ) : null}

      {shot.overlay ? (
        <Overlay
          overlay={shot.overlay}
          durationInFrames={durationInFrames}
          contato={contato}
        />
      ) : null}
    </AbsoluteFill>
  );
};
