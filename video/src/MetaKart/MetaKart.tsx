import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { z } from "zod";
import { shots } from "./shots";
import { theme } from "./theme";
import { ShotClip } from "./components/ShotClip";

export const metaKartSchema = z.object({
  /** Linha de contato exibida no fechamento. Editável direto no Studio. */
  contato: z.string(),
});

/** Quadros de cross-dissolve entre os takes. */
const CROSS_DISSOLVE = 10;

const Vignette: React.FC = () => (
  <AbsoluteFill
    style={{
      background:
        "radial-gradient(ellipse at center, rgba(0,0,0,0) 52%, rgba(0,0,0,0.55) 100%)",
      pointerEvents: "none",
    }}
  />
);

const FadeOut: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const opacity = interpolate(
    frame,
    [durationInFrames - 20, durationInFrames - 1],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );
  return (
    <AbsoluteFill style={{ backgroundColor: "#000000", opacity }} />
  );
};

export const MetaKart: React.FC<z.infer<typeof metaKartSchema>> = ({
  contato,
}) => {
  const { fps, durationInFrames: totalFrames } = useVideoConfig();

  // Offsets acumulados: cada take entra exatamente quando o anterior termina e
  // se sobrepõe por CROSS_DISSOLVE quadros para a passagem não ficar seca.
  let cursor = 0;
  const timeline = shots.map((shot, index) => {
    const from = cursor;
    const durationInFrames = Math.round(shot.durationInSeconds * fps);
    cursor += durationInFrames;
    return { shot, index, from, durationInFrames };
  });

  return (
    <AbsoluteFill style={{ backgroundColor: theme.bg }}>
      {timeline.map(({ shot, index, from, durationInFrames }) => (
        <Sequence
          key={shot.id}
          from={from}
          durationInFrames={durationInFrames + CROSS_DISSOLVE}
          name={`${String(index + 1).padStart(2, "0")} · ${shot.id}`}
        >
          <ShotClip
            shot={shot}
            index={index}
            durationInFrames={durationInFrames + CROSS_DISSOLVE}
            fadeInFrames={index === 0 ? 0 : CROSS_DISSOLVE}
            contato={contato}
          />
        </Sequence>
      ))}

      <Vignette />

      {theme.music ? (
        <Audio
          src={staticFile(theme.music)}
          // Entra suave e some no fade final.
          volume={(f) =>
            interpolate(
              f,
              [0, 24, totalFrames - 36, totalFrames - 1],
              [0, theme.musicVolume, theme.musicVolume, 0],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
            )
          }
        />
      ) : null}

      <FadeOut />
    </AbsoluteFill>
  );
};
