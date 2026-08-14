import React from "react";
import { useVideoConfig } from "remotion";
import type { Corte } from "./decupagem";

/**
 * Placa usada no modo prova, no lugar do material bruto.
 * Serve pra validar tempo, ritmo e legibilidade do texto antes de ter as imagens.
 */
export const Placa: React.FC<{ corte: Corte; indice: number }> = ({ corte, indice }) => {
  const { width, height } = useVideoConfig();
  const base = Math.min(width, height);

  // Um tom por bloco, pra dar leitura visual de onde um bloco termina e o outro começa.
  const tom = 22 + corte.bloco * 8;

  return (
    <div
      style={{
        width,
        height,
        backgroundColor: `rgb(${tom}, ${tom}, ${tom + 7})`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: base * 0.025,
        padding: base * 0.1,
        fontFamily: "Montserrat, sans-serif",
        textAlign: "center",
      }}
    >
      <div style={{ fontSize: base * 0.028, fontWeight: 700, color: "rgba(255,255,255,0.45)", letterSpacing: "0.18em" }}>
        BLOCO {corte.bloco} · CORTE {String(indice + 1).padStart(2, "0")} · {corte.duracao.toFixed(1)}s
      </div>
      <div style={{ fontSize: base * 0.042, fontWeight: 800, color: "rgba(255,255,255,0.88)", lineHeight: 1.25 }}>
        {corte.descricao}
      </div>
      <div style={{ fontSize: base * 0.026, fontWeight: 600, color: "rgba(255,255,255,0.4)" }}>
        {corte.arquivo} · entrada {corte.entrada}s{corte.zoom ? " · zoom leve" : ""}
      </div>
    </div>
  );
};
