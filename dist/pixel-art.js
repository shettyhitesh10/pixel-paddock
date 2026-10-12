/* Original pixel artwork. Every visible contour is drawn on a one- or two-pixel grid.
   Shared SVG definitions keep the six genuinely different poses compact. */
(function () {
  'use strict';
  let serial = 0;
  const artworkCache = new Map();
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const color = (c, fallback) => /^#[0-9a-f]{6}$/i.test(c || '') ? c : fallback;
  function tint(hex, amount) { const n=parseInt(hex.slice(1),16); return '#'+[n>>16,(n>>8)&255,n&255].map(v=>Math.max(0,Math.min(255,v+amount)).toString(16).padStart(2,'0')).join(''); }
  class Pixels {
    constructor(w,h) { this.w=w;this.h=h;this.p=new Array(w*h); }
    dot(x,y,c) { x=Math.round(x);y=Math.round(y);if(x>=0&&x<this.w&&y>=0&&y<this.h)this.p[y*this.w+x]=c; }
    box(x,y,w,h,c) { for(let j=y;j<y+h;j++)for(let i=x;i<x+w;i++)this.dot(i,j,c); }
    poly(points,c) { const min=Math.max(0,Math.floor(Math.min(...points.map(p=>p[1])))),max=Math.min(this.h-1,Math.ceil(Math.max(...points.map(p=>p[1]))));for(let y=min;y<=max;y++){const hits=[];for(let i=0;i<points.length;i++){const a=points[i],b=points[(i+1)%points.length];if((a[1]<=y+.5&&b[1]>y+.5)||(b[1]<=y+.5&&a[1]>y+.5))hits.push(a[0]+(y+.5-a[1])*(b[0]-a[0])/(b[1]-a[1]));}hits.sort((a,b)=>a-b);for(let i=0;i<hits.length;i+=2)for(let x=Math.ceil(hits[i]-.5);x<hits[i+1]-.5;x++)this.dot(x,y,c);} }
    ellipse(cx,cy,rx,ry,c) { for(let y=Math.floor(cy-ry);y<=cy+ry;y++)for(let x=Math.floor(cx-rx);x<=cx+rx;x++)if(((x-cx)/rx)**2+((y-cy)/ry)**2<=1)this.dot(x,y,c); }
    line(x0,y0,x1,y1,c,width=1) { const n=Math.max(Math.abs(x1-x0),Math.abs(y1-y0));for(let i=0;i<=n;i++)this.box(Math.round(x0+(x1-x0)*i/(n||1)),Math.round(y0+(y1-y0)*i/(n||1)),width,width,c); }
    svg() { const rects=[];let previous=new Map();for(let y=0;y<this.h;y++){const next=new Map();for(let x=0;x<this.w;){const c=this.p[y*this.w+x];if(!c){x++;continue;}let end=x+1;while(end<this.w&&this.p[y*this.w+end]===c)end++;const key=x+':'+(end-x)+':'+c;let r=previous.get(key);if(r)r.h++;else{r={x,y,w:end-x,h:1,c};rects.push(r);}next.set(key,r);x=end;}previous=next;}return rects.map(r=>`<rect x="${r.x}" y="${r.y}" width="${r.w}" height="${r.h}" fill="${r.c}"/>`).join(''); }
  }
  const people = {
    'toto-wolff':{skin:'#d2a582',hair:'#292420',hairStyle:'swept',face:'long',eyes:'#465050',age:true},
    'fred-vasseur':{skin:'#dfb493',hair:'#928d82',hairStyle:'receding',face:'wide',age:true},
    'andrea-stella':{skin:'#c99a77',hair:'#625f59',hairStyle:'short',face:'long',facialHair:'stubble',age:true},
    'laurent-mekies':{skin:'#c79c7b',hair:'#3c3730',hairStyle:'short',face:'long',facialHair:'beard',glasses:true},
    'alan-permane':{skin:'#dbad8e',hair:'#b9b2a3',hairStyle:'receding',face:'wide',age:true},
    'flavio-briatore':{skin:'#c99c7e',hair:'#c5c1b6',hairStyle:'wavy',face:'wide',facialHair:'beard',age:true},
    'ayao-komatsu':{skin:'#c59b73',hair:'#252321',hairStyle:'short',face:'wide',eyes:'#252321',age:true},
    'mattia-binotto':{skin:'#cf9e7b',hair:'#35322c',hairStyle:'curly',face:'long',glasses:true,age:true},
    'james-vowles':{skin:'#e0b496',hair:'#76614b',hairStyle:'swept',face:'long',age:true},
    'adrian-newey':{skin:'#dca889',hair:'#b1a99a',hairStyle:'bald',face:'long',age:true},
    'marcin-budkowski':{skin:'#d5ad8e',hair:'#463c32',hairStyle:'receding',face:'wide',facialHair:'stubble',age:true},
    antonelli:{face:'round',eyes:'#554735'},russell:{face:'long',eyes:'#5b8591'},
    hamilton:{face:'wide',eyes:'#3d291f',earring:true},leclerc:{face:'long',eyes:'#6e8472'},
    norris:{face:'round',eyes:'#668c81'},max_verstappen:{face:'wide',eyes:'#6a8b91'},
    piastri:{face:'round',eyes:'#55412e'},hadjar:{face:'round',eyes:'#312820'},
    lawson:{face:'long',eyes:'#668197'},gasly:{face:'long',eyes:'#6d8fa1'},
    arvid_lindblad:{face:'long',eyes:'#463528'},colapinto:{face:'round',eyes:'#594832'},
    bearman:{face:'long',eyes:'#584a36'},bortoleto:{face:'round',eyes:'#463729'},
    hulkenberg:{face:'long',eyes:'#5e8791'},ocon:{face:'long',eyes:'#4b342a'},
    alonso:{face:'wide',eyes:'#514536'},sainz:{face:'long',eyes:'#433127'},
    albon:{face:'long',eyes:'#3a2922'},stroll:{face:'wide',eyes:'#4a382b'},
    bottas:{face:'wide',eyes:'#6b9099'},perez:{face:'round',eyes:'#3d2e22'}
  };
  const kit = {
    mercedes:['#17232a','#00d2be','#e2ecec'],ferrari:['#ce1424','#ffe34b','#f1ece5'],
    mclaren:['#ec7921','#151c27','#f7e9d8'],red_bull:['#20284c','#dc2942','#f2d849'],
    racing_bulls:['#e9ebed','#264ee1','#c8dbef'],rb:['#e9ebed','#264ee1','#c8dbef'],alpine:['#135aa8','#ee90bb','#eeeaf4'],
    haas:['#dedfe0','#c82637','#232a35'],audi:['#c52a32','#262b30','#eceded'],
    aston_martin:['#166259','#b9d742','#e3e9d9'],williams:['#1854b8','#36b5d6','#eef3f6'],
    cadillac:['#d6d4c8','#252a33','#dfb649']
  };
  function palette(item,teamColor,principal) { const k=kit[item.teamId]||[color(teamColor,'#3567ac'),'#dde6e8','#f4f2e8'];const base=principal?'#26323b':k[0];return {base,shadow:tint(base,-34),dark:tint(base,-56),light:tint(base,29),shine:tint(base,52),trim:k[1],white:k[2],black:'#101923'}; }
  function body(item,p,principal) {
    const g=new Pixels(56,88),O='#0b111a';
    // Racing boots and separated legs, with articulated knee and shin panels.
    g.poly([[20,57],[29,58],[28,82],[18,83],[19,75]],O);g.poly([[29,57],[36,57],[38,82],[28,83]],O);
    g.poly([[21,58],[28,59],[26,79],[20,79]],p.base);g.poly([[30,58],[35,58],[36,79],[30,79]],p.base);
    g.poly([[21,60],[24,61],[22,78],[20,78]],p.light);g.poly([[25,63],[28,62],[26,79],[24,79]],p.shadow);
    g.poly([[31,61],[33,60],[34,78],[31,78]],p.light);g.line(35,63,36,77,p.dark);
    g.box(21,68,5,2,p.shadow);g.box(30,68,5,2,p.shadow);g.line(22,69,24,69,p.shine);g.line(31,69,33,69,p.shine);
    g.poly([[19,78],[26,78],[26,85],[16,85],[16,82]],p.black);g.poly([[30,78],[37,78],[40,83],[40,85],[29,85]],p.black);
    g.box(17,83,9,1,'#54616b');g.box(30,83,9,1,'#54616b');g.line(20,79,24,80,p.trim);g.line(31,79,35,80,p.trim);g.box(17,85,9,1,O);g.box(30,85,10,1,O);
    // Tailored shoulders, collar, rib panels, zipper, belts and seam highlights.
    g.poly([[23,32],[32,32],[38,35],[39,41],[36,48],[35,59],[20,59],[19,48],[16,41],[17,35]],O);
    g.poly([[23,33],[31,33],[37,36],[37,43],[34,49],[34,58],[21,58],[21,48],[18,42],[18,36]],p.base);
    g.poly([[19,36],[22,35],[24,41],[23,52],[24,57],[21,57],[20,45]],p.light);
    g.poly([[33,35],[36,37],[35,46],[32,51],[33,57],[30,57],[30,39]],p.shadow);
    g.poly([[24,36],[27,38],[27,55],[24,55]],p.shine);g.poly([[28,38],[31,36],[30,54],[28,55]],p.light);
    g.poly([[23,33],[26,35],[29,35],[32,33],[32,36],[29,39],[26,39],[23,36]],p.black);
    g.line(24,34,26,36,p.trim);g.line(29,36,31,34,p.trim);g.line(27,38,27,55,'#778a95');g.box(27,38,1,2,'#e1e6e8');
    g.line(21,48,23,54,p.shadow);g.line(32,49,31,54,p.dark);g.box(21,55,13,3,p.black);g.box(22,56,4,1,p.trim);g.box(28,55,3,3,'#87929a');g.box(29,56,1,1,'#cdd7d8');
    g.line(19,37,21,39,p.white);g.line(34,37,36,39,p.trim);g.box(22,41,4,3,p.white);g.box(22,42,3,1,p.trim);g.box(29,41,4,3,p.trim);g.box(30,42,2,1,p.dark);
    g.box(24,46,8,3,p.white);g.box(25,47,2,1,p.dark);g.box(28,47,3,1,p.dark);g.box(24,50,3,2,p.trim);g.box(29,50,3,2,p.white);
    if(principal){g.box(24,46,8,5,p.base);g.line(22,52,25,53,p.light);g.line(30,53,33,52,p.dark);g.box(21,57,13,2,'#131c25');g.box(27,57,2,2,'#9ba8ae');}
    return g.svg();
  }
  function head(a) {
    const g=new Pixels(44,58),s=color(a.skin,'#dfb494'),h=color(a.hair,'#4c3324'),dark=tint(s,-69),shade=tint(s,-34),lit=tint(s,23),hi=tint(s,38),hairD=tint(h,-19),hairL=tint(h,32),wide=a.face==='wide',long=a.face==='long',L=wide?5:7,R=wide?37:35;
    // Neck and face are individually shaded, not a single flat ellipse.
    g.poly([[15,43],[29,43],[29,57],[15,57]],dark);g.box(17,45,10,10,s);g.box(17,47,3,7,shade);g.box(21,47,6,5,lit);
    g.ellipse(L,29,3,7,dark);g.ellipse(R,29,3,7,dark);g.ellipse(L,28,2,5,s);g.ellipse(R,28,2,5,s);g.box(L,27,1,4,shade);g.box(R-1,27,1,4,shade);
    g.poly([[L+1,13],[12,7],[30,7],[R-1,14],[R,31],[R-4,43],[27,long?49:46],[17,long?49:46],[L+4,41],[L,30]],dark);
    g.poly([[L+2,14],[13,9],[29,9],[R-2,15],[R-1,31],[R-5,42],[26,long?47:44],[18,long?47:44],[L+5,40],[L+1,30]],s);
    g.poly([[12,16],[17,12],[27,12],[31,17],[30,28],[25,32],[15,30],[11,24]],lit);
    g.poly([[L+1,22],[11,25],[12,35],[17,41],[18,45],[13,41],[9,34]],shade);
    g.poly([[32,17],[R-1,20],[R-1,31],[31,40],[27,44],[29,36],[30,26]],shade);
    g.line(15,16,18,14,hi);g.line(24,14,28,16,hi);g.box(13,32,5,2,lit);g.box(27,32,4,2,lit);
    // Cheekbones, brow sockets, whites, colored irises and one-pixel highlights.
    g.line(10,23,17,22,shade);g.line(25,22,32,23,shade);g.line(10,21,17,20,hairD);g.line(25,20,32,21,hairD);g.box(11,21,6,1,h);
    g.box(11,24,7,3,dark);g.box(25,24,7,3,dark);g.box(12,24,5,2,'#efece0');g.box(26,24,5,2,'#efece0');g.box(14,24,2,3,color(a.eyes,'#604838'));g.box(27,24,2,3,color(a.eyes,'#604838'));g.dot(14,24,'#f8f4e8');g.dot(27,24,'#f8f4e8');g.dot(15,26,'#19201f');g.dot(28,26,'#19201f');
    g.line(21,23,19,32,shade);g.line(23,24,24,32,lit);g.box(19,32,6,2,shade);g.dot(20,33,dark);g.dot(24,33,dark);g.box(21,31,2,2,hi);
    g.line(16,38,20,37,tint(s,-83));g.line(20,37,25,37,tint(s,-83));g.line(25,37,28,38,tint(s,-83));g.box(19,38,6,1,tint(s,-42));g.box(19,40,7,1,lit);g.line(19,43,26,43,shade);
    if(a.age){g.line(13,18,18,17,shade);g.line(24,17,29,18,shade);g.line(10,28,13,29,shade);g.line(29,29,32,28,shade);g.line(15,34,14,37,shade);g.line(28,34,29,37,shade);g.box(17,41,1,3,shade);}
    if(a.facialHair==='stubble'){for(let y=35;y<45;y+=2)for(let x=12;x<32;x+=3)if((x<17||x>26||y>40)&&g.p[y*44+x])g.dot(x,y,tint(s,-49));}
    if(a.facialHair==='beard') {g.poly([[10,32],[13,35],[16,39],[19,41],[25,41],[29,37],[33,32],[32,41],[27,47],[17,47],[12,41]],hairD);g.line(14,38,18,44,h);g.line(27,43,31,36,h);g.line(18,45,25,45,hairL);g.box(17,36,10,2,h);g.box(19,38,6,1,tint(s,-45));g.box(20,39,4,1,lit);}
    if(a.facialHair==='moustache'){g.poly([[15,35],[21,34],[27,35],[29,38],[24,37],[21,36],[17,38],[14,38]],hairD);g.line(16,35,20,35,hairL);g.line(23,35,26,36,h);}
    // Distinct hairstyles: sculpted sweeps, curls, cornrows, receding hair and a mullet.
    const style=a.hairStyle||'short';
    if(style==='bald'||style==='receding'){g.poly([[8,14],[10,10],[12,9],[11,19],[9,23],[7,23]],h);g.poly([[31,9],[34,12],[36,19],[35,23],[33,20]],h);if(style==='receding'){g.line(12,8,30,7,h);g.line(15,7,28,6,hairL);}g.line(16,10,26,10,hi);}
    else {g.poly([[6,16],[7,9],[12,5],[19,3],[28,4],[34,8],[37,15],[35,24],[32,19],[31,13],[24,12],[17,14],[12,13],[10,21],[7,24]],hairD);g.poly([[8,12],[13,7],[21,5],[30,7],[34,11],[31,14],[23,11],[16,13],[11,15]],h);
      if(style==='swept'){g.poly([[9,11],[19,5],[29,5],[33,8],[22,8],[14,12]],hairL);g.line(15,9,25,6,tint(h,49));g.line(13,14,23,10,hairD);g.line(24,11,32,12,hairL);}
      if(style==='short'){g.line(11,9,31,9,hairL);g.line(11,12,20,11,hairL);g.box(31,14,3,6,h);}
      if(style==='curly'||style==='wavy'){for(const [x,y]of [[9,9],[14,6],[20,5],[27,6],[32,9],[11,13],[18,11],[25,10],[32,14]]){g.ellipse(x,y,3,3,h);g.line(x-1,y-2,x+1,y-2,hairL);g.dot(x+2,y+1,hairD);}if(style==='wavy'){g.line(10,11,20,7,hairL);g.line(22,8,31,11,hairL);}}
      if(style==='braids'){g.poly([[7,15],[9,8],[16,4],[27,4],[34,8],[36,15],[33,14],[30,11],[13,11],[10,15]],h);for(let x=11;x<=31;x+=4){g.line(x,7,x-2,14,hairL);g.line(x+1,7,x-1,14,hairD);}for(let y=15;y<45;y+=3){g.box(5,y,3,2,h);g.dot(6,y,hairL);g.box(36,y,3,2,h);g.dot(37,y,hairL);}g.box(5,44,3,3,hairD);g.box(36,44,3,3,hairD);}
      if(style==='mullet'){g.poly([[6,18],[10,17],[11,32],[8,46],[3,46],[5,36]],h);g.poly([[33,16],[37,17],[39,38],[41,47],[35,46],[32,33]],h);g.line(6,27,5,43,hairL);g.line(36,27,39,44,hairL);g.line(11,9,30,8,hairL);g.line(16,7,28,6,tint(h,48));}
    }
    if(a.glasses){g.box(9,23,10,6,'#212b31');g.box(24,23,10,6,'#212b31');g.box(11,24,6,3,'#c2bdac');g.box(26,24,6,3,'#c2bdac');g.box(13,25,3,2,'#383e3c');g.box(27,25,3,2,'#383e3c');g.line(19,24,24,24,'#212b31');g.line(10,24,13,24,'#f3ede1');g.line(26,24,28,24,'#f3ede1');}
    if(a.earring){g.box(4,31,2,3,'#f6e5a0');g.dot(4,31,'#fff9df');g.box(38,31,2,3,'#f6e5a0');}
    return g.svg();
  }
  function limb(g,start,elbow,end,p,skin,principal,hand='fist') {
    // Polygon rasterization gives angled sleeves hard pixel stair steps.
    const segment=(a,b,width,base)=>{const dx=b[0]-a[0],dy=b[1]-a[1],len=Math.hypot(dx,dy)||1,nx=-dy/len*width,ny=dx/len*width;g.poly([[a[0]+nx,a[1]+ny],[b[0]+nx,b[1]+ny],[b[0]-nx,b[1]-ny],[a[0]-nx,a[1]-ny]],'#111821');g.poly([[a[0]+nx*.65,a[1]+ny*.65],[b[0]+nx*.65,b[1]+ny*.65],[b[0]-nx*.65,b[1]-ny*.65],[a[0]-nx*.65,a[1]-ny*.65]],base);g.line(a[0]-nx*.5,a[1]-ny*.5,b[0]-nx*.5,b[1]-ny*.5,p.light,1);};
    segment(start,elbow,4,p.base);segment(elbow,end,3.4,p.base);g.box(elbow[0]-1,elbow[1]-1,3,2,p.shadow);
    const handColor=principal?skin:p.white,hshade=principal?tint(skin,-35):'#89969e';g.box(end[0]-2,end[1]-2,5,5,hshade);g.box(end[0]-2,end[1]-2,4,3,handColor);g.box(end[0]-1,end[1]-2,2,1,principal?tint(skin,20):'#f8f8ed');
    if(hand==='wave'){g.box(end[0]-3,end[1]-5,1,4,handColor);g.box(end[0]-1,end[1]-6,1,4,handColor);g.box(end[0]+1,end[1]-5,1,4,handColor);g.box(end[0]+3,end[1]-4,1,4,handColor);g.dot(end[0]+3,end[1],hshade);}
    if(hand==='point'){g.box(end[0],end[1]-7,2,6,handColor);g.box(end[0],end[1]-7,1,1,'#fff8df');}
    g.line(end[0]-2,end[1]+1,end[0]+1,end[1]+1,hshade);
  }
  function arms(item,p,a,principal,frame,type) {
    const g=new Pixels(56,88),s=color(a.skin,'#dfb494');let left=[[18,36],[16,46],[16,54]],right=[[37,36],[40,46],[39,54]],hand='fist';
    const cycle=[0,1,2,3,4,2][frame];
    if(frame>0){
      if(type==='wave'){right=[[37,36],[44,32],[42+cycle,21-cycle]];hand='wave';}
      else if(type==='salute'){right=[[37,36],[46,31],[39,20+cycle]];hand='wave';}
      else if(type==='shrug'){left=[[18,36],[12,39],[7,31+cycle]];right=[[37,36],[44,39],[49,31+cycle]];hand='wave';}
      else if(type==='point'){right=[[37,36],[44,29],[43,18-cycle]];hand='point';left=[[18,36],[13,43],[21,45]];}
      else if(type==='celebrate'){if(item.id==='russell'){left=[[18,36],[9,35-cycle],[2,35-cycle]];right=[[37,36],[45,35-cycle],[53,35-cycle]];}else{left=[[18,36],[10,29],[12-cycle,19-cycle]];right=[[37,36],[44,29],[43+cycle,19-cycle]];}}
      else if(type==='dance'||type==='shuffle'){left=[[18,36],[12,40-cycle],[17-cycle,33+cycle]];right=[[37,36],[43,40+cycle],[39+cycle,34-cycle]];}
      else {right=[[37,36],[41,43],[32,43-cycle]];left=[[18,36],[15,44],[18,51]];}
    }
    limb(g,...left,p,s,principal,type==='shrug'?hand:'fist');limb(g,...right,p,s,principal,hand);
    if(principal){ // Pit-wall headset: a shaded radio with screen and aerial in the left hand.
      const [hx,hy]=left[2];g.box(hx-2,hy-1,5,8,'#111820');g.box(hx-1,hy,3,3,'#4b797f');g.box(hx-1,hy+4,3,2,'#777f84');g.line(hx+1,hy-5,hx+1,hy-1,'#303e47');g.dot(hx,hy+4,p.trim);
    } else if(type==='wave'||type==='point'||type==='nod'||type==='salute') {
      // A small full-face helmet hangs from the other hand; its visor and paint
      // are pixels too, and follow the hand instead of moving the whole sprite.
      const [hx,hy]=left[2],cx=hx-2,cy=hy+5;
      g.ellipse(cx,cy,6,6,'#111820');g.ellipse(cx,cy-1,5,5,p.trim);g.poly([[cx-5,cy],[cx-2,cy+4],[cx+5,cy+3],[cx+5,cy]],p.white);
      g.box(cx-4,cy-2,8,3,'#172c40');g.line(cx-3,cy-2,cx+2,cy-2,'#72b6c7');g.line(cx-2,cy-4,cx+2,cy-4,'#fff0c8');g.box(cx+3,cy-1,2,2,p.shadow);g.line(cx-3,cy+3,cx+3,cy+3,p.base);
    } else if(type==='celebrate'&&item.id!=='russell') {
      const [hx,hy]=right[2],gold='#ddaa3d',light='#ffe8a0',shade='#956121';
      g.box(hx-1,hy-5,2,4,gold);g.box(hx-3,hy-2,6,2,shade);g.box(hx-2,hy-2,4,1,light);
      g.poly([[hx-4,hy-12],[hx+4,hy-12],[hx+3,hy-7],[hx,hy-5],[hx-3,hy-7]],gold);g.box(hx-3,hy-11,2,4,light);g.box(hx+2,hy-10,1,3,shade);g.line(hx-4,hy-12,hx+3,hy-12,light);g.line(hx-5,hy-10,hx-5,hy-7,gold);g.line(hx+5,hy-10,hx+5,hy-7,gold);g.dot(hx-4,hy-6,gold);g.dot(hx+4,hy-6,gold);
    }
    return g.svg();
  }
  function person(item,kind,teamColor) {
    item=item||{};const principal=kind==='principal'||kind==='principals',a={skin:'#dfb494',hair:'#4c3324',hairStyle:'short',facialHair:'none',...(people[item.id]||{}),...(item.appearance||{})},p=palette(item,teamColor,principal),id='ppa'+(++serial),type=item.id==='max_verstappen'?'point':item.animation?.type||'wave';
    const key=JSON.stringify([item.id,item.teamId,principal,teamColor,a,type]);let art=artworkCache.get(key);
    if(!art){art={body:body(item,p,principal),head:head(a),arms:Array.from({length:6},(_,f)=>arms(item,p,a,principal,f,type))};artworkCache.set(key,art);}
    let defs=`<g id="${id}b" transform="scale(2)">${art.body}</g><g id="${id}h">${art.head}</g>`;
    for(let f=0;f<6;f++)defs+=`<g id="${id}a${f}" transform="scale(2)">${art.arms[f]}</g>`;
    let frames='';
    for(let f=0;f<6;f++) {const nod=[0,1,2,3,1,0][f],shift=(type==='dance'||type==='shuffle')?[0,-2,-3,0,3,2][f]:0,hy=type==='nod'?nod:type==='celebrate'?[0,-1,-3,-2,-3,-1][f]:0,hx=item.id==='norris'?[0,1,2,2,1,0][f]:0;
      const blink=f===3?`<g fill="${tint(a.skin,-37)}"><rect x="45" y="33" width="7" height="3"/><rect x="59" y="33" width="7" height="3"/></g><path d="M45 35h7m7 0h7" stroke="${tint(a.hair,-15)}" stroke-width="1"/>`:'';
      const smile=f===2||f===4?`<rect x="54" y="47" width="9" height="2" fill="#7c4436"/><rect x="55" y="47" width="7" height="1" fill="#f4e6cc"/>`:'';
      frames+=`<g class="pixel-frame frame-${f}" data-frame="${f}"><g transform="translate(${shift} 0)"><use href="#${id}b"/><use href="#${id}a${f}"/><g transform="translate(${34+hx} ${9+hy})"><use href="#${id}h"/></g><g transform="translate(${hx} ${hy})">${blink}${smile}</g>${principal?`<g fill="#17222d"><rect x="40" y="29" width="4" height="12"/><rect x="72" y="29" width="4" height="12"/><rect x="42" y="13" width="2" height="18"/><rect x="43" y="12" width="29" height="2"/><rect x="70" y="14" width="2" height="17"/><rect x="70" y="40" width="3" height="8"/><rect x="65" y="46" width="7" height="2"/></g><rect x="65" y="46" width="3" height="2" fill="#7e959d"/>`:''}</g></g>`;
    }
    return `<svg class="detailed-person pixel-person" data-frames="6" data-pose="${esc(type)}" viewBox="0 0 112 176" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${esc(item.name||'Paddock character')} original pixel portrait" shape-rendering="crispEdges"><defs>${defs}</defs><g fill="#101b2a"><rect x="28" y="172" width="58" height="2"/><rect x="35" y="174" width="44" height="2"/></g>${frames}</svg>`;
  }
  function car(team) {
    team=team||{};const c=color(team.color,'#e33135'),d=tint(c,-45),l=tint(c,38),accent=color(team.accentColor,'#efdf9e'),g=new Pixels(128,64),O='#0a111b';
    // Low three-quarter side view, with visible cockpit, halo, suspension and aero surfaces.
    g.poly([[8,44],[16,36],[40,32],[44,24],[53,20],[70,23],[76,29],[97,33],[119,37],[122,46],[108,50],[22,50]],O);
    g.poly([[16,40],[39,35],[43,29],[59,27],[78,31],[97,35],[115,38],[113,45],[26,46]],c);
    g.poly([[17,42],[41,40],[50,35],[80,36],[106,40],[106,44],[26,46]],d);g.line(24,37,39,35,l,2);g.line(77,33,112,38,l,2);
    g.poly([[42,29],[48,22],[57,21],[67,25],[66,30]],d);g.line(49,23,58,23,l,2);g.box(52,24,13,8,'#1b2530');g.box(56,23,5,5,'#f4d257');g.box(57,24,4,2,'#26475a');g.box(55,28,7,2,'#d1c1a3');
    g.poly([[66,28],[75,29],[88,33],[85,36],[67,35]],l);g.line(49,25,52,30,'#a6abb0',2);g.line(52,30,72,29,'#111820',2);g.line(69,26,73,30,'#111820',2);
    g.box(9,26,16,3,O);g.box(11,23,14,3,c);g.box(13,26,2,14,O);g.box(24,28,3,10,O);g.box(6,42,22,3,d);g.box(101,43,23,3,O);g.box(99,40,22,3,c);g.box(119,36,4,8,d);
    g.line(26,43,42,35,'#63717b');g.line(89,35,105,44,'#63717b');g.line(89,38,105,45,'#111820');
    for(const x of [28,102]){g.ellipse(x,45,10,12,O);g.ellipse(x,45,8,10,'#252e35');g.ellipse(x,45,7,9,'#0d141c');g.ellipse(x,45,4,6,'#68747d');g.ellipse(x,45,2,4,'#202b34');g.line(x-6,38,x-4,36,'#cfa745');g.line(x+4,53,x+6,51,'#cfa745');g.box(x-7,41,1,6,'#3c4449');}
    g.box(44,36,11,4,accent);g.box(46,37,2,2,d);g.box(50,37,3,1,d);g.box(66,38,8,3,'#e6e6d9');g.box(77,38,5,2,accent);g.line(39,44,88,44,accent);g.box(87,32,7,1,accent);
    return `<svg class="detailed-car pixel-car" viewBox="0 0 256 128" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${esc(team.name||'Formula 1')} original pixel racing car" shape-rendering="crispEdges"><g transform="scale(2)">${g.svg()}</g></svg>`;
  }
  function raceScene() {
    const g=new Pixels(240,120);g.box(0,0,240,120,'#153386');g.box(0,0,240,36,'#468ac0');g.box(0,36,240,6,'#f5d183');g.box(0,42,240,78,'#347c40');
    g.poly([[107,42],[133,42],[218,120],[22,120]],'#777985');g.poly([[110,42],[114,42],[43,120],[28,120]],'#cbd0cb');g.poly([[126,42],[131,42],[214,120],[197,120]],'#cbd0cb');
    for(let i=0;i<7;i++){const y=46+i*i*1.7,w=1+i;g.box(119-w/2,y,w,2+i,'#e4e4cb');const edge=106-(y-42)*.98;g.box(edge,y,3+i,2+i,i%2?'#f3e3c5':'#c83339');g.box(132+(y-42)*.97,y,3+i,2+i,i%2?'#c83339':'#f3e3c5');}
    g.poly([[0,38],[16,23],[30,28],[48,14],[76,31],[93,25],[109,39]],'#3a6483');g.poly([[147,39],[163,24],[178,26],[195,15],[217,29],[239,23],[240,41]],'#3a6483');
    for(let x=2;x<240;x+=15){g.box(x,35,10,4,'#e2e6d2');g.box(x+2,32,7,3,'#16284b');}g.box(0,103,240,17,'#0c1649');g.box(0,104,240,2,'#65a2de');
    return `<svg class="pixel-race-scene" viewBox="0 0 480 240" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" shape-rendering="crispEdges"><g transform="scale(2)">${g.svg()}</g></svg>`;
  }
  window.PixelPaddockArt={person,car,raceScene};
})();
