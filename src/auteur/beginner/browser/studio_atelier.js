/* Living Narrative Atelier — experimental visual study stage (opt-in via ?atelier).
   A stable atlas of the working Architecture with local constellations unfolded by one of three
   treatments (A progressive revelation, B spatial choreography, C contextual unfolding).
   Presentation only: layout, camera and focus live in memory; nothing is saved or accepted. */
(function(global,document){
  'use strict';
  var M=global.AuteurStudioAtelierModel,SVG='http://www.w3.org/2000/svg';
  var TIMING={
    A:{stagger:30,first:90,grow:460,camera:640,move:0,moveDelay:0,moveStagger:0},
    B:{stagger:16,first:30,grow:560,camera:820,move:780,moveDelay:0,moveStagger:14},
    C:{stagger:26,first:80,grow:460,camera:700,move:660,moveDelay:420,moveStagger:14},
    back:{move:560,camera:640}
  };
  var EASE_MOVE=function(t){return t<0.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;};
  var EASE_CAM=function(t){return 1-Math.pow(1-t,3)*(1-t*0.35);};
  var EASE_GROW=function(t){return 1-Math.pow(1-t,3);};
  function el(tag,cls,text){var e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=String(text);return e;}
  function sv(tag,attrs){var e=document.createElementNS(SVG,tag);Object.keys(attrs||{}).forEach(function(k){e.setAttribute(k,attrs[k]);});return e;}
  function clamp(v,a,b){return Math.max(a,Math.min(b,v));}
  function hash(t){var h=2166136261;t=String(t);for(var i=0;i<t.length;i++){h^=t.charCodeAt(i);h=Math.imul(h,16777619);}return (h>>>0)/4294967295;}
  function lerp(a,b,k){return {x:a.x+(b.x-a.x)*k,y:a.y+(b.y-a.y)*k};}
  function prefersReduced(){try{return global.matchMedia('(prefers-reduced-motion: reduce)').matches;}catch(_){return false;}}
  var facetOrder={genres:0,emotions:1,timeline:2,tropes:3,structure:4,other:5};
  function roman(n){var map=[[10,'X'],[9,'IX'],[5,'V'],[4,'IV'],[1,'I']],out='';
    if(n>39)return String(n);map.forEach(function(p){while(n>=p[0]){out+=p[1];n-=p[0];}});return out;}

  function create(binding){
    if(!M)throw Error('Atelier model unavailable');
    if(!binding||!binding.root||typeof binding.getCandidate!=='function'||typeof binding.getRequestSha!=='function')
      throw Error('Atelier binding requires root, getCandidate and getRequestSha');
    var root=binding.root;
    var S={model:null,atlas:null,sha:null,treatment:['A','B','C'].includes(binding.treatment)?binding.treatment:'C',
      focus:null,depth:1,trail:[],cam:{cx:0,cy:0,z:1},restCam:null,pos:{},sides:{},hood:null,comp:null,
      metrics:null,reduced:prefersReduced(),lens:null,roving:null,tw:null,raf:null,frames:[],shown:false,
      pending:binding.initial||null,lastAction:null,edgeGrow:{},sizedOnce:false};

    /* ---------- Static frame ---------- */
    root.replaceChildren();root.classList.add('atl');
    var bar=el('header','atl-bar');
    var heading=el('div','atl-heading');
    heading.append(el('span','atl-eyebrow','Visual study · experimental · presentation only'),
      el('strong','atl-title','The Living Narrative Atelier'));
    var treatments=el('div','atl-treatments');treatments.setAttribute('role','radiogroup');
    treatments.setAttribute('aria-label','Unfolding treatment');
    var treatmentButtons={};
    ['A','B','C'].forEach(function(t){
      var b=el('button','atl-treatment');b.type='button';b.setAttribute('role','radio');b.dataset.treatment=t;
      b.append(el('span','atl-treatment-letter',t),el('span','atl-treatment-name',M.TREATMENTS[t]));
      b.addEventListener('click',function(){setTreatment(t);});
      b.addEventListener('keydown',function(e){
        var order=['A','B','C'],i=order.indexOf(t);
        if(e.key==='ArrowRight'||e.key==='ArrowDown'){e.preventDefault();setTreatment(order[(i+1)%3]);treatmentButtons[S.treatment].focus();}
        if(e.key==='ArrowLeft'||e.key==='ArrowUp'){e.preventDefault();setTreatment(order[(i+2)%3]);treatmentButtons[S.treatment].focus();}
      });
      treatmentButtons[t]=b;treatments.append(b);
    });
    var tools=el('div','atl-tools');
    var motion=el('button','atl-tool','Reduced motion');motion.type='button';
    motion.addEventListener('click',function(){S.reduced=!S.reduced;syncChrome();announce(S.reduced?'Reduced motion on: changes appear without travel.':'Full motion on.');});
    var readout=el('details','atl-readout');var readoutSummary=el('summary','','Study readout');
    var readoutBody=el('dl','atl-readout-body');readout.append(readoutSummary,readoutBody);
    tools.append(motion,readout);
    bar.append(heading,treatments,tools);
    var ribbon=el('p','atl-ribbon');
    var body=el('div','atl-body');
    var stage=el('div','atl-stage');stage.setAttribute('role','group');
    stage.setAttribute('aria-roledescription','narrative atlas');
    var svg=sv('svg',{'class':'atl-paths','aria-hidden':'true'});
    var defs=sv('defs');
    ['genres','emotions','timeline','tropes','structure','other','ink'].forEach(function(f){
      var m=sv('marker',{id:'atl-arrow-'+f,viewBox:'0 0 10 10',refX:'8.5',refY:'5',markerWidth:'7',markerHeight:'7',orient:'auto-start-reverse'});
      m.append(sv('path',{d:'M1 1.5 L9 5 L1 8.5',fill:'none','class':'atl-arrow atl-arrow-'+f}));defs.append(m);
    });
    var gBands=sv('g',{'class':'atl-g-bands'}),gSpine=sv('g',{'class':'atl-g-spine'}),gTethers=sv('g',{'class':'atl-g-tethers'});
    var gEdges=sv('g',{'class':'atl-g-edges'}),gVerbs=sv('g',{'class':'atl-g-verbs'});
    svg.append(defs,gBands,gSpine,gTethers,gEdges,gVerbs);
    var bandLabels=el('div','atl-band-labels');bandLabels.setAttribute('aria-hidden','true');
    var starLayer=el('div','atl-stars');starLayer.setAttribute('role','group');
    var trail=el('nav','atl-trail');trail.setAttribute('aria-label','Exploration path');
    var zoom=el('div','atl-zoom');
    function zoomButton(text,label,fn){var b=el('button','atl-zoom-btn',text);b.type='button';b.setAttribute('aria-label',label);b.title=label;b.addEventListener('click',fn);zoom.append(b);return b;}
    zoomButton('+','Zoom in',function(){zoomBy(1.25);});
    zoomButton('−','Zoom out',function(){zoomBy(0.8);});
    zoomButton('⤢','Fit the whole atlas',function(){fitAtlas(true);});
    var hint=el('p','atl-hint','Arrows move between concepts · Enter unfolds · ] deeper · Esc returns to the atlas');
    var empty=el('div','atl-empty');
    stage.append(svg,bandLabels,starLayer,trail,zoom,hint,empty);
    var folio=el('aside','atl-folio');folio.setAttribute('aria-label','Reading of the narrative atlas');
    body.append(stage,folio);
    var live=el('p','atl-live');live.setAttribute('aria-live','polite');live.setAttribute('role','status');
    root.append(bar,ribbon,body,live);

    var starEls={},edgeEls={},verbEls={},tetherEls={},bandEls=[],bandLabelEls=[],spineEls=null;

    /* ---------- Camera ---------- */
    // The stage size is read once per resize, never inside a frame (reading it per point forces layout).
    function measureView(){S.view={width:stage.clientWidth||960,height:stage.clientHeight||600};return S.view;}
    function view(){return S.view||measureView();}
    function toScreen(p){var v=view();return {x:(p.x-S.cam.cx)*S.cam.z+v.width/2,y:(p.y-S.cam.cy)*S.cam.z+v.height/2};}
    function atlasCamera(){
      // Leave a gutter for the band names, then fit the whole score.
      var v=view(),a=S.atlas,gutter=v.width<600?92:150,left=150;
      var room=v.width-gutter-24,z=clamp(Math.min(room/(a.width-left),(v.height-24)/a.height),0.26,1.05);
      var spare=Math.max(0,room-(a.width-left)*z)/2;
      return {cx:left-(gutter+spare-v.width/2)/z,cy:a.height/2,z:z};
    }
    function rectOf(ids,targets,sides,scale){
      var x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity;
      ids.forEach(function(id){var r=M.labelRect(S.model,id,targets[id],sides[id]||'right',S.focus,scale||1);
        x0=Math.min(x0,r.x0);y0=Math.min(y0,r.y0-8);x1=Math.max(x1,r.x1);y1=Math.max(y1,r.y1+8);});
      return {x0:x0,y0:y0,x1:x1,y1:y1};
    }
    function zoomBy(f,anchor){
      if(!S.model)return;
      var v=view(),ax=anchor?anchor.x:v.width/2,ay=anchor?anchor.y:v.height/2;
      var wx=(ax-v.width/2)/S.cam.z+S.cam.cx,wy=(ay-v.height/2)/S.cam.z+S.cam.cy,z=clamp(S.cam.z*f,0.22,2.2);
      var to={z:z,cx:wx-(ax-v.width/2)/z,cy:wy-(ay-v.height/2)/z};
      animate({camera:to,cameraDuration:S.reduced?0:220});
    }
    function fitAtlas(animated){
      if(!S.model)return;
      var to=atlasCamera();
      if(animated&&!S.reduced)animate({camera:to,cameraDuration:520});else{S.cam=to;paint();syncZoomClass();}
    }

    /* ---------- Scene ---------- */
    function buildScene(){
      starLayer.replaceChildren();gEdges.replaceChildren();gVerbs.replaceChildren();gTethers.replaceChildren();
      gBands.replaceChildren();gSpine.replaceChildren();bandLabels.replaceChildren();
      starEls={};edgeEls={};verbEls={};tetherEls={};bandEls=[];bandLabelEls=[];S.edgeGrow={};
      var model=S.model,atlas=S.atlas;
      starLayer.setAttribute('aria-label','Narrative atlas: '+model.concepts.length+' concepts and '+
        model.relations.length+' documented relationships. Arrow keys move between concepts.');
      atlas.bands.forEach(function(b,i){
        var rect=sv('rect',{'class':'atl-band atl-band-'+b.facet+(i%2?' is-alt':'')});gBands.append(rect);bandEls.push({band:b,rect:rect});
        var label=el('span','atl-band-label atl-facet-'+b.facet);
        label.append(el('span','atl-band-glyph'),el('span','',b.label+' · '+b.count));
        bandLabels.append(label);bandLabelEls.push({band:b,label:label});
      });
      var spinePath=sv('path',{'class':'atl-spine'});gSpine.append(spinePath);
      var books=atlas.books.map(function(bk){
        var line=sv('path',{'class':'atl-book'}),text=sv('text',{'class':'atl-book-label'});
        text.textContent=M.shorten(bk.label.toUpperCase(),34);gSpine.append(line,text);return {book:bk,line:line,text:text};
      });
      spineEls={path:spinePath,books:books};
      model.relations.forEach(function(r){
        var other=model.byId[r.to],p=sv('path',{'class':'atl-edge','data-facet':other.facet});
        gEdges.append(p);edgeEls[r.id]=p;S.edgeGrow[r.id]=1;
      });
      model.concepts.forEach(function(cn){
        var b=el('button','atl-star');b.type='button';b.tabIndex=-1;
        b.dataset.id=cn.id;b.dataset.facet=cn.facet;b.dataset.tier=String(cn.tier);
        b.style.setProperty('--room',String(Math.round(atlas.rooms[cn.id]||176)));
        var glyph=el('span','atl-glyph');glyph.setAttribute('aria-hidden','true');
        var text=el('span','atl-text');
        var kicker=el('span','atl-kicker',M.FACET_SINGULAR[cn.facet]+(cn.role?' · '+M.human(cn.role):''));
        text.append(kicker,el('span','atl-label',cn.label));
        if(cn.facet==='timeline')text.dataset.ordinal=roman(model.timeline.indexOf(cn)+1);
        b.append(glyph,text);b.title=cn.title;
        var count=model.adjacency[cn.id].length;
        b.setAttribute('aria-label',M.FACET_SINGULAR[cn.facet]+': '+cn.title+'. '+count+' documented relationship'+(count===1?'':'s')+
          '. Agent proposal, not accepted story.');
        b.addEventListener('click',function(){if(S.focus!==cn.id)select(cn.id,{via:'atlas'});else focusFolio();});
        b.addEventListener('pointerenter',function(){preview(cn.id);});
        b.addEventListener('pointerleave',function(){preview(null);});
        b.addEventListener('focus',function(){setRoving(cn.id);preview(cn.id);});
        b.addEventListener('blur',function(){preview(null);});
        starLayer.append(b);starEls[cn.id]=b;
      });
      var first=model.timeline[0]||model.concepts[0];if(first)setRoving(first.id);
    }
    function setRoving(id){
      if(S.roving&&starEls[S.roving])starEls[S.roving].tabIndex=-1;
      S.roving=id;if(starEls[id])starEls[id].tabIndex=0;
    }

    /* ---------- Painting (screen space; one pass per frame, idle once settled) ---------- */
    function curve(a,b,id,ra,rb){
      var dx=b.x-a.x,dy=b.y-a.y,len=Math.sqrt(dx*dx+dy*dy)||1,bend=Math.min(54,len*0.13)*(hash(id)<0.5?-1:1);
      var c={x:(a.x+b.x)/2-dy/len*bend,y:(a.y+b.y)/2+dx/len*bend};
      function trim(p,toward,r){var vx=toward.x-p.x,vy=toward.y-p.y,l=Math.sqrt(vx*vx+vy*vy)||1;return {x:p.x+vx/l*r,y:p.y+vy/l*r};}
      return {p0:trim(a,c,ra),c:c,p1:trim(b,c,rb)};
    }
    function partial(q,s,reverse){
      var p0=reverse?q.p1:q.p0,p1=reverse?q.p0:q.p1,c=q.c;
      var a=lerp(p0,c,s),b=lerp(c,p1,s),e=lerp(a,b,s);
      return 'M'+p0.x.toFixed(1)+' '+p0.y.toFixed(1)+'Q'+a.x.toFixed(1)+' '+a.y.toFixed(1)+' '+e.x.toFixed(1)+' '+e.y.toFixed(1);
    }
    function radius(id){
      if(id===S.focus)return 15;var cn=S.model.byId[id];return cn.tier===2?(S.hood&&S.hood.levels[id]!==undefined?7:4):8;
    }
    function paint(){
      if(!S.model)return;
      var model=S.model,v=view();svg.setAttribute('viewBox','0 0 '+v.width+' '+v.height);
      svg.setAttribute('width',v.width);svg.setAttribute('height',v.height);
      var screen={};
      model.concepts.forEach(function(cn){
        var p=toScreen(S.pos[cn.id]);screen[cn.id]=p;
        var left=S.sides[cn.id]==='left'&&cn.id!==S.focus&&(cn.facet!=='timeline'||!!(S.hood&&S.hood.levels[cn.id]));
        var b=starEls[cn.id];
        b.style.transform='translate('+p.x.toFixed(1)+'px,'+p.y.toFixed(1)+'px)'+(left?' translateX(calc(-100% + 18px))':'');
        if(b.__left!==left){b.classList.toggle('label-left',left);b.__left=left;}
      });
      bandEls.forEach(function(x){
        var a=toScreen({x:-4000,y:x.band.y0}),b=toScreen({x:S.atlas.width+4000,y:x.band.y1});
        x.rect.setAttribute('x',0);x.rect.setAttribute('width',v.width);
        x.rect.setAttribute('y',a.y.toFixed(1));x.rect.setAttribute('height',Math.max(0,b.y-a.y).toFixed(1));
      });
      bandLabelEls.forEach(function(x){
        var y=toScreen({x:0,y:(x.band.y0+x.band.y1)/2}).y;
        x.label.style.transform='translateY('+(y-9).toFixed(1)+'px)';
        var off=y<-20||y>v.height+20;if(x.label.hidden!==off)x.label.hidden=off;
      });
      var spine=model.timeline.map(function(p){return screen[p.id];});
      if(spine.length){
        var homeSpine=model.timeline.map(function(p){return toScreen(S.atlas.positions[p.id]);});
        var l=homeSpine[0],r=homeSpine[homeSpine.length-1];
        spineEls.path.setAttribute('d','M'+(l.x-60*S.cam.z)+' '+l.y+'L'+(r.x+60*S.cam.z)+' '+r.y);
        var lastEnd=-Infinity;
        spineEls.books.forEach(function(x){
          var a=toScreen({x:x.book.x0-26,y:S.atlas.positions[model.timeline[0].id].y-30}),
            b=toScreen({x:x.book.x1+26,y:S.atlas.positions[model.timeline[0].id].y-30});
          x.line.setAttribute('d','M'+a.x+' '+(a.y+5)+'L'+a.x+' '+a.y+'L'+b.x+' '+b.y+'L'+b.x+' '+(b.y+5));
          x.text.setAttribute('x',a.x+4);x.text.setAttribute('y',a.y-5);
          // Book names never overprint each other: a crowded name waits for a closer zoom.
          var w=x.text.textContent.length*6.4+10,show=a.x+4>=lastEnd;
          x.text.style.display=show?'':'none';if(show)lastEnd=a.x+4+w;
        });
      }
      model.relations.forEach(function(r){
        var path=edgeEls[r.id],q=curve(screen[r.from],screen[r.to],r.id,radius(r.from),radius(r.to));
        var grow=S.edgeGrow[r.id],reverse=false;
        if(S.hood){var lf=S.hood.levels[r.from],lt=S.hood.levels[r.to];reverse=lf!==undefined&&lt!==undefined&&lt<lf;}
        path.setAttribute('d',grow>=0.999?partial(q,1,false):grow<=0.001?'M0 0':partial(q,grow,reverse));
        if(verbEls[r.id]){var mid=lerp(lerp(q.p0,q.c,0.5),lerp(q.c,q.p1,0.5),0.5);verbEls[r.id].setAttribute('x',mid.x.toFixed(1));verbEls[r.id].setAttribute('y',(mid.y-4).toFixed(1));}
      });
      Object.keys(tetherEls).forEach(function(id){
        var t=tetherEls[id],h=toScreen(S.atlas.positions[id]),p=screen[id];
        var d=Math.sqrt(Math.pow(h.x-p.x,2)+Math.pow(h.y-p.y,2));
        t.line.setAttribute('x1',h.x);t.line.setAttribute('y1',h.y);t.line.setAttribute('x2',p.x);t.line.setAttribute('y2',p.y);
        t.dot.setAttribute('cx',h.x);t.dot.setAttribute('cy',h.y);
        t.g.style.opacity=d<6?'0':'';
      });
    }
    function syncZoomClass(){
      // Semantic zoom: spacing scales, type does not, so resting labels shorten to the room they have.
      root.style.setProperty('--atl-z',S.cam.z.toFixed(3));
      root.classList.toggle('atl-zoom-far',S.cam.z<0.5);
      root.classList.toggle('atl-zoom-mid',S.cam.z>=0.5&&S.cam.z<0.82);
    }

    /* ---------- Motion engine ---------- */
    function animate(spec){
      var now=performance.now(),tw=S.tw||{nodes:{},cam:null,edges:{}};
      if(spec.targets){
        Object.keys(spec.targets).forEach(function(id){
          var to=spec.targets[id],from=S.pos[id];
          if(!from||(Math.abs(to.x-from.x)<0.5&&Math.abs(to.y-from.y)<0.5)){if(from)S.pos[id]={x:to.x,y:to.y};delete tw.nodes[id];return;}
          var dur=spec.duration||0,delay=spec.delay?spec.delay(id):0;
          if(dur<=0){S.pos[id]={x:to.x,y:to.y};delete tw.nodes[id];return;}
          tw.nodes[id]={from:{x:from.x,y:from.y},to:{x:to.x,y:to.y},t0:now+delay,dur:dur};
        });
      }
      if(spec.camera){
        if(!spec.cameraDuration){S.cam={cx:spec.camera.cx,cy:spec.camera.cy,z:spec.camera.z};tw.cam=null;}
        else tw.cam={from:{cx:S.cam.cx,cy:S.cam.cy,z:S.cam.z},to:spec.camera,t0:now+(spec.cameraDelay||0),dur:spec.cameraDuration};
      }
      if(spec.edges){
        Object.keys(spec.edges).forEach(function(id){
          var e=spec.edges[id];
          if(!e.dur){S.edgeGrow[id]=e.to;delete tw.edges[id];return;}
          if(e.from!==undefined)S.edgeGrow[id]=e.from;
          tw.edges[id]={from:S.edgeGrow[id],to:e.to,t0:now+(e.delay||0),dur:e.dur};
        });
      }
      S.tw=tw;S.frames=[];S.motionStart=now;
      if(!S.raf)S.raf=global.requestAnimationFrame(tick);
    }
    function tick(now){
      S.raf=null;var tw=S.tw,active=false;if(!tw)return;
      Object.keys(tw.nodes).forEach(function(id){
        var t=tw.nodes[id],k=(now-t.t0)/t.dur;
        if(k<=0){active=true;return;}
        if(k>=1){S.pos[id]=t.to;delete tw.nodes[id];return;}
        S.pos[id]=lerp(t.from,t.to,EASE_MOVE(k));active=true;
      });
      if(tw.cam){
        var c=tw.cam,k=(now-c.t0)/c.dur;
        if(k>=1){S.cam=c.to;tw.cam=null;}
        else if(k>0){var e=EASE_CAM(k);
          // Interpolate zoom geometrically so the scene's scale changes at an even pace.
          S.cam={cx:c.from.cx+(c.to.cx-c.from.cx)*e,cy:c.from.cy+(c.to.cy-c.from.cy)*e,z:c.from.z*Math.pow(c.to.z/c.from.z,e)};active=true;}
        else active=true;
      }
      Object.keys(tw.edges).forEach(function(id){
        var t=tw.edges[id],k=(now-t.t0)/t.dur;
        if(k<=0){active=true;return;}
        if(k>=1){S.edgeGrow[id]=t.to;delete tw.edges[id];return;}
        S.edgeGrow[id]=t.from+(t.to-t.from)*EASE_GROW(k);active=true;
      });
      S.frames.push(now);paint();syncZoomClass();
      if(active)S.raf=global.requestAnimationFrame(tick);else settle();
    }
    function flushInstant(){
      // Reduced motion and instant restores: apply every pending end state in one frame.
      if(S.raf){global.cancelAnimationFrame(S.raf);S.raf=null;}
      var tw=S.tw;if(tw){Object.keys(tw.nodes).forEach(function(id){S.pos[id]=tw.nodes[id].to;});
        if(tw.cam)S.cam=tw.cam.to;Object.keys(tw.edges).forEach(function(id){S.edgeGrow[id]=tw.edges[id].to;});}
      S.tw={nodes:{},cam:null,edges:{}};S.frames=[];paint();syncZoomClass();settle();
    }

    /* ---------- States ---------- */
    function starState(id){
      if(!S.hood)return 'rest';
      var lv=S.hood.levels[id];return lv===0?'focus':lv===1?'near':lv===2?'far':'dim';
    }
    function applyStates(delays){
      root.classList.toggle('atl-focused',!!S.focus);
      S.model.concepts.forEach(function(cn){
        var b=starEls[cn.id],st=starState(cn.id);
        b.style.transitionDelay=delays&&delays[cn.id]!==undefined?delays[cn.id]+'ms':'0ms';
        ['rest','focus','near','far','dim'].forEach(function(name){b.classList.toggle('is-'+name,st===name);});
        if(st==='focus')b.setAttribute('aria-current','true');else b.removeAttribute('aria-current');
        b.classList.toggle('is-moved',!!(S.comp&&S.comp.moved.indexOf(cn.id)>=0&&st!=='focus'));
      });
      var edgeLevel={};if(S.hood)S.hood.edges.forEach(function(e){edgeLevel[e.relation.id]=e.level;});
      S.model.relations.forEach(function(r){
        var p=edgeEls[r.id],lv=edgeLevel[r.id];
        p.setAttribute('class','atl-edge'+(S.hood?(lv===1?' lv-1':lv===1.5?' lv-15':lv===2?' lv-2':' is-mute'):''));
        var other=S.hood&&S.hood.levels[r.from]===0?r.to:S.hood&&S.hood.levels[r.to]===0?r.from:r.to;
        p.setAttribute('data-facet',S.model.byId[other].facet);
        if(lv===1){var f=S.model.byId[other].facet;p.setAttribute(S.hood.levels[r.to]===0?'marker-start':'marker-end','url(#atl-arrow-'+f+')');
          p.removeAttribute(S.hood.levels[r.to]===0?'marker-end':'marker-start');}
        else{p.removeAttribute('marker-end');p.removeAttribute('marker-start');}
      });
      root.dataset.lens=S.lens||'';
    }
    function syncVerbs(){
      gVerbs.replaceChildren();verbEls={};
      if(!S.hood)return;
      S.hood.edges.filter(function(e){return e.level===1;}).forEach(function(e){
        var r=e.relation,t=sv('text',{'class':'atl-verb is-pending','text-anchor':'middle'});
        var focusIsTarget=S.hood.levels[r.to]===0;
        t.textContent=M.shorten(focusIsTarget?(r.reverseVerb||r.verb):r.verb,30);
        gVerbs.append(t);verbEls[r.id]=t;
      });
    }
    function syncTethers(){
      gTethers.replaceChildren();tetherEls={};
      if(!S.comp)return;
      S.comp.moved.forEach(function(id){
        if(id===S.focus)return;
        var g=sv('g',{'class':'atl-tether','data-facet':S.model.byId[id].facet});
        var line=sv('line',{}),dot=sv('circle',{r:'3.2'});g.append(line,dot);gTethers.append(g);
        tetherEls[id]={g:g,line:line,dot:dot};
      });
    }

    /* ---------- Unfolding choreography ---------- */
    function select(id,opts){
      opts=opts||{};
      if(!S.model||!S.model.byId[id])return;
      var fromAtlas=!S.focus;
      if(fromAtlas)S.restCam={cx:S.cam.cx,cy:S.cam.cy,z:S.cam.z};
      if(opts.trailIndex!==undefined)S.trail=S.trail.slice(0,opts.trailIndex+1);
      else if(fromAtlas)S.trail=[id];
      else if(S.focus!==id)S.trail.push(id);
      if(S.trail.length>12)S.trail=S.trail.slice(-12);
      S.focus=id;S.depth=opts.depth||(fromAtlas||opts.via==='atlas'?1:S.depth===2?2:1);
      S.lastAction={kind:'select',id:id,at:performance.now()};
      unfold({fresh:true});
      setRoving(id);
      renderFolio();renderTrail();
      var cn=S.model.byId[id],n=S.hood.first.length;
      announce(M.FACET_SINGULAR[cn.facet]+' “'+cn.title+'” unfolded: '+n+' documented relationship'+(n===1?'':'s')+'.'+
        (S.comp.moved.length?' '+S.comp.moved.length+' concepts moved closer for reading; their atlas places stay marked.':''));
      if(opts.focusStar!==false&&starEls[id]&&document.activeElement&&root.contains(document.activeElement)&&
         document.activeElement.classList.contains('atl-star'))starEls[id].focus({preventScroll:true});
    }
    // B and C compose at reading scale (zoom 1); A never moves anything and keeps the current zoom.
    function compositionView(){var v=view();return {width:v.width,height:v.height,z:S.treatment==='A'?S.cam.z:1};}
    function unfold(mode){
      var T=TIMING[S.treatment],reduced=S.reduced;
      var previous=S.hood;
      S.hood=M.neighbourhood(S.model,S.focus,S.depth);
      S.comp=M.compose(S.model,S.atlas,S.hood,S.treatment,compositionView());
      S.sides=Object.assign({},S.comp.sides);
      Object.keys(S.sides).forEach(function(id){if(S.hood.levels[id]===undefined)delete S.sides[id];});
      // Reveal order: by kind of idea, then by bearing, so relationships arrive as readable groups.
      var delays={},fresh=mode.fresh,i=0;
      var reveal=S.hood.first.slice().sort(function(a,b){
        return facetOrder[S.model.byId[a].facet]-facetOrder[S.model.byId[b].facet]||a.localeCompare(b);});
      var newlyShown=function(id){return fresh||!previous||previous.levels[id]===undefined;};
      reveal.forEach(function(id){if(newlyShown(id))delays[id]=reduced?0:Math.min(T.first+(i++)*T.stagger,T.first+620);});
      var j=0;
      S.hood.second.forEach(function(id){if(newlyShown(id))delays[id]=reduced?0:Math.min(T.first+260+(j++)*T.stagger*0.7,T.first+900);});
      delays[S.focus]=0;
      applyStates(delays);syncVerbs();syncTethers();
      // Relationship paths grow out of the focus as each related concept arrives.
      var edges={};
      S.hood.edges.forEach(function(e){
        var r=e.relation,other=S.hood.levels[r.from]>S.hood.levels[r.to]?r.from:r.to;
        var isNew=fresh||!previous||!previous.edges.some(function(x){return x.relation.id===r.id;});
        if(!isNew&&!mode.regrow)return;
        edges[r.id]=reduced?{to:1}:{from:0,to:1,dur:T.grow,delay:(delays[other]||0)+(e.level===1?0:120)};
      });
      var targets={};S.model.concepts.forEach(function(cn){targets[cn.id]=S.comp.targets[cn.id];});
      var moveDur=T.move||TIMING.back.move,moveDelay=fresh?T.moveDelay:0;
      var ids=S.hood.order,cam=cameraFor(ids);
      animate({targets:targets,duration:reduced?0:moveDur,
        delay:function(id){var k=ids.indexOf(id);return moveDelay+(k<0?0:Math.min(k*T.moveStagger,260));},
        camera:cam,cameraDuration:reduced||!cam?0:T.camera,cameraDelay:S.treatment==='C'&&fresh?Math.max(0,T.moveDelay-80):0,
        edges:edges});
      if(reduced)flushInstant();
    }
    function cameraFor(ids){
      var v=view(),pad=40,t=S.comp.targets,f=t[S.focus];
      if(S.treatment==='A'){
        // Glyphs stay put; labels keep their screen size, so fit glyphs plus a label margin.
        var gx0=Infinity,gy0=Infinity,gx1=-Infinity,gy1=-Infinity;
        ids.forEach(function(id){var p=t[id];gx0=Math.min(gx0,p.x);gy0=Math.min(gy0,p.y);gx1=Math.max(gx1,p.x);gy1=Math.max(gy1,p.y);});
        var over={l:140,r:210,t:24,b:72};
        var a=toScreen({x:gx0,y:gy0}),b=toScreen({x:gx1,y:gy1});
        if(a.x-over.l>=pad&&a.y-over.t>=pad&&b.x+over.r<=v.width-pad&&b.y+over.b<=v.height-pad&&S.cam.z>=0.62)return null;
        var z=clamp(Math.min((v.width-2*pad-over.l-over.r)/Math.max(gx1-gx0,1),(v.height-2*pad-over.t-over.b)/Math.max(gy1-gy0,1)),0.35,1.05);
        return {z:z,cx:(gx0-over.l/z+gx1+over.r/z)/2,cy:(gy0-over.t/z+gy1+over.b/z)/2};
      }
      var rect=rectOf(ids,t,S.comp.sides,1),w=rect.x1-rect.x0,h=rect.y1-rect.y0;
      var cx=w<=v.width-2*pad?(rect.x0+rect.x1)/2:clamp((rect.x0+rect.x1)/2,f.x-v.width/2+170,f.x+v.width/2-170);
      var cy=h<=v.height-2*pad?(rect.y0+rect.y1)/2:f.y+v.height/2-110;
      return {z:1,cx:cx,cy:cy};
    }
    function deeper(on){
      if(!S.focus)return;
      S.depth=on?2:1;S.lastAction={kind:on?'deeper':'shallower',id:S.focus,at:performance.now()};
      unfold({fresh:false});renderFolio();
      announce(on?'Second-order connections revealed: '+S.hood.second.length+' concepts.'+
        (S.hood.hiddenSecond?' '+S.hood.hiddenSecond+' more are listed in the index, not drawn.':''):'Showing first-order relationships only.');
    }
    function setTreatment(t){
      if(!['A','B','C'].includes(t)||t===S.treatment){syncChrome();return;}
      S.treatment=t;syncChrome();
      if(S.focus){S.lastAction={kind:'treatment',id:S.focus,at:performance.now()};unfold({fresh:false,regrow:false});renderFolio();}
      announce('Treatment '+t+' · '+M.TREATMENTS[t]+'.');
    }
    function returnToAtlas(){
      if(!S.focus)return;
      var last=S.focus,reduced=S.reduced,delays={};
      if(S.hood)S.hood.order.slice().reverse().forEach(function(id,i){delays[id]=reduced?0:Math.min(i*10,180);});
      S.focus=null;S.hood=null;S.comp=null;S.trail=[];S.sides={};S.depth=1;
      S.lastAction={kind:'return',id:last,at:performance.now()};
      applyStates(delays);syncVerbs();syncTethers();
      var targets={};S.model.concepts.forEach(function(cn){targets[cn.id]=S.atlas.positions[cn.id];});
      var edges={};S.model.relations.forEach(function(r){edges[r.id]={to:1};});
      animate({targets:targets,duration:reduced?0:TIMING.back.move,camera:S.restCam||atlasCamera(),
        cameraDuration:reduced?0:TIMING.back.camera,edges:edges});
      if(reduced)flushInstant();
      renderFolio();renderTrail();setRoving(last);
      if(root.contains(document.activeElement))starEls[last].focus({preventScroll:true});
      announce('Returned to the atlas. “'+S.model.byId[last].title+'” is still in its place.');
    }
    function back(){
      if(S.trail.length>1)select(S.trail[S.trail.length-2],{trailIndex:S.trail.length-2});
      else returnToAtlas();
    }

    /* ---------- Hover preview (atlas and constellation) ---------- */
    function preview(id){
      root.querySelectorAll('.atl-edge.is-preview').forEach(function(p){p.classList.remove('is-preview');});
      root.querySelectorAll('.atl-star.is-linked').forEach(function(b){b.classList.remove('is-linked');});
      root.querySelectorAll('.atl-rel.is-linked').forEach(function(b){b.classList.remove('is-linked');});
      if(!id||!S.model)return;
      S.model.adjacency[id].forEach(function(a){
        if(S.focus&&S.hood&&S.hood.levels[a.other]===undefined)return;
        edgeEls[a.relation.id].classList.add('is-preview');
        if(S.focus===id||!S.focus)starEls[a.other].classList.add('is-linked');
      });
      if(S.focus&&id!==S.focus){
        starEls[id].classList.add('is-linked');
        folio.querySelectorAll('.atl-rel[data-other="'+cssEscape(id)+'"]').forEach(function(b){b.classList.add('is-linked');});
      }
    }
    function previewRelation(relId,otherId){
      preview(null);if(!relId)return;
      if(edgeEls[relId])edgeEls[relId].classList.add('is-preview');
      if(starEls[otherId])starEls[otherId].classList.add('is-linked');
    }
    function cssEscape(v){return global.CSS&&CSS.escape?CSS.escape(v):String(v).replace(/"/g,'\\"');}

    /* ---------- Settling and study measures ---------- */
    function cullLabels(){
      // The same etiquette for every treatment: a label that would overprint another stays quiet
      // (its glyph remains; hover or keyboard focus reveals it; the folio lists every relationship).
      var placed=[],quiet=0;
      S.model.concepts.forEach(function(cn){starEls[cn.id].classList.remove('is-quiet');});
      if(S.hood)S.hood.order.forEach(function(id){
        var text=starEls[id].querySelector('.atl-text'),r=text&&text.getBoundingClientRect();
        if(!r||!r.width)return;
        var hit=placed.some(function(o){return r.left<o.right-1&&o.left<r.right-1&&r.top<o.bottom-1&&o.top<r.bottom-1;});
        if(hit&&id!==S.focus){starEls[id].classList.add('is-quiet');quiet++;}else placed.push(r);
      });
      S.quiet=quiet;
    }
    function settle(){
      if(S.model)cullLabels();
      cullVerbs();
      if(!S.model)return;
      var frames=S.frames,intervals=[];
      for(var i=1;i<frames.length;i++)intervals.push(frames[i]-frames[i-1]);
      var base=S.focus?M.measure(S.model,S.atlas,S.hood,S.comp,S.treatment==='A'?S.cam.z:1):null;
      var overlapsRendered=renderedOverlaps();
      S.metrics={treatment:S.treatment,focus:S.focus,depth:S.depth,action:S.lastAction&&S.lastAction.kind,
        settleMs:S.lastAction?Math.round(performance.now()-S.lastAction.at):0,
        frames:frames.length,meanFrameMs:intervals.length?+(intervals.reduce(function(s,v){return s+v;},0)/intervals.length).toFixed(1):0,
        maxFrameMs:intervals.length?+Math.max.apply(null,intervals).toFixed(1):0,
        zoom:+S.cam.z.toFixed(2),renderedLabelOverlaps:overlapsRendered,quietLabels:S.quiet||0,
        verbLabels:{shown:gVerbs.querySelectorAll('.atl-verb:not(.is-culled)').length,total:gVerbs.children.length},
        composition:base,reducedMotion:S.reduced,concepts:S.model.concepts.length,relations:S.model.relations.length};
      renderReadout();
      root.dispatchEvent(new CustomEvent('atelier:settled',{detail:S.metrics}));
    }
    function renderedOverlaps(){
      var boxes=[];
      S.model.concepts.forEach(function(cn){
        var st=starState(cn.id);
        if(S.focus?['focus','near','far'].indexOf(st)<0:cn.tier!==1)return;
        if(starEls[cn.id].classList.contains('is-quiet'))return;
        var label=starEls[cn.id].querySelector('.atl-label');
        if(!label||!label.offsetParent)return;
        var r=label.getBoundingClientRect();if(r.width&&getComputedStyle(label).visibility!=='hidden'&&getComputedStyle(label).opacity>0.2)boxes.push(r);
      });
      var count=0;
      for(var i=0;i<boxes.length;i++)for(var j=i+1;j<boxes.length;j++){
        var a=boxes[i],b=boxes[j];if(a.left<b.right-2&&b.left<a.right-2&&a.top<b.bottom-2&&b.top<a.bottom-2)count++;}
      return {count:count,labels:boxes.length};
    }
    function cullVerbs(){
      // Keep verb labels that do not collide with concept labels or with each other.
      var placed=[];
      if(S.hood)S.hood.order.forEach(function(id){
        if(starEls[id].classList.contains('is-quiet'))return;
        var label=starEls[id]&&starEls[id].querySelector('.atl-text');if(label)placed.push(label.getBoundingClientRect());});
      // Verbs speak only once the composition has settled, and only where they have room.
      Array.prototype.forEach.call(gVerbs.children,function(t){
        t.classList.remove('is-culled');
        var r=t.getBoundingClientRect(),hit=placed.some(function(o){return r.left<o.right&&o.left<r.right&&r.top<o.bottom&&o.top<r.bottom;});
        if(hit||!r.width)t.classList.add('is-culled');else placed.push(r);
        t.classList.remove('is-pending');
      });
    }
    function renderReadout(){
      readoutBody.replaceChildren();var m=S.metrics;if(!m)return;
      function row(k,v){readoutBody.append(el('dt','',k),el('dd','',v));}
      row('Treatment',m.treatment+' · '+M.TREATMENTS[m.treatment]);
      row('Atlas',m.concepts+' concepts · '+m.relations+' relationships');
      if(m.composition){var c=m.composition;
        row('Neighbourhood',c.first+' first-order · '+c.second+' second-order');
        row('Moved',c.moved+' of '+(c.visible-1)+' · mean '+c.meanMove+'px · max '+c.maxMove+'px');
        row('Estimated label overlaps',String(c.labelOverlaps));
        row('First-order crossings',String(c.firstEdgeCrossings));
        row('Reach from focus','mean '+c.meanReach+'px · max '+c.maxReach+'px');}
      row('Rendered label overlaps',m.renderedLabelOverlaps.count+' among '+m.renderedLabelOverlaps.labels+' labels');
      row('Quieted labels',m.quietLabels+' (glyph kept; revealed on hover or focus)');
      row('Relationship verbs shown',m.verbLabels.shown+' of '+m.verbLabels.total);
      row('Settled after',m.settleMs+' ms · '+m.frames+' frames · mean '+m.meanFrameMs+' ms · worst '+m.maxFrameMs+' ms');
      row('Zoom',String(m.zoom));
    }

    /* ---------- Folio: the editorial reading ---------- */
    function focusFolio(){var h=folio.querySelector('h3');if(h){h.tabIndex=-1;h.focus({preventScroll:false});}}
    function provenanceLine(cn){
      var p=el('p','atl-provenance');
      p.append(el('span','atl-chip atl-chip-proposal','Agent proposal · not accepted story'));
      if(cn&&cn.sourceRef)p.append(el('span','atl-chip atl-chip-source','Source · '+cn.sourceRef));
      if(S.sha)p.append(el('span','atl-chip','Request '+String(S.sha).slice(0,10)));
      return p;
    }
    function fact(dl,label,value){if(!value||(Array.isArray(value)&&!value.length))return;
      dl.append(el('dt','',label),el('dd','',Array.isArray(value)?value.join(' · '):String(value)));}
    function renderFolio(){
      folio.replaceChildren();
      var status=binding.getSourceStatus?binding.getSourceStatus():null;
      if(!S.model){
        folio.append(el('p','atl-kicker-line','The atlas'),el('h3','atl-folio-title','No working Architecture yet'),
          el('p','atl-folio-detail','Develop a working Architecture proposal in the Studio, then return to this study. The study only reads what the proposal records.'));
        return;
      }
      if(!S.focus)return renderAtlasFolio(status);
      var cn=S.model.byId[S.focus],model=S.model;
      folio.setAttribute('aria-label','Reading of '+cn.title);
      folio.append(el('p','atl-kicker-line atl-facet-'+cn.facet,M.FACET_SINGULAR[cn.facet]+(cn.role?' · '+M.human(cn.role):'')));
      folio.append(el('h3','atl-folio-title',cn.title));
      var rec=cn.record||{},dl=el('dl','atl-facts');
      if(cn.facet==='genres'&&rec.genre_node_id){
        if(cn.coverage)folio.append(el('p','atl-coverage',cn.coverage));
        fact(dl,'Narrative engine',rec.narrative_engine);fact(dl,'Structural pattern',rec.structural_pattern);
        fact(dl,'Reader payoffs',rec.payoff_expectations);fact(dl,'Aesthetic strategies',rec.aesthetic_strategies);
      }else if(cn.facet==='emotions'&&rec.intended_effect!==undefined){
        fact(dl,'Intended effect',rec.intended_effect);fact(dl,'Eliciting condition',rec.eliciting_condition);
        fact(dl,'Aesthetic strategy',rec.aesthetic_strategy);fact(dl,'Provenance',M.human(rec.provenance));
      }else if(cn.facet==='emotions'&&rec.basic_emotions){
        fact(dl,'Blend of',rec.basic_emotions);fact(dl,'Context',rec.context);
      }else if(cn.facet==='timeline'){
        var index=model.timeline.indexOf(cn);
        fact(dl,'Place in story order','Phase '+(index+1)+' of '+model.timeline.length+' (order is not a chapter count)');
        fact(dl,'Scope',M.human(rec.scope||'whole story'));fact(dl,'Narrative function',rec.narrative_function);
        fact(dl,'Reader experience',rec.reader_experience);fact(dl,'Aesthetic',rec.aesthetic);fact(dl,'Transition',rec.transition);
      }else{
        if(cn.detail&&cn.detail!==cn.title)folio.append(el('p','atl-folio-detail',cn.detail));
        if(cn.tier===2){
          var owner=cn.phaseId?model.byId['timeline|phase:'+cn.phaseId]:cn.ownerGenreId?model.byId['genres|genre:'+cn.ownerGenreId]:null;
          if(owner)fact(dl,'Recorded as a local function of',owner.title);
          fact(dl,'Status','A local phrase without its own identity; equal wording elsewhere is not assumed to be the same idea.');
        }
        if(cn.nodeId){fact(dl,'Category',M.human(rec.category));fact(dl,'Scope',M.human(rec.scope||'whole story'));}
      }
      if(dl.children.length)folio.append(dl);
      folio.append(provenanceLine(cn));
      renderRelations(cn);
      var deep=el('div','atl-depth');
      var depthButton=el('button','atl-action atl-action-primary');depthButton.type='button';
      var potential=M.neighbourhood(model,cn.id,2).second.length;
      depthButton.textContent=S.depth===2?'Show first-order only':'Reveal deeper connections · '+potential;
      depthButton.setAttribute('aria-pressed',String(S.depth===2));depthButton.disabled=S.depth!==2&&!potential;
      depthButton.addEventListener('click',function(){deeper(S.depth!==2);});
      deep.append(depthButton);
      if(S.depth===2)deep.append(el('p','atl-note',S.hood.second.length+' second-order concepts drawn faintly'+
        (S.hood.hiddenSecond?'; '+S.hood.hiddenSecond+' more are not drawn.':'.')));
      folio.append(deep);
      var src=el('details','atl-source');src.append(el('summary','','Source record · '+(cn.sourceRef||'unavailable')));
      var srcList=el('dl','atl-facts atl-facts-source');
      Object.keys(rec).forEach(function(k){
        var v=rec[k];if(v===null||v===undefined||typeof v==='object'&&!Array.isArray(v))return;
        if(Array.isArray(v))v=v.map(function(x){return typeof x==='object'?(x.genre_node_id||x.genre||JSON.stringify(x)):x;}).join(' · ');
        srcList.append(el('dt','',M.human(k)),el('dd','',M.shorten(String(v),420)));
      });
      if(!srcList.children.length)srcList.append(el('dd','',cn.title));
      src.append(srcList);folio.append(src);
      var actions=el('div','atl-actions');
      if(binding.onInspect&&cn.nodeId)actionButton(actions,'Open in Studio inspector',function(){binding.onInspect(cn);});
      if(binding.onExplain&&['genres','tropes','structure','timeline','emotions'].indexOf(cn.facet)>=0)
        actionButton(actions,'Read the full explanation',function(){binding.onExplain(cn);});
      if(binding.onUnfold&&cn.nodeId){
        actionButton(actions,'Develop new possibilities (Focused Unfolding)',function(){binding.onUnfold(cn);});
        actions.append(el('p','atl-note','Focused Unfolding proposes new working ideas for you to review. This study only shows what the proposal already records.'));
      }
      if(binding.inspectorOpen&&binding.inspectorOpen()&&binding.onCloseInspector)
        actionButton(actions,'Hide the Studio inspector',function(){binding.onCloseInspector();});
      var ret=el('button','atl-action atl-return','Return to the atlas');ret.type='button';ret.addEventListener('click',returnToAtlas);
      actions.append(ret);folio.append(actions);
    }
    function actionButton(parent,text,fn){var b=el('button','atl-action',text);b.type='button';b.addEventListener('click',fn);parent.append(b);return b;}
    function renderRelations(cn){
      var model=S.model,list=model.adjacency[cn.id],wrap=el('section','atl-relations');
      wrap.append(el('h4','atl-section-title','Documented relationships · '+list.length));
      if(!list.length)wrap.append(el('p','atl-note','No documented relationships. A missing link does not mean the ideas are incompatible.'));
      M.FACETS.forEach(function(facet){
        var rows=list.filter(function(a){return model.byId[a.other].facet===facet;});
        if(!rows.length)return;
        wrap.append(el('h5','atl-group atl-facet-'+facet,M.FACET_LABEL[facet]));
        rows.forEach(function(a,i){
          var other=model.byId[a.other],b=el('button','atl-rel');b.type='button';b.dataset.other=other.id;b.dataset.rel=a.relation.id;
          b.append(el('span','atl-rel-verb',a.verb),el('span','atl-rel-target',other.label));
          b.title=other.title;
          b.addEventListener('click',function(){select(other.id,{via:'folio'});focusFolio();});
          b.addEventListener('pointerenter',function(){previewRelation(a.relation.id,other.id);});
          b.addEventListener('focus',function(){previewRelation(a.relation.id,other.id);});
          b.addEventListener('pointerleave',function(){preview(null);});
          b.addEventListener('blur',function(){preview(null);});
          wrap.append(b);
          if(a.relation.reason){var why=el('p','atl-why',a.relation.reason);why.id='atl-why-'+Math.round(hash(a.relation.id+i)*1e9);
            b.setAttribute('aria-describedby',why.id);wrap.append(why);}
        });
      });
      folio.append(wrap);
    }
    function renderAtlasFolio(status){
      var model=S.model;folio.setAttribute('aria-label','Reading of the narrative atlas');
      folio.append(el('p','atl-kicker-line','The atlas · '+model.concepts.length+' concepts · '+model.relations.length+' documented relationships'));
      folio.append(el('h3','atl-folio-title','The shape of this story'));
      if(model.summary)folio.append(el('p','atl-folio-detail atl-summary',model.summary));
      if(status&&status!=='ready')folio.append(el('p','atl-coverage','Source status: '+M.human(status)+'. The atlas reads the current working proposal as it is.'));
      var how=el('ul','atl-how');
      ['Bands hold kinds of narrative idea; story time runs left to right in recorded phase order.',
       'Across, a concept follows the phases it is recorded with, directly or through its genre. Nearness alone is never a relationship.',
       'Dashed paths are recorded proposal relationships, not accepted story.',
       'Small points are local phrases recorded inside a genre or phase; they gain words as you unfold them.']
        .forEach(function(t){how.append(el('li','',t));});
      folio.append(how);
      var legend=el('div','atl-legend');legend.setAttribute('role','group');legend.setAttribute('aria-label','Highlight a kind of idea');
      M.FACETS.forEach(function(facet){
        var count=model.concepts.filter(function(x){return x.facet===facet;}).length;if(!count)return;
        var b=el('button','atl-legend-item atl-facet-'+facet);b.type='button';b.setAttribute('aria-pressed',String(S.lens===facet));
        b.append(el('span','atl-legend-glyph'),el('span','',M.FACET_LABEL[facet]+' · '+count));
        b.addEventListener('click',function(){S.lens=S.lens===facet?null:facet;root.dataset.lens=S.lens||'';renderFolio();});
        legend.append(b);
      });
      folio.append(el('h4','atl-section-title','Highlight a kind of idea'),legend);
      var task=el('section','atl-task');
      task.append(el('h4','atl-section-title','Study task · the same for A, B and C'));
      var steps=el('ol','');
      ['Choose a concept in the atlas.','Read its documented relationships as they appear.',
       'Reveal deeper connections.','Inspect a source record.','Return to the atlas.']
        .forEach(function(t){steps.append(el('li','',t));});
      task.append(steps);folio.append(task);
      var index=el('section','atl-index');index.append(el('h4','atl-section-title','Atlas index'));
      M.FACETS.forEach(function(facet){
        var members=model.concepts.filter(function(x){return x.facet===facet;})
          .sort(function(a,b){return a.tier-b.tier||(facet==='timeline'?(a.order||0)-(b.order||0):a.title.localeCompare(b.title));});
        if(!members.length)return;
        var d=el('details','atl-index-group');d.append(el('summary','atl-facet-'+facet,M.FACET_LABEL[facet]+' · '+members.length));
        members.forEach(function(cn){var b=el('button','atl-index-item',cn.label);b.type='button';b.title=cn.title;
          b.addEventListener('click',function(){select(cn.id,{via:'atlas'});});d.append(b);});
        index.append(d);
      });
      folio.append(index);
    }
    function renderTrail(){
      trail.replaceChildren();
      var home=el('button','atl-crumb atl-crumb-home','Atlas');home.type='button';
      home.disabled=!S.focus;home.addEventListener('click',returnToAtlas);trail.append(home);
      S.trail.forEach(function(id,i){
        var cn=S.model.byId[id];if(!cn)return;
        trail.append(el('span','atl-crumb-sep','›'));
        var b=el('button','atl-crumb atl-facet-'+cn.facet,M.shorten(cn.title,26));b.type='button';b.title=cn.title;
        if(i===S.trail.length-1){b.setAttribute('aria-current','location');b.disabled=true;}
        else b.addEventListener('click',function(){select(id,{trailIndex:i});});
        trail.append(b);
      });
    }
    function syncChrome(){
      ['A','B','C'].forEach(function(t){treatmentButtons[t].setAttribute('aria-checked',String(t===S.treatment));
        treatmentButtons[t].tabIndex=t===S.treatment?0:-1;});
      root.dataset.treatment=S.treatment;
      motion.setAttribute('aria-pressed',String(S.reduced));
      root.classList.toggle('atl-reduced',S.reduced);
      ribbon.textContent='Treatment '+S.treatment+' · '+M.TREATMENTS[S.treatment]+' — '+
        ({A:'positions stay where they are; relationships are revealed in place.',
          B:'the neighbourhood is recomposed into a balanced constellation; the wider atlas stays still.',
          C:'relationships are revealed first; only neighbours that are hard to read move closer.'})[S.treatment]+
        ' Positions are presentation, never narrative evidence. Nothing is saved.';
    }
    function announce(text){live.textContent='';global.setTimeout(function(){live.textContent=text;},30);}

    /* ---------- Input ---------- */
    starLayer.addEventListener('keydown',function(e){
      var star=e.target.closest&&e.target.closest('.atl-star');if(!star)return;
      var id=star.dataset.id,dirs={ArrowRight:0,ArrowDown:Math.PI/2,ArrowLeft:Math.PI,ArrowUp:-Math.PI/2};
      if(dirs[e.key]!==undefined){e.preventDefault();var next=nearest(id,dirs[e.key]);if(next){setRoving(next);starEls[next].focus({preventScroll:true});ensureVisible(next);}}
      else if(e.key===']'||e.key==='+'||e.code==='BracketRight'){e.preventDefault();deeper(true);}
      else if(e.key==='['||e.key==='-'||e.code==='BracketLeft'){e.preventDefault();deeper(false);}
      else if(e.key==='Backspace'&&S.focus){e.preventDefault();back();}
    });
    root.addEventListener('keydown',function(e){
      if(e.key==='Escape'&&S.focus&&!(e.target.closest&&e.target.closest('details[open] summary'))){e.preventDefault();returnToAtlas();}
    });
    function navigable(){
      var ids=S.model.concepts.map(function(c){return c.id;});
      if(S.hood)return ids.filter(function(id){return S.hood.levels[id]!==undefined;});
      return ids.filter(function(id){return S.model.byId[id].tier===1||S.cam.z>=0.82;});
    }
    function nearest(id,angle){
      var from=S.pos[id],best=null,score=Infinity;
      navigable().forEach(function(other){
        if(other===id)return;var p=S.pos[other],dx=p.x-from.x,dy=p.y-from.y,d=Math.sqrt(dx*dx+dy*dy);
        var diff=Math.abs(Math.atan2(dy,dx)-angle);diff=Math.min(diff,2*Math.PI-diff);
        if(diff>Math.PI*0.42)return;var s=d*(1+diff*1.8);if(s<score){score=s;best=other;}
      });
      return best;
    }
    function ensureVisible(id){
      var p=toScreen(S.pos[id]),v=view();
      if(p.x<60||p.y<40||p.x>v.width-200||p.y>v.height-40)
        animate({camera:{cx:S.pos[id].x,cy:S.pos[id].y,z:Math.max(S.cam.z,0.7)},cameraDuration:S.reduced?0:360});
      if(S.reduced)flushInstant();
    }
    var drag=null;
    stage.addEventListener('pointerdown',function(e){
      if(e.button!==0||e.target.closest('button,a,nav,.atl-zoom'))return;
      drag={x:e.clientX,y:e.clientY,cx:S.cam.cx,cy:S.cam.cy,moved:false,id:e.pointerId};
      stage.setPointerCapture(e.pointerId);
    });
    stage.addEventListener('pointermove',function(e){
      if(!drag||e.pointerId!==drag.id)return;
      var dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.abs(dx)+Math.abs(dy)>4)drag.moved=true;
      if(drag.moved){S.cam={cx:drag.cx-dx/S.cam.z,cy:drag.cy-dy/S.cam.z,z:S.cam.z};if(S.tw)S.tw.cam=null;paint();stage.classList.add('is-panning');}
    });
    function endDrag(e){
      if(!drag||e.pointerId!==drag.id)return;
      var wasClick=!drag.moved;drag=null;stage.classList.remove('is-panning');
      if(wasClick&&S.focus&&e.type==='pointerup')returnToAtlas();
    }
    stage.addEventListener('pointerup',endDrag);stage.addEventListener('pointercancel',endDrag);
    stage.addEventListener('wheel',function(e){
      if(!(e.ctrlKey||e.metaKey)||!S.model)return;e.preventDefault();
      var r=stage.getBoundingClientRect();zoomBy(e.deltaY<0?1.12:0.89,{x:e.clientX-r.left,y:e.clientY-r.top});
    },{passive:false});
    var resizeTimer=null;
    if(global.ResizeObserver)new ResizeObserver(function(){
      if(!S.model||!S.shown)return;global.clearTimeout(resizeTimer);
      resizeTimer=global.setTimeout(function(){
        measureView();
        if(!S.sizedOnce){S.sizedOnce=true;fitAtlas(false);applyPending();return;}
        if(!S.focus)fitAtlas(false);else{var cam=cameraFor(S.hood.order);if(cam)S.cam=cam;paint();settle();}
      },80);
    }).observe(stage);

    /* ---------- Source binding ---------- */
    function update(){
      var candidate=binding.getCandidate(),sha=binding.getRequestSha();
      if(S.model&&sha===S.sha&&candidate===S.candidateRef)return;
      var hadFocus=!!S.focus;
      S.candidateRef=candidate;
      if(!candidate||!(candidate.nodes||[]).length){S.model=null;S.atlas=null;S.sha=sha;
        buildEmpty();renderFolio();renderTrail();return;}
      var aspect=stage.clientWidth&&stage.clientHeight?stage.clientWidth/stage.clientHeight:1.4;
      try{S.model=M.buildModel(candidate,sha);S.atlas=M.layoutAtlas(S.model,{aspect:aspect});}
      catch(error){S.model=null;buildEmpty('The atlas could not be drawn: '+error.message);renderFolio();return;}
      S.sha=sha;S.pos={};Object.keys(S.atlas.positions).forEach(function(id){S.pos[id]={x:S.atlas.positions[id].x,y:S.atlas.positions[id].y};});
      S.focus=null;S.hood=null;S.comp=null;S.trail=[];S.depth=1;S.sides={};S.restCam=null;S.tw=null;
      empty.hidden=true;buildScene();syncChrome();applyStates();syncVerbs();syncTethers();
      if(S.shown&&stage.clientWidth){fitAtlas(false);applyPending();}
      renderFolio();renderTrail();
      if(hadFocus)announce('The working Architecture changed; the atlas was redrawn and your previous focus cleared. Nothing was saved.');
    }
    function applyPending(){
      var p=S.pending;S.pending=null;
      if(p&&p.focus&&S.model&&S.model.byId[p.focus]){
        var keep=S.reduced;S.reduced=true;select(p.focus,{via:'atlas',depth:p.depth===2?2:1,focusStar:false});S.reduced=keep;
      }else settle();
    }
    function buildEmpty(message){
      starLayer.replaceChildren();gEdges.replaceChildren();gVerbs.replaceChildren();gTethers.replaceChildren();
      gBands.replaceChildren();gSpine.replaceChildren();bandLabels.replaceChildren();
      empty.hidden=false;empty.replaceChildren(el('h3','','The atlas is waiting for an Architecture'),
        el('p','',message||'Develop a working Architecture proposal, then come back to explore it here.'));
    }
    function show(){
      var first=!S.shown;S.shown=true;root.hidden=false;measureView();update();
      var inspector=!!(binding.inspectorOpen&&binding.inspectorOpen());
      if(inspector!==S.inspectorOpen){S.inspectorOpen=inspector;if(!first)renderFolio();}
      if(first&&S.model&&stage.clientWidth){S.sizedOnce=true;fitAtlas(false);applyPending();}
    }
    function hide(){S.shown=false;root.hidden=true;}
    syncChrome();
    var api={update:update,show:show,hide:hide,select:function(id,o){select(id,Object.assign({via:'atlas'},o||{}));},
      returnToAtlas:returnToAtlas,deeper:deeper,setTreatment:setTreatment,
      setReducedMotion:function(on){S.reduced=!!on;syncChrome();},
      fitAtlas:function(){fitAtlas(false);settle();},
      metrics:function(){return S.metrics;},
      snapshot:function(){return {treatment:S.treatment,focus:S.focus,depth:S.depth,trail:S.trail.slice(),
        camera:Object.assign({},S.cam),restCamera:S.restCam&&Object.assign({},S.restCam),
        positions:S.model?Object.keys(S.pos).reduce(function(o,id){o[id]={x:Math.round(S.pos[id].x),y:Math.round(S.pos[id].y)};return o;},{}):{},
        home:S.atlas?Object.keys(S.atlas.positions).reduce(function(o,id){o[id]={x:Math.round(S.atlas.positions[id].x),y:Math.round(S.atlas.positions[id].y)};return o;},{}):{},
        concepts:S.model?S.model.concepts.map(function(c){return {id:c.id,facet:c.facet,tier:c.tier,title:c.title,
          relations:S.model.adjacency[c.id].length};}):[]};}};
    // Read-only handle for study evidence capture; it cannot change story or canvas state.
    root.atelierStudy={metrics:api.metrics,snapshot:api.snapshot};
    return api;
  }
  global.AuteurStudioAtelier={create:create};
})(window,document);
