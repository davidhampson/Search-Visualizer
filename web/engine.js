// Reference check: search("Tourmaline") and the original Python program on a
// 128 × 128 field both visit 5,600 points and find -15.744653683643985 at (37,11).
// The optional alternate objectives and budget are browser-demo extensions.
// A visit includes two objective lookups. Cost is simulated and no wall-clock
// performance claim is implied. Revisit counts include repeated coordinates.
// Browser port of David Hampson's Search-Visualizer, revision 9b839856.
// Reproduce Python's string seeding, MT19937, random() and _randbelow().
class PythonRandom {
  static async fromString(seed) {
    const utf8 = new TextEncoder().encode(seed);
    const digest = new Uint8Array(await crypto.subtle.digest('SHA-512', utf8));
    const bytes = [...utf8, ...digest].reverse();
    const key = [];
    for (let i=0; i<bytes.length; i+=4) {
      key.push(((bytes[i] || 0) | (bytes[i+1] || 0)<<8 | (bytes[i+2] || 0)<<16 | (bytes[i+3] || 0)<<24) >>> 0);
    }
    return new PythonRandom(key);
  }
  constructor(key) {
    const s=this.state=new Uint32Array(624);
    s[0]=19650218;
    for(let i=1;i<624;i++) s[i]=Math.imul(s[i-1]^s[i-1]>>>30,1812433253)+i;
    let i=1,j=0;
    for(let k=Math.max(624,key.length);k>0;k--) {
      s[i]=(s[i]^Math.imul(s[i-1]^s[i-1]>>>30,1664525))+key[j]+j;
      if(++i===624){s[0]=s[623];i=1;} j=(j+1)%key.length;
    }
    for(let k=623;k>0;k--) {
      s[i]=(s[i]^Math.imul(s[i-1]^s[i-1]>>>30,1566083941))-i;
      if(++i===624){s[0]=s[623];i=1;}
    }
    s[0]=0x80000000;this.index=624;
  }
  word() {
    const s=this.state;
    if(this.index===624) {
      for(let i=0;i<624;i++){
        const y=(s[i]&0x80000000)|(s[(i+1)%624]&0x7fffffff);
        s[i]=s[(i+397)%624]^(y>>>1)^((y&1)?0x9908b0df:0);
      }
      this.index=0;
    }
    let y=s[this.index++];y^=y>>>11;y^=(y<<7)&0x9d2c5680;y^=(y<<15)&0xefc60000;y^=y>>>18;return y>>>0;
  }
  unit(){return ((this.word()>>>5)*67108864+(this.word()>>>6))/9007199254740992;}
  below(n){const shift=32-(32-Math.clz32(n));let x;do{x=this.word()>>>shift;}while(x>=n);return x;}
}
// The public breadth comparison reserves 500 moves for sampling, 4,000 for
// branching, 1,000 for refinement and 100 for the final path. A round gives
// each active crawler one move. Balanced reproduces the reference schedule.
const breadthPlans = {
  focused:  {starts:1, refine:1},
  balanced: {starts:4, refine:2},
  wide:     {starts:16, refine:8}
};
async function search(seed, {size=128,objective='valley',budget=11200,cost=1,greed=4,breadth='balanced'}={}) {
  const plan=breadthPlans[breadth];
  const rng=await PythonRandom.fromString(seed);
  const noise=()=>-10+20*rng.unit();
  const [a,b,c,d,field]=Array.from({length:5},()=>new Float64Array(size*size));
  const id=(x,y)=>x*size+y;
  for(let x=0;x<size;x++) for(let y=0;y<size;y++) {
    const i=id(x,y);
    a[i]=(x===0?(y===0?0:a[i-1]):(a[id(x-1,(y+size-1)%size)]+a[id(x-1,y)]+a[id(x-1,(y+1)%size)])/3)+noise();
  }
  for(let x=0;x<size;x++) for(let y=0;y<size;y++){
    const i=id(x,y);b[i]=(x===0?(y===0?0:b[i-1]):y===0?b[i-size]:(b[i-size]+b[i-1])/2)+noise();
  }
  for(let y=0;y<size;y++) for(let x=0;x<size;x++){
    const i=id(x,y);c[i]=(y===0?0:(c[id((x+size-1)%size,y-1)]+c[id(x,y-1)]+c[id((x+1)%size,y-1)])/3)+noise();
  }
  for(let x=0;x<size;x++) for(let y=size-1;y>=0;y--){
    const i=id(x,y);d[i]=(x===0?(y===size-1?0:d[i+1]):y===size-1?d[i-size]:(d[i-size]+d[i+1])/2)+noise();
  }
  let globalIndex=0;
  for(let i=0;i<field.length;i++){const raw=(a[i]+b[i]+c[i]+d[i])/4;
    field[i]=objective==='peak'?-raw:objective==='contour'?Math.abs(raw):raw;if(field[i]<field[globalIndex])globalIndex=i;}
  const moves=[[1,0],[0,1],[1,1],[-1,0],[0,-1],[-1,1],[1,-1],[-1,-1]];
  const visits=[];let best=Infinity,bestIndex;
  function run(crawlers,greed,rounds,stage){
    for(let k=0;k<rounds;k++) crawlers.forEach((agent,lane)=>{
      if ((visits.length+1)*2*cost>budget) return;
      const index=id(agent.x,agent.y);agent.value=field[index];
      if(agent.value<best){best=agent.value;bestIndex=index;}
      const [dx,dy]=moves[rng.below(8)];
      rng.below(50); // The Python list repetition consumes a draw but leaves dx,dy unchanged.
      const x=Math.max(0,Math.min(size-1,agent.x+dx)),y=Math.max(0,Math.min(size-1,agent.y+dy));
      const next=field[id(x,y)];
      if(next<agent.value || Math.pow(2.71828,-(next-agent.value)/greed)<rng.unit()){agent.x=x;agent.y=y;}
      visits.push({index:id(agent.x,agent.y),from:index,stage,lane,bestIndex});
    });
  }
  const children=(pool,top,count)=>pool.slice().sort((a,b)=>a.value-b.value).slice(0,top)
    .flatMap(({x,y})=>Array.from({length:count},()=>({x,y,value:0})));
  const first=Array.from({length:500},()=>({x:rng.below(size),y:rng.below(size),value:0}));
  run(first,100,1,0);
  const second=children(first,plan.starts,2);run(second,greed,4000/second.length,1);
  const third=children(second,plan.refine,1);run(third,10,1000/third.length,2);
  run([third.slice().sort((a,b)=>a.value-b.value)[0]],1000,100,3);
  return {size,field,visits,bestIndex,globalIndex,cost,budget,objective,contributions:[a,b,c,d]};
}

// The original generator averages four directional random fields. Partial
// surfaces use the same denominator and objective as the finished field.
function terrainLayers(run) {
  const {size, contributions, objective} = run;
  const sum = new Float64Array(size * size);
  return contributions.map((part, layer) => {
    let z = part.map((value, index) => {
      sum[index] += value;
      if (layer === 3) return run.field[index];
      const raw = sum[index] / 4;
      return objective === 'peak' ? -raw : objective === 'contour' ? Math.abs(raw) : raw;
    });
    let buffer = new Float64Array(z.length);
    // This smoothing is for display only. Search always uses the original field.
    for (let pass = 0; pass < 16; pass++) {
      for (let x = 0; x < size; x++) for (let y = 0; y < size; y++) {
        const i = x * size + y;
        buffer[i] = (z[i] * 4 + z[Math.max(0,x-1)*size+y] + z[Math.min(size-1,x+1)*size+y] +
          z[x*size+Math.max(0,y-1)] + z[x*size+Math.min(size-1,y+1)]) / 8;
      }
      [z, buffer] = [buffer, z];
    }
    return z;
  });
}
