import { Config } from "@remotion/cli/config";
import fs from "fs";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setEntryPoint("src/index.ts");
// Em ambientes sem download do Chrome (ex.: sandbox do Claude), use o navegador local:
const shells = fs.existsSync("/opt/pw-browsers")
  ? fs.readdirSync("/opt/pw-browsers").filter((d) => d.startsWith("chromium_headless_shell-")).flatMap((d) => [
      `/opt/pw-browsers/${d}/chrome-linux/headless_shell`,
      `/opt/pw-browsers/${d}/chrome-headless-shell-linux64/chrome-headless-shell`,
    ])
  : [];
const candidates = [process.env.REMOTION_BROWSER, ...shells].filter(Boolean) as string[];
const found = candidates.find((p) => fs.existsSync(p));
if (found) Config.setBrowserExecutable(found);
