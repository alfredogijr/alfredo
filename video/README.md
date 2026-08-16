# Remotion video

<p align="center">
  <a href="https://github.com/remotion-dev/logo">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/remotion-dev/logo/raw/main/animated-logo-banner-dark.apng">
      <img alt="Animated Remotion Logo" src="https://github.com/remotion-dev/logo/raw/main/animated-logo-banner-light.gif">
    </picture>
  </a>
</p>

Welcome to your Remotion project!

## Projetos de cliente

| Composição | Cliente | Formato | Arquivos |
|---|---|---|---|
| `MetaKartB2B` | Meta Kart — institucional B2B | 16:9, 60s | `src/MetaKart/` |

**Meta Kart:** roteiro e decupagem em
[`clientes/meta-kart/roteiro-video-institucional-b2b.md`](../clientes/meta-kart/roteiro-video-institucional-b2b.md).

Para montar: copie os takes para `public/`, preencha `src` e
`trimBeforeInSeconds` em `src/MetaKart/shots.ts`, ajuste marca e trilha em
`src/MetaKart/theme.ts` e exporte com:

```console
npx remotion render MetaKartB2B out/meta-kart-b2b.mp4
```

Enquanto os takes não estiverem definidos, cada slot aparece como cartela de
storyboard — o filme já roda do começo ao fim para aprovação de estrutura.

Para descobrir a duração de um arquivo bruto: `npx remotion ffprobe public/ARQUIVO.mp4`

## Commands

**Install Dependencies**

```console
npm i
```

**Start Preview**

```console
npm run dev
```

**Render video**

```console
npx remotion render
```

**Upgrade Remotion**

```console
npx remotion upgrade
```

## Docs

Get started with Remotion by reading the [fundamentals page](https://www.remotion.dev/docs/the-fundamentals).

## Help

We provide help on our [Discord server](https://discord.gg/6VzzNDwUwV).

## Issues

Found an issue with Remotion? [File an issue here](https://github.com/remotion-dev/remotion/issues/new).

## License

Note that for some entities a company license is needed. [Read the terms here](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md).
