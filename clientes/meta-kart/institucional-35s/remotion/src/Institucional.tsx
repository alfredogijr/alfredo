import React from "react";
import {
  AbsoluteFill,
  Audio,
  interpolate,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { CORTES, DURACAO_TOTAL, FPS, inicioDoCorte, seg, type Corte } from "./decupagem";
import { Legenda, type EstiloLegenda } from "./Legenda";
import { Placa } from "./Placa";

export type PropsInstitucional = {
  /** "prova" usa placas no lugar do bruto; "real" usa os arquivos de public/fontes. */
  modo: "prova" | "real";
  estiloLegenda: EstiloLegenda;
  /** Nome do arquivo de trilha em public/fontes. Vazio = sem trilha. */
  trilha: string;
};

const FADE_FINAL = seg(0.6);

/** Um corte: o plano em si, com o leve zoom quando pedido. */
const Plano: React.FC<{ corte: Corte; indice: number; modo: "prova" | "real" }> = ({
  corte,
  indice,
  modo,
}) => {
  const frame = useCurrentFrame();
  const duracao = seg(corte.duracao);

  // Leve zoom in, até 8% ao longo do corte. Nenhum outro efeito.
  const escala = corte.zoom
    ? interpolate(frame, [0, duracao], [1, 1.08], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 1;

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: "#000" }}>
      <AbsoluteFill style={{ transform: `scale(${escala})` }}>
        {modo === "prova" ? (
          <Placa corte={corte} indice={indice} />
        ) : (
          <OffthreadVideo
            src={staticFile(`fontes/${corte.arquivo}`)}
            trimBefore={seg(corte.entrada)}
            muted
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const Institucional: React.FC<PropsInstitucional> = ({
  modo,
  estiloLegenda,
  trilha,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const fadeFinal = interpolate(
    frame,
    [durationInFrames - FADE_FINAL, durationInFrames],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {CORTES.map((corte, i) => (
        <Sequence
          key={i}
          from={inicioDoCorte(i)}
          durationInFrames={seg(corte.duracao)}
          name={`B${corte.bloco} · ${corte.descricao}`}
        >
          <Plano corte={corte} indice={i} modo={modo} />
        </Sequence>
      ))}

      <Legenda estilo={estiloLegenda} />

      {/* Fade out no final, conforme o briefing. */}
      <AbsoluteFill style={{ backgroundColor: "#000", opacity: fadeFinal, pointerEvents: "none" }} />

      {trilha ? (
        <Audio
          src={staticFile(`fontes/${trilha}`)}
          volume={(f) =>
            interpolate(f, [seg(DURACAO_TOTAL - 1), seg(DURACAO_TOTAL)], [1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            })
          }
        />
      ) : null}
    </AbsoluteFill>
  );
};

export const DURACAO_EM_FRAMES = DURACAO_TOTAL * FPS;
