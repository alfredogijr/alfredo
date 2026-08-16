import { chromium } from 'playwright';
const b = await chromium.launch();
const p = await b.newPage();
await p.goto('file:///home/user/alfredo/src/page.html?cfg=' + encodeURIComponent(JSON.stringify(
  {w:600,h:200,bg:'#fff',fg:'#000',lines:['x'],r:'none',fill:0.3})));
await p.waitForFunction(() => document.title === 'pronto');
const m = await p.evaluate(async () => {
  await document.fonts.ready;
  const S = 200;
  const cv = document.createElement('canvas'); cv.width = 600; cv.height = 400;
  const ctx = cv.getContext('2d');
  const ink = (ch) => {
    ctx.clearRect(0,0,600,400);
    ctx.font = `${S}px CF`; ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = '#000'; ctx.fillText(ch, 50, 300);
    const d = ctx.getImageData(0,0,600,400).data;
    let x0=1e9,x1=-1,y0=1e9,y1=-1;
    for (let y=0;y<400;y++) for (let x=0;x<600;x++) {
      if (d[(y*600+x)*4+3] > 40) { if(x<x0)x0=x; if(x>x1)x1=x; if(y<y0)y0=y; if(y>y1)y1=y; }
    }
    return {left:x0-50, right:x1-50, top:300-y1, height:y1-y0+1, width:x1-x0+1};
  };
  ctx.font = `${S}px CF`;
  return {
    S,
    adv_r: ctx.measureText('r').width,
    adv_n: ctx.measureText('n').width,
    adv_o: ctx.measureText('o').width,
    x_height: ink('x').height,
    stem: (() => {              // espessura do traço: corre uma linha no meio do 'n'
      ctx.clearRect(0,0,600,400); ctx.font = `${S}px CF`; ctx.textBaseline='alphabetic';
      ctx.fillStyle='#000'; ctx.fillText('n', 50, 300);
      const y = 300 - 55, d = ctx.getImageData(0,y,600,1).data;
      let run=0, best=0;
      for (let x=0;x<600;x++){ if(d[x*4+3]>40){run++; if(run>best)best=run;} else run=0; }
      return best;
    })(),
    r_ink: ink('r'),
    n_ink: ink('n'),
  };
});
console.log(JSON.stringify(m, null, 1));
await b.close();
