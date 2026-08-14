import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { BLOCOS, FPS, seg } from "./decupagem";

/**
 * Texto na tela, conforme o briefing: branco em negrito, com fundo
 * semitransparente, sempre centralizado na parte inferior do quadro.
 */

export type EstiloLegenda = "caixa" | "sombra";

const FADE = seg(0.15); // fade de entrada/saída, curto pra não piscar no corte

export const Legenda: React.FC<{ estilo?: EstiloLegenda }> = ({ estilo = "caixa" }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const vertical = height > width;

  const bloco = BLOCOS.find(
    (b) => frame >= seg(b.inicio) && frame < seg(b.fim),
  );
  if (!bloco) {
    return null;
  }

  const inicio = seg(bloco.inicio);
  const fim = seg(bloco.fim);
  const opacidade = interpolate(
    frame,
    [inicio, inicio + FADE, fim - FADE, fim],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  // O vertical sobe o texto pra escapar da interface do Instagram e do WhatsApp.
  const margemInferior = vertical ? height * 0.14 : height * 0.078;
  const tamanhoFonte = vertical ? width * 0.054 : width * 0.027;

  const comCaixa = estilo === "caixa";

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        alignItems: "flex-end",
        justifyContent: "center",
        paddingBottom: margemInferior,
        paddingLeft: width * 0.07,
        paddingRight: width * 0.07,
        opacity: opacidade,
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: tamanhoFonte * 0.18,
          textAlign: "center",
          ...(comCaixa
            ? {
                backgroundColor: "rgba(0, 0, 0, 0.65)",
                padding: `${tamanhoFonte * 0.5}px ${tamanhoFonte * 0.75}px`,
                borderRadius: tamanhoFonte * 0.16,
              }
            : {}),
        }}
      >
        {bloco.linhas.map((linha, i) => (
          <span
            key={i}
            style={{
              fontFamily: "Montserrat, sans-serif",
              fontWeight: 800,
              fontSize: tamanhoFonte,
              lineHeight: 1.16,
              color: "#FFFFFF",
              letterSpacing: "-0.01em",
              // Sem caixa, a sombra é o que garante a leitura sobre o LED.
              textShadow: comCaixa
                ? `0 ${tamanhoFonte * 0.03}px ${tamanhoFonte * 0.1}px rgba(0,0,0,0.55)`
                : `0 ${tamanhoFonte * 0.06}px ${tamanhoFonte * 0.22}px rgba(0,0,0,0.95)`,
            }}
          >
            {linha}
          </span>
        ))}
      </div>
    </div>
  );
};
