import React from "react";
import { Composition } from "remotion";
import { FPS, H, Reel, TOTAL, W } from "./Reel";

export const RemotionRoot: React.FC = () => (
  <Composition id="LojasShoppings" component={Reel} durationInFrames={TOTAL} fps={FPS} width={W} height={H} />
);
