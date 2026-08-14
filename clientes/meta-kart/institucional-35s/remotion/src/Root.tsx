import React from "react";
import { Composition } from "remotion";
import "@fontsource/montserrat/latin-400.css";
import "@fontsource/montserrat/latin-800.css";
import { DURACAO_TOTAL, FPS } from "./decupagem";
import { Institucional, type PropsInstitucional } from "./Institucional";

const padrao: PropsInstitucional = {
  modo: "prova",
  estiloLegenda: "caixa",
  trilha: "",
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Institucional-16x9"
        component={Institucional}
        durationInFrames={DURACAO_TOTAL * FPS}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={padrao}
      />
      <Composition
        id="Institucional-9x16"
        component={Institucional}
        durationInFrames={DURACAO_TOTAL * FPS}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={padrao}
      />
    </>
  );
};
