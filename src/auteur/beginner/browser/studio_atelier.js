/* Living Narrative Atelier — experimental visual study stage (opt-in via ?atelier).
   A is the world: a stable, information-rich atlas of the working Architecture in which selecting a
   concept brings its recorded relationships forward in place; nothing moves and the view is kept.
   B is the magnifying glass: an explicit Focused Constellation that recomposes one neighbourhood for
   close reading and returns to the atlas as it was left. C (contextual unfolding) survives only as a
   research comparison (?atelier=C). Presentation only: layout, camera and focus live in memory;
   nothing is saved or accepted. */
(function(global,document){
  'use strict';
  var M=global.AuteurStudioAtelierModel,SVG='http://www.w3.org/2000/svg';
  var SERIF='"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif';
  var SANS='system-ui,-apple-system,"Segoe UI",sans-serif';
  var TIMING={
    A:{stagger:34,first:110,grow:540,camera:620,move:0,moveDelay:0,moveStagger:0},
    B:{stagger:16,first:40,grow:560,camera:820,move:780,moveDelay:0,moveStagger:14},
    C:{stagger:26,first:80,grow:460,camera:700,move:660,moveDelay:420,moveStagger:14},
    back:{move:620,camera:660}
  };
  var ATLAS_X0=150;
  var EASE_MOVE=function(t){return t<0.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;};
  var EASE_CAM=function(t){return 1-Math.pow(1-t,3)*(1-t*0.35);};
  var EASE_GROW=function(t){return 1-Math.pow(1-t,3);};
  /* Typography is measured before it is set, so every label is placed where it will actually fit.
     Each style here is mirrored exactly by a [data-style] rule in studio_atelier.css. */
  var STYLE={
    genre:{font:'600 12.5px '+SERIF,lh:15,px:2,py:1,maxW:152,lines:2},
    phase:{font:'500 11.5px '+SERIF,lh:13.5,px:2,py:1,maxW:118,lines:3},
    rest:{font:'500 10.5px '+SANS,lh:12.5,px:2,py:1,maxW:128,lines:2},
    mote:{font:'400 10px '+SANS,lh:12,px:2,py:0,maxW:150,lines:1},
    near:{font:'500 12px '+SANS,lh:14.5,px:7,py:3,maxW:196,lines:2},
    far:{font:'400 11px '+SANS,lh:13,px:5,py:2,maxW:180,lines:2},
    verb:{font:'italic 11.5px '+SERIF,lh:14,px:4,py:1,maxW:190,lines:1},
    focus:{font:'600 16px '+SERIF,lh:20,px:12,py:7,maxW:260,lines:4,kicker:'700 9.5px '+SANS,klh:15},
    focusLong:{font:'600 14px '+SERIF,lh:18,px:12,py:7,maxW:300,lines:7,kicker:'700 9.5px '+SANS,klh:15},
    callout:{font:'500 12px '+SANS,lh:15.5,px:8,py:5,maxW:250,lines:8,kicker:'700 9px '+SANS,klh:13},
    nearVerb:{font:'500 12px '+SANS,lh:14.5,px:7,py:3,maxW:260,lines:2,kicker:'italic 11px '+SERIF,klh:13}
  };
  var FACET_BASE={genres:640,timeline:620,emotions:440,structure:452,tropes:444,other:430};
  var GLYPH_R={genres:5.6,emotions:5,timeline:6.5,tropes:6.5,structure:4.8,other:5};
  var AROUND=['e','w','se','ne','sw','nw','s','n'];
  function el(tag,cls,text){var e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=String(text);return e;}
  function sv(tag,attrs){var e=document.createElementNS(SVG,tag);Object.keys(attrs||{}).forEach(function(k){e.setAttribute(k,attrs[k]);});return e;}
  function clamp(v,a,b){return Math.max(a,Math.min(b,v));}
  function hash(t){var h=2166136261;t=String(t);for(var i=0;i<t.length;i++){h^=t.charCodeAt(i);h=Math.imul(h,16777619);}return (h>>>0)/4294967295;}
  function lerp(a,b,k){return {x:a.x+(b.x-a.x)*k,y:a.y+(b.y-a.y)*k};}
  function prefersReduced(){try{return global.matchMedia('(prefers-reduced-motion: reduce)').matches;}catch(_){return false;}}
  var facetOrder={genres:0,emotions:1,timeline:2,tropes:3,structure:4,other:5};

  /* ---------- Text measurement ---------- */
  var ctx=null,widths={};
  function textWidth(text,font){
    var k=font+'|'+text;if(widths[k]!==undefined)return widths[k];
    if(!ctx)ctx=document.createElement('canvas').getContext('2d');
    if(!ctx)return (widths[k]=text.length*6.4);
    ctx.font=font;return (widths[k]=ctx.measureText(text).width);
  }
  // A shortened line ends at a word, never inside one, unless a single word is itself too long.
  function fitLine(text,font,maxW){
    if(textWidth(text,font)<=maxW)return text;
    var s=text;while(s.length>1&&textWidth(s+'…',font)>maxW)s=s.slice(0,-1);
    var space=s.lastIndexOf(' ');if(space>s.length*0.4)s=s.slice(0,space);
    return s.replace(/[\s,;:.·–-]+$/,'')+'…';
  }
  function wrapText(text,style,maxW,maxLines){
    maxW=Math.max(24,maxW||style.maxW);var limit=maxLines||style.lines;
    var font=style.font,words=String(text||'').split(/\s+/).filter(Boolean),lines=[],cur='';
    words.forEach(function(w){var t=cur?cur+' '+w:w;if(!cur||textWidth(t,font)<=maxW)cur=t;else{lines.push(cur);cur=w;}});
    if(cur)lines.push(cur);
    if(lines.length>limit){var keep=lines.slice(0,limit);keep[limit-1]=lines.slice(limit-1).join(' ');lines=keep;}
    lines=lines.map(function(l){return fitLine(l,font,maxW);});
    var w=0;lines.forEach(function(l){w=Math.max(w,textWidth(l,font));});
    return {lines:lines,w:Math.ceil(w)+2*style.px+1,h:Math.ceil(lines.length*style.lh)+2*style.py};
  }

  function create(binding){
    if(!M)throw Error('Atelier model unavailable');
    if(!binding||!binding.root||typeof binding.getCandidate!=='function'||typeof binding.getRequestSha!=='function')
      throw Error('Atelier binding requires root, getCandidate and getRequestSha');
    var root=binding.root,requested=String(binding.treatment||'').toUpperCase();
    var S={model:null,atlas:null,sha:null,mode:'atlas',research:requested==='C',researchAvailable:requested==='C',
      focus:null,depth:1,trail:[],cam:{cx:0,cy:0,z:1},restCam:null,atlasCam:null,userCam:false,pos:{},sides:{},
      hood:null,comp:null,metrics:null,reduced:prefersReduced(),lens:null,roving:null,tw:null,raf:null,frames:[],
      shown:false,pending:binding.initial?Object.assign({examine:requested==='B'},binding.initial):null,
      lastAction:null,edgeGrow:{},mix:0,sizedOnce:false,verbAt:{},verbFor:{},labelStats:null,lastFocus:null,
      hover:null,folioHint:null,callout:null,latched:false,ptr:null,dragging:false};

    /* ---------- Static frame ---------- */
    root.replaceChildren();root.classList.add('atl');
    var bar=el('header','atl-bar');
    var heading=el('div','atl-heading');
    heading.append(el('span','atl-eyebrow','Visual study · experimental · presentation only'),
      el('strong','atl-title','The Living Narrative Atelier'));
    var modes=el('div','atl-modes');modes.setAttribute('role','group');modes.setAttribute('aria-label','Way of looking');
    var modeButtons={};
    function modeButton(key,name,note,fn){
      var b=el('button','atl-mode');b.type='button';b.dataset.mode=key;
      b.append(el('span','atl-mode-glyph'),el('span','atl-mode-name',name));
      if(note)b.title=note;b.addEventListener('click',fn);modes.append(b);modeButtons[key]=b;return b;
    }
    modeButton('atlas',M.MODES.atlas,'The whole story, with relationships revealed in place',function(){
      if(S.mode==='constellation')leaveConstellation();else if(S.research)setResearch(false);});
    modeButton('constellation',M.MODES.constellation,'Recompose the selected concept’s neighbourhood for close reading',function(){
      if(S.mode==='constellation')leaveConstellation();else examine();});
    if(S.researchAvailable)modeButton('research','C · research','Research comparison: contextual unfolding',function(){setResearch(!S.research);});
    var tools=el('div','atl-tools');
    var motion=el('button','atl-tool','Reduced motion');motion.type='button';
    motion.addEventListener('click',function(){S.reduced=!S.reduced;syncChrome();announce(S.reduced?'Reduced motion on: changes appear without travel.':'Full motion on.');});
    var readout=el('details','atl-readout');var readoutSummary=el('summary','','Study readout');
    var readoutBody=el('dl','atl-readout-body');readout.append(readoutSummary,readoutBody);
    tools.append(motion,readout);
    bar.append(heading,modes,tools);
    var ribbon=el('p','atl-ribbon');
    var body=el('div','atl-body');
    var stage=el('div','atl-stage');stage.setAttribute('role','group');
    stage.setAttribute('aria-roledescription','narrative atlas');
    var lensGlow=el('div','atl-lens');lensGlow.setAttribute('aria-hidden','true');
    var svg=sv('svg',{'class':'atl-paths','aria-hidden':'true'});
    var defs=sv('defs');
    ['genres','emotions','timeline','tropes','structure','other','ink'].forEach(function(f){
      var m=sv('marker',{id:'atl-arrow-'+f,viewBox:'0 0 10 10',refX:'8.5',refY:'5',markerWidth:'7',markerHeight:'7',orient:'auto-start-reverse'});
      m.append(sv('path',{d:'M1 1.5 L9 5 L1 8.5',fill:'none','class':'atl-arrow atl-arrow-'+f}));defs.append(m);
    });
    var gGrid=sv('g',{'class':'atl-g-grid'}),gBands=sv('g',{'class':'atl-g-bands'}),gSpine=sv('g',{'class':'atl-g-spine'});
    // Threads outside the current neighbourhood live in their own group: it dims as one, and it rests
    // while the camera travels, so a transition never redraws the whole relationship network per frame.
    var gTethers=sv('g',{'class':'atl-g-tethers'}),gBack=sv('g',{'class':'atl-g-back'}),gEdges=sv('g',{'class':'atl-g-edges'}),gVerbs=sv('g',{'class':'atl-g-verbs'});
    svg.append(defs,gBands,gGrid,gSpine,gTethers,gBack,gEdges,gVerbs);
    var bandLabels=el('div','atl-band-labels');bandLabels.setAttribute('aria-hidden','true');
    var starLayer=el('div','atl-stars');starLayer.setAttribute('role','group');
    var trail=el('nav','atl-trail');trail.setAttribute('aria-label','Exploration path');
    var lensbar=el('div','atl-lensbar');lensbar.hidden=true;
    var zoom=el('div','atl-zoom');
    function zoomButton(text,label,fn){var b=el('button','atl-zoom-btn',text);b.type='button';b.setAttribute('aria-label',label);b.title=label;b.addEventListener('click',fn);zoom.append(b);return b;}
    zoomButton('+','Zoom in',function(){zoomBy(1.25);});
    zoomButton('−','Zoom out',function(){zoomBy(0.8);});
    zoomButton('⤢','Show the whole story',function(){S.userCam=true;fitAtlas(true);});
    var fitHood=zoomButton('◎','Fit this neighbourhood',function(){fitNeighbourhood();});fitHood.hidden=true;
    var compass=el('div','atl-compass');
    var hint=el('p','atl-hint','Arrows move · Enter reveals · E examines as a constellation · ] deeper · Esc returns');
    var empty=el('div','atl-empty');
    stage.append(lensGlow,svg,bandLabels,starLayer,compass,trail,lensbar,zoom,hint,empty);
    var folio=el('aside','atl-folio');folio.setAttribute('aria-label','Reading of the narrative atlas');
    body.append(stage,folio);
    var live=el('p','atl-live');live.setAttribute('aria-live','polite');live.setAttribute('role','status');
    root.append(bar,ribbon,body,live);

    var starEls={},edgeEls={},verbEls={},tetherEls={},bandEls=[],bandLabelEls=[],gridEls=null,bandOf={};

    /* ---------- Camera ---------- */
    // The stage size is read once per resize, never inside a frame (reading it per point forces layout).
    function measureView(){S.view={width:stage.clientWidth||960,height:stage.clientHeight||600};return S.view;}
    function view(){return S.view||measureView();}
    function screenOf(p,cam){var v=view();cam=cam||S.cam;return {x:(p.x-cam.cx)*cam.z+v.width/2,y:(p.y-cam.cy)*cam.z+v.height/2};}
    function toScreen(p){return screenOf(p,S.cam);}
    function narrow(){return view().width<600;}
    // On a phone the folio sits below the stage; after a change of view the stage is brought back to the top.
    function bringStageIntoView(){
      if(!narrow()||!stage.getBoundingClientRect)return;
      var top=stage.getBoundingClientRect().top;
      if(top<0||top>global.innerHeight*0.6)stage.scrollIntoView({block:'start'});
    }
    /* Phone constellation: the focus sits near the top-left with its card beside it, and the list of
       related concepts hangs below. The stage grows to hold the whole list, so the page scrolls to it
       as any document does; leaving the constellation gives the stage its height back. */
    var PHONE_FOCUS={x:36,y:130};
    function fitPhoneStage(on){
      if(!S.model)return;
      var want='';
      if(on&&S.focus&&stage.clientWidth&&stage.clientWidth<600){
        var h=M.neighbourhood(S.model,S.focus,S.depth),L=M.PHONE_LIST;
        if(!stage.style.height)S.phoneBaseH=stage.clientHeight;
        want=Math.max(S.phoneBaseH||0,Math.round(PHONE_FOCUS.y+L.start+h.first.length*L.near+h.second.length*L.far+72))+'px';
      }
      if(stage.style.height===want)return;
      stage.style.height=want;measureView();S.paintedView={width:S.view.width,height:S.view.height};
    }
    function zoomBy(f,anchor){
      if(!S.model)return;
      var v=view(),ax=anchor?anchor.x:v.width/2,ay=anchor?anchor.y:v.height/2;
      var wx=(ax-v.width/2)/S.cam.z+S.cam.cx,wy=(ay-v.height/2)/S.cam.z+S.cam.cy,z=clamp(S.cam.z*f,0.22,2.2);
      S.userCam=true;S.lastAction={kind:'zoom',at:performance.now()};
      animate({camera:{z:z,cx:wx-(ax-v.width/2)/z,cy:wy-(ay-v.height/2)/z},cameraDuration:S.reduced?0:220});
      if(S.reduced)flushInstant();
    }
    function fitAtlas(animated){
      if(!S.model)return;
      var to=M.restCamera(S.atlas,view());S.lastAction={kind:'fit',at:performance.now()};
      if(animated&&!S.reduced)animate({camera:to,cameraDuration:520});else{S.cam=to;paint();}
    }
    // Progressive revelation keeps the author's viewpoint: the camera pans only as far as the focus
    // needs to be readable, and never zooms out because a neighbourhood is large.
    function atlasFocusCamera(id,base){
      base=base||S.cam;var v=view(),p=screenOf(S.atlas.positions[id],base);
      // The focus's title card is centred under it, so the focus keeps half a card clear of each side
      // (and of the zoom buttons on the right).
      var half=focusSpec(S.model.byId[id]).w/2+10;
      // On a phone the card has room above the focus clear of the trail, or below it (from PR #629).
      var m={l:Math.max((narrow()?96:172)+16,half),r:Math.max(56,half+44),t:narrow()?64:34,b:narrow()?130:48},dx=0,dy=0;
      if(p.x<m.l)dx=p.x-m.l;else if(p.x>v.width-m.r)dx=p.x-(v.width-m.r);
      if(p.y<m.t)dy=p.y-m.t;else if(p.y>v.height-m.b)dy=p.y-(v.height-m.b);
      if(Math.abs(dx)<1&&Math.abs(dy)<1)return null;
      return {cx:base.cx+dx/base.z,cy:base.cy+dy/base.z,z:base.z};
    }
    function rectOf(ids,targets,sides,scale){
      var x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity;
      ids.forEach(function(id){var r=M.labelRect(S.model,id,targets[id],sides[id]||'right',S.focus,scale||1);
        x0=Math.min(x0,r.x0);y0=Math.min(y0,r.y0-8);x1=Math.max(x1,r.x1);y1=Math.max(y1,r.y1+8);});
      return {x0:x0,y0:y0,x1:x1,y1:y1};
    }
    // The constellation is composed at reading scale (zoom 1) and framed around its composition.
    function constellationCamera(ids){
      var v=view(),pad=40,t=S.comp.targets,f=t[S.focus];
      if(narrow())return {z:1,cx:f.x+v.width/2-PHONE_FOCUS.x,cy:f.y+v.height/2-PHONE_FOCUS.y};
      var fits=function(r){return r.x1-r.x0<=v.width-2*pad&&r.y1-r.y0<=v.height-2*pad;};
      var rect=rectOf(ids,t,S.comp.sides,1);
      // When second-order concepts make the composition too big, the direct relatives are kept in view.
      if(!fits(rect)&&S.hood){var core=rectOf([S.focus].concat(S.hood.first),t,S.comp.sides,1);if(fits(core))rect=core;}
      var w=rect.x1-rect.x0,h=rect.y1-rect.y0;
      var cx=w<=v.width-2*pad?(rect.x0+rect.x1)/2:clamp((rect.x0+rect.x1)/2,f.x-v.width/2+170,f.x+v.width/2-170);
      // Too tall even so: centre on the direct relatives, keeping the focus well inside the stage.
      var cy=h<=v.height-2*pad?(rect.y0+rect.y1)/2:clamp((rect.y0+rect.y1)/2,f.y-v.height/2+150,f.y+v.height/2-150);
      return {z:1,cx:cx,cy:cy};
    }
    function neighbourhoodFit(ids){
      // Glyphs stay put; labels keep their screen size, so fit glyphs plus a label margin.
      var v=view(),pad=36,t=S.atlas.positions,gx0=Infinity,gy0=Infinity,gx1=-Infinity,gy1=-Infinity;
      ids.forEach(function(id){var p=t[id];gx0=Math.min(gx0,p.x);gy0=Math.min(gy0,p.y);gx1=Math.max(gx1,p.x);gy1=Math.max(gy1,p.y);});
      var over={l:(narrow()?96:172),r:190,t:30,b:80};
      var z=clamp(Math.min((v.width-2*pad-over.l-over.r)/Math.max(gx1-gx0,1),(v.height-2*pad-over.t-over.b)/Math.max(gy1-gy0,1)),0.26,1.2);
      return {z:z,cx:(gx0-over.l/z+gx1+over.r/z)/2,cy:(gy0-over.t/z+gy1+over.b/z)/2};
    }
    function fitNeighbourhood(){
      if(!S.focus||S.mode!=='atlas')return;
      S.userCam=true;S.lastAction={kind:'fit-neighbourhood',id:S.focus,at:performance.now()};
      animate({camera:neighbourhoodFit(S.hood.order),cameraDuration:S.reduced?0:560});
      if(S.reduced)flushInstant();
    }
    function panToward(ids){
      if(!S.focus)return;
      var v=view(),pts=ids.concat([S.focus]).map(function(id){return S.pos[id];});
      var x0=Math.min.apply(null,pts.map(function(p){return p.x;})),x1=Math.max.apply(null,pts.map(function(p){return p.x;}));
      var y0=Math.min.apply(null,pts.map(function(p){return p.y;})),y1=Math.max.apply(null,pts.map(function(p){return p.y;}));
      var z=S.cam.z,to;
      if((x1-x0)*z<v.width-340&&(y1-y0)*z<v.height-140)to={cx:(x0+x1)/2+60/z,cy:(y0+y1)/2,z:z};
      else{var f=S.pos[S.focus],near=ids.slice().sort(function(a,b){return Math.hypot(S.pos[a].x-f.x,S.pos[a].y-f.y)-Math.hypot(S.pos[b].x-f.x,S.pos[b].y-f.y);})[0];
        to={cx:S.pos[near].x,cy:S.pos[near].y,z:z};}
      S.userCam=true;S.lastAction={kind:'pan',at:performance.now()};
      animate({camera:to,cameraDuration:S.reduced?0:520});if(S.reduced)flushInstant();
    }

    /* ---------- Scene ---------- */
    function gs(cn){return cn.tier===2?1:0.8+0.55*Math.sqrt((cn.degree||0)/(S.model.maxDegree||1));}
    function glyphRadius(id,st){
      var cn=S.model.byId[id];st=st||starState(id);
      return (GLYPH_R[cn.facet]||5)*(cn.tier===2?(st==='near'||st==='far'?0.8:0.55):1)*gs(cn)*(st==='focus'?1.75:1)+1;
    }
    function buildScene(){
      starLayer.replaceChildren();gEdges.replaceChildren();gBack.replaceChildren();gVerbs.replaceChildren();gTethers.replaceChildren();
      gBands.replaceChildren();gSpine.replaceChildren();gGrid.replaceChildren();bandLabels.replaceChildren();
      starEls={};edgeEls={};verbEls={};tetherEls={};bandEls=[];bandLabelEls=[];bandOf={};S.edgeGrow={};S.verbAt={};S.back={};
      var model=S.model,atlas=S.atlas;
      starLayer.setAttribute('aria-label','Narrative atlas: '+model.concepts.length+' concepts and '+
        model.relations.length+' documented relationships. Arrow keys move between concepts.');
      atlas.bands.forEach(function(b,i){
        var rect=sv('rect',{'class':'atl-band atl-band-'+b.facet+(i%2?' is-alt':'')});gBands.append(rect);bandEls.push({band:b,rect:rect});
        var label=el('span','atl-band-label atl-facet-'+b.facet);
        label.append(el('span','atl-band-glyph'),el('span','atl-band-name',b.label),el('span','atl-band-count',String(b.count)));
        bandLabels.append(label);bandLabelEls.push({band:b,label:label,w:0});
      });
      model.concepts.forEach(function(cn){bandOf[cn.id]=atlas.bands.findIndex(function(b){return b.facet===cn.facet;});});
      // Story-time grid: a hairline under every phase across all bands, alternate Books lightly shaded,
      // and each Book named once as a running head.
      var shades=atlas.books.map(function(bk,i){var r=sv('rect',{'class':'atl-book-shade'+(i%2?' is-alt':'')});gGrid.append(r);return r;});
      var meridians=model.timeline.map(function(){var l=sv('line',{'class':'atl-meridian'});gGrid.append(l);return l;});
      var heads=atlas.books.map(function(bk){var t=sv('text',{'class':'atl-book-label'});t.textContent=bk.label.toUpperCase();
        t.__w=textWidth(t.textContent,'600 8.5px '+SANS)+t.textContent.length*0.68+10;
        var title=sv('title');title.textContent=bk.label+(bk.durationUnknown?' · duration unknown':'');t.append(title);gGrid.append(t);return t;});
      var spinePath=sv('path',{'class':'atl-spine'}),railPath=sv('path',{'class':'atl-rail'});gSpine.append(spinePath);gEdges.before(railPath);
      gridEls={shades:shades,meridians:meridians,heads:heads,spine:spinePath,rail:railPath};
      model.relations.forEach(function(r){
        var p=sv('path',{'class':'atl-edge','data-facet':model.byId[r.to].facet});
        gBack.append(p);edgeEls[r.id]=p;S.edgeGrow[r.id]=1;S.back[r.id]=true;
      });
      model.concepts.forEach(function(cn){
        var b=el('button','atl-star');b.type='button';b.tabIndex=-1;
        b.dataset.id=cn.id;b.dataset.facet=cn.facet;b.dataset.tier=String(cn.tier);
        b.style.setProperty('--gs',gs(cn).toFixed(3));
        var glyph=el('span','atl-glyph');glyph.setAttribute('aria-hidden','true');
        var text=el('span','atl-text');text.setAttribute('aria-hidden','true');
        var kicker=el('span','atl-kicker'),label=el('span','atl-label');
        text.append(kicker,label);b.append(glyph,text);b.__text=text;b.__label=label;b.__kicker=kicker;
        b.title=cn.title;
        var count=model.adjacency[cn.id].length;
        b.setAttribute('aria-label',M.FACET_SINGULAR[cn.facet]+': '+cn.title+'. '+count+' documented relationship'+(count===1?'':'s')+
          '. Agent proposal, not accepted story.');
        if(cn.category)b.dataset.category=cn.category;
        b.addEventListener('click',function(){if(S.focus!==cn.id)select(cn.id,{via:'atlas'});else focusFolio();});
        b.addEventListener('focus',function(){setRoving(cn.id);refreshEmphasis();});
        b.addEventListener('blur',function(){global.setTimeout(refreshEmphasis,0);});
        starLayer.append(b);starEls[cn.id]=b;
      });
      var first=model.timeline[0]||model.concepts[0];if(first)setRoving(first.id);
    }
    function setRoving(id){
      if(S.roving&&starEls[S.roving])starEls[S.roving].tabIndex=-1;
      S.roving=id;if(starEls[id])starEls[id].tabIndex=0;
    }

    /* ---------- Relationship paths ----------
       In the atlas every relationship is a thread that leaves and enters its concepts vertically,
       so the score reads as warp threads between bands rather than a tangle. In a constellation the
       same relationship bends into a gentle arc. A path's shape never changes its meaning. */
    function trim(p,toward,fallback,r){
      var vx=toward.x-p.x,vy=toward.y-p.y,l=Math.sqrt(vx*vx+vy*vy);
      if(l<0.5){vx=fallback.x-p.x;vy=fallback.y-p.y;l=Math.sqrt(vx*vx+vy*vy)||1;}
      return {x:p.x+vx/l*r,y:p.y+vy/l*r};
    }
    function edgeGeom(r,a,b,mix,ra,rb){
      var dx=b.x-a.x,dy=b.y-a.y,c1,c2;
      if(Math.abs(dy)<14){
        var down=S.atlas.bands[bandOf[r.from]]&&S.atlas.bands[bandOf[r.from]].facet==='timeline'?1:-1;
        var lift=Math.min(90,Math.abs(dx)*0.26+14)*down;
        c1={x:a.x+dx*0.2,y:a.y+lift};c2={x:b.x-dx*0.2,y:b.y+lift};
      }else{c1={x:a.x,y:a.y+dy*0.5};c2={x:b.x,y:b.y-dy*0.5};}
      if(mix>0.001&&narrow()&&S.focus&&(r.from===S.focus||r.to===S.focus)){
        var fp=r.from===S.focus?a:b,op=r.from===S.focus?b:a,corner={x:fp.x,y:op.y};
        c1=lerp(c1,corner,mix);c2=lerp(c2,corner,mix);
      }else if(mix>0.001){
        var len=Math.sqrt(dx*dx+dy*dy)||1,bend=Math.min(54,len*0.13)*(hash(r.id)<0.5?-1:1);
        var c={x:(a.x+b.x)/2-dy/len*bend,y:(a.y+b.y)/2+dx/len*bend};
        c1=lerp(c1,{x:a.x+(c.x-a.x)*2/3,y:a.y+(c.y-a.y)*2/3},mix);
        c2=lerp(c2,{x:b.x+(c.x-b.x)*2/3,y:b.y+(c.y-b.y)*2/3},mix);
      }
      return {p0:trim(a,c1,b,ra),c1:c1,c2:c2,p1:trim(b,c2,a,rb)};
    }
    function fmt(p){return p.x.toFixed(1)+' '+p.y.toFixed(1);}
    function cubicPath(g,s,reverse){
      var p0=reverse?g.p1:g.p0,c1=reverse?g.c2:g.c1,c2=reverse?g.c1:g.c2,p1=reverse?g.p0:g.p1;
      if(s>=0.999)return 'M'+fmt(p0)+'C'+fmt(c1)+' '+fmt(c2)+' '+fmt(p1);
      var a=lerp(p0,c1,s),b=lerp(c1,c2,s),c=lerp(c2,p1,s),d=lerp(a,b,s),e=lerp(b,c,s),k=lerp(d,e,s);
      return 'M'+fmt(p0)+'C'+fmt(a)+' '+fmt(d)+' '+fmt(k);
    }
    function pointAt(g,t){var u=1-t,a=u*u*u,b=3*u*u*t,c=3*u*t*t,d=t*t*t;
      return {x:a*g.p0.x+b*g.c1.x+c*g.c2.x+d*g.p1.x,y:a*g.p0.y+b*g.c1.y+c*g.c2.y+d*g.p1.y};}

    /* ---------- Painting (screen space; one pass per frame, idle once settled) ---------- */
    function paint(){
      if(!S.model)return;
      var model=S.model,atlas=S.atlas,v=view();svg.setAttribute('viewBox','0 0 '+v.width+' '+v.height);
      svg.setAttribute('width',v.width);svg.setAttribute('height',v.height);
      var screen={};
      model.concepts.forEach(function(cn){
        var p=toScreen(S.pos[cn.id]),b=starEls[cn.id],tf='translate('+p.x.toFixed(1)+'px,'+p.y.toFixed(1)+'px)';screen[cn.id]=p;
        if(b.__tf!==tf){b.__tf=tf;b.style.transform=tf;}
      });
      bandEls.forEach(function(x){
        var a=toScreen({x:0,y:x.band.y0}),b=toScreen({x:0,y:x.band.y1});
        x.rect.setAttribute('x',0);x.rect.setAttribute('width',v.width);
        x.rect.setAttribute('y',a.y.toFixed(1));x.rect.setAttribute('height',Math.max(0,b.y-a.y).toFixed(1));
      });
      bandLabelEls.forEach(function(x){
        var y=toScreen({x:0,y:(x.band.y0+x.band.y1)/2}).y;
        x.label.style.transform='translateY('+(y-9).toFixed(1)+'px)';
        var off=y<-20||y>v.height+20;if(x.label.hidden!==off)x.label.hidden=off;
      });
      var top=atlas.bands.length?atlas.bands[0].y0:0,bottom=atlas.bands.length?atlas.bands[atlas.bands.length-1].y1:atlas.height;
      var yTop=toScreen({x:0,y:top-8}).y,yBot=toScreen({x:0,y:bottom}).y,half=atlas.phaseGap/2;
      atlas.books.forEach(function(bk,i){
        var a=toScreen({x:bk.x0-half,y:top}),b=toScreen({x:bk.x1+half,y:top});
        var r=gridEls.shades[i];r.setAttribute('x',a.x.toFixed(1));r.setAttribute('width',Math.max(0,b.x-a.x).toFixed(1));
        r.setAttribute('y',(yTop-22).toFixed(1));r.setAttribute('height',Math.max(0,yBot-yTop+22).toFixed(1));
      });
      model.timeline.forEach(function(p,i){
        var x=toScreen(atlas.positions[p.id]).x,l=gridEls.meridians[i];
        l.setAttribute('x1',x.toFixed(1));l.setAttribute('x2',x.toFixed(1));l.setAttribute('y1',yTop.toFixed(1));l.setAttribute('y2',yBot.toFixed(1));
      });
      // Book names never overprint each other: a crowded name takes the line above, and only when both
      // lines are taken does it wait for a closer zoom.
      var lineEnd=[-Infinity,-Infinity];
      atlas.books.forEach(function(bk,i){
        var t=gridEls.heads[i],x=toScreen({x:bk.x0-half,y:top}).x+8,w=t.__w,line=x>=lineEnd[0]?0:x>=lineEnd[1]?1:-1,show=line>=0&&x<v.width;
        t.__x=x;t.__line=line;t.setAttribute('x',x.toFixed(1));t.setAttribute('y',(yTop-8-(line===1?12:0)).toFixed(1));
        t.style.display=show?'':'none';if(show)lineEnd[line]=x+w;
      });
      if(model.timeline.length){
        var l=toScreen(atlas.positions[model.timeline[0].id]),r=toScreen(atlas.positions[model.timeline[model.timeline.length-1].id]);
        gridEls.spine.setAttribute('d','M'+(l.x-60*S.cam.z).toFixed(1)+' '+l.y.toFixed(1)+'L'+(r.x+60*S.cam.z).toFixed(1)+' '+r.y.toFixed(1));
      }
      var railIds=S.comp&&S.comp.rail||[];
      if(railIds.length>1&&S.mix>0.01){var r0=screen[railIds[0]],r1=screen[railIds[railIds.length-1]];
        gridEls.rail.setAttribute('d','M'+(r0.x-18).toFixed(1)+' '+r0.y.toFixed(1)+'L'+(r1.x+18).toFixed(1)+' '+r1.y.toFixed(1));
        gridEls.rail.style.opacity=(S.mix*0.5).toFixed(2);}
      else gridEls.rail.setAttribute('d','M0 0');
      var radii={};function rad(id){return radii[id]||(radii[id]=glyphRadius(id));}
      model.relations.forEach(function(r){
        if(S.travelling&&S.back[r.id])return;
        var path=edgeEls[r.id],g=edgeGeom(r,screen[r.from],screen[r.to],S.mix,rad(r.from),rad(r.to));
        var grow=S.edgeGrow[r.id],reverse=false;
        if(S.hood){var lf=S.hood.levels[r.from],lt=S.hood.levels[r.to];reverse=lf!==undefined&&lt!==undefined&&lt<lf;}
        var d=grow<=0.001?'M0 0':cubicPath(g,grow,reverse);if(path.__d!==d){path.__d=d;path.setAttribute('d',d);}
        var verb=verbEls[r.id];
        if(verb){var p=pointAt(g,S.verbAt[r.id]||0.5),vx=p.x.toFixed(1),vy=p.y.toFixed(1);
          if(verb.__x!==vx){verb.__x=vx;verb.setAttribute('x',vx);}if(verb.__y!==vy){verb.__y=vy;verb.setAttribute('y',vy);}}
      });
      Object.keys(tetherEls).forEach(function(id){
        var t=tetherEls[id],h=toScreen(atlas.positions[id]),p=screen[id];
        var d=Math.sqrt(Math.pow(h.x-p.x,2)+Math.pow(h.y-p.y,2));
        t.line.setAttribute('x1',h.x);t.line.setAttribute('y1',h.y);t.line.setAttribute('x2',p.x);t.line.setAttribute('y2',p.y);
        t.dot.setAttribute('cx',h.x);t.dot.setAttribute('cy',h.y);
        t.g.style.opacity=d<6?'0':'';
      });
      if(S.focus){var f=screen[S.focus],lt='translate('+f.x.toFixed(0)+'px,'+f.y.toFixed(0)+'px)';if(lensGlow.__tf!==lt){lensGlow.__tf=lt;lensGlow.style.transform=lt;}}
    }

    /* ---------- Motion engine ---------- */
    function animate(spec){
      if(spec.camera||spec.targets)latchPointer();
      var now=performance.now(),tw=S.tw||{nodes:{},cam:null,edges:{},mix:null};
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
      if(spec.mix){
        if(!spec.mix.dur||Math.abs(spec.mix.to-S.mix)<0.001){S.mix=spec.mix.to;tw.mix=null;}
        else tw.mix={from:S.mix,to:spec.mix.to,t0:now,dur:spec.mix.dur};
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
      // Only a change of composition rests the background threads; a plain zoom or pan keeps them drawn.
      if(spec.travel&&(tw.cam||tw.mix||Object.keys(tw.nodes).length)&&!S.travelling){S.travelling=true;root.classList.add('atl-travelling');}
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
      if(tw.mix){var mx=tw.mix,km=(now-mx.t0)/mx.dur;
        if(km>=1){S.mix=mx.to;tw.mix=null;}else{S.mix=mx.from+(mx.to-mx.from)*EASE_MOVE(Math.max(0,km));active=true;}}
      Object.keys(tw.edges).forEach(function(id){
        var t=tw.edges[id],k=(now-t.t0)/t.dur;
        if(k<=0){active=true;return;}
        if(k>=1){S.edgeGrow[id]=t.to;delete tw.edges[id];return;}
        S.edgeGrow[id]=t.from+(t.to-t.from)*EASE_GROW(k);active=true;
      });
      S.frames.push(now);paint();
      if(active)S.raf=global.requestAnimationFrame(tick);else settle();
    }
    function flushInstant(){
      // Reduced motion and instant restores: apply every pending end state in one frame.
      if(S.raf){global.cancelAnimationFrame(S.raf);S.raf=null;}
      var tw=S.tw;if(tw){Object.keys(tw.nodes).forEach(function(id){S.pos[id]=tw.nodes[id].to;});
        if(tw.cam)S.cam=tw.cam.to;if(tw.mix)S.mix=tw.mix.to;Object.keys(tw.edges).forEach(function(id){S.edgeGrow[id]=tw.edges[id].to;});}
      S.tw={nodes:{},cam:null,edges:{},mix:null};S.frames=[];paint();settle();
    }

    /* ---------- States ---------- */
    function starState(id){
      if(!S.hood)return 'rest';
      var lv=S.hood.levels[id];return lv===0?'focus':lv===1?'near':lv===2?'far':'dim';
    }
    function activeTreatment(){return S.mode==='constellation'?'B':S.research?'C':'A';}
    function applyStates(delays){
      root.classList.toggle('atl-focused',!!S.focus);
      root.classList.toggle('atl-examining',S.mode==='constellation');
      root.classList.toggle('atl-deep',!!S.focus&&S.depth===2);
      S.model.concepts.forEach(function(cn){
        var b=starEls[cn.id],st=starState(cn.id);
        b.style.setProperty('--d',(delays&&delays[cn.id]!==undefined?delays[cn.id]:0)+'ms');
        ['rest','focus','near','far','dim'].forEach(function(name){b.classList.toggle('is-'+name,st===name);});
        if(st==='focus')b.setAttribute('aria-current','true');else b.removeAttribute('aria-current');
        b.classList.toggle('is-moved',!!(S.comp&&S.comp.moved.indexOf(cn.id)>=0&&st!=='focus'));
        b.classList.toggle('was-focus',!S.focus&&cn.id===S.lastFocus);
      });
      var edgeLevel={};if(S.hood)S.hood.edges.forEach(function(e){edgeLevel[e.relation.id]=e.level;});
      S.model.relations.forEach(function(r){
        var p=edgeEls[r.id],lv=edgeLevel[r.id],back=lv===undefined,home=back?gBack:gEdges;
        if(p.parentNode!==home)home.append(p);
        if(S.back[r.id]&&!back)p.__d=null;S.back[r.id]=back;
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
      gVerbs.replaceChildren();verbEls={};S.verbAt={};S.verbFor={};
      if(!S.hood)return;
      var onPills=S.mode==='constellation'&&narrow();
      S.hood.edges.filter(function(e){return e.level===1;}).forEach(function(e){
        var r=e.relation,focusIsTarget=S.hood.levels[r.to]===0,other=focusIsTarget?r.from:r.to;
        var verb=focusIsTarget?(r.reverseVerb||('related through “'+r.verb+'”')):r.verb;
        if(S.hood.levels[other]===1)S.verbFor[other]=S.verbFor[other]?S.verbFor[other]+' · '+verb:verb;
        if(onPills)return;
        var t=sv('text',{'class':'atl-verb is-pending','text-anchor':'middle','dominant-baseline':'central'});
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

    /* ---------- Labels: measured, prioritised, placed around fixed glyphs ---------- */
    function spec(style,text,maxW,lines){var st=STYLE[style],w=wrapText(text,st,maxW,lines);return {style:style,lines:w.lines,w:w.w,h:w.h};}
    function kindLine(cn){var kind=M.FACET_SINGULAR[cn.facet],role=cn.role?M.human(cn.role):'';
      return (kind+(role&&role.toLowerCase()!==kind.toLowerCase()&&role!==cn.name?' · '+role:'')).toUpperCase();}
    // Kicker and wrapped name together, for the title card and the call-out.
    function cardSpec(cn,style,maxW){
      var st=STYLE[style],t=wrapText(cn.name,st,maxW);
      var kick=fitLine(kindLine(cn),st.kicker,maxW),kw=textWidth(kick,st.kicker)+kick.length*9.5*0.13;
      return {style:style,lines:t.lines,kicker:kick,w:Math.ceil(Math.max(t.w-2*st.px,kw))+2*st.px+1,h:t.h+st.klh};
    }
    // The focus wears its whole name; a long one is set smaller rather than cut.
    function focusSpec(cn){
      var long=cn.name.length>90,style=long?'focusLong':'focus';
      return cardSpec(cn,style,narrow()?Math.min(STYLE[style].maxW,view().width-64):STYLE[style].maxW);
    }
    function verbSpec(cn){
      var st=STYLE.nearVerb,maxW=Math.min(st.maxW,view().width-90),t=wrapText(cn.name,st,maxW),verb=fitLine(S.verbFor[cn.id]||'',st.kicker,maxW);
      return {style:'nearVerb',lines:t.lines,kicker:verb,w:Math.ceil(Math.max(t.w-2*st.px,textWidth(verb,st.kicker)))+2*st.px+1,h:t.h+st.klh};
    }
    function specsFor(cn,st,z){
      // The title card has a narrower, taller form for crowded places, so it can avoid covering a neighbour.
      if(st==='focus'){var wide=focusSpec(cn),slim=cardSpec(cn,wide.style,170);return slim.w<wide.w-20?[wide,slim]:[wide];}
      if(st==='near'&&S.mode==='constellation'&&narrow())return [verbSpec(cn)];
      // Relationship pills: the whole name when there is room, then two lines, then a phrase cut at a word.
      if(st==='near')return [spec('near',cn.name,220,3),spec('near',cn.name,196,2),spec('near',M.shorten(cn.name,30),196,1)];
      if(st==='far')return [spec('far',cn.name),spec('far',M.shorten(cn.name,28),180,1)];
      if(cn.tier===2)return [spec('mote',M.shorten(cn.name,34))];
      if(cn.facet==='genres')return [spec('genre',cn.name),spec('genre',cn.name,112,3)];
      if(cn.facet==='timeline'){
        // Phase names are landmarks: the complete name is preferred, a little wider than its column if the
        // neighbours leave room, before a shortened one.
        var room=clamp(S.atlas.phaseGap*z+4,62,STYLE.phase.maxW),wide=Math.min(STYLE.phase.maxW,room*1.3);
        var whole=function(s){return s.lines.join(' ')===cn.name;};
        var options=[spec('phase',cn.name,room),spec('phase',cn.name,wide),spec('phase',cn.name,room,4)];
        // Never a bare numeral: a shortened name still says which phase it is.
        return options.filter(whole).concat(options.filter(function(s){return !whole(s);}).slice(0,1));
      }
      return [spec('rest',cn.name)];
    }
    function furniture(cam){
      var out=[],sr=stage.getBoundingClientRect(),v=view();
      function add(elm,soft){if(!elm||elm.hidden)return;var r=elm.getBoundingClientRect();if(!r.width||!r.height)return;
        out.push({rect:{x0:r.left-sr.left-4,y0:r.top-sr.top-4,x1:r.right-sr.left+4,y1:r.bottom-sr.top+4},owner:'ui',soft:!!soft});}
      add(trail);add(zoom);add(hint);add(lensbar);
      // In a constellation the atlas furniture has withdrawn behind the lens and is not in the way.
      if(S.mode==='constellation')return out;
      bandLabelEls.forEach(function(x){
        if(!x.w)x.w=x.label.offsetWidth||130;
        var y=(((x.band.y0+x.band.y1)/2)-cam.cy)*cam.z+v.height/2;
        out.push({rect:{x0:0,y0:y-11,x1:x.w,y1:y+11},owner:'ui',soft:S.focus?'hood':false});
      });
      // Book running heads sit above the score; labels leave them readable.
      var top=S.atlas.bands.length?S.atlas.bands[0].y0:0,half=S.atlas.phaseGap/2,yTop=(top-8-cam.cy)*cam.z+v.height/2;
      S.atlas.books.forEach(function(bk,i){
        var t=gridEls.heads[i];if(!t||t.style.display==='none')return;
        var x=(bk.x0-half-cam.cx)*cam.z+v.width/2+8,up=t.__line===1?12:0;
        out.push({rect:{x0:x-2,y0:yTop-16-up,x1:x+t.__w,y1:yTop+4-up},owner:'ui'});
      });
      return out;
    }
    function labelPass(final){
      if(!S.model)return;
      final=final||{};
      var v=view(),cam=final.cam||S.cam,pos=final.pos||S.pos,mix=final.mix!==undefined?final.mix:S.mix,model=S.model;
      var examining=S.mode==='constellation',maxDeg=model.maxDegree||1;
      var obstacles=furniture(cam),items=[],anchors={},specs={},onStage={},radii={},isItem={},focusItem=null;
      var inset=narrow()?10:4,bounds={x0:inset,y0:inset,x1:v.width-inset,y1:v.height-inset};
      model.concepts.forEach(function(cn){
        var p=pos[cn.id],a={x:(p.x-cam.cx)*cam.z+v.width/2,y:(p.y-cam.cy)*cam.z+v.height/2},st=starState(cn.id);
        anchors[cn.id]=a;var sp=specsFor(cn,st,cam.z);specs[cn.id]=sp;
        var inHood=st==='focus'||st==='near'||st==='far',r=glyphRadius(cn.id,st);radii[cn.id]=r;
        onStage[cn.id]=a.x>-20&&a.x<v.width+20&&a.y>-20&&a.y<v.height+20;
        if(!onStage[cn.id]||(examining&&!inHood))return;
        obstacles.push({rect:{x0:a.x-r,y0:a.y-r,x1:a.x+r,y1:a.y+r},owner:cn.id,soft:!inHood&&(st==='dim'||cn.tier===2)});
        // Far away, local phrases stay points: named on hover, focus or when the author comes closer.
        if(!sp.length||(!inHood&&cn.tier===2&&cam.z<0.9))return;
        var item={id:cn.id,x:a.x,y:a.y,gap:r+3,variants:sp.map(function(s,i){return {key:i,w:s.w,h:s.h};})};
        // A rail name sits directly above or below its own phase, never diagonally, so order stays unambiguous.
        var sd=S.sides[cn.id],side=sd==='left'?['w','nw','sw']:sd==='rail-s'?['s','n']:sd==='rail-n'?['n','s']:
          examining&&narrow()?['e']:['e','ne','se'];
        var weight=Math.sqrt((cn.degree||0)/maxDeg);
        if(st==='focus'){item.priority=1000;item.required=true;item.overSoft=true;item.gap=r+5;
          item.places=examining&&narrow()?['e','n','s']:examining||narrow()?['s','n']:['s','n','e','w','se','sw','ne','nw'];
          if(!examining)focusItem=item;}
        else if(st==='near'){item.priority=800-facetOrder[cn.facet]*3+10*weight;item.overSoft=true;item.places=examining?side:AROUND;
          if(sd==='rail-s'||sd==='rail-n')item.gap=r+9;}
        else if(st==='far'){item.priority=600+5*weight;item.overSoft=true;item.places=examining?side:AROUND;}
        else{
          item.priority=(S.focus?-200:0)+(FACET_BASE[cn.facet]||420)-(cn.tier===2?300:0)+60*weight+(/^(governing|primary)/.test(cn.role||'')?20:0);
          item.overSoft=cn.facet==='genres'||cn.facet==='timeline'?true:'fallback';
          item.places=cn.facet==='timeline'?['s','n']:cn.facet==='genres'?['n','e','w','ne','nw','s','se','sw']:AROUND;
        }
        items.push(item);isItem[cn.id]=true;
      });
      if(focusItem)chooseCardPlace(focusItem,obstacles,anchors,radii,bounds,v);
      // Relationship verbs come after the neighbours they explain, set along their own path.
      var T=[0.5,0.4,0.6,0.32,0.68];
      Object.keys(verbEls).forEach(function(rid){
        var r=model.relById[rid],g=edgeGeom(r,anchors[r.from],anchors[r.to],mix,radii[r.from],radii[r.to]);
        var s=wrapText(verbEls[rid].textContent,STYLE.verb);
        items.push({id:'verb:'+rid,priority:700,overSoft:true,places:['c'],gap:0,
          anchors:T.map(function(t){return pointAt(g,t);}),variants:[{key:0,w:s.w,h:s.h}]});
      });
      var placed=M.placeLabels(items,obstacles,bounds);
      var stats={placed:0,quiet:0,forced:0,restLandmarks:0,restNamed:0,neighbours:0,neighboursNamed:0,verbsPlaced:0,verbs:Object.keys(verbEls).length};
      model.concepts.forEach(function(cn){
        var star=starEls[cn.id],res=placed[cn.id],sp=specs[cn.id],a=anchors[cn.id],st=starState(cn.id);
        if(res){applyLabel(star,sp[res.variant],res.rect,a,res.place);star.classList.remove('is-quiet');stats.placed++;if(res.forced)stats.forced++;}
        else if(sp.length){
          var place=st==='focus'?'s':S.sides[cn.id]==='left'?'w':'e';
          applyLabel(star,sp[0],M.placeRect(place,a.x,a.y,radii[cn.id]+3,sp[0].w,sp[0].h),a,place);
          star.classList.add('is-quiet');if(isItem[cn.id])stats.quiet++;
        }else{clearLabel(star);star.classList.remove('is-quiet');}
        if(st==='rest'&&cn.tier===1&&onStage[cn.id]){stats.restLandmarks++;if(res)stats.restNamed++;}
        if((st==='near'||st==='far')&&onStage[cn.id]){stats.neighbours++;if(res)stats.neighboursNamed++;}
        star.classList.toggle('is-ambient',!!S.focus&&st==='dim'&&!!res);
      });
      Object.keys(verbEls).forEach(function(rid){
        var res=placed['verb:'+rid];S.verbAt[rid]=res?T[res.anchor]:0.5;
        verbEls[rid].classList.toggle('is-culled',!res);if(res)stats.verbsPlaced++;
      });
      S.labelStats=stats;
    }
    /* The focus title card in the atlas: of the places around its mark (some standing a little off it),
       the one that covers nothing, keeps clear of its own mark and leaves the most room for the
       neighbours' names nearby. A neighbour's name matters more than the card's exact position. */
    function chooseCardPlace(item,obstacles,anchors,radii,bounds,v){
      var a={x:item.x,y:item.y},own={x0:a.x-radii[item.id],y0:a.y-radii[item.id],x1:a.x+radii[item.id],y1:a.y+radii[item.id]};
      var hood=Object.keys(anchors).filter(function(id){var st=starState(id);return st==='near'||st==='far';}).map(function(id){return anchors[id];});
      var hard=obstacles.filter(function(o){return o.owner!==item.id&&o.soft!==true;});
      var OPT=[['s',0,0],['n',0,0],['e',0,0],['w',0,0],['s',0,22],['n',0,-22],['e',26,0],['w',-26,0],['se',0,0],['sw',0,0],['ne',0,0],['nw',0,0],
        ['s',0,46],['n',0,-46],['e',56,0],['w',-56,0],['se',24,24],['sw',-24,24],['ne',24,-24],['nw',-24,-24],
        ['n',28,0],['n',-28,0],['s',28,0],['s',-28,0],['n',56,0],['n',-56,0],['s',56,0],['s',-56,0]];
      function hit(r,b){return r.x0<b.x1&&b.x0<r.x1&&r.y0<b.y1&&b.y0<r.y1;}
      // Covering a control (trail, zoom, way back) is worst, then a direct relative's mark; a faint second-order mark less so.
      function cost(b){if(b.soft==='hood')return 2;if(b.owner==='ui')return 600;var st=starState(b.owner);return st==='far'?40:300;}
      function score(o,i,vr){
        var r=M.placeRect(o[0],a.x+o[1],a.y+o[2],item.gap,vr.w,vr.h);
        var sc=i*0.01+(r.x0<bounds.x0||r.y0<bounds.y0||r.x1>bounds.x1||r.y1>bounds.y1?500:0)+(hit(r,own)?1000:0);
        hard.forEach(function(b){if(hit(r,b.rect))sc+=cost(b);});
        var room={x0:r.x0-70,y0:r.y0-16,x1:r.x1+70,y1:r.y1+16};
        hood.forEach(function(p){if(p.x>room.x0&&p.x<room.x1&&p.y>room.y0&&p.y<room.y1)sc+=6;});
        return sc;
      }
      var best=null;
      item.variants.forEach(function(vr,vi){OPT.forEach(function(o,i){
        var sc=score(o,i,vr);if(!best||sc<best.score)best={score:sc,opt:i,vi:vi,place:o[0],anchor:{x:a.x+o[1],y:a.y+o[2]},variant:vr};
      });});
      // The card keeps its place while the same concept stays in focus (deepening, following back), as long
      // as that place still covers no direct relative: names should not jump about.
      var prev=S.card&&S.card.id===item.id&&item.variants[S.card.vi]?S.card:null;
      if(prev){var keep=score(OPT[prev.opt],prev.opt,item.variants[prev.vi]);
        if(keep<40)best={score:keep,opt:prev.opt,vi:prev.vi,place:OPT[prev.opt][0],anchor:{x:a.x+OPT[prev.opt][1],y:a.y+OPT[prev.opt][2]},variant:item.variants[prev.vi]};}
      if(best){S.card={id:item.id,opt:best.opt,vi:best.vi};item.places=[best.place];item.anchors=[best.anchor];item.variants=[best.variant];}
    }
    function applyLabel(star,s,rect,anchor,place,transient){
      if(!transient)star.__placed={s:s,rect:rect,anchor:anchor,place:place};
      if(!transient&&star.classList.contains('is-callout'))return;
      var key=s.style+'|'+s.lines.join('\n')+'|'+(s.kicker||'');
      if(star.__key!==key){star.__key=key;star.__label.textContent=s.lines.join('\n');star.__kicker.textContent=s.kicker||'';
        star.__text.dataset.style=s.style;}
      var t=star.__text;t.style.width=s.w+'px';t.style.height=s.h+'px';
      t.style.transform='translate('+(rect.x0-anchor.x).toFixed(1)+'px,'+(rect.y0-anchor.y).toFixed(1)+'px)';
      if(t.dataset.place!==place)t.dataset.place=place;
    }
    function clearLabel(star){
      star.__placed=null;
      if(star.__key==='')return;star.__key='';star.__label.textContent='';star.__kicker.textContent='';
      star.__text.dataset.style='none';star.__text.style.width='0px';star.__text.style.height='0px';
    }

    /* ---------- Unfolding choreography ---------- */
    function select(id,opts){
      opts=opts||{};
      if(!S.model||!S.model.byId[id])return;
      var fromAtlas=!S.focus;
      if(fromAtlas){S.restCam={cx:S.cam.cx,cy:S.cam.cy,z:S.cam.z};S.userCam=false;}
      if(opts.trailIndex!==undefined)S.trail=S.trail.slice(0,opts.trailIndex+1);
      else if(fromAtlas)S.trail=[id];
      else if(S.focus!==id)S.trail.push(id);
      if(S.trail.length>12)S.trail=S.trail.slice(-12);
      S.focus=id;S.lastFocus=id;S.depth=opts.depth||(fromAtlas||opts.via==='atlas'?1:S.depth===2?2:1);
      if(S.mode==='constellation')fitPhoneStage(true);
      S.lastAction={kind:'select',id:id,at:performance.now()};
      renderTrail();syncChrome();
      unfold({fresh:true});
      setRoving(id);
      renderFolio();
      var cn=S.model.byId[id],n=S.hood.first.length;
      announce(M.FACET_SINGULAR[cn.facet]+' “'+cn.title+'”: '+n+' documented relationship'+(n===1?'':'s')+
        (S.mode==='constellation'?', recomposed as a focused constellation.':', revealed in place.')+
        (S.comp.moved.length?' '+S.comp.moved.length+' concepts moved closer for reading; their atlas places stay marked.':''));
      if(opts.focusStar!==false&&starEls[id]&&document.activeElement&&root.contains(document.activeElement)&&
         document.activeElement.classList.contains('atl-star'))starEls[id].focus({preventScroll:true});
    }
    function unfold(mode){
      latchPointer();
      var tr=activeTreatment(),T=TIMING[tr],reduced=S.reduced,previous=S.hood,v=view();
      S.hood=M.neighbourhood(S.model,S.focus,S.depth);
      S.comp=M.compose(S.model,S.atlas,S.hood,tr,{width:v.width,height:v.height,z:tr==='A'?S.cam.z:1});
      S.sides=Object.assign({},S.comp.sides);
      Object.keys(S.sides).forEach(function(id){if(S.hood.levels[id]===undefined)delete S.sides[id];});
      if(tr==='A')S.sides={};
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
      var cam=mode.camera!==undefined?mode.camera:tr==='A'?atlasFocusCamera(S.focus):tr==='B'?constellationCamera(S.hood.order):researchCamera(S.hood.order);
      var mixTo=tr==='A'?0:1,camDur=reduced||!cam?0:(mode.cameraDuration||T.camera);
      S.lastAction.cameraMoved=!!cam&&(Math.abs(cam.cx-S.cam.cx)>0.5||Math.abs(cam.cy-S.cam.cy)>0.5||Math.abs(cam.z-S.cam.z)>0.001);
      S.lastAction.zoomBefore=S.cam.z;
      lensbar.hidden=S.mode!=='constellation';fitHood.hidden=S.mode!=='atlas';
      labelPass({pos:S.comp.targets,cam:cam||S.cam,mix:mixTo});
      var moveDur=mode.moveDuration||T.move||TIMING.back.move,moveDelay=fresh?T.moveDelay:0,ids=S.hood.order;
      animate({travel:true,targets:S.comp.targets,duration:reduced?0:moveDur,
        delay:function(id){var k=ids.indexOf(id);return moveDelay+(k<0?0:Math.min(k*T.moveStagger,260));},
        camera:cam,cameraDuration:camDur,cameraDelay:tr==='C'&&fresh?Math.max(0,T.moveDelay-80):0,
        mix:{to:mixTo,dur:reduced?0:T.camera},edges:edges});
      if(reduced)flushInstant();
    }
    // Research comparison C: the previous study's camera for contextual unfolding.
    function researchCamera(ids){
      var v=view(),pad=40,t=S.comp.targets,f=t[S.focus];
      var rect=rectOf(ids,t,S.comp.sides,1),w=rect.x1-rect.x0,h=rect.y1-rect.y0;
      return {z:1,cx:w<=v.width-2*pad?(rect.x0+rect.x1)/2:clamp((rect.x0+rect.x1)/2,f.x-v.width/2+170,f.x+v.width/2-170),
        cy:h<=v.height-2*pad?(rect.y0+rect.y1)/2:f.y+v.height/2-110};
    }
    function deeper(on){
      if(!S.focus)return;
      S.depth=on?2:1;S.lastAction={kind:on?'deeper':'shallower',id:S.focus,at:performance.now()};
      if(S.mode==='constellation')fitPhoneStage(true);
      unfold({fresh:false,camera:S.mode==='constellation'?undefined:null});renderFolio();
      announce(on?'Second-order connections revealed: '+S.hood.second.length+' concepts.'+
        (S.hood.hiddenSecond?' '+S.hood.hiddenSecond+' more are listed in the index, not drawn.':''):'Showing first-order relationships only.');
    }
    function examine(){
      if(!S.focus||S.mode==='constellation')return;
      S.atlasCam={cx:S.cam.cx,cy:S.cam.cy,z:S.cam.z};S.mode='constellation';
      S.lastAction={kind:'examine',id:S.focus,at:performance.now()};
      fitPhoneStage(true);
      var inStage=stage.contains(document.activeElement);
      syncChrome();renderTrail();unfold({fresh:false,regrow:false});renderFolio();
      if(inStage&&starEls[S.focus])starEls[S.focus].focus({preventScroll:true});
      bringStageIntoView();
      var cn=S.model.byId[S.focus];
      announce('Focused constellation of “'+cn.title+'”: '+S.hood.first.length+' documented relationships recomposed for close reading. '+
        'Dotted tethers mark each concept’s place in the atlas. Escape returns to the atlas.');
    }
    function leaveConstellation(){
      if(S.mode!=='constellation')return;
      S.mode='atlas';S.lastAction={kind:'leave-constellation',id:S.focus,at:performance.now()};
      fitPhoneStage(false);
      // The atlas view the author left is restored; if the focus changed meanwhile, it is kept in view.
      var base=S.atlasCam||S.cam,cam=atlasFocusCamera(S.focus,base)||base,inStage=stage.contains(document.activeElement);
      syncChrome();renderTrail();unfold({fresh:false,regrow:false,camera:cam,cameraDuration:TIMING.back.camera,moveDuration:TIMING.back.move});
      renderFolio();
      if(inStage&&starEls[S.focus])starEls[S.focus].focus({preventScroll:true});
      bringStageIntoView();
      announce('Back in the living atlas. “'+S.model.byId[S.focus].title+'” and its relationships are shown in place.');
    }
    function setResearch(on){
      if(!S.researchAvailable||S.research===!!on)return;
      S.research=!!on;if(S.mode==='constellation')S.mode='atlas';syncChrome();
      if(S.focus){S.lastAction={kind:'treatment',id:S.focus,at:performance.now()};unfold({fresh:false});renderFolio();}
      announce(S.research?'Research comparison C: contextual unfolding.':'Living atlas: progressive revelation.');
    }
    function setTreatment(t){
      t=String(t||'').toUpperCase();
      if(t==='B'){if(S.research)setResearch(false);examine();}
      else if(t==='C'){if(S.mode==='constellation')leaveConstellation();setResearch(true);}
      else if(t==='A'){if(S.mode==='constellation')leaveConstellation();if(S.research)setResearch(false);}
      syncChrome();
    }
    function returnToAtlas(){
      if(!S.focus)return;
      latchPointer();
      var last=S.focus,reduced=S.reduced,delays={},wasExamining=S.mode==='constellation',hadFocus=root.contains(document.activeElement);
      if(S.hood)S.hood.order.slice().reverse().forEach(function(id,i){delays[id]=reduced?0:Math.min(i*10,180);});
      // Automatic pans are undone; a view the author chose themselves is kept.
      var cam=S.userCam?(wasExamining?S.atlasCam:null):S.restCam;
      S.focus=null;S.hood=null;S.comp=null;S.trail=[];S.sides={};S.depth=1;S.mode='atlas';
      fitPhoneStage(false);
      S.lastAction={kind:'return',id:last,at:performance.now()};
      applyStates(delays);syncVerbs();syncTethers();syncChrome();renderTrail();lensbar.hidden=true;fitHood.hidden=true;compass.replaceChildren();
      var targets={};S.model.concepts.forEach(function(cn){targets[cn.id]=S.atlas.positions[cn.id];});
      var edges={};S.model.relations.forEach(function(r){edges[r.id]={to:1};});
      labelPass({pos:targets,cam:cam||S.cam,mix:0});
      animate({travel:true,targets:targets,duration:reduced?0:TIMING.back.move,camera:cam,
        cameraDuration:reduced||!cam?0:TIMING.back.camera,edges:edges,mix:{to:0,dur:reduced?0:TIMING.back.move}});
      if(reduced)flushInstant();
      renderFolio();setRoving(last);
      if(hadFocus)starEls[last].focus({preventScroll:true});
      if(wasExamining)bringStageIntoView();
      announce('Returned to the atlas. “'+S.model.byId[last].title+'” is still in its place.');
    }
    function back(){
      if(S.trail.length>1)select(S.trail[S.trail.length-2],{trailIndex:S.trail.length-2});
      else if(S.mode==='constellation')leaveConstellation();
      else returnToAtlas();
    }

    /* ---------- Emphasis: pointer, folio and keyboard ----------
       One precedence for every transient emphasis: the concept under a pointer that has really moved,
       else a relationship or landmark the pointer rests on in the folio, else what holds visible
       keyboard focus. Emphasis never re-places labels: it rings the related glyphs, lifts their threads
       and raises one call-out with the complete name above the composition. Every change of composition
       or camera suspends pointer emphasis until the pointer actually moves, so a pointer left where it
       clicked never leaves a stale preview behind. */
    // Keyboard emphasis follows keyboard navigation (Tab or arrows), not any key pressed while focus rests.
    function keyboardTarget(){
      var a=document.activeElement;if(!S.keyNav||!a||!root.contains(a)||!a.matches||!a.matches(':focus-visible'))return null;
      if(a.classList.contains('atl-star'))return {id:a.dataset.id};
      if(a.classList.contains('atl-rel'))return {rel:a.dataset.rel,id:a.dataset.other};
      if(a.classList.contains('atl-landmark'))return {id:a.dataset.id};
      return null;
    }
    function refreshEmphasis(){
      if(!S.model)return;
      var hint=S.hover?{id:S.hover}:(S.folioHint||keyboardTarget());
      // The focus is already revealed; emphasising it again would only ring what is shown.
      if(hint&&!hint.rel&&hint.id===S.focus)hint=null;
      if(hint&&hint.rel)previewRelation(hint.rel,hint.id);else preview(hint?hint.id:null);
      setCallout(hint&&hint.id&&hint.id!==S.focus&&starEls[hint.id]?hint.id:null);
    }
    function pointerTarget(t){
      var star=t&&t.closest?t.closest('.atl-star'):null,rel=t&&t.closest?t.closest('.atl-rel'):null,mark=t&&t.closest?t.closest('.atl-landmark'):null;
      S.hover=star&&root.contains(star)?star.dataset.id:null;
      S.folioHint=rel?{rel:rel.dataset.rel,id:rel.dataset.other}:mark?{id:mark.dataset.id}:null;
      refreshEmphasis();
    }
    function latchPointer(){S.latched=true;S.keyNav=false;S.hover=null;S.folioHint=null;refreshEmphasis();}
    root.addEventListener('keydown',function(e){if(e.key==='Tab')S.keyNav=true;},true);
    root.addEventListener('pointerover',function(e){if(e.pointerType==='touch'||S.latched||S.dragging)return;pointerTarget(e.target);});
    // A press also tells where the pointer is, so a click that follows no movement is still a known position.
    root.addEventListener('pointerdown',function(e){if(e.pointerType!=='touch')S.ptr={x:e.clientX,y:e.clientY};},true);
    root.addEventListener('pointerleave',function(){S.ptr=null;if(S.hover||S.folioHint){S.hover=null;S.folioHint=null;refreshEmphasis();}});
    root.addEventListener('pointermove',function(e){
      if(e.pointerType==='touch')return;
      var p=S.ptr;S.ptr={x:e.clientX,y:e.clientY};
      // Layout changes under a still pointer produce synthetic moves at the same place with no movement;
      // only real travel counts.
      var travelled=!p||!!(e.movementX||e.movementY)||Math.abs(p.x-e.clientX)>=1||Math.abs(p.y-e.clientY)>=1;
      if(!S.latched||S.dragging||!travelled)return;
      S.latched=false;pointerTarget(document.elementFromPoint(e.clientX,e.clientY));
    });
    /* The call-out: one concept at a time shows its complete recorded name, wrapped, above everything. */
    function setCallout(id){
      if(S.callout===id)return;
      var prev=S.callout&&starEls[S.callout];
      if(prev){prev.classList.remove('is-callout');if(prev.__placed)applyLabel(prev,prev.__placed.s,prev.__placed.rect,prev.__placed.anchor,prev.__placed.place,true);}
      S.callout=id;var b=id&&starEls[id];if(!b)return;
      b.classList.add('is-callout');
      var cn=S.model.byId[id],shown=b.__placed&&!b.classList.contains('is-quiet')?b.__placed.s.lines.join(' '):'';
      if(shown===cn.name)return;
      var c=cardSpec(cn,'callout',STYLE.callout.maxW),v=view(),a=toScreen(S.pos[id]),g=glyphRadius(id)+4,place=null,rect=null;
      ['e','w','s','n','se','ne','sw','nw'].some(function(pl){var r=M.placeRect(pl,a.x,a.y,g,c.w,c.h);
        if(r.x0>=4&&r.y0>=4&&r.x1<=v.width-4&&r.y1<=v.height-4){place=pl;rect=r;return true;}return false;});
      if(!rect){place='e';rect=M.placeRect('e',a.x,a.y,g,c.w,c.h);}
      applyLabel(b,c,rect,a,place,true);
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
    function settle(){
      if(!S.model){return;}
      // The resting threads are redrawn once for the view that has settled, then fade back in.
      if(S.travelling){S.travelling=false;root.classList.remove('atl-travelling');paint();}
      labelPass();
      Array.prototype.forEach.call(gVerbs.children,function(t){t.classList.remove('is-pending');});
      syncCompass();
      if(S.mode==='atlas'&&S.focus)S.aCam={cx:S.cam.cx,cy:S.cam.cy,z:S.cam.z};
      var frames=S.frames,intervals=[];
      for(var i=1;i<frames.length;i++)intervals.push(frames[i]-frames[i-1]);
      var tr=activeTreatment();
      var base=S.focus?M.measure(S.model,S.atlas,S.hood,S.comp,tr==='A'?S.cam.z:1):null;
      var st=S.labelStats||{};
      S.metrics={mode:S.focus?S.mode:'rest',treatment:tr,focus:S.focus,depth:S.depth,action:S.lastAction&&S.lastAction.kind,
        settleMs:S.lastAction?Math.round(performance.now()-S.lastAction.at):0,
        frames:frames.length,meanFrameMs:intervals.length?+(intervals.reduce(function(s,v){return s+v;},0)/intervals.length).toFixed(1):0,
        maxFrameMs:intervals.length?+Math.max.apply(null,intervals).toFixed(1):0,
        zoom:+S.cam.z.toFixed(3),cameraMoved:!!(S.lastAction&&S.lastAction.cameraMoved),
        renderedLabelOverlaps:renderedOverlaps(),quietLabels:st.quiet||0,
        labels:{placed:st.placed||0,quiet:st.quiet||0,forced:st.forced||0,restLandmarks:st.restLandmarks||0,restNamed:st.restNamed||0,
          neighbours:st.neighbours||0,neighboursNamed:st.neighboursNamed||0},
        verbLabels:{shown:st.verbsPlaced||0,total:st.verbs||0},offStageNeighbours:S.offStage||0,
        composition:base,reducedMotion:S.reduced,concepts:S.model.concepts.length,relations:S.model.relations.length};
      renderReadout();
      root.dispatchEvent(new CustomEvent('atelier:settled',{detail:S.metrics}));
    }
    function renderedOverlaps(){
      var boxes=[],stageRect=stage.getBoundingClientRect();
      S.model.concepts.forEach(function(cn){
        var b=starEls[cn.id];if(b.classList.contains('is-quiet')||!b.__key)return;
        if(S.mode==='constellation'&&starState(cn.id)==='dim')return;
        var r=b.__text.getBoundingClientRect();
        if(!r.width||r.right<stageRect.left||r.left>stageRect.right||r.bottom<stageRect.top||r.top>stageRect.bottom)return;
        boxes.push(r);
      });
      var count=0;
      for(var i=0;i<boxes.length;i++)for(var j=i+1;j<boxes.length;j++){
        var a=boxes[i],b=boxes[j];if(a.left<b.right-2&&b.left<a.right-2&&a.top<b.bottom-2&&b.top<a.bottom-2)count++;}
      return {count:count,labels:boxes.length};
    }
    function syncCompass(){
      compass.replaceChildren();S.offStage=0;
      fitHood.hidden=!(S.focus&&S.mode==='atlas');
      if(!S.focus||S.mode!=='atlas'||!S.hood)return;
      var v=view(),groups={};
      S.hood.first.forEach(function(id){
        var p=toScreen(S.pos[id]),side=p.x<-6?'left':p.x>v.width+6?'right':p.y<-6?'top':p.y>v.height+6?'bottom':null;
        if(!side)return;(groups[side]=groups[side]||[]).push(id);S.offStage++;
      });
      var arrows={left:'←',right:'→',top:'↑',bottom:'↓'};
      Object.keys(groups).forEach(function(side){
        var ids=groups[side],names=ids.map(function(id){return S.model.byId[id].title;});
        var b=el('button','atl-compass-pin atl-compass-'+side);b.type='button';
        b.append(el('span','atl-compass-arrow',arrows[side]),el('span','',ids.length+' related'));
        b.title=names.join('\n');b.setAttribute('aria-label',ids.length+' related concept'+(ids.length===1?'':'s')+' beyond the view: '+names.join(', ')+'. Bring into view.');
        var mean=ids.reduce(function(s,id){var p=toScreen(S.pos[id]);return s+(side==='left'||side==='right'?p.y:p.x);},0)/ids.length;
        if(side==='left'||side==='right')b.style.top=clamp(mean,70,v.height-60).toFixed(0)+'px';
        else b.style.left=clamp(mean,narrow()?110:170,v.width-130).toFixed(0)+'px';
        b.addEventListener('click',function(){panToward(ids);});
        compass.append(b);
      });
    }
    function renderReadout(){
      readoutBody.replaceChildren();var m=S.metrics;if(!m)return;
      function row(k,v){readoutBody.append(el('dt','',k),el('dd','',v));}
      row('Mode',m.mode==='rest'?'Living atlas · at rest':(m.mode==='constellation'?'Focused constellation (B)':m.treatment==='C'?'Research C · contextual unfolding':'Living atlas · progressive revelation (A)'));
      row('Atlas',m.concepts+' concepts · '+m.relations+' relationships');
      row('Named landmarks',m.labels.restNamed+' of '+m.labels.restLandmarks+' resting landmarks in view');
      if(m.composition){var c=m.composition;
        row('Neighbourhood',c.first+' first-order · '+c.second+' second-order');
        row('Moved',c.moved+' of '+(c.visible-1)+' · mean '+c.meanMove+'px');
        row('Neighbours named',m.labels.neighboursNamed+' of '+m.labels.neighbours+' in view');
        row('Camera on select',m.cameraMoved?'panned to keep the focus readable':'unchanged');
        if(m.offStageNeighbours)row('Beyond the view',m.offStageNeighbours+' related concepts (pins at the edge)');}
      row('Labels',m.labels.placed+' set · '+m.labels.quiet+' quiet (glyph kept; named on hover or focus)');
      row('Rendered label overlaps',m.renderedLabelOverlaps.count+' among '+m.renderedLabelOverlaps.labels+' labels');
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
      var active=document.activeElement,key=active&&folio.contains(active)&&active.dataset?active.dataset.key:null;
      renderFolioContent();
      if(S.folioFor!==S.focus){S.folioFor=S.focus;folio.scrollTop=0;}
      if(key){var again=folio.querySelector('[data-key="'+cssEscape(key)+'"]');if(again)again.focus({preventScroll:true});else focusFolio();}
    }
    function renderFolioContent(){
      folio.replaceChildren();
      var status=binding.getSourceStatus?binding.getSourceStatus():null;
      if(!S.model){
        folio.append(el('p','atl-kicker-line','The atlas'),el('h3','atl-folio-title','No working Architecture yet'),
          el('p','atl-folio-detail','Develop a working Architecture proposal in the Studio, then return to this study. The study only reads what the proposal records.'));
        return;
      }
      if(!S.focus)return renderAtlasFolio(status);
      var cn=S.model.byId[S.focus],model=S.model,examining=S.mode==='constellation';
      folio.setAttribute('aria-label','Reading of '+cn.title);
      if(examining)folio.append(el('p','atl-mode-chip','Focused constellation · close reading'));
      folio.append(el('p','atl-kicker-line atl-facet-'+cn.facet,M.FACET_SINGULAR[cn.facet]+(cn.role?' · '+M.human(cn.role):'')));
      folio.append(el('h3','atl-folio-title'+(cn.title.length>90?' is-long':''),cn.title));
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
        var scope=M.bookScope(rec.scope);fact(dl,'Scope',scope.text+(scope.durationUnknown?' · duration unknown':''));
        fact(dl,'Narrative function',rec.narrative_function);
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
      // Ways of looking come first: the magnifying glass and the next depth.
      var look=el('div','atl-look');
      if(examining){
        var leave=actionButton(look,'Back to the living atlas',leaveConstellation,'look');leave.classList.add('atl-action-primary');
        look.append(el('p','atl-note','The constellation rearranges only what the proposal already records, for reading. Dotted tethers mark each concept’s place in the atlas; leaving restores the atlas view you came from.'));
      }else{
        var ex=actionButton(look,'Examine as constellation',examine,'look');ex.classList.add('atl-action-primary');
        ex.setAttribute('aria-keyshortcuts','E');
      }
      var potential=M.neighbourhood(model,cn.id,2).second.length;
      var depthButton=actionButton(look,S.depth===2?'Show first-order only':'Reveal deeper connections · '+potential,function(){deeper(S.depth!==2);},'depth');
      depthButton.setAttribute('aria-pressed',String(S.depth===2));depthButton.disabled=S.depth!==2&&!potential;
      if(S.depth===2)look.append(el('p','atl-note',S.hood.second.length+' second-order concepts drawn faintly'+
        (S.hood.hiddenSecond?'; '+S.hood.hiddenSecond+' more are not drawn.':'.')));
      folio.append(look);
      if(dl.children.length)folio.append(dl);
      folio.append(provenanceLine(cn));
      renderRelations(cn);
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
      var ret=el('button','atl-action atl-return','Return to the whole atlas');ret.type='button';ret.addEventListener('click',returnToAtlas);
      actions.append(ret);folio.append(actions);
    }
    function actionButton(parent,text,fn,key){var b=el('button','atl-action',text);b.type='button';if(key)b.dataset.key=key;b.addEventListener('click',fn);parent.append(b);return b;}
    function renderRelations(cn){
      var model=S.model,list=model.adjacency[cn.id],wrap=el('section','atl-relations');
      wrap.append(el('h4','atl-section-title','Documented relationships · '+list.length));
      if(!list.length)wrap.append(el('p','atl-note','No documented relationships. A missing link does not mean the ideas are incompatible.'));
      M.FACETS.forEach(function(facet){
        var rows=list.filter(function(a){return model.byId[a.other].facet===facet;});
        if(!rows.length)return;
        wrap.append(el('h5','atl-group atl-facet-'+facet,M.FACET_LABEL[facet]+' · '+rows.length));
        rows.forEach(function(a,i){
          var other=model.byId[a.other],b=el('button','atl-rel');b.type='button';b.dataset.other=other.id;b.dataset.rel=a.relation.id;
          b.append(el('span','atl-rel-verb',a.verb),el('span','atl-rel-target',other.name));
          b.title=other.title;
          b.addEventListener('click',function(){select(other.id,{via:'folio'});focusFolio();});
          b.addEventListener('focus',refreshEmphasis);
          b.addEventListener('blur',function(){global.setTimeout(refreshEmphasis,0);});
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
      // Landmarks: the most connected ideas of each kind, by count of documented relationships.
      var marks=el('section','atl-landmarks');
      marks.append(el('h4','atl-section-title','Landmarks · most documented relationships'));
      ['genres','emotions','structure','tropes','other'].forEach(function(facet){
        // Genres are the first reading of the story; the folio names every one of them.
        var top=model.concepts.filter(function(x){return x.facet===facet&&x.tier===1&&x.degree>0;})
          .sort(function(a,b){return b.degree-a.degree||a.title.localeCompare(b.title);}).slice(0,facet==='genres'?7:3);
        if(!top.length)return;
        var row=el('div','atl-landmark-row');row.append(el('span','atl-landmark-kind atl-facet-'+facet,M.FACET_LABEL[facet]));
        top.forEach(function(cn){var b=el('button','atl-landmark atl-facet-'+facet);b.type='button';b.title=cn.title;
          b.append(el('span','atl-landmark-name',cn.name),el('span','atl-landmark-count',String(cn.degree)));
          b.setAttribute('aria-label',cn.title+', '+cn.degree+' documented relationships');
          b.addEventListener('click',function(){select(cn.id,{via:'atlas'});focusFolio();});
          b.dataset.id=cn.id;b.addEventListener('focus',refreshEmphasis);b.addEventListener('blur',function(){global.setTimeout(refreshEmphasis,0);});
          row.append(b);});
        marks.append(row);
      });
      folio.append(marks);
      var how=el('ul','atl-how');
      ['Bands hold kinds of narrative idea; story time runs left to right in recorded phase order, one hairline per phase, Books shaded in turn.',
       'Across, a concept sits near the phases it is recorded with: directly, through its genre, or through its recorded neighbours. Concepts with no such record are spread evenly. Nearness alone is never a relationship.',
       'Threads are recorded proposal relationships, coloured by the kind of idea they reach. Larger marks have more of them.',
       'Small points are local phrases recorded inside a genre or phase; they gain words as you come closer or unfold them.']
        .forEach(function(t){how.append(el('li','',t));});
      folio.append(el('h4','atl-section-title','How to read the atlas'),how);
      var legend=el('div','atl-legend');legend.setAttribute('role','group');legend.setAttribute('aria-label','Highlight a kind of idea');
      M.FACETS.forEach(function(facet){
        var count=model.concepts.filter(function(x){return x.facet===facet;}).length;if(!count)return;
        var b=el('button','atl-legend-item atl-facet-'+facet);b.type='button';b.dataset.key='lens:'+facet;b.setAttribute('aria-pressed',String(S.lens===facet));
        b.append(el('span','atl-legend-glyph'),el('span','',M.FACET_LABEL[facet]+' · '+count));
        b.addEventListener('click',function(){S.lens=S.lens===facet?null:facet;root.dataset.lens=S.lens||'';renderFolio();});
        legend.append(b);
      });
      folio.append(el('h4','atl-section-title','Highlight a kind of idea'),legend);
      var ways=el('section','atl-task');
      ways.append(el('h4','atl-section-title','Ways of looking'));
      var steps=el('ol','');
      ['Select a concept: its documented relationships come forward in place. Nothing moves.',
       'Reveal deeper connections to see what its neighbours are recorded with.',
       'Examine as constellation to recompose one neighbourhood for close reading.',
       'Escape, or Return, brings back the whole atlas exactly where you were.']
        .forEach(function(t){steps.append(el('li','',t));});
      ways.append(steps);folio.append(ways);
      var index=el('section','atl-index');index.append(el('h4','atl-section-title','Atlas index'));
      M.FACETS.forEach(function(facet){
        var members=model.concepts.filter(function(x){return x.facet===facet;})
          .sort(function(a,b){return a.tier-b.tier||(facet==='timeline'?(a.order||0)-(b.order||0):a.title.localeCompare(b.title));});
        if(!members.length)return;
        var d=el('details','atl-index-group');d.append(el('summary','atl-facet-'+facet,M.FACET_LABEL[facet]+' · '+members.length));
        members.forEach(function(cn){var b=el('button','atl-index-item',cn.name);b.type='button';b.title=cn.title;
          b.addEventListener('click',function(){select(cn.id,{via:'atlas'});focusFolio();});d.append(b);});
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
        var b=el('button','atl-crumb atl-facet-'+cn.facet,M.shorten(cn.name,30));b.type='button';b.title=cn.title;
        if(i===S.trail.length-1){b.setAttribute('aria-current','location');b.disabled=true;}
        else b.addEventListener('click',function(){var hadFocus=root.contains(document.activeElement);select(id,{trailIndex:i});
          if(hadFocus&&starEls[id])starEls[id].focus({preventScroll:true});});
        trail.append(b);
      });
      lensbar.replaceChildren();
      if(S.focus&&S.mode==='constellation'){
        lensbar.append(el('span','atl-lensbar-title','Focused constellation'));
        var leave=el('button','atl-lensbar-leave','Back to the atlas · Esc');leave.type='button';leave.addEventListener('click',leaveConstellation);
        lensbar.append(leave);
      }
    }
    function syncChrome(){
      modeButtons.atlas.setAttribute('aria-pressed',String(S.mode==='atlas'&&!S.research));
      modeButtons.constellation.setAttribute('aria-pressed',String(S.mode==='constellation'));
      modeButtons.constellation.disabled=!S.focus&&S.mode!=='constellation';
      modeButtons.constellation.title=S.focus?'Recompose “'+S.model.byId[S.focus].title+'” and its neighbourhood for close reading (E)':'Select a concept first, then examine it as a constellation';
      if(modeButtons.research)modeButtons.research.setAttribute('aria-pressed',String(S.research&&S.mode==='atlas'));
      root.dataset.treatment=activeTreatment();root.dataset.mode=S.mode;
      motion.setAttribute('aria-pressed',String(S.reduced));
      root.classList.toggle('atl-reduced',S.reduced);
      var cn=S.focus&&S.model?S.model.byId[S.focus]:null;
      var name=cn?M.shorten(cn.name,56):'';
      ribbon.textContent=S.mode==='constellation'?
        'Focused constellation of “'+name+'” — recomposed for close reading; tethers mark atlas places. Esc returns to the atlas.':
        S.research?'Research comparison C · contextual unfolding — kept for comparison, not proposed for authors.':
        cn?'Living atlas — “'+name+'” and its documented relationships, revealed in place. E examines it as a constellation.':
        'Living atlas — the whole working Architecture. Select a concept to bring its documented relationships forward in place.';
      ribbon.append(el('span','atl-ribbon-note',' Nothing moves · positions are presentation · nothing is saved.'));
      ribbon.title=cn?cn.title:'';
    }
    function announce(text){live.textContent='';global.setTimeout(function(){live.textContent=text;},30);}

    /* ---------- Input ---------- */
    starLayer.addEventListener('keydown',function(e){
      var star=e.target.closest&&e.target.closest('.atl-star');if(!star)return;
      var id=star.dataset.id,dirs={ArrowRight:0,ArrowDown:Math.PI/2,ArrowLeft:Math.PI,ArrowUp:-Math.PI/2};
      if(dirs[e.key]!==undefined){e.preventDefault();var next=nearest(id,dirs[e.key]);if(next){setRoving(next);ensureVisible(next);S.keyNav=true;starEls[next].focus({preventScroll:true});}}
      else if(e.key===']'||e.key==='+'||e.code==='BracketRight'){e.preventDefault();deeper(true);}
      else if(e.key==='['||e.key==='-'||e.code==='BracketLeft'){e.preventDefault();deeper(false);}
      else if((e.key==='e'||e.key==='E')&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&S.focus){e.preventDefault();if(S.mode==='constellation')leaveConstellation();else examine();}
      else if(e.key==='Backspace'&&S.focus){e.preventDefault();back();}
    });
    root.addEventListener('keydown',function(e){
      if(e.key!=='Escape')return;
      latchPointer();
      if(!S.focus||(e.target.closest&&e.target.closest('details[open] summary')))return;
      e.preventDefault();if(S.mode==='constellation')leaveConstellation();else returnToAtlas();
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
      if(p.x<(narrow()?100:160)||p.y<40||p.x>v.width-120||p.y>v.height-40){
        S.userCam=true;S.lastAction={kind:'pan',at:performance.now()};
        animate({camera:{cx:S.pos[id].x,cy:S.pos[id].y,z:S.cam.z},cameraDuration:S.reduced?0:360});
        if(S.reduced)flushInstant();
      }
    }
    var drag=null,relabelTimer=null;
    stage.addEventListener('pointerdown',function(e){
      // A touch drag may begin on a concept's mark (a tap still selects it; a moving finger cancels the tap).
      var fromStar=e.pointerType==='touch'&&e.target.closest('.atl-star');
      if(e.button!==0||(!fromStar&&e.target.closest('button,a,nav,.atl-zoom,.atl-lensbar')))return;
      // The phone constellation is a list read by scrolling the page; there is nothing to travel sideways.
      if(e.pointerType==='touch'&&S.mode==='constellation'&&narrow())return;
      // Touch: the stage allows vertical page panning (touch-action: pan-y), so a vertical swipe scrolls
      // the page and ends here with pointercancel; a horizontal drag travels the atlas along story time.
      drag={x:e.clientX,y:e.clientY,cx:S.cam.cx,cy:S.cam.cy,moved:false,id:e.pointerId,touch:e.pointerType==='touch'};
      if(!drag.touch)stage.setPointerCapture(e.pointerId);
    });
    stage.addEventListener('pointermove',function(e){
      if(!drag||e.pointerId!==drag.id)return;
      var dx=e.clientX-drag.x,dy=e.clientY-drag.y;
      if(drag.touch){dy=0;if(Math.abs(dx)>8)drag.moved=true;}else if(Math.abs(dx)+Math.abs(dy)>4)drag.moved=true;
      if(drag.moved){if(!S.dragging){S.dragging=true;latchPointer();}
        var cx=drag.cx-dx/S.cam.z;
        // A touch drag travels story time between its first and last phase, never into empty paper.
        if(drag.touch&&S.atlas){var hw=view().width/2/S.cam.z;cx=clamp(cx,Math.min(drag.cx,ATLAS_X0+hw-120/S.cam.z),Math.max(drag.cx,S.atlas.width-hw+40/S.cam.z));}
        S.cam={cx:cx,cy:drag.cy-dy/S.cam.z,z:S.cam.z};if(S.tw)S.tw.cam=null;paint();stage.classList.add('is-panning');}
    });
    function endDrag(e){
      if(!drag||e.pointerId!==drag.id)return;
      var wasClick=!drag.moved;drag=null;S.dragging=false;stage.classList.remove('is-panning');
      if(!wasClick){S.userCam=true;S.lastAction={kind:'pan',at:performance.now()};global.clearTimeout(relabelTimer);
        relabelTimer=global.setTimeout(function(){S.frames=[];settle();},90);return;}
      if(S.focus&&e.type==='pointerup'){if(S.mode==='constellation')leaveConstellation();else returnToAtlas();}
    }
    stage.addEventListener('pointerup',endDrag);stage.addEventListener('pointercancel',endDrag);
    stage.addEventListener('wheel',function(e){
      if(!(e.ctrlKey||e.metaKey)||!S.model)return;e.preventDefault();
      var r=stage.getBoundingClientRect();zoomBy(e.deltaY<0?1.12:0.89,{x:e.clientX-r.left,y:e.clientY-r.top});
    },{passive:false});
    // The scene is refitted only when the stage it was last fitted for has really changed size.
    function refit(){
      if(!S.model||!S.shown)return;
      measureView();
      if(!S.sizedOnce){S.sizedOnce=true;S.paintedView={width:S.view.width,height:S.view.height};fitAtlas(false);applyPending();return;}
      var before=S.paintedView;
      if(before&&before.width===S.view.width&&before.height===S.view.height)return;
      S.paintedView={width:S.view.width,height:S.view.height};
      if(!S.focus){if(!S.userCam)fitAtlas(false);paint();settle();return;}
      // A focus is recomposed for the new stage at once, without travel.
      var keep=S.reduced;S.reduced=true;unfold({fresh:false,camera:S.mode==='constellation'?undefined:null});S.reduced=keep;
    }
    var resizeTimer=null;
    if(global.ResizeObserver)new ResizeObserver(function(){
      if(!S.model||!S.shown)return;global.clearTimeout(resizeTimer);
      resizeTimer=global.setTimeout(refit,80);
    }).observe(stage);

    /* ---------- Source binding ---------- */
    function clearExploration(){
      if(S.raf){global.cancelAnimationFrame(S.raf);S.raf=null;}
      S.focus=null;S.hood=null;S.comp=null;S.trail=[];S.depth=1;S.sides={};S.restCam=null;S.atlasCam=null;S.tw=null;
      S.mode='atlas';S.mix=0;S.lastFocus=null;S.userCam=false;S.travelling=false;stage.style.height='';
      root.classList.remove('atl-focused','atl-examining','atl-deep','atl-travelling');
      lensbar.hidden=true;fitHood.hidden=true;compass.replaceChildren();
    }
    function update(){
      var candidate=binding.getCandidate(),sha=binding.getRequestSha();
      if(S.model&&sha===S.sha&&candidate===S.candidateRef)return;
      var hadFocus=!!S.focus;
      S.candidateRef=candidate;clearExploration();
      if(!candidate||!(candidate.nodes||[]).length){S.model=null;S.atlas=null;S.sha=sha;
        buildEmpty();syncChrome();renderFolio();renderTrail();return;}
      var v=measureView();
      try{S.model=M.buildModel(candidate,sha);S.atlas=M.layoutAtlas(S.model,{aspect:v.width/v.height,view:v});}
      catch(error){S.model=null;S.atlas=null;buildEmpty('The atlas could not be drawn: '+error.message);syncChrome();renderFolio();renderTrail();return;}
      S.sha=sha;S.pos={};Object.keys(S.atlas.positions).forEach(function(id){S.pos[id]={x:S.atlas.positions[id].x,y:S.atlas.positions[id].y};});
      empty.hidden=true;buildScene();syncChrome();applyStates();syncVerbs();syncTethers();renderTrail();
      if(S.shown&&stage.clientWidth){S.sizedOnce=true;S.paintedView={width:v.width,height:v.height};fitAtlas(false);applyPending();}
      renderFolio();
      if(hadFocus)announce('The working Architecture changed; the atlas was redrawn and your previous focus cleared. Nothing was saved.');
    }
    function applyPending(){
      var p=S.pending;S.pending=null;
      if(p&&p.focus&&S.model&&S.model.byId[p.focus]){
        var keep=S.reduced;S.reduced=true;select(p.focus,{via:'atlas',depth:p.depth===2?2:1,focusStar:false});
        if(p.examine)examine();S.reduced=keep;
      }else settle();
    }
    function buildEmpty(message){
      starLayer.replaceChildren();gEdges.replaceChildren();gVerbs.replaceChildren();gTethers.replaceChildren();
      gBands.replaceChildren();gSpine.replaceChildren();gGrid.replaceChildren();bandLabels.replaceChildren();
      empty.hidden=false;empty.replaceChildren(el('h3','','The atlas is waiting for an Architecture'),
        el('p','',message||'Develop a working Architecture proposal, then come back to explore it here.'));
    }
    function show(){
      var first=!S.shown,built=!!S.model;S.shown=true;root.hidden=false;measureView();update();
      var inspector=!!(binding.inspectorOpen&&binding.inspectorOpen());
      if(inspector!==S.inspectorOpen){S.inspectorOpen=inspector;if(!first)renderFolio();}
      if(built&&stage.clientWidth)refit();
    }
    function hide(){S.shown=false;root.hidden=true;}
    syncChrome();
    var api={update:update,show:show,hide:hide,select:function(id,o){select(id,Object.assign({via:'atlas'},o||{}));},
      returnToAtlas:returnToAtlas,deeper:deeper,setTreatment:setTreatment,examine:examine,leaveConstellation:leaveConstellation,
      setReducedMotion:function(on){S.reduced=!!on;syncChrome();},
      fitAtlas:function(){fitAtlas(false);settle();},
      metrics:function(){return S.metrics;},
      snapshot:function(){return {mode:S.mode,treatment:activeTreatment(),research:S.research,focus:S.focus,depth:S.depth,trail:S.trail.slice(),
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
