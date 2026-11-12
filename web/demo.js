'use strict';
const get=id=>document.getElementById(id);
const canvas=document.querySelector('canvas'),ctx=canvas.getContext('2d');
const background=document.createElement('canvas'),ink=document.createElement('canvas');
for(const layer of [background,ink]){layer.width=canvas.width;layer.height=canvas.height;}
const bg=background.getContext('2d'),trails=ink.getContext('2d');
const inks=['#1769a5','#c93b58','#007f77','#ad5519','#8742b0','#3c7340','#cc447c','#414ca6'];
function laneColor(stage,lane){
  if(stage===3)return '#36214e';
  if(stage===2)return inks[(lane+2)%inks.length];
  if(lane<inks.length)return inks[lane];
  return 'hsl('+Math.round((lane*137.508)%360)+' 67% 37%)';
}
const titles=['Sampling starting points','Following promising starts','Refining the best paths','Tracing the final path'];
let animationFrame=0;
let result,points,heads=new Map(),stage=-1,cursor=0,playing=false,last=0,accum=0,generation=0;
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const phaseMs = 290;
const buildMs = 4 * phaseMs;
let surface, mesh = [], layerEnds = [], buildTime = 0, painted = 0;
function resetTerrain(){
  bg.fillStyle='#f1ede7';
  bg.fillRect(0,0,background.width,background.height);
  painted=0;
}
function projectTerrain(run) {
  const {size:n} = run;
  const angle=Math.max(0,Math.min(1.45,(canvas.height/canvas.width-.63)*1.65));
  const cs=Math.cos(angle),sn=Math.sin(angle);
  const field=Array.from(surface,(v,i)=>{
    const x=Math.floor(i/n),y=i%n,u=.85*x+.52*y,w=-.42*x+.53*y-v*1.25;
    return [u*cs-w*sn,u*sn+w*cs];
  });
  const xs=field.map(p=>p[0]),ys=field.map(p=>p[1]);
  const left=Math.min(...xs),right=Math.max(...xs),top=Math.min(...ys),bottom=Math.max(...ys);
  const scale=Math.min(canvas.width*.97/(right-left),canvas.height*.94/(bottom-top));
  for(const p of field){
    p[0]=(p[0]-(right+left)/2)*scale+canvas.width/2;
    p[1]=(p[1]-(bottom+top)/2)*scale+canvas.height/2;
  }
  mesh=[];layerEnds=[];
  const add=(vertices,color,width)=>{
    const path=new Path2D();
    vertices.forEach((p,i)=>i?path.lineTo(...p):path.moveTo(...p));
    mesh.push({path,vertices,color,width});
  };
  // Put the broad grid down first and bisect the gaps in each following pass.
  for(let layer=0;layer<4;layer++){
    const rowStep=16>>layer,colStep=96>>layer;
    for(let y=layer?rowStep:0;y<n;y+=layer?2*rowStep:rowStep){
      add(Array.from({length:n},(_,x)=>field[x*n+y]),y%8?'#bdb2be':'#9c8aa1',y%8?1:1.4);
    }
    for(let x=layer?colStep:0;x<n;x+=layer?2*colStep:colStep){
      add(Array.from({length:n},(_,y)=>field[x*n+y]),'#c2b9c4',.7);
    }
    layerEnds.push(mesh.length);
  }
  resetTerrain();
  return field;
}
function drawTerrain(time) {
  const layer=Math.min(3,Math.floor(time/phaseMs));
  const first=layer?layerEnds[layer-1]:0;
  const progress=first+(time/phaseMs-layer)*(layerEnds[layer]-first);
  const complete=Math.floor(progress);
  if(complete<painted)resetTerrain();
  while(painted<complete){
    const line=mesh[painted++];
    bg.strokeStyle=line.color;bg.lineWidth=line.width;bg.stroke(line.path);
  }
  if(time<buildMs){
    ctx.drawImage(background,0,0);
    const line=mesh[complete],fraction=progress-complete;
    if(fraction>0 && line){
      const vertices=line.vertices,pos=fraction*(vertices.length-1),i=Math.floor(pos);
      ctx.beginPath();ctx.moveTo(...vertices[0]);
      for(let j=1;j<=i;j++)ctx.lineTo(...vertices[j]);
      const a=vertices[i],b=vertices[i+1],t=pos-i;
      ctx.lineTo(a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]));
      ctx.strokeStyle=line.color;ctx.lineWidth=line.width;ctx.stroke();
    }
    get('stage').textContent='Building terrain';
    get('stats').textContent='Layer '+(layer+1)+' of 4';
  }
}
function prepareReport(run) {
  // Count the cells scored for the best-so-far record, once per grid coordinate.
  const distinct = new Set(run.visits.map(visit => visit.from)).size;
  const total = run.field.length;
  const best = run.field[run.bestIndex], optimum = run.field[run.globalIndex];
  const gap = best - optimum;
  get('coverage').textContent = (100 * distinct / total).toFixed(1) + '%';
  get('cell-count').textContent = distinct.toLocaleString() + ' of ' + total.toLocaleString() + ' cells';
  get('gap').textContent = gap === 0 ? 'Exact match' : '+' + Number(gap.toPrecision(3)) + (gap === 1 ? ' point' : ' points');
  get('comparison').textContent = 'Best ' + best.toFixed(3) + ' · Optimum ' + optimum.toFixed(3);
}
function show(target){
  if(!result)return;
  if(target<cursor || target===0){ink.width=canvas.width;cursor=0;stage=-1;heads.clear();}
  const unit=canvas.width/canvas.clientWidth;
  while(cursor<target){
    const v=result.visits[cursor++],pt=points[v.index];
    if(stage!==v.stage){heads.clear();stage=v.stage;}
    if(stage===0){
      trails.fillStyle='#8c798f';
      trails.beginPath();trails.arc(...points[v.from],1.25*unit,0,Math.PI*2);trails.fill();
    }else{
      const color=laneColor(stage,v.lane);
      trails.lineCap='round';
      trails.beginPath();trails.moveTo(...points[v.from]);trails.lineTo(...pt);
      trails.strokeStyle=color;trails.lineWidth=2.6*unit;trails.stroke();
      heads.set(v.lane,{pt,color});
    }
  }
  ctx.drawImage(background,0,0);ctx.drawImage(ink,0,0);
  for(const {pt,color} of heads.values()){
    ctx.beginPath();ctx.arc(...pt,3.8*unit,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();
    ctx.lineWidth=1.4*unit;ctx.strokeStyle='white';ctx.stroke();
  }
  const done=target===result.visits.length,lastVisit=result.visits[target-1];
  if(lastVisit){
    const [x,y]=points[lastVisit.bestIndex];
    ctx.beginPath();
    for(let k=0;k<10;k++){
      const angle=k*Math.PI/5-Math.PI/2,rad=(k%2?3.8:8)*unit;
      const a=x+rad*Math.cos(angle),b=y+rad*Math.sin(angle);
      if(k)ctx.lineTo(a,b);else ctx.moveTo(a,b);
    }
    ctx.closePath();ctx.strokeStyle='white';ctx.lineWidth=2.8*unit;ctx.stroke();
    ctx.fillStyle='#3a2045';ctx.fill();
  }
  get('stage').textContent=target===0?'Ready to explore':done?'Search complete':titles[stage];
  const score=lastVisit?' · Best '+result.field[lastVisit.bestIndex].toFixed(2):'';
  get('stats').textContent=target.toLocaleString()+' / '+result.visits.length.toLocaleString()+' moves'+score;
  get('scrub').value=target;
  get('report').hidden=!done;
  if(done)stop();
}
function stop(){cancelAnimationFrame(animationFrame);playing=false;get('play').textContent=cursor===result?.visits.length?'Replay':'Play';}
function tick(now){
  if(!playing)return;
  const delta=Math.max(0,Math.min(80,now-last));
  last=now;
  if(buildTime<buildMs){
    buildTime=Math.min(buildMs,buildTime+delta);
    drawTerrain(buildTime);
    if(buildTime===buildMs){
      show(0);
    }
    animationFrame=requestAnimationFrame(tick);
    return;
  }
  accum+=delta*.46;
  const advance=Math.floor(accum);accum-=advance;
  if(advance)show(Math.min(result.visits.length,cursor+advance));
  if(playing)animationFrame=requestAnimationFrame(tick);
}
function play(){
  if(playing || !result)return;
  if(cursor===result.visits.length){
    show(0);
    buildTime=buildMs;
    drawTerrain(buildTime);
  }
  playing=true;last=performance.now();accum=0;get('play').textContent='Pause';animationFrame=requestAnimationFrame(tick);
}
async function initialize(){
  get('report').hidden=true;
  const token=++generation;stop();get('play').disabled=true;get('scrub').disabled=true;
  const breadth=document.querySelector('[name=breadth]:checked').value;
  const crawlers=breadthPlans[breadth].starts*2;
  get('allocation').textContent=crawlers+' branching crawlers × '+(4000/crawlers).toLocaleString()+' moves each';
  try {
    const run=await search('Tourmaline',{breadth});
    if(token!==generation)return;
    const first=!result;
    result=run;
    prepareReport(run);
    if(first){surface=terrainLayers(run).at(-1);points=projectTerrain(run);}
    buildTime=first && !reducedMotion.matches?0:buildMs;
    get('scrub').max=run.visits.length;get('play').disabled=false;get('scrub').disabled=false;
    show(0);drawTerrain(buildTime);
    if(reducedMotion.matches)show(run.visits.length);
    else{if(buildTime===buildMs)show(0);play();}
  } catch(error){if(token===generation)get('stage').textContent='Unable to prepare this search.';console.error(error);}
}
for(const radio of document.querySelectorAll('[name=breadth]'))radio.addEventListener('change',initialize);
get('play').addEventListener('click',()=>playing?stop():play());
get('scrub').addEventListener('input',()=>{stop();buildTime=buildMs;drawTerrain(buildTime);show(Number(get('scrub').value));stop();});
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
new ResizeObserver(([entry])=>{
  const box=entry.contentRect;
  if(box.width<1 || box.height<1)return;
  const h=Math.round(canvas.width*box.height/box.width);
  if(canvas.height===h)return;
  for(const layer of [canvas,background,ink])layer.height=h;
  if(result){
    const position=cursor,resume=playing;
    points=projectTerrain(result);drawTerrain(buildTime);show(0);show(position);if(buildTime<buildMs)drawTerrain(buildTime);
    if(resume && !playing)play();
  }
}).observe(document.querySelector('.terrain'));
reducedMotion.addEventListener('change',()=>{
  if(reducedMotion.matches && result){stop();buildTime=buildMs;drawTerrain(buildTime);show(result.visits.length);}
});
initialize();
