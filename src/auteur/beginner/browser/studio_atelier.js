/* Living Narrative Atelier — experimental visual study stage (opt-in via ?atelier).
   A is the world: a stable, information-rich atlas of the working Architecture in which selecting a
   concept brings its recorded relationships forward in place; nothing moves and the view is kept.
   B is the magnifying glass: an explicit Focused Constellation that recomposes one neighbourhood for
   close reading and returns to the atlas as it was left. C (contextual unfolding) survives only as a
   research comparison (?atelier=C). Presentation only: layout, camera and focus live in memory;
   nothing is saved or accepted. */
(function(global,document){
  'use strict';
  var M=global.AuteurStudioAtelierModel,X=global.AuteurAtelierSeries,B=global.AuteurAtelierBook,SVG='http://www.w3.org/2000/svg';
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
    nearVerb:{font:'500 12px '+SANS,lh:14.5,px:7,py:3,maxW:260,lines:2,kicker:'italic 11px '+SERIF,klh:13},
    // Story-structure comparison: a recorded role or parenthood is named above the resting label, and while
    // a concept is selected each phase that records it names the role that phase records.
    landmark:{font:'600 14px '+SERIF,lh:17,px:2,py:1,maxW:176,lines:2,kicker:'700 8.5px '+SANS,klh:12},
    landmarkName:{font:'600 14px '+SERIF,lh:17,px:2,py:1,maxW:176,lines:2},
    restRole:{font:'500 10.5px '+SANS,lh:12.5,px:2,py:1,maxW:128,lines:2,kicker:'700 8px '+SANS,klh:11},
    nearRole:{font:'500 12px '+SANS,lh:14.5,px:7,py:3,maxW:196,lines:2,kicker:'700 8px '+SANS,klh:11},
    phaseListed:{font:'500 11.5px '+SERIF,lh:13.5,px:4,py:2,maxW:124,lines:3,kicker:'700 8px '+SANS,klh:11}
  };
  /* Story-structure comparison: a genre mark is sized by the role its contract records, never by how many
     relationships it has; every other mark keeps one size. Parenthood is shown as a frame, not as size. */
  var ROLE_GS={governing:1.6,primary:1.6,supporting:1.12,secondary:1.12,tertiary:0.9,local:0.9};
  var ROLE_REST={governing:260,primary:260,supporting:60,secondary:60,tertiary:30,local:30};
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
      hover:null,folioHint:null,callout:null,latched:false,ptr:null,dragging:false,
      narrative:!!(binding.initial&&binding.initial.narrative),structure:null,time:null,seriesCtx:null,leaf:null};

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
    // Comparison switch for this study: the same atlas, with recorded roles and parenthood given weight.
    var structureTool=el('button','atl-tool atl-tool-structure','Story structure');structureTool.type='button';
    structureTool.title='Comparison: genre marks sized by the role their contract records, structural parents framed. Mark size stops counting relationships. Nothing moves.';
    structureTool.addEventListener('click',function(){setNarrative(!S.narrative);});
    var readout=el('details','atl-readout');var readoutSummary=el('summary','','Study readout');
    var readoutBody=el('dl','atl-readout-body');readout.append(readoutSummary,readoutBody);
    tools.append(structureTool,motion,readout);
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
    function gs(cn){
      if(S.narrative&&S.structure){var role=S.structure.roles[cn.id];return cn.tier===2||!role?1:ROLE_GS[role.role]||1;}
      return cn.tier===2?1:0.8+0.55*Math.sqrt((cn.degree||0)/(S.model.maxDegree||1));
    }
    function isParent(id){return !!(S.structure&&S.structure.contains[id]);}
    function roleOf(id){return S.structure&&S.structure.roles[id]?S.structure.roles[id].role:null;}
    // The resting hierarchy of the story-structure comparison: sizes, frames and spoken labels follow records.
    function syncNarrative(){
      if(!S.model)return;
      root.dataset.narrative=S.narrative?'on':'off';
      S.model.concepts.forEach(function(cn){
        var b=starEls[cn.id];if(!b)return;
        b.style.setProperty('--gs',gs(cn).toFixed(3));
        var role=S.narrative?roleOf(cn.id):null,parent=S.narrative&&isParent(cn.id);
        if(role)b.dataset.role=role;else delete b.dataset.role;
        b.classList.toggle('is-parent',parent);
        var said=b.__aria;
        if(role)said+=' Recorded role: '+M.human(role)+', in the genre contract.';
        if(parent)said+=' Recorded structural parent of '+S.structure.contains[cn.id].length+'.';
        b.setAttribute('aria-label',said);
      });
    }
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
        var p=sv('path',{'class':'atl-edge','data-facet':model.byId[r.to].facet,'data-kind':r.sourceKind});
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
        b.__aria=M.FACET_SINGULAR[cn.facet]+': '+cn.title+'. '+count+' documented relationship'+(count===1?'':'s')+
          '. Agent proposal, not accepted story.';
        b.setAttribute('aria-label',b.__aria);
        if(cn.category)b.dataset.category=cn.category;
        b.addEventListener('click',function(){if(S.focus!==cn.id)select(cn.id,{via:'atlas'});else focusFolio();});
        b.addEventListener('focus',function(){setRoving(cn.id);refreshEmphasis();});
        b.addEventListener('blur',function(){global.setTimeout(refreshEmphasis,0);});
        starLayer.append(b);starEls[cn.id]=b;
      });
      var first=model.timeline[0]||model.concepts[0];if(first)setRoving(first.id);
      syncNarrative();
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
      // Story structure: a phase that lists the selected genre without activating it is marked in place, with
      // no thread, because the phase records no relationship to draw.
      S.model.concepts.forEach(function(cn){
        var b=starEls[cn.id],st=starState(cn.id);
        b.style.setProperty('--d',(delays&&delays[cn.id]!==undefined?delays[cn.id]:0)+'ms');
        ['rest','focus','near','far','dim'].forEach(function(name){b.classList.toggle('is-'+name,st===name);});
        if(st==='focus')b.setAttribute('aria-current','true');else b.removeAttribute('aria-current');
        b.classList.toggle('is-moved',!!(S.comp&&S.comp.moved.indexOf(cn.id)>=0&&st!=='focus'));
        b.classList.toggle('was-focus',!S.focus&&cn.id===S.lastFocus);
        b.classList.toggle('is-listed',(st==='dim'||st==='far')&&!!phaseCue(cn.id));
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
    // A label with a short recorded statement above the name.
    function kickSpec(style,text,kick,maxW,lines){
      var st=STYLE[style],t=wrapText(text,st,maxW,lines),k=fitLine(kick,st.kicker,maxW||st.maxW);
      var kw=textWidth(k,st.kicker)+k.length*0.12*parseFloat(/(\d+(?:\.\d+)?)px/.exec(st.kicker)[1]);
      return {style:style,lines:t.lines,kicker:k,w:Math.ceil(Math.max(t.w-2*st.px,kw))+2*st.px+1,h:t.h+st.klh};
    }
    function upper(t){return M.human(t).toUpperCase();}
    /* Story time inside Progressive Revelation: while Story structure is on and a concept is selected in the
       atlas, each phase whose record names it says which role that phase records. Phase roles are the
       phase's own record and may differ from the genre contract's role; "PHASE ROLE" keeps them apart. */
    function syncTime(){
      var cn=S.narrative&&S.focus&&S.mode==='atlas'&&!S.research?S.model.byId[S.focus]:null;
      var p=cn&&cn.facet!=='timeline'?M.storyPathway(S.model,cn.id):null;
      S.time=p&&p.recorded?{id:cn.id,pathway:p,byPhase:{}}:null;
      if(S.time)p.phases.forEach(function(ph){S.time.byPhase[ph.phase]=ph;});
    }
    function phaseCue(id){var ph=S.time&&S.time.byPhase[id];return ph&&ph.status==='recorded'?ph:null;}
    function cueKick(ph){return ph.phaseRole?'PHASE ROLE · '+upper(ph.phaseRole.role):'RECORDED IN THIS PHASE';}
    function verbSpec(cn){
      var st=STYLE.nearVerb,maxW=Math.min(st.maxW,view().width-90),t=wrapText(cn.name,st,maxW),verb=fitLine(S.verbFor[cn.id]||'',st.kicker,maxW);
      return {style:'nearVerb',lines:t.lines,kicker:verb,w:Math.ceil(Math.max(t.w-2*st.px,textWidth(verb,st.kicker)))+2*st.px+1,h:t.h+st.klh};
    }
    function specsFor(cn,st,z){
      // The title card has a narrower, taller form for crowded places, so it can avoid covering a neighbour.
      if(st==='focus'){var wide=focusSpec(cn),slim=cardSpec(cn,wide.style,170);return slim.w<wide.w-20?[wide,slim]:[wide];}
      if(st==='near'&&S.mode==='constellation'&&narrow())return [verbSpec(cn)];
      var cue=cn.facet==='timeline'?phaseCue(cn.id):null;
      if(cue&&st==='near'){var k=cueKick(cue);
        return [kickSpec('nearRole',cn.name,k,220,3),kickSpec('nearRole',cn.name,k,196,2),kickSpec('nearRole',M.shorten(cn.name,30),k,196,1),
          spec('near',M.shorten(cn.name,30),196,1)];}
      // A phase that records the concept without a relationship to it (listed only) keeps its own mark, even
      // when a deeper reveal reaches it through other concepts.
      if(cue&&(st==='dim'||st==='far'))return [kickSpec('phaseListed',cn.name,cueKick(cue)),kickSpec('phaseListed',M.shorten(cn.name,30),cueKick(cue),124,2)];
      // Relationship pills: the whole name when there is room, then two lines, then a phrase cut at a word.
      if(st==='near')return [spec('near',cn.name,220,3),spec('near',cn.name,196,2),spec('near',M.shorten(cn.name,30),196,1)];
      if(st==='far')return [spec('far',cn.name),spec('far',M.shorten(cn.name,28),180,1)];
      if(cn.tier===2)return [spec('mote',M.shorten(cn.name,34))];
      if(S.narrative&&st==='rest'){
        var role=roleOf(cn.id);
        // Where a crowded score leaves no room for the role line, the name alone is set larger; the call-out,
        // the folio and the spoken label still state the recorded role.
        if(role==='governing'||role==='primary')return [kickSpec('landmark',cn.name,upper(role)+' · PROPOSED'),
          kickSpec('landmark',cn.name,upper(role)+' · PROPOSED',300,1),kickSpec('landmark',cn.name,upper(role)+' · PROPOSED',130,3),
          spec('landmarkName',cn.name),spec('landmarkName',cn.name,124,3),spec('genre',cn.name)];
        if(isParent(cn.id))return [kickSpec('restRole',cn.name,'CONTAINS '+S.structure.contains[cn.id].length),spec('rest',cn.name)];
      }
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
        if(st==='dim'&&cn.facet==='timeline'&&phaseCue(cn.id)){item.priority=650;item.overSoft=true;item.places=['s','n'];item.gap=r+4;}
        else if(st==='focus'){item.priority=1000;item.required=true;item.overSoft=true;item.gap=r+5;
          item.places=examining&&narrow()?['e','n','s']:examining||narrow()?['s','n']:['s','n','e','w','se','sw','ne','nw'];
          if(!examining)focusItem=item;}
        else if(st==='near'){item.priority=800-facetOrder[cn.facet]*3+10*weight;item.overSoft=true;item.places=examining?side:AROUND;
          if(sd==='rail-s'||sd==='rail-n')item.gap=r+9;}
        else if(st==='far'){item.priority=600+5*weight;item.overSoft=true;item.places=examining?side:AROUND;}
        else{
          // The comparison ranks resting names by recorded role and parenthood only, never by relationship count.
          item.priority=(S.focus?-200:0)+(FACET_BASE[cn.facet]||420)-(cn.tier===2?300:0)+(S.narrative?
            (ROLE_REST[roleOf(cn.id)]||0)+(isParent(cn.id)?120:0):60*weight+(/^(governing|primary)/.test(cn.role||'')?20:0));
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
      // A card cut off by the stage edge is worst, then one covering a control (trail, zoom, way back), then a
      // direct relative's mark; a faint second-order mark matters least.
      function cost(b){if(b.soft==='hood')return 2;if(b.owner==='ui')return 600;var st=starState(b.owner);return st==='far'?40:300;}
      function score(o,i,vr){
        var r=M.placeRect(o[0],a.x+o[1],a.y+o[2],item.gap,vr.w,vr.h);
        var sc=i*0.01+(r.x0<bounds.x0||r.y0<bounds.y0||r.x1>bounds.x1||r.y1>bounds.y1?2000:0)+(hit(r,own)?1000:0);
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
      if(S.leaf&&S.leaf.from!==id)S.leaf=null;
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
      S.hood=M.neighbourhood(S.model,S.focus,S.depth);syncTime();
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
      S.leaf=null;
      latchPointer();S.time=null;
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
    /* ---------- Story structure comparison ----------
       The switch changes what the resting atlas gives weight to and what a selection says about story
       time; it never moves anything, so switching back gives exactly the view it was switched from. */
    function setNarrative(on){
      on=!!on;if(S.narrative===on)return;
      S.narrative=on;S.lastAction={kind:on?'structure-on':'structure-off',at:performance.now()};
      syncNarrative();syncChrome();if(S.model){syncTime();applyStates();renderFolio();S.frames=[];settle();}
      announce(on?'Story structure on: genre marks are sized by their recorded contract role and structural parents are framed. Nothing moved.':
        'Story structure off: mark size counts documented relationships again. Nothing moved.');
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
      if(a.classList.contains('atl-landmark')||a.classList.contains('atl-st-row'))return {id:a.dataset.id};
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
      var star=t&&t.closest?t.closest('.atl-star'):null,rel=t&&t.closest?t.closest('.atl-rel'):null,mark=t&&t.closest?t.closest('.atl-landmark,.atl-st-row'):null;
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
        composition:base,reducedMotion:S.reduced,concepts:S.model.concepts.length,relations:S.model.relations.length,
        narrative:S.narrative,storyTime:S.time?{id:S.time.id,recorded:S.time.pathway.recorded,notRecorded:S.time.pathway.absent}:null};
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
      row('Story structure',m.narrative?'on · sizes follow recorded roles':'off · sizes count relationships');
      if(m.storyTime)row('Story time',m.storyTime.recorded+' phases record it · '+m.storyTime.notRecorded+' record nothing for it');
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
    // A recorded list whose entries each keep their own source (an agent proposal, not a plan or commitment).
    function sourcedList(dl,label,values,base){
      if(!Array.isArray(values)||!values.length)return;
      var dd=el('dd','atl-sourced'),ol=el('ol','atl-sourced-list');
      values.forEach(function(v,i){var li=el('li','',String(v));li.append(el('span','atl-chip atl-chip-source','Source · '+base+i));ol.append(li);});
      dd.append(ol,el('p','atl-note','Agent proposal: payoffs the proposal hopes for, not recorded setups or commitments of a Series or Book plan.'));
      dl.append(el('dt','',label),dd);
    }
    function renderFolio(){
      var active=document.activeElement,key=active&&folio.contains(active)&&active.dataset?active.dataset.key:null;
      var onTitle=!!(active&&folio.contains(active)&&active.classList.contains('atl-folio-title')),top=folio.scrollTop;
      // A field the author is typing in survives a re-render as the same element: its words, caret and
      // scroll stay exactly where they were, whatever finishes reading in the meantime.
      var typing=key&&active.tagName==='TEXTAREA'&&!active.readOnly?active:null;
      var caret=typing?[typing.selectionStart,typing.selectionEnd,typing.selectionDirection,typing.scrollTop]:null;
      renderFolioContent();
      if(S.folioFor!==S.focus){S.folioFor=S.focus;folio.scrollTop=0;}
      // A re-render under the reader (for example when plans finish reading) keeps the title focused.
      if(onTitle&&!key){var h=folio.querySelector('h3');if(h){h.tabIndex=-1;h.focus({preventScroll:true});folio.scrollTop=top;}}
      if(key){var again=folio.querySelector('[data-key="'+cssEscape(key)+'"]');
        if(again&&typing&&again.tagName==='TEXTAREA'){again.replaceWith(typing);again=typing;}
        if(again){again.focus({preventScroll:true});
          if(again===typing){try{typing.setSelectionRange(caret[0],caret[1],caret[2]);}catch(_){}typing.scrollTop=caret[3];}}
        else focusFolio();}
      // A composer just opened takes the keyboard once it is drawn, after any focus a re-render restores.
      var dv=S.dev,field=dv&&dv.focusPending&&folio.querySelector('[data-key="book-instruction:'+dv.book+'"]');
      if(field){dv.focusPending=false;field.focus({preventScroll:false});}
    }
    function renderFolioContent(){
      folio.replaceChildren();
      var status=binding.getSourceStatus?binding.getSourceStatus():null;
      if(!S.model){
        folio.append(el('p','atl-kicker-line','The atlas'),el('h3','atl-folio-title','No working Architecture yet'),
          el('p','atl-folio-detail','Develop a working Architecture proposal in the Studio, then return to this study. The study only reads what the proposal records.'));
        return;
      }
      renderWorking();
      if(S.leaf&&X)return renderSeriesLeaf();
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
        sourcedList(dl,'Proposed reader payoffs',rec.payoff_expectations,'genre_contracts/'+rec.genre_node_id+'/payoff_expectations/');
        fact(dl,'Aesthetic strategies',rec.aesthetic_strategies);
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
        if(cn.nodeId&&rec.category==='trope')renderTropeUses(cn,dl);
      }
      // Story structure: what the records state about this concept's standing, each with its source.
      var role=S.narrative&&S.structure?S.structure.roles[cn.id]:null;
      if(role)fact(dl,'Recorded role',M.human(role.role)+' · genre contract ('+role.sourceRef+'), an agent proposal');
      if(S.narrative&&S.structure){
        var up=S.structure.partOf[cn.id],kids=S.structure.contains[cn.id];
        if(up&&model.byId[up.id])fact(dl,'Recorded as part of',model.byId[up.id].title);
        if(kids)fact(dl,'Recorded as the parent of',kids.length+': '+kids.map(function(k){return model.byId[k.id].title;}).join(' · '));
        if(kids||up)fact(dl,'Parenthood','A recorded parent link. The atlas frames a parent but does not size or rank it as governing; what the link means for the story is in the proposal’s own words.');
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
      var pathway=S.narrative&&cn.facet!=='timeline'?M.storyPathway(model,cn.id):null;
      folio.append(look);
      renderRevisedNote(cn);
      // What story time records comes straight after the ways of looking, beside the phases it marks.
      if(pathway)renderStoryTime(cn,pathway);
      renderDevelop(cn);
      if(X)renderSeriesSection(cn);
      if(dl.children.length)folio.append(dl);
      folio.append(provenanceLine(cn));
      if(S.structure)renderInterpretations(S.structure.interpretations[cn.id],'Agent interpretations naming it');
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
    /* In story time: each phase in recorded order, with what that phase's record states for the concept
       and where. A phase with no record says so; that is a gap in the records, not absence from the story.
       Equal wording is not identity: a phrase is linked to a phase only by a record that refers to it. */
    /* A shared trope and its contextual functions: only a recorded trope-function reference joins them.
       Phrases that repeat the trope's words are counted separately and are not drawn or linked. */
    function renderTropeUses(cn,dl){
      var model=S.model,realised=model.adjacency[cn.id].filter(function(a){return a.relation.verb==='realises trope'&&a.direction==='reverse';});
      var linked={};realised.forEach(function(a){linked[a.other]=true;});
      var name=String(cn.name).trim().toLowerCase();
      var same=model.concepts.filter(function(x){return x.tier===2&&x.facet==='tropes'&&!linked[x.id]&&String(x.name).trim().toLowerCase()===name;});
      fact(dl,'Recorded contextual functions',realised.length?realised.length+' function'+(realised.length===1?'':'s')+' recorded as realising this trope (listed among its relationships)':
        'None recorded. No genre or phase record names this trope as the one its function realises.');
      if(same.length)fact(dl,'Same words, not recorded as this trope',same.length+' local phrase'+(same.length===1?'':'s')+' ('+
        same.map(function(x){var o=x.phaseId?model.byId['timeline|phase:'+x.phaseId]:model.byId['genres|genre:'+x.ownerGenreId];return o?o.name:x.sourceRef;})
          .filter(function(v,i,a){return a.indexOf(v)===i;}).join(' · ')+
        ') repeat its words. Equal wording is not a recorded link, so the atlas does not join them; a revision could record which ones realise it.');
    }
    function sameWords(cn){
      if(cn.tier!==2||cn.phaseId)return [];
      var key=String(cn.name).trim().toLowerCase(),seen={};
      S.model.concepts.forEach(function(x){if(x.tier===2&&x.phaseId&&x.facet===cn.facet&&String(x.name).trim().toLowerCase()===key)seen[x.phaseId]=true;});
      return S.model.timeline.filter(function(ph){return seen[(ph.record||{}).id];});
    }
    function phaseRow(ph,i,model){
      var phase=model.byId[ph.phase],li=el('li','atl-st-item'+(ph.status==='recorded'?' is-recorded':' is-unrecorded'));
      var b=el('button','atl-st-row');b.type='button';b.dataset.id=phase.id;b.dataset.key='st:'+phase.id;
      b.append(el('span','atl-st-num',String(i+1)),el('span','atl-st-name',phase.name));
      var what=ph.status!=='recorded'?'Not recorded':ph.phaseRole?'Phase role · '+M.human(ph.phaseRole.role):'Recorded in this phase';
      if(ph.status==='recorded'&&ph.kinds.indexOf('relation')<0&&ph.kinds.indexOf('recorded-in')<0)what+=' · listed, no activation';
      b.append(el('span','atl-st-what',what));
      var alongside=ph.parallel.map(function(id){return model.timeline.indexOf(model.byId[id])+1;}).filter(Boolean);
      b.setAttribute('aria-label','Phase '+(i+1)+', '+phase.title+': '+what+(alongside.length?'; recorded as parallel with phase '+alongside.join(' and '):'')+'.');
      b.addEventListener('click',function(){select(phase.id,{via:'folio'});focusFolio();});
      b.addEventListener('focus',refreshEmphasis);b.addEventListener('blur',function(){global.setTimeout(refreshEmphasis,0);});
      li.append(b);
      if(alongside.length)li.append(el('p','atl-st-par','Recorded as running parallel with phase '+alongside.join(' and ')));
      if(ph.status==='recorded'){
        // Every marked phase names the records that state it; what they say opens on demand.
        var src=el('p','atl-st-src');
        ph.evidence.map(function(e){return e.sourceRef;}).filter(function(r,k,a){return a.indexOf(r)===k;})
          .forEach(function(r){src.append(el('span','atl-chip atl-chip-source',r));});
        li.append(src);
        var more=el('details','atl-st-more');more.append(el('summary','','What this phase records'));
        ph.evidence.forEach(function(e){
          more.append(el('p','atl-st-ev',e.kind==='role'?'Listed among the phase’s genres as '+M.human(e.role)+' (the phase’s own record; the genre contract may say otherwise).':
            e.kind==='recorded-in'?'Recorded inside this phase.':M.capital(e.verb)+(e.reason?': '+e.reason:'.')));
        });
        if(ph.locals.length)more.append(el('p','atl-st-ev','Local functions here: '+ph.locals.map(function(l){return model.byId[l.id].name;}).join(' · ')));
        li.append(more);
      }
      return li;
    }
    function renderStoryTime(cn,p){
      var model=S.model,wrap=el('section','atl-storytime');
      if(!p.available){
        wrap.append(el('h4','atl-section-title','In story time · no phase record refers to it'));
        var same=sameWords(cn);
        wrap.append(el('p','atl-note','No phase record refers to this concept. Auteur does not infer phase participation from chains of other '+
          'relationships, so this is not evidence that it is absent from the story.'+
          (same.length?' Local functions in '+(same.length===1?'phase ':'phases ')+same.map(function(ph){return model.timeline.indexOf(ph)+1;}).join(', ')+
            ' use the same words; without a recorded reference, equal wording is not treated as the same idea.':'')+
          (S.structure&&(S.structure.contains[cn.id]||S.structure.partOf[cn.id])?' Its recorded structure is listed below and among its relationships.':'')));
        folio.append(wrap);return;
      }
      var list=el('ol','atl-st-list');
      if(p.recorded===1&&cn.tier===2){
        // A function recorded inside one phase belongs there; listing every other phase would only repeat that.
        var at=p.phases.findIndex(function(ph){return ph.status==='recorded';});
        wrap.append(el('h4','atl-section-title','In story time · recorded in phase '+(at+1)+' of '+p.phases.length));
        list.start=at+1;list.append(phaseRow(p.phases[at],at,model));
        wrap.append(list);folio.append(wrap);return;
      }
      wrap.append(el('h4','atl-section-title','In story time · '+p.recorded+' of '+p.phases.length+' phases record it'));
      var parallel=p.phases.some(function(ph){return ph.parallel.length;});
      wrap.append(el('p','atl-note','Phases in recorded story order'+(parallel?'; some are recorded as running in parallel':'')+'. Order is not recorded causation, '+
        'and “not recorded” is a gap in the records, not absence from the story.'+
        (cn.facet==='genres'&&S.structure&&S.structure.roles[cn.id]?' A phase role is that phase’s own record; the genre contract records '+M.human(S.structure.roles[cn.id].role)+'.':'')));
      p.phases.forEach(function(ph,i){list.append(phaseRow(ph,i,model));});
      wrap.append(list);folio.append(wrap);
    }
    // Agent interpretations that name this concept: readings offered by the agent, never author decisions.
    function renderInterpretations(list,title){
      if(!list||!list.length)return;
      var wrap=el('section','atl-interp');wrap.append(el('h4','atl-section-title',title+' · '+list.length));
      list.forEach(function(it){
        var d=el('details','atl-interp-item'),sum=el('summary','');
        sum.append(el('span','atl-interp-text',M.shorten(it.text,150)));d.append(sum);
        if(it.text.length>150)d.append(el('p','atl-st-ev',it.text));
        if(it.consequences)d.append(el('p','atl-st-ev','Consequences: '+it.consequences));
        if(it.alternative)d.append(el('p','atl-st-ev','Alternative reading: '+it.alternative));
        var chips=el('p','atl-provenance');
        chips.append(el('span','atl-chip atl-chip-proposal','Agent interpretation · not author-established'));
        if(it.decisionRequired)chips.append(el('span','atl-chip atl-chip-decision','The proposal asks for your decision'));
        chips.append(el('span','atl-chip atl-chip-source','Source · '+it.sourceRef));
        d.append(chips);wrap.append(d);
      });
      folio.append(wrap);
    }
    /* Creative hand-off: the concept's own recorded source goes to the Studio's existing coding-agent
       inquiry and revision workflow. The atlas keeps its place; nothing here calls an agent or changes a record. */
    var DEVELOP=[['challenge','Challenge this design'],['explain','Explain this narrative role'],['explore','Explore possibilities'],['revise','Request a revision']];
    function renderDevelop(cn){
      if(!binding.onDevelop)return;
      var s=M.sourceAnchor(S.model,cn.id),wrap=el('section','atl-develop');wrap.setAttribute('aria-label','Develop with your coding agent');
      wrap.append(el('h4','atl-section-title','Develop with your coding agent'));
      if(!s.anchor){wrap.append(el('p','atl-note',s.reason));folio.append(wrap);return;}
      var about=el('p','atl-develop-about');
      about.append(el('span','atl-develop-subject',s.subject));
      if(s.quote)about.append(el('q','atl-develop-quote',M.shorten(s.quote,160)));
      about.append(el('span','atl-chip atl-chip-source','Source · '+(s.sourceRef||'unavailable')));
      wrap.append(about);
      if(s.precision==='activation')wrap.append(el('p','atl-note','The request is anchored on the recorded activation that holds this phrase; name the phrase in your question.'));
      if(s.precision==='field'&&s.anchor.field==='genre_activations')wrap.append(el('p','atl-note','This genre is activated more than once in the phase, so the request is anchored on all of the phase’s activations.'));
      var row=el('div','atl-develop-actions'),offered=binding.developOperations?binding.developOperations(s.anchor):['challenge','explore','revise'];
      DEVELOP.filter(function(d){return offered.indexOf(d[0])>=0&&!(d[0]==='explain'&&offered.indexOf('challenge')>=0);}).forEach(function(d){
        var b=actionButton(row,d[1],function(){binding.onDevelop({conceptId:cn.id,title:cn.title,anchor:JSON.parse(JSON.stringify(s.anchor)),
          precision:s.precision,subject:s.subject,quote:s.quote,sourceRef:s.sourceRef,operation:d[0]});},'develop:'+d[0]);
        b.dataset.operation=d[0];
      });
      wrap.append(row,el('p','atl-note','Opens the Studio’s coding-agent panel below with this exact source; you write the question. Asking never changes the Architecture. A revision is prepared for your review and applies to the working Architecture only when you choose. The atlas keeps your place.'));
      folio.append(wrap);
    }
    // Where a local phrase is recorded: its genre contract, or its phase and genre.
    function ownerName(x){
      if(!x||x.tier!==2)return null;var m=S.model,g=x.ownerGenreId&&m.byId['genres|genre:'+x.ownerGenreId],ph=x.phaseId&&m.byId['timeline|phase:'+x.phaseId];
      return ph?ph.name+(g?' · '+g.name:''):g?g.name+' contract':null;
    }
    function renderRevisedNote(cn){
      var r=S.revision,why=r&&r.delta.touched[cn.id];if(!why)return;
      var model=S.model,box=el('section','atl-revised');box.setAttribute('aria-label','Changed by the revision you applied');
      box.append(el('h4','atl-section-title','Changed by the revision you applied'));
      var ul=el('ul','atl-revised-list');
      r.delta.reworded.filter(function(x){return x.id===cn.id;}).forEach(function(x){
        if(x.titleChanged){var li=el('li','');
          li.append(el('span','atl-revised-kind',x.positional?'Entry at this position · ':'Recorded wording · '),el('del','',x.before),document.createTextNode(' → '),el('ins','',x.after));
          if(x.positional)li.append(el('span','atl-revised-note',' A list entry is identified only by its position, so this may be a different entry rather than new wording.'));
          ul.append(li);}
        if(x.fields.length)ul.append(el('li','',['Recorded fields changed · '+x.fields.map(function(k){return M.human(k);}).join(', ')].join('')));
        else if(!x.titleChanged)ul.append(el('li','','Recorded description changed.'));});
      if(why.indexOf('added')>=0)ul.append(el('li','',M.positional(cn)?'A new position in its list.':'Newly recorded by the revision.'));
      var rel=function(list,word,lookup){list.filter(function(x){return x.from===cn.id||x.to===cn.id;}).forEach(function(x){
        var otherId=x.from===cn.id?x.to:x.from,other=model.byId[otherId]||r.prev.byId[otherId];
        var rr=lookup.relById[x.id]||{},verb=x.from===cn.id?x.verb:(rr.reverseVerb||'related through “'+x.verb+'”');
        var li=el('li','');li.append(el('span','atl-revised-kind',word),document.createTextNode(verb+' '+(other?other.name+(ownerName(other)?' ('+ownerName(other)+')':''):'a concept no longer recorded')+' '),
          el('span','atl-chip atl-chip-source','Source · '+x.sourceRef));ul.append(li);});};
      rel(r.delta.relationsAdded,'Relationship added · ',model);rel(r.delta.relationsRemoved,'Relationship removed · ',r.prev);
      box.append(ul,el('p','atl-note','Compared with the working version before the revision you applied. A working change, not accepted story; the Architecture records only its current version.'));
      folio.append(box);
    }
    function revisedSummary(){
      var r=S.revision;if(!r)return null;
      var ids=Object.keys(r.delta.touched);
      var wrap=el('section','atl-revised');wrap.setAttribute('aria-label','Your applied revision');
      wrap.append(el('h4','atl-section-title','Your applied revision · '+ids.length+' concept'+(ids.length===1?'':'s')+' changed'));
      if(r.requestedChange)wrap.append(el('p','atl-folio-detail','You asked: “'+M.shorten(r.requestedChange,220)+'”'));
      var list=el('div','atl-revised-index');
      ids.slice(0,24).forEach(function(id){var cn=S.model.byId[id];var b=el('button','atl-index-item',cn.name);b.type='button';b.title=cn.title;b.dataset.id=id;
        b.addEventListener('click',function(){select(id,{via:'atlas'});focusFolio();});list.append(b);});
      wrap.append(list);
      if(ids.length>24)wrap.append(el('p','atl-note',(ids.length-24)+' more are marked in the atlas.'));
      if(r.delta.removed.length)wrap.append(el('p','atl-note',r.delta.removed.length+' concept'+(r.delta.removed.length===1?' is':'s are')+' no longer recorded: '+
        r.delta.removed.slice(0,6).map(function(x){return x.title;}).join(' · ')));
      if(r.delta.summaryChanged)wrap.append(el('p','atl-note','The Architecture summary changed.'));
      wrap.append(el('p','atl-note','Marked with a dashed ring in the atlas. Working changes only; accepted story is unchanged.'+
        (r.keptLayout?' Positions are kept from before the revision, so a concept with new relationships may sit away from the phases it now relates to.':'')));
      if(r.keptLayout)actionButton(wrap,'Lay out the atlas again',relayout,'relayout');
      actionButton(wrap,'Clear revision marks',function(){S.revision=null;syncRevisionMarks();renderFolio();announce('Revision marks cleared.');},'clear-revision');
      return wrap;
    }
    // A fresh layout from the current records, on the author's request; marks and selection are kept.
    function relayout(){
      if(!S.model)return;var v=measureView(),focus=S.focus,depth=S.depth;
      S.atlas=M.layoutAtlas(S.model,{aspect:v.width/v.height,view:v});if(S.revision)S.revision.keptLayout=false;
      S.pos={};Object.keys(S.atlas.positions).forEach(function(id){S.pos[id]={x:S.atlas.positions[id].x,y:S.atlas.positions[id].y};});
      clearExploration();buildScene();syncRevisionMarks();syncChrome();applyStates();syncVerbs();syncTethers();renderTrail();
      fitAtlas(false);if(focus)S.pending={focus:focus,depth:depth};applyPending();renderFolio();
      announce('The atlas was laid out again from the current records.');
    }
    function syncRevisionMarks(){
      if(!S.model)return;var t=S.revision?S.revision.delta.touched:{};
      S.model.concepts.forEach(function(cn){var b=starEls[cn.id];if(b)b.classList.toggle('is-revised',!!t[cn.id]);});
    }
    /* ---------- Series and Book context (read-only) ----------
       The canvas's working Book architectures, the project's Series plan and its Series and Book Directions,
       each read through its own owner. A concept is joined to a Book plan only by a reference that Book
       records to the concept's node id; the project-level plans are shown beside the Architecture, never
       linked to it. Opening this view changes nothing, and Back returns to the concept the author left. */
    var SERIES_MAX_AGE=20000;
    function readSeries(force,announceResult,quiet){
      if(!binding.getSeriesContext)return;
      var c=S.seriesCtx;
      // A read already in flight answers this one too; an explicit request is read again after it.
      if(c&&c.status==='loading'){if(force)S.seriesAgain={announce:!!announceResult,quiet:!!quiet};return;}
      if(c&&c.status==='ready'&&!force&&!S.seriesStale&&Date.now()-c.readAt.getTime()<SERIES_MAX_AGE)return;
      var prev=c&&c.data?c.data.version:(c&&c.prevVersion)||null,seq=(S.seriesSeq||0)+1;S.seriesSeq=seq;S.seriesStale=false;
      S.seriesCtx={status:'loading',data:c&&c.data||null,prevVersion:prev};
      var call;try{call=Promise.resolve(binding.getSeriesContext());}catch(error){call=Promise.reject(error);}
      call.then(function(data){
        if(seq!==S.seriesSeq)return;
        var changed=!!(prev&&data&&prev!==data.version);
        S.seriesCtx={status:'ready',data:data,readAt:new Date(),prevVersion:prev,changed:changed};
        renderFolio();
        if(announceResult)announce(changed?'Read again: the Book and Series plans changed since you last read them.':'Read again: nothing changed.');
        else if(changed&&!quiet)announce('The Book and Series plans changed since you last read them.');
        againAfter();
      },function(error){
        if(seq!==S.seriesSeq)return;
        S.seriesCtx={status:'error',error:error&&error.message||String(error),data:null,prevVersion:prev};renderFolio();againAfter();
      });
      function againAfter(){var a=S.seriesAgain;S.seriesAgain=null;if(a)readSeries(true,a.announce,a.quiet);}
    }
    function toneLine(t,cls){return el('p','atl-tone atl-tone-'+t.tone+(cls?' '+cls:''),t.text);}
    function chip(text,kind){return el('span','atl-chip'+(kind?' atl-chip-'+kind:''),text);}
    function sourceChip(src){return chip('Source · '+X.sourceLine(src),'source');}
    function conceptForNode(nodeId){if(!S.model||!nodeId)return null;
      for(var i=0;i<S.model.concepts.length;i++)if(S.model.concepts[i].nodeId===nodeId)return S.model.concepts[i];return null;}
    function renderSeriesSection(cn){
      if(!binding.getSeriesContext)return;
      readSeries(false);
      var c=S.seriesCtx,wrap=el('section','atl-series');wrap.setAttribute('aria-label','Series and Book plans');
      wrap.append(el('h4','atl-section-title','Series and Book plans'));
      if(!c||(c.status==='loading'&&!c.data)){wrap.append(el('p','atl-note','Reading the Book and Series plans this canvas and project keep…'));folio.append(wrap);return;}
      if(c.status==='error'){wrap.append(el('p','atl-note','Could not read the Book and Series plans: '+c.error));
        actionButton(wrap,'Try again',function(){readSeries(true);},'series-retry');folio.append(wrap);return;}
      var d=c.data,hits=cn?X.forNode(d,cn.nodeId):[],wbs=X.workingBooks(d),bad=X.unreadableBooks(d),proj=X.projectSummary(d);
      if(hits.length){
        var ul=el('ul','atl-series-hits');
        hits.forEach(function(h){var li=el('li','atl-series-hit');
          var p=el('p','atl-provenance');p.append(chip('Working Book architecture · agent proposal · not accepted','proposal'));
          li.append(el('p','atl-series-book','Book '+h.book.book_number+' · '+h.book.title),p);
          li.append(el('p','atl-series-line','Records a reference to this concept in '+X.refSummary(h.ref)+'.'));
          var st=X.refStanding(h.ref);if(st)li.append(toneLine(st));
          X.bookFreshness(h.book).forEach(function(f){if(f.tone!=='ok')li.append(toneLine(f));});
          var dl=h.book.development&&B.phaseLine(h.book.development.phase,h.book.book_number);if(dl)li.append(toneLine(dl));
          actionButton(li,'Open Book '+h.book.book_number+' at this concept',function(){openLeaf({book:h.book.book_number});},'series-open:'+h.book.book_number);
          ul.append(li);});
        wrap.append(el('p','atl-series-kicker','Recorded in Book plans'),ul);
      }else if(cn&&cn.nodeId&&wbs.length){
        wrap.append(el('p','atl-note',(wbs.length===1?'Book '+wbs[0].book_number+'’s working architecture records no reference to this concept':
          'None of the '+wbs.length+' readable working Book architectures records a reference to this concept')+
          (bad.length?'; a Book that could not be read might.':'.')));
      }else if(cn&&!cn.nodeId&&wbs.length){
        wrap.append(el('p','atl-note','Working Book architectures refer only to recorded Architecture nodes, so none can refer to this '+
          M.FACET_SINGULAR[cn.facet].toLowerCase()+' directly.'));
      }
      bad.forEach(function(t){wrap.append(toneLine({tone:'bad',text:t}));});
      if(proj.length){
        var pl=el('ul','atl-series-project');proj.forEach(function(p){pl.append(el('li','atl-tone-'+p.tone,p.text));});
        wrap.append(el('p','atl-series-kicker','Also kept in this project'),pl,
          el('p','atl-note',cn?'Not linked to this concept: nothing records that it refers to these plans, and equal words are not a link.':
            'Nothing records that this working Architecture refers to these plans.'));
      }
      if(!hits.length&&!wbs.length&&!bad.length&&!proj.length){
        wrap.append(el('p','atl-folio-detail','No Book or Series plan is kept for this canvas or project, so nothing here can say how this '+
          (cn?'concept':'Architecture')+' is planned across Books.'));
        wrap.append(el('p','atl-note','Each kind of plan has its own owner: a full Series plan is series_identity.yaml (auteur series validate); '+
          'Series and Book Directions are accepted through auteur series journey; a working Book architecture is developed with '+
          'python -m auteur.series.working_book_architecture. Any of them would be shown here, read-only.'));
      }
      if(d.available)actionButton(wrap,hits.length?'Explore all Series and Book context':'Explore Series and Book context',function(){openLeaf({});},'series-open');
      wrap.append(el('p','atl-note atl-series-status','Read at '+readTime(c)+(c.status==='loading'?'; reading again…':'.')));
      folio.append(wrap);
    }
    function openLeaf(opts){
      var a=document.activeElement;
      if(S.dev&&S.dev.from!==S.focus)S.dev=null;
      S.leaf={from:S.focus,book:opts&&opts.book||null,opener:a&&folio.contains(a)&&a.dataset?a.dataset.key:null,scroll:folio.scrollTop};
      readSeries(true,false);renderFolio();folio.scrollTop=0;focusFolio();
      var from=S.focus&&S.model.byId[S.focus];
      announce('Series and Book context.'+(from?' Back returns to “'+from.title+'”; the atlas keeps your place.':''));
    }
    function closeLeaf(){
      var l=S.leaf;if(!l)return;S.leaf=null;renderFolio();
      folio.scrollTop=l.scroll||0;
      var again=l.opener&&folio.querySelector('[data-key="'+cssEscape(l.opener)+'"]');
      if(again)again.focus({preventScroll:false});else focusFolio();
      var from=S.focus&&S.model.byId[S.focus];
      announce(from?'Back to “'+from.title+'”. Your place in the atlas is unchanged.':'Back to the atlas.');
    }
    function hypothesisButton(parent,from,label,src){
      if(!from||!binding.onDevelop||!src)return;
      var s=M.sourceAnchor(S.model,from.id);if(!s.anchor)return;
      var offered=binding.developOperations?binding.developOperations(s.anchor):['explore'];
      var op=['explore','challenge','explain'].filter(function(o){return offered.indexOf(o)>=0;})[0];if(!op)return;
      var b=actionButton(parent,'Ask your coding agent whether this relates',function(){
        binding.onDevelop({conceptId:from.id,title:from.title,anchor:JSON.parse(JSON.stringify(s.anchor)),precision:s.precision,
          subject:s.subject,quote:s.quote,sourceRef:s.sourceRef,operation:op,draft:X.hypothesisDraft(from.title,label,src)});
      },'series-ask:'+(src.path+'#'+(src.ref||'')));
      b.classList.add('atl-action-quiet');
    }
    function factList(pairs){var dl=el('dl','atl-facts');pairs.forEach(function(p){fact(dl,p[0],p[1]);});return dl;}
    function leafSection(title,note){var sec=el('section','atl-series-owner');sec.setAttribute('aria-label',title);
      sec.append(el('h4','atl-section-title',title));if(note)sec.append(el('p','atl-note',note));folio.append(sec);return sec;}
    function readTime(c){return c&&c.readAt?c.readAt.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',second:'2-digit'}):'';}
    function day(iso){var t=Date.parse(iso);return isNaN(t)?String(iso).slice(0,10):new Date(t).toLocaleDateString([],{year:'numeric',month:'short',day:'numeric'});}
    function renderSeriesLeaf(){
      // The view re-reads whenever the Architecture changed or the last read is old.
      readSeries(false);
      var l=S.leaf,c=S.seriesCtx,d=c&&c.data,from=l.from&&S.model.byId[l.from];
      folio.setAttribute('aria-label','Series and Book context');
      folio.append(el('p','atl-kicker-line','Series and Book context'));
      var recorded=from&&d?X.forNode(d,from.nodeId).length:0;
      folio.append(el('h3','atl-folio-title',recorded?'Plans that record “'+from.title+'”':'Book and Series plans in this canvas and project'));
      if(from&&!recorded)folio.append(el('p','atl-folio-detail','Opened from “'+from.title+'”. '+(d&&X.unreadableBooks(d).length?
        'No readable plan here records a reference to it; a Book that could not be read might.':'No plan here records a reference to it.')));
      var nav=el('div','atl-look');
      var bk=actionButton(nav,from?'← Back to '+from.name:'← Back to the atlas',closeLeaf,'series-back');bk.classList.add('atl-action-primary');
      bk.setAttribute('aria-keyshortcuts','Escape');
      actionButton(nav,'Read again',function(){readSeries(true,true);},'series-reread');
      folio.append(nav);
      var status=!c||c.status==='loading'?(d?'Reading the plans again… (showing the read of '+readTime(c)+')':'Reading the plans…'):c.status==='error'?'Could not read the plans: '+c.error:
        (c.changed?'Changed since you last read them. ':'')+'Read at '+readTime(c)+'.';
      folio.append(el('p','atl-note atl-series-status',status));
      folio.append(el('p','atl-note','Reading a plan here changes nothing. Each plan keeps its own owner, revision and acceptance; a working Book changes only when you apply a revision you reviewed.'));
      if(!d)return;
      renderLeafBooks(d,from,l);renderLeafPlan(d,from);renderLeafDirections(d,from);
      if(d.separate_owners_note)folio.append(el('p','atl-note',d.separate_owners_note));
      var s=d.sources,missing=[];
      if(s.working_books.state==='absent')missing.push('working Book architectures for this canvas');
      if(s.series_plan.state==='absent')missing.push('a Series plan (series_identity.yaml)');
      if(s.series_direction.state==='absent')missing.push('Series or Book Directions');
      if(missing.length)folio.append(el('p','atl-note','Not kept here: '+missing.join(' · ')+'.'));
      var end=el('div','atl-actions');
      var bk2=actionButton(end,from?'← Back to '+from.name:'← Back to the atlas',closeLeaf,'series-back-end');bk2.classList.add('atl-action-primary');
      folio.append(end);
    }
    function renderLeafBooks(d,from,l){
      var wb=d.sources.working_books;if(!wb||wb.state==='absent')return;
      var sec=leafSection('Working Book architectures · this canvas',wb.authority_note);
      if(wb.state==='unreadable'){sec.append(toneLine({tone:'bad',text:'The working Book architectures could not be read ('+wb.reason+'). Nothing from them is shown.'}));return;}
      var list=wb.books.slice().sort(function(a,b){return (b.book_number===l.book)-(a.book_number===l.book)||a.book_number-b.book_number;});
      list.forEach(function(b){
        var det=el('details','atl-series-record');det.dataset.book=String(b.book_number);
        det.open=b.book_number===l.book||list.length===1||!!b.development||!!devFor(b.book_number);
        det.append(el('summary','','Book '+b.book_number+(b.title?' · '+b.title:'')));
        if(b.state!=='working'){det.append(toneLine({tone:'bad',text:'Could not be read ('+b.reason+'). Nothing from it is shown.'}));sec.append(det);return;}
        var chips=el('p','atl-provenance');chips.append(chip('Working · agent proposal · not accepted','proposal'));det.append(chips);
        X.bookFreshness(b).forEach(function(f){det.append(toneLine(f));});
        det.append(factList([['Question',b.question],['Pressure',b.pressure]]));
        if(from){
          var ref=from.nodeId&&(b.references||[]).filter(function(r){return r.node_id===from.nodeId;})[0];
          if(ref){
            var box=el('div','atl-series-about');
            box.append(el('h5','atl-series-subtitle','What Book '+b.book_number+' records about “'+from.title+'”'));
            var st=X.refStanding(ref);if(st)box.append(toneLine(st));
            var ul=el('ul','atl-series-elements');
            var la=b.last_applied,touched=la?la.changed.concat(la.added):[];
            ref.elements.forEach(function(e){var li=el('li','');
              li.append(el('span','atl-series-kind',(X.COLLECTION[e.collection]||M.human(e.collection))+(e.via==='name_source'?' · takes its name from this concept':'')));
              li.append(el('span','atl-series-text',e.text));
              li.append(chip(X.AUTHORITY[e.commitment_authority]||M.human(e.commitment_authority),'proposal'));
              // A Book revision is marked as a change to the working Book, never to the Architecture concept.
              if(touched.indexOf(e.id)>=0)li.append(chip('Changed in working Book revision '+la.revision_number,'book-changed'));
              if(binding.books&&e.collection!=='open_author_decisions'){var dv=actionButton(li,'Develop this element',function(){openDevelop(b.book_number,[e.id],false,from);},'book-dev:'+b.book_number+':'+e.id);
                dv.classList.add('atl-action-quiet');dv.setAttribute('aria-label','Develop this '+(X.COLLECTION[e.collection]||'element').toLowerCase()+' of Book '+b.book_number);}
              ul.append(li);});
            ref.edges.forEach(function(e){var li=el('li','');
              li.append(el('span','atl-series-kind','Typed edge · '+e.source_element+' '+(X.DEPENDENCY[e.dependency]||e.dependency)+' this concept'));
              li.append(el('span','atl-series-text',e.function));ul.append(li);});
            box.append(ul);det.append(box);
          }else det.append(el('p','atl-note','Book '+b.book_number+' records no reference to “'+from.title+'”.'));
        }
        if(b.last_applied)det.append(el('p','atl-note','Working Book revision '+b.last_applied.revision_number+' was applied'+
          (b.last_applied.changed.length?'; it changed '+X.plural(b.last_applied.changed.length,'element'):'')+
          (b.last_applied.added.length?'; it added '+X.plural(b.last_applied.added.length,'element'):'')+
          '. That was a change to this working Book, not to the Architecture.'));
        renderBookDevelopment(det,b,from);
        var others=(b.references||[]).filter(function(r){return !from||r.node_id!==from.nodeId;});
        if(others.length){
          var o=el('div','atl-series-others');
          o.append(el('h5','atl-series-subtitle',(from?'Other Architecture concepts it refers to · ':'Architecture concepts it refers to · ')+others.length));
          var row=el('div','atl-revised-index');
          others.forEach(function(r){var target=conceptForNode(r.node_id),label=target?target.name:(r.title||r.node_id);
            var btn=el('button','atl-index-item',label+(r.present?'':' · no longer recorded'));btn.type='button';
            btn.title=(target?target.title+' · ':'')+X.refSummary(r)+(r.changed_since_book?' · changed since the Book was written':'');
            btn.dataset.key='series-node:'+b.book_number+':'+r.node_id;
            if(target)btn.addEventListener('click',function(){select(target.id,{via:'series'});focusFolio();});else btn.disabled=true;
            row.append(btn);});
          o.append(row,el('p','atl-note','Selecting one shows it in the atlas; the trail keeps the way back.'));det.append(o);
        }
        if(b.open_author_decisions)det.append(el('p','atl-note',X.plural(b.open_author_decisions,'open author decision')+
          ' kept by this Book, each recorded against one of the Architecture’s open questions'+
          (b.freshness==='ready'?'':' as they stood when the Book was written; the Architecture has changed since, so those bindings are not checked here')+
          '. They stay yours to decide.'));
        var src=el('p','atl-provenance');src.append(sourceChip(b.source),chip('Written against request '+String(b.written_against_request||'').slice(0,10)));det.append(src);
        var how=el('details','atl-series-how');how.append(el('summary','','How this plan is changed'));
        how.append(el('p','atl-note','Through its own owner and its reviewed workflow. Choose an element above and Develop it: the Working Book owner prepares '+
          'a request for your coding agent, turns its answer into a review, and changes the Book only when you apply that review. The same owner is '+
          'reachable directly: '+wb.owner_route.replace('<n>',String(b.book_number))+'.'));
        det.append(how);sec.append(det);
      });
    }
    /* Developing a working Book from the concept the author is reading. The Working Book Architecture owner
       runs the whole lifecycle: it prepares the request, validates the coding agent's response into a review,
       and applies only the reviewed request, checking the Book and its sources again at that moment. This
       view shows each step in words and never settles anything itself: no state is assumed after a refused
       operation, and an answer that arrives for another canvas or Book is dropped. The atlas never moves,
       and a Book revision never marks an Architecture concept as changed. */
    function canvasKey(){return binding.getCanvasId?binding.getCanvasId()||'':'';}
    function bookKey(n){return canvasKey()+'#'+n;}
    function bookState(n){S.books=S.books||{};return S.books[bookKey(n)]||null;}
    function bookDraft(n){S.drafts=S.drafts||{};var k=bookKey(n);return S.drafts[k]||(S.drafts[k]={instruction:'',response:''});}
    function bookNote(n,tone,text,phase){S.notes=S.notes||{};S.notes[bookKey(n)]=tone?{tone:tone,text:text,phase:phase||null}:null;}
    function busy(n){S.busy=S.busy||{};return S.busy[bookKey(n)]||null;}
    function setBusy(n,what){S.busy=S.busy||{};S.busy[bookKey(n)]=what;}
    function devFor(n){var d=S.dev;return d&&d.canvas===canvasKey()&&d.book===n?d:null;}
    function readBook(n,force,then){
      if(!binding.books)return;
      var k=bookKey(n),cur=bookState(n);
      if(cur&&cur.status==='loading'){if(then)cur.then=(cur.then||[]).concat([then]);return;}
      if(cur&&cur.status==='ready'&&!force)return;
      var seq=S.bookSeq=(S.bookSeq||0)+1,canvas=canvasKey();
      S.books[k]={status:'loading',data:cur&&cur.data||null,readAt:cur&&cur.readAt,seq:seq,then:then?[then]:[]};
      var call;try{call=Promise.resolve(binding.books.read(n));}catch(error){call=Promise.reject(error);}
      call.then(function(r){
        var mine=S.books[k];if(!mine||mine.seq!==seq)return;
        // An answer for another canvas or Book is not this Book's state.
        if(r.canvasId!==canvas||canvasKey()!==canvas||!r.data||r.data.book_number!==n){delete S.books[k];return;}
        S.books[k]={status:'ready',data:r.data,readAt:new Date(),seq:seq};renderFolio();
        (mine.then||[]).forEach(function(f){f(r.data);});
      },function(error){
        var mine=S.books[k];if(!mine||mine.seq!==seq)return;
        S.books[k]={status:'error',error:error&&error.message||String(error),data:mine.data,readAt:mine.readAt,seq:seq};renderFolio();
      });
    }
    function focusKey(key){global.setTimeout(function(){var t=folio.querySelector('[data-key="'+cssEscape(key)+'"]');
      if(t){t.focus({preventScroll:false});}},0);}
    function openDevelop(n,targets,holistic,from,seed){
      var d=bookDraft(n);
      if(seed&&!d.instruction)d.instruction=seed.instruction||'';
      S.dev={canvas:canvasKey(),book:n,targets:(targets||[]).slice(),holistic:!!holistic,from:from?from.id:null,
        replace:!!(seed&&seed.replace),scope:null,focusPending:true};
      var dev=S.dev;bookNote(n,null);
      readBook(n,true);
      if(!holistic&&dev.targets.length&&binding.books.scope){
        Promise.resolve(binding.books.scope(n,dev.targets)).then(function(r){
          if(S.dev!==dev||r.canvasId!==canvasKey())return;dev.scope=r.data;renderFolio();
        },function(error){if(S.dev!==dev)return;dev.scopeError=error&&error.message||String(error);renderFolio();});
      }
      renderFolio();
      announce('Developing Book '+n+'. Write what should change; preparing calls no model and changes nothing in the Book.');
    }
    function closeDevelop(n){var dev=devFor(n);S.dev=null;renderFolio();
      focusKey(dev&&dev.targets.length===1?'book-dev:'+n+':'+dev.targets[0]:'series-back');}
    function bookElementsOf(n){var st=bookState(n);return st&&st.data&&st.data.elements||[];}
    function nodeName(nodeId){var c=conceptForNode(nodeId);return c?c.title:nodeId;}
    function renderBookDevelopment(det,b,from){
      if(!binding.books)return;
      var n=b.book_number,summary=b.development,dev=devFor(n),st=bookState(n),k=bookKey(n),note=S.notes&&S.notes[k];
      if(!summary&&!dev&&!note)return;
      if(!st)readBook(n,false);
      // The context and this Book's own read can disagree only for a moment: the newer read decides.
      else if(st.status==='ready'&&S.seriesCtx&&S.seriesCtx.readAt&&st.readAt<S.seriesCtx.readAt&&
        ((summary&&summary.request_sha256)||null)!==(st.data.pending&&st.data.phase!=='none'?st.data.pending.request_sha256:null))readBook(n,true);
      st=bookState(n);
      var box=el('section','atl-book-dev');box.setAttribute('aria-label','Developing Book '+n);
      box.append(el('h5','atl-series-subtitle','Developing Book '+n+' · working revision'));
      var data0=st&&st.data;if(note&&note.phase&&data0&&data0.phase!==note.phase)note=null;
      if(note){var np=toneLine(note,'atl-book-note');np.tabIndex=-1;np.dataset.key='book-note:'+n;np.setAttribute('role','status');box.append(np);}
      var data=st&&st.data;
      if(!data){box.append(el('p','atl-note',st&&st.status==='error'?'Could not read Book '+n+'’s revision state: '+st.error:'Reading Book '+n+'’s revision state…'));
        if(st&&st.status==='error')actionButton(box,'Try again',function(){readBook(n,true);},'book-retry:'+n);det.append(box);return;}
      if(data.state==='unreadable'){box.append(toneLine({tone:'bad',text:'Book '+n+' could not be read ('+data.reason+'). Nothing can be prepared for it here.'}));det.append(box);return;}
      if(data.state!=='working'){box.append(el('p','atl-note','Book '+n+' has no working architecture to revise.'));det.append(box);return;}
      if(st.status==='error')box.append(toneLine({tone:'bad',text:'Could not read Book '+n+' again: '+st.error+'. Showing the read of '+readTime(st)+'.'}));
      var phase=data.phase,line=B.phaseLine(phase,n);
      if(line&&!dev)box.append(toneLine(line));
      if(phase==='stale'&&!dev)renderStale(box,n,data,from);
      else if(phase==='awaiting_coding_agent'&&!dev)renderAwaiting(box,n,data,from);
      else if((phase==='review_ready'||phase==='review_blocked')&&!dev)renderBookReview(box,n,data,from);
      if(dev)renderComposer(box,n,b,data,dev,from);
      det.append(box);
    }
    function targetLines(parent,n,data,dev,from){
      var map={};data.elements.forEach(function(e){map[e.id]=e;});
      var card=el('div','atl-book-target');
      card.append(el('p','atl-series-book','Book '+n+(data.book.title?' · '+data.book.title:'')+' · working revision '+data.book.revision_number));
      if(dev.holistic)card.append(el('p','atl-series-line','The whole Book: your coding agent may change any of its elements.'));
      dev.targets.forEach(function(id){var e=map[id];if(!e)return;
        card.append(el('p','atl-series-line',B.elementLabel(map,id)));
        if(e.text)card.append(el('p','atl-series-text',e.text));
        var p=el('p','atl-provenance');p.append(chip('Working · '+(X.AUTHORITY[e.commitment_authority]||M.human(e.commitment_authority||'element')),'proposal'));card.append(p);
        if(from&&from.nodeId)card.append(el('p','atl-note',e.series_refs.indexOf(from.nodeId)>=0?
          'It records a reference to “'+from.title+'”, the concept you came from.':'It records no reference to “'+from.title+'” itself.'));
      });
      X.bookFreshness(data.book).forEach(function(f){if(f.tone!=='ok')card.append(toneLine(f));});
      var ids=el('details','atl-series-how');ids.append(el('summary','','Exact identifiers'));
      ids.append(factList([['Elements',dev.targets.join(', ')||'whole Book'],['Book request',data.book.request_sha256],
        ['Book content',data.book.content_sha256],['Architecture node',from&&from.nodeId||''],['Architecture request',data.book.series_request_sha256]]));
      card.append(ids);parent.append(card);
    }
    function renderComposer(box,n,b,data,dev,from){
      var d=bookDraft(n),busyNow=busy(n);
      var form=el('div','atl-book-compose');
      form.append(el('p','atl-kicker-line',dev.holistic?'Revise the whole Book':'Revise one element'));
      targetLines(form,n,data,dev,from);
      var scope=el('fieldset','atl-book-scope');scope.append(el('legend','','How far may the revision reach?'));
      function radio(value,label,detail){var lab=el('label','atl-book-choice'),r=el('input');r.type='radio';r.name='book-scope-'+n;r.value=value;
        r.checked=value==='holistic'?dev.holistic:!dev.holistic;r.dataset.key='book-scope:'+n+':'+value;
        r.addEventListener('change',function(){if(r.checked){dev.holistic=value==='holistic';renderFolio();}});
        lab.append(r,el('span','',label));scope.append(lab);if(detail)scope.append(el('p','atl-note',detail));}
      if(dev.targets.length){
        var map={};data.elements.forEach(function(e){map[e.id]=e;});
        radio('targeted',dev.targets.length===1?'Only this element':'Only these elements',dev.scope?B.scopeSentence(dev.scope,map)+
          (dev.scope.dependents.length?' They are: '+B.labels(map,dev.scope.dependents).join('; ')+'.':''):dev.scopeError?'Could not check which elements refer to it: '+dev.scopeError:'Checking which elements refer to it…');
      }
      radio('holistic','The whole Book','Use this only when the change cannot stay inside the chosen element. Your coding agent may then change any element of Book '+n+', and the review shows each one.');
      form.append(scope);
      var label=el('label','atl-bookdev-label','What should change?'),ta=el('textarea','atl-book-text');ta.id='atl-book-instruction-'+n;label.htmlFor=ta.id;
      ta.rows=4;ta.maxLength=4000;ta.value=d.instruction;ta.dataset.key='book-instruction:'+n;
      ta.placeholder='For example: make the cost of refusing the count visible inside this mechanism.';
      ta.addEventListener('input',function(){d.instruction=ta.value;});
      form.append(label,ta);
      if(data.pending){
        var rp=el('label','atl-book-choice'),cb=el('input');cb.type='checkbox';cb.checked=!!dev.replace;cb.dataset.key='book-replace:'+n;
        cb.addEventListener('change',function(){dev.replace=cb.checked;});
        rp.append(cb,el('span','',data.phase==='stale'?'Replace the request that no longer matches the Book':'Replace the request that is already waiting'+
          (data.pending.instruction?' (“'+B.clip(data.pending.instruction,80)+'”)':'')+'; it can then no longer be applied'));
        form.append(rp);
      }
      form.append(el('p','atl-note','Preparing calls no model and changes nothing in Book '+n+'. Your coding agent fulfils the request through the Working Book owner; you review what it proposes, and only Apply changes the working Book.'));
      var row=el('div','atl-actions');
      var go=actionButton(row,busyNow==='prepare'?'Preparing…':'Prepare the request for your coding agent',function(){prepareBook(n,dev,from);},'book-prepare:'+n);
      go.classList.add('atl-action-primary');go.disabled=!!busyNow;
      actionButton(row,'Not now',function(){closeDevelop(n);},'book-cancel:'+n);
      if(from&&dev.targets.length===1)askAboutElement(row,from,n,data,dev.targets[0]);
      form.append(row);box.append(form);
    }
    // Investigating instead of revising is a question in the existing coding-agent panel; it is never sent for the author.
    function askAboutElement(parent,from,n,data,id){
      if(!binding.onDevelop)return;
      var s=M.sourceAnchor(S.model,from.id);if(!s.anchor)return;
      var offered=binding.developOperations?binding.developOperations(s.anchor):['explore'];
      var op=['explore','challenge','explain'].filter(function(o){return offered.indexOf(o)>=0;})[0];if(!op)return;
      var e=data.elements.filter(function(x){return x.id===id;})[0];if(!e)return;
      var b=actionButton(parent,'Ask your coding agent about it instead',function(){
        binding.onDevelop({conceptId:from.id,title:from.title,anchor:JSON.parse(JSON.stringify(s.anchor)),precision:s.precision,
          subject:s.subject,quote:s.quote,sourceRef:s.sourceRef,operation:op,
          draft:'Working Book '+n+' records this '+B.kind(e.collection).toLowerCase()+' ('+id+') about “'+from.title+'”: “'+B.clip(e.text,400)+
            '”. Does the working Architecture support it, and what would it imply for “'+from.title+'”? This is a question, not a change.'});
      },'book-ask:'+n+':'+id);
      b.classList.add('atl-action-quiet');
    }
    function prepareBook(n,dev,from){
      var d=bookDraft(n),st=bookState(n),data=st&&st.data,k=bookKey(n),canvas=canvasKey();
      if(busy(n)||!data||data.state!=='working')return;
      if(!d.instruction.trim()){bookNote(n,'bad','Write what should change first. Nothing was prepared.');renderFolio();focusKey('book-instruction:'+n);return;}
      var body={instruction:d.instruction,targets:dev.holistic?[]:dev.targets,holistic:!!dev.holistic,
        expected_book_request_sha256:data.book.request_sha256};
      if(data.pending){if(!dev.replace){bookNote(n,'bad','A request for Book '+n+' is already waiting. Tick “Replace…” to prepare this one instead; nothing was prepared.');
        renderFolio();focusKey('book-replace:'+n);return;}
        body.replace_pending_request_sha256=data.pending.request_sha256;}
      setBusy(n,'prepare');renderFolio();
      var call;try{call=Promise.resolve(binding.books.prepare(n,body));}catch(error){call=Promise.reject(error);}
      call.then(function(r){
        setBusy(n,null);if(r.canvasId!==canvas||canvasKey()!==canvas)return;
        S.books[k]={status:'ready',data:r.data,readAt:new Date(),seq:S.bookSeq=(S.bookSeq||0)+1};
        d.instruction='';if(S.dev===dev)S.dev=null;
        bookNote(n,'ok','Prepared for your coding agent. Nothing in Book '+n+' has changed. Give it the request below, then check for its response.','awaiting_coding_agent');
        readSeries(true,false,true);renderFolio();focusKey('book-check:'+n);
        announce('Request prepared for your coding agent. Nothing in Book '+n+' has changed.');
      },function(error){
        setBusy(n,null);if(error.canvasId&&error.canvasId!==canvasKey())return;
        bookNote(n,'bad','Not prepared: '+(error&&error.message||error)+'. Your words are kept.');
        readBook(n,true);renderFolio();focusKey('book-note:'+n);
      });
    }
    function scopeLine(n,pending,data){
      if(!pending)return '';
      if(pending.mode==='holistic')return 'It may change any element of Book '+n+'.';
      return 'It may change '+B.labels(data.elements,pending.permitted_ids||pending.targets).join('; ')+'. Every other element must stay as it is.';
    }
    function renderAwaiting(box,n,data,from){
      var p=data.pending;
      if(p.instruction)box.append(factList([['You asked',p.instruction],['Scope',scopeLine(n,p,data)]]));
      if(p.stale_response_kept)box.append(toneLine({tone:'warn',text:'A response arrived for an earlier state of this Book and was kept as evidence; it was not reviewed.'}));
      var row=el('div','atl-actions');
      var chk=actionButton(row,'Check for your coding agent’s response',function(){checkResponse(n);},'book-check:'+n);chk.classList.add('atl-action-primary');
      actionButton(row,'Prepare a different request',function(){openDevelop(n,p.targets,p.mode==='holistic',from,{instruction:p.instruction,replace:true});},'book-redo:'+n);
      box.append(row);
      var give=el('details','atl-series-how');give.dataset.key='book-agent:'+n;
      give.append(el('summary','','What to give your coding agent'));
      give.append(el('p','atl-note','The Studio does not run your coding agent. Ask it to fulfil this request; it uses the Working Book owner’s own commands.'));
      var msg=el('textarea','atl-book-text');msg.readOnly=true;msg.rows=7;msg.value=B.agentMessage(data.handoff,n,data.canvas_id,p);
      msg.setAttribute('aria-label','Message for your coding agent');give.append(msg);
      if(data.request){var exact=el('details','atl-series-how');exact.append(el('summary','','The exact request · '+B.shortSha(p.request_sha256)));
        var raw=el('textarea','atl-book-text');raw.readOnly=true;raw.rows=6;raw.value=JSON.stringify(data.request,null,2);
        raw.setAttribute('aria-label','Exact host-agent request');exact.append(raw);give.append(exact);}
      var manual=el('details','atl-series-how');manual.append(el('summary','','Paste its response instead (manual fallback)'));
      var d=bookDraft(n),resp=el('textarea','atl-book-text');resp.rows=4;resp.value=d.response;resp.dataset.key='book-response:'+n;
      resp.setAttribute('aria-label','HostAgentResponse JSON');resp.placeholder='The complete HostAgentResponse JSON for this request.';
      resp.addEventListener('input',function(){d.response=resp.value;});
      var v=actionButton(manual,busy(n)==='complete'?'Checking…':'Validate the response',function(){completeBook(n);},'book-validate:'+n);v.disabled=!!busy(n);
      manual.insertBefore(resp,v);give.append(manual);box.append(give);
    }
    function checkResponse(n){
      var before=bookState(n),was=before&&before.data&&before.data.phase;
      readSeries(true,false,true);
      readBook(n,true,function(data){
        var now=data.phase;
        announce(now===was?(now==='awaiting_coding_agent'?'No response yet. Nothing in Book '+n+' has changed.':'Nothing changed.'):
          (B.phaseLine(now,n)||{text:'Book '+n+' was read again.'}).text);
        if(now!==was)focusKey(now==='review_ready'||now==='review_blocked'?'book-review:'+n:'book-check:'+n);
      });
    }
    function completeBook(n){
      var d=bookDraft(n),k=bookKey(n),canvas=canvasKey(),payload;
      if(busy(n))return;
      try{payload=JSON.parse(d.response);}catch(_){bookNote(n,'bad','The response must be one HostAgentResponse JSON object. Nothing was submitted.');renderFolio();focusKey('book-note:'+n);return;}
      setBusy(n,'complete');renderFolio();
      Promise.resolve(binding.books.complete(n,payload)).then(function(r){
        setBusy(n,null);if(r.canvasId!==canvas||canvasKey()!==canvas)return;
        d.response='';S.books[k]={status:'ready',data:r.data,readAt:new Date(),seq:S.bookSeq=(S.bookSeq||0)+1};
        bookNote(n,null);readSeries(true,false,true);renderFolio();focusKey('book-review:'+n);
        announce((B.phaseLine(r.data.phase,n)||{text:'Response checked.'}).text);
      },function(error){
        setBusy(n,null);if(error.canvasId&&error.canvasId!==canvasKey())return;
        bookNote(n,'bad','The Working Book owner refused the response: '+(error&&error.message||error)+'. Nothing was stored; the request is still open.');
        readBook(n,true);renderFolio();focusKey('book-note:'+n);
      });
    }
    function renderStale(box,n,data,from){
      var p=data.pending;
      box.append(el('p','atl-folio-detail','Why: '+B.staleReason(p)+'.'));
      if(p.instruction)box.append(factList([['You asked',p.instruction],['Scope',scopeLine(n,p,data)]]));
      if(p.completed)box.append(el('p','atl-note','Its review was made against that earlier state, so it is not shown as applicable.'));
      var row=el('div','atl-actions');
      var again=actionButton(row,'Prepare it again against the current Book',function(){
        openDevelop(n,p.targets,p.mode==='holistic',from,{instruction:p.instruction,replace:true});},'book-redo:'+n);
      again.classList.add('atl-action-primary');box.append(row);
    }
    function renderBookReview(box,n,data,from){
      var r=data.review,g=B.reviewDigest(r,data.elements,nodeName),ready=data.phase==='review_ready';
      var sec=el('div','atl-book-review');sec.setAttribute('aria-label','Review of the revision of Book '+n);
      var h=el('h5','atl-series-subtitle','Review · working revision '+g.fromRevision+' → '+g.toRevision);h.tabIndex=-1;h.dataset.key='book-review:'+n;sec.append(h);
      sec.append(factList([['You asked',g.instruction],['Scope',g.mode==='holistic'?'the whole Book':g.permitted.join('; ')]]));
      if(g.unexpected.length){var u=el('div','atl-book-block');u.append(el('p','atl-tone atl-tone-bad','Outside what you allowed — this blocks Apply:'));
        var ul=el('ul','atl-series-elements');g.unexpected.forEach(function(x){ul.append(el('li','',x.text));});u.append(ul);sec.append(u);}
      if(g.changed.length){sec.append(el('p','atl-series-kicker','Changed · '+g.changed.length));
        var cl=el('ul','atl-series-elements');g.changed.forEach(function(c){var li=el('li','');
          li.append(el('span','atl-series-kind',c.label),el('span','atl-note',c.kind+(c.fields.length?' ('+c.fields.join(', ')+')':'')+'.'));
          if(c.before!==null&&c.before!==undefined){li.append(el('span','atl-book-before','Before: '+c.before));li.append(el('span','atl-book-after','After: '+c.after));}
          cl.append(li);});sec.append(cl);}
      if(g.added.length){sec.append(el('p','atl-series-kicker','Added · '+g.added.length));var al=el('ul','atl-series-elements');
        g.added.forEach(function(a){al.append(el('li','',a.label+(a.refersTo.length?' — refers to '+a.refersTo.join('; '):'')));});sec.append(al);}
      if(g.removed.length){sec.append(el('p','atl-series-kicker','Removed · '+g.removed.length));var rl=el('ul','atl-series-elements');
        g.removed.forEach(function(x){rl.append(el('li','',x.label));});sec.append(rl);}
      sec.append(el('p','atl-note',X.plural(g.preserved,'other element')+' stay exactly as they are; the owner compared every element by content.'));
      if(g.reread.length){sec.append(el('p','atl-series-kicker','To re-read · recorded links, not established consequences'));
        var ll=el('ul','atl-series-elements');g.reread.forEach(function(t){ll.append(el('li','',t));});sec.append(ll);}
      if(g.series.length){sec.append(el('p','atl-series-kicker','Architecture concepts these elements cite'));
        var sl=el('ul','atl-series-elements');g.series.forEach(function(t){sl.append(el('li','atl-tone-'+t.tone,t.text));});sec.append(sl);}
      g.decisions.forEach(function(t){sec.append(toneLine({tone:'warn',text:t}));});
      if(g.authority.length)sec.append(factList([['Standing changes',g.authority.join(' ')]]));
      g.unresolved.forEach(function(t){sec.append(el('p','atl-note',t));});
      var ids=el('details','atl-series-how');ids.append(el('summary','','Request identity and baseline'));ids.append(factList(g.identity));sec.append(ids);
      if(g.note)sec.append(el('p','atl-note',g.note));
      var row=el('div','atl-actions');
      if(ready){var ap=actionButton(row,busy(n)==='apply'?'Applying…':'Apply this revision to working Book '+n,function(){applyBook(n,r.request_sha256);},'book-apply:'+n);
        ap.classList.add('atl-action-primary');ap.disabled=!!busy(n);
        row.append(el('p','atl-note','Applying changes this working Book only. It accepts nothing, and the Architecture, the Series plan and the Directions stay as they are.'));}
      else{var wide=B.widenedTargets(r,data.elements);
        if(wide.length&&r.mode!=='holistic'){var w=actionButton(row,'Prepare again, allowing those elements too',function(){
          openDevelop(n,wide,false,from,{instruction:r.instruction,replace:true});},'book-widen:'+n);w.classList.add('atl-action-primary');}
        actionButton(row,'Prepare again for the whole Book',function(){openDevelop(n,[],true,from,{instruction:r.instruction,replace:true});},'book-holistic:'+n);}
      actionButton(row,'Prepare a different request',function(){openDevelop(n,data.pending.targets,data.pending.mode==='holistic',from,{instruction:r.instruction,replace:true});},'book-redo:'+n);
      sec.append(row);box.append(sec);
    }
    function applyBook(n,sha){
      var k=bookKey(n),canvas=canvasKey();
      if(busy(n))return;
      setBusy(n,'apply');renderFolio();
      var call;try{call=Promise.resolve(binding.books.apply(n,sha));}catch(error){call=Promise.reject(error);}
      call.then(function(r){
        setBusy(n,null);if(r.canvasId!==canvas||canvasKey()!==canvas)return;
        var data=r.data,a=data.application||{},la=data.book&&data.book.last_applied;
        S.books[k]={status:'ready',data:data,readAt:new Date(),seq:S.bookSeq=(S.bookSeq||0)+1};
        if(a.result==='already_applied')bookNote(n,'note','That revision was already applied. Nothing changed.','none');
        else{var what=la?[].concat(la.changed.length?['changed '+B.labels(data.elements,la.changed).join('; ')]:[],
            la.added.length?['added '+B.labels(data.elements,la.added).join('; ')]:[],la.removed.length?['removed '+la.removed.join(', ')]:[]).join(', and '):'';
          bookNote(n,'ok','Applied to working Book '+n+', now working revision '+data.book.revision_number+(what?': '+what:'')+
            '. Only this working Book changed. The Architecture and its concepts, the Series plan and the Directions are unchanged, and nothing was accepted.','none');}
        readSeries(true,false,true);renderFolio();focusKey('book-note:'+n);
        announce(a.result==='already_applied'?'Already applied; nothing changed.':'Applied to working Book '+n+'. Only the working Book changed; the atlas is unchanged.');
      },function(error){
        setBusy(n,null);if(error.canvasId&&error.canvasId!==canvasKey())return;
        bookNote(n,'bad','Not applied: '+(error&&error.message||error)+'. Working Book '+n+' is unchanged.');
        readBook(n,true);readSeries(true,false,true);renderFolio();focusKey('book-note:'+n);
      });
    }
    function renderLeafPlan(d,from){
      var plan=d.sources.series_plan;if(!plan||plan.state==='absent')return;
      var sec=leafSection('Series plan · this project',plan.authority_note);
      if(plan.state==='invalid'||plan.state==='unreadable'){sec.append(toneLine({tone:'bad',text:plan.path+' could not be read as a Series plan ('+plan.reason+'). Nothing from it is shown.'}));return;}
      var chips=el('p','atl-provenance');chips.append(chip('Author-declared plan · no acceptance record'),sourceChip(plan.source));sec.append(chips);
      var arc=plan.global_arc||{};
      sec.append(factList([['Series',plan.title+' · '+M.human(plan.series_type)],['Core question',plan.core_question],
        ['Global arc',[arc.beginning,arc.midpoint,arc.ending].filter(Boolean).join(' → ')]]));
      var label=function(t){return t+' in the Series plan “'+plan.title+'”';};
      var books=el('details','atl-series-record');books.append(el('summary','','Book plans · '+plan.books.length));
      plan.books.forEach(function(b){var det=el('details','atl-series-sub');
        det.append(el('summary','','Book '+b.book_number+' · '+b.title+' · '+M.human(b.series_function)));
        det.append(factList([['Core answer',b.core_answer],['Reader experience',b.target_experience],['Scope',M.human(b.scope)],
          ['Carries',b.series_threads_carried],['Sets up',b.required_setups],['Pays off',b.required_payoffs]]));
        var p=el('p','atl-provenance');p.append(sourceChip(b.source));det.append(p);
        hypothesisButton(det,from,label('Book '+b.book_number+' plan “'+b.title+'”'),b.source);books.append(det);});
      sec.append(books);
      if(plan.setups.length||plan.payoffs.length){
        var sp=el('details','atl-series-record');sp.open=true;
        sp.append(el('summary','','Setups and payoffs · '+X.plural(plan.setups.length,'setup')+', '+X.plural(plan.payoffs.length,'payoff')));
        var byId={};plan.payoffs.forEach(function(p){byId[p.id]=p;});var used={};
        var ul=el('ul','atl-series-elements');
        plan.setups.forEach(function(s){var li=el('li','');
          li.append(el('span','atl-series-kind','Setup · introduced in Book '+s.book_introduced+' · payoff expected by Book '+s.expected_payoff_by_book+' · '+M.human(s.status)));
          li.append(el('span','atl-series-text',s.description));
          var pay=s.payoff_id&&byId[s.payoff_id];if(pay)used[pay.id]=true;
          li.append(el('span','atl-series-line',pay?'The plan records its payoff in Book '+pay.book+': '+pay.description:
            s.payoff_id?'Names payoff '+s.payoff_id+', which the plan does not record.':'No payoff recorded for it.'));
          if(s.reason_abandoned)li.append(el('span','atl-series-line','Abandoned: '+s.reason_abandoned));
          li.append(sourceChip(s.source));hypothesisButton(li,from,label('the setup “'+M.shorten(s.description,80)+'”'),s.source);ul.append(li);});
        plan.payoffs.filter(function(p){return !used[p.id];}).forEach(function(p){var li=el('li','');
          li.append(el('span','atl-series-kind','Payoff in Book '+p.book+' · for setup '+p.setup_id),el('span','atl-series-text',p.description),sourceChip(p.source));ul.append(li);});
        sp.append(ul);sec.append(sp);
      }
      if(plan.mysteries.length){var my=el('details','atl-series-record');my.append(el('summary','','Mysteries · '+plan.mysteries.length));
        var mu=el('ul','atl-series-elements');plan.mysteries.forEach(function(m){var li=el('li','');
          li.append(el('span','atl-series-kind','Introduced in Book '+m.introduced_book+' · payoff expected in Book '+m.expected_payoff_book+
            (m.actual_payoff_book?' · paid off in Book '+m.actual_payoff_book:'')),el('span','atl-series-text',m.question),sourceChip(m.source));
          hypothesisButton(li,from,label('the mystery “'+M.shorten(m.question,80)+'”'),m.source);mu.append(li);});my.append(mu);sec.append(my);}
      if(plan.thematic_arcs.length){var th=el('details','atl-series-record');th.append(el('summary','','Thematic progression · '+plan.thematic_arcs.length));
        plan.thematic_arcs.forEach(function(t){var dl=el('dl','atl-facts');
          Object.keys(t.progression).forEach(function(k){fact(dl,'Book '+k,t.progression[k]);});
          th.append(el('p','atl-series-book',t.theme),dl);var p=el('p','atl-provenance');p.append(sourceChip(t.source));th.append(p);
          hypothesisButton(th,from,label('the thematic arc “'+t.theme+'”'),t.source);});sec.append(th);}
      var dv=plan.derived;
      if(dv){var der=el('details','atl-series-record atl-series-derived');der.append(el('summary','','Derived from this plan · not stored'));
        der.append(el('p','atl-note',dv.note+' An edge reads “source affects target”.'));
        var eu=el('ul','atl-series-elements');
        dv.edges.forEach(function(e){eu.append(el('li','',e.source_id+' '+(X.DEPENDENCY[e.type]||e.type)+' '+e.target_id+
          (e.origin==='declared'?' · declared in the plan':' · derived from the plan')));});
        der.append(eu);
        if(dv.setup_payoff_checks.length){var cu=el('ul','atl-series-elements');
          dv.setup_payoff_checks.forEach(function(k){cu.append(el('li','atl-tone-'+(k.severity==='ERROR'?'bad':'warn'),k.explanation+' ('+k.id+')'));});
          der.append(el('p','atl-series-kicker','Setup and payoff checks'),cu);}
        else der.append(el('p','atl-note','The setup and payoff check reports nothing.'));
        sec.append(der);}
      sec.append(el('p','atl-note',d.architecture_link.statement));
    }
    function renderLeafDirections(d,from){
      var dir=d.sources.series_direction;if(!dir||dir.state==='absent')return;
      var sec=leafSection('Series and Book Directions · this project',dir.authority_note);
      if(dir.state==='unreadable'){sec.append(toneLine({tone:'bad',text:'The Series and Book Directions could not be read ('+dir.reason+'). Nothing from them is shown.'}));return;}
      var ser=dir.series||{};
      if(ser.state==='accepted'){
        var chips=el('p','atl-provenance');
        chips.append(chip('Accepted · revision '+ser.revision+(ser.accepted_by?' · by '+ser.accepted_by:'')+(ser.accepted_at?' · '+day(ser.accepted_at):''),'accepted'),sourceChip(ser.source));
        sec.append(chips,factList([['Series Direction',ser.title],['Promise',ser.promise],['Pressure',ser.pressure],['Open question',ser.open_question]]));
        var cu=el('ul','atl-series-elements');
        ser.commitments.forEach(function(k){var li=el('li','');
          li.append(el('span','atl-series-kind','Commitment · '+k.commitment_id+' · '+k.scope),el('span','atl-series-text',k.statement),sourceChip(k.source));
          hypothesisButton(li,from,'the accepted Series commitment “'+k.commitment_id+'”',k.source);cu.append(li);});
        sec.append(el('p','atl-series-kicker','Accepted commitments'),cu);
      }else if(ser.state==='unverified')sec.append(toneLine({tone:'bad',text:ser.path+': '+ser.reason}));
      else sec.append(el('p','atl-note','No accepted Series Direction.'));
      (dir.books||[]).forEach(function(b){
        var det=el('details','atl-series-record');
        det.append(el('summary','','Book '+b.book_number+' Direction'+(b.title?' · '+b.title:'')+(b.state==='accepted'?' · accepted revision '+b.revision:'')));
        if(b.state!=='accepted'){det.append(toneLine({tone:'bad',text:b.path+': '+b.reason}));sec.append(det);return;}
        // A Direction accepted against an older or unverified Series Direction opens, so the warning is seen.
        if(b.freshness!=='current')det.open=true;
        var chips=el('p','atl-provenance');chips.append(chip('Accepted · revision '+b.revision+(b.accepted_at?' · '+day(b.accepted_at):''),'accepted'),sourceChip(b.source));
        det.append(chips,toneLine(X.directionBookFreshness(b)));
        det.append(factList([['Core answer',b.core_answer],['Reader experience',b.target_experience],['Want',b.want],['Stakes',b.stakes],
          ['Serves Series commitments',b.series_commitment_ids]]));
        hypothesisButton(det,from,'the accepted Book '+b.book_number+' Direction “'+b.title+'”',b.source);sec.append(det);
      });
      sec.append(el('p','atl-note',X.proposalNote(dir)));
      sec.append(el('p','atl-note',d.architecture_link.statement));
    }
    /* What is waiting in the Studio's own workflow, stated where the author is looking. */
    function renderWorking(){
      var w=binding.getWorkingState?binding.getWorkingState():null;if(!w||!w.kind)return;
      var box=el('div','atl-working atl-working-'+w.kind);
      box.append(el('p','atl-working-text',w.text));
      if(w.action&&binding.onShowWorking)actionButton(box,w.action,function(){binding.onShowWorking(w.kind);},'working');
      folio.append(box);
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
          var where=ownerName(other);if(where)b.append(el('span','atl-rel-owner',where));
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
      var revised=revisedSummary();if(revised)folio.append(revised);
      if(S.narrative)renderStructureFolio();
      // Landmarks: the most connected ideas of each kind, by count of documented relationships.
      var marks=el('section','atl-landmarks');
      marks.append(el('h4','atl-section-title',S.narrative?'Most connected · documented relationships':'Landmarks · most documented relationships'));
      if(S.narrative)marks.append(el('p','atl-note','A count of documented relationships measures connectivity, not importance.'));
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
      if(X)renderSeriesSection(null);
      var how=el('ul','atl-how');
      ['Bands hold kinds of narrative idea; story time runs left to right in recorded phase order, one hairline per phase, Books shaded in turn.',
       'Across, a concept sits near the phases it is recorded with: directly, through its genre, or through its recorded neighbours. Concepts with no such record are spread evenly. Nearness alone is never a relationship.',
       S.narrative?'Threads are recorded proposal relationships, coloured by the kind of idea they reach. With Story structure on, a larger genre mark has a larger role in its contract, a framed mark is a recorded structural parent, and size no longer counts relationships.':
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
        .concat(S.narrative?['With Story structure on, selecting a genre also marks the role each phase records for it, in place; the folio lists every phase in story order with its sources.']:[])
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
    // Recorded story structure at rest: genre roles from their contracts and recorded structural parents.
    function renderStructureFolio(){
      var model=S.model,s=S.structure,wrap=el('section','atl-structure');
      wrap.append(el('h4','atl-section-title','Recorded story structure'));
      var order=['governing','primary','supporting','secondary','tertiary','local'],roles={};
      Object.keys(s.roles).forEach(function(id){var r=s.roles[id].role;(roles[r]=roles[r]||[]).push(id);});
      Object.keys(roles).sort(function(a,b){var x=order.indexOf(a),y=order.indexOf(b);return (x<0?99:x)-(y<0?99:y)||a.localeCompare(b);}).forEach(function(r){
        var row=el('div','atl-landmark-row');row.append(el('span','atl-landmark-kind atl-facet-genres',M.capital(M.human(r))+' genre'+(roles[r].length>1?'s':'')));
        roles[r].forEach(function(id){row.append(markButton(model.byId[id],'genres',s.roles[id].sourceRef));});
        wrap.append(row);
      });
      var parents=Object.keys(s.contains).sort(function(a,b){return s.contains[b].length-s.contains[a].length||a.localeCompare(b);});
      if(parents.length){
        var row=el('div','atl-landmark-row');row.append(el('span','atl-landmark-kind atl-facet-structure','Structural parents'));
        parents.forEach(function(id){var b=markButton(model.byId[id],model.byId[id].facet,'contains '+s.contains[id].length);
          b.querySelector('.atl-landmark-count').textContent='contains '+s.contains[id].length;row.append(b);});
        wrap.append(row);
      }
      if(!Object.keys(s.roles).length&&!parents.length)wrap.append(el('p','atl-note','This proposal records no genre roles or structural parents.'));
      wrap.append(el('p','atl-note','Roles come from each genre contract'+(parents.length?' and parents from recorded parent links':'')+'; these are the agent proposal’s, not author decisions.'+
        (parents.length?' The atlas frames a parent but does not size or rank it as governing; what a parent link means for the story is in the proposal’s own words.':'')));
      folio.append(wrap);
      // An interpretation that names two or more of the role-bearing genres speaks to the roles themselves.
      var seen={},about=[];
      Object.keys(s.roles).forEach(function(id){(s.interpretations[id]||[]).forEach(function(it){seen[it.id]=(seen[it.id]||0)+1;if(seen[it.id]===2)about.push(it);});});
      renderInterpretations(about,'Agent interpretations about these roles');
    }
    function markButton(cn,facet,note){
      var b=el('button','atl-landmark atl-facet-'+facet);b.type='button';b.title=cn.title+(note?' · '+note:'');
      b.append(el('span','atl-landmark-name',cn.name),el('span','atl-landmark-count',''));
      b.setAttribute('aria-label',cn.title+(note?', '+note:''));b.dataset.id=cn.id;
      b.addEventListener('click',function(){select(cn.id,{via:'atlas'});focusFolio();});
      b.addEventListener('focus',refreshEmphasis);b.addEventListener('blur',function(){global.setTimeout(refreshEmphasis,0);});
      return b;
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
      structureTool.setAttribute('aria-pressed',String(S.narrative));root.dataset.narrative=S.narrative?'on':'off';
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
      // Escape first closes the read-only Series and Book context, back to the concept it was opened from.
      if(S.leaf&&!(e.target.closest&&e.target.closest('details[open] summary'))){e.preventDefault();closeLeaf();return;}
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
      S.focus=null;S.hood=null;S.comp=null;S.trail=[];S.depth=1;S.sides={};S.restCam=null;S.atlasCam=null;S.tw=null;S.time=null;
      S.mode='atlas';S.mix=0;S.lastFocus=null;S.userCam=false;S.travelling=false;stage.style.height='';
      root.classList.remove('atl-focused','atl-examining','atl-deep','atl-travelling');
      lensbar.hidden=true;fitHood.hidden=true;compass.replaceChildren();
    }
    function update(){
      var candidate=binding.getCandidate(),sha=binding.getRequestSha();
      if(S.model&&sha===S.sha&&candidate===S.candidateRef)return;
      // The same request SHA is the same recorded proposal: a re-read (for example while a revision request
      // is prepared) keeps the author's place and announces nothing.
      if(S.model&&sha&&sha===S.sha&&candidate&&(candidate.nodes||[]).length){S.candidateRef=candidate;return;}
      var hadFocus=!!S.focus,prevModel=S.model,prevAtlas=S.atlas,prevSha=S.sha,keepFocus=S.focus,keepDepth=S.depth;
      var keepExamine=S.mode==='constellation',keepTrail=S.trail.slice(),keepCam=S.userCam&&S.cam?Object.assign({},S.cam):null;
      // Book freshness is measured against the working Architecture, so a new one is read again.
      var keepLeaf=S.leaf;S.leaf=null;if(sha!==prevSha){S.seriesStale=true;S.books={};}
      var ctx=binding.getRevisionContext?binding.getRevisionContext():null;
      var revised=!!(prevModel&&ctx&&ctx.fromSha===prevSha&&ctx.toSha===sha);
      S.candidateRef=candidate;clearExploration();S.revision=null;
      if(!candidate||!(candidate.nodes||[]).length){S.model=null;S.atlas=null;S.sha=sha;
        buildEmpty();syncChrome();renderFolio();renderTrail();return;}
      var v=measureView();
      var keptLayout=false;
      try{S.model=M.buildModel(candidate,sha);S.structure=M.narrativeStructure(S.model);
        // A revision that leaves story order, scopes and every concept's place of belonging unchanged keeps
        // the atlas the author was reading: concepts stay where they were and threads and words change.
        // Anything else the layout is computed from needs a new layout. The author can always ask for one.
        keptLayout=!!(revised&&prevAtlas&&M.layoutBasis(prevModel)===M.layoutBasis(S.model));
        S.atlas=keptLayout?prevAtlas:M.layoutAtlas(S.model,{aspect:v.width/v.height,view:v});}
      catch(error){S.model=null;S.atlas=null;buildEmpty('The atlas could not be drawn: '+error.message);syncChrome();renderFolio();renderTrail();return;}
      S.sha=sha;S.pos={};Object.keys(S.atlas.positions).forEach(function(id){S.pos[id]={x:S.atlas.positions[id].x,y:S.atlas.positions[id].y};});
      // An applied revision of the Architecture the author was reading: compare by recorded identity, mark
      // what changed, and keep the selected concept when the revision still records it.
      var kept=false;
      if(revised){
        S.revision={delta:M.revisionDelta(prevModel,S.model),requestedChange:ctx.requestedChange||null,fromSha:prevSha,toSha:sha,prev:prevModel,keptLayout:keptLayout};
        if(keepFocus&&S.model.byId[keepFocus]){S.pending={focus:keepFocus,depth:keepDepth,examine:keepExamine,
          trail:keepTrail.filter(function(id){return !!S.model.byId[id];}),camera:keptLayout?keepCam:null};kept=true;
          if(keepLeaf&&keepLeaf.from===keepFocus)S.leaf=keepLeaf;}
      }
      empty.hidden=true;buildScene();syncRevisionMarks();syncChrome();applyStates();syncVerbs();syncTethers();renderTrail();
      if(S.shown&&stage.clientWidth){S.sizedOnce=true;S.paintedView={width:v.width,height:v.height};fitAtlas(false);applyPending();}
      renderFolio();
      if(revised){var d=S.revision.delta,n=Object.keys(d.touched).length,was=keepFocus&&prevModel.byId[keepFocus];
        var now=kept?S.model.byId[keepFocus]:null,moved=now&&M.positional(now)&&now.recordTitle!==was.recordTitle;
        announce('Your revision was applied to the working Architecture. '+
          (n?n+' concept'+(n===1?'':'s')+' changed and '+(n===1?'is':'are')+' marked in the atlas. ':
            'No concept or relationship drawn in the atlas changed'+(d.summaryChanged?'; the Architecture summary did. ':'. '))+
          (moved?'The entry at the same position is selected; it now reads “'+now.title+'”, and a list entry is identified only by its position. ':
            now?'“'+now.title+'” is still selected. ':was?'“'+was.title+'” is no longer recorded, so the whole atlas is shown. ':'')+
          (keptLayout?'Every concept kept its place. ':'Story order, scope or the recorded concepts changed, so the atlas was laid out again. ')+
          'Accepted story is unchanged.');}
      else if(hadFocus)announce('The working Architecture changed; the atlas was redrawn and your previous focus cleared. The atlas itself saves nothing.');
    }
    function applyPending(){
      var p=S.pending;S.pending=null;
      if(p&&p.focus&&S.model&&S.model.byId[p.focus]){
        var keep=S.reduced;S.reduced=true;select(p.focus,{via:'atlas',depth:p.depth===2?2:1,focusStar:false});
        if(p.examine)examine();
        if(p.trail&&p.trail.length&&p.trail[p.trail.length-1]===p.focus){S.trail=p.trail;renderTrail();}
        if(p.camera&&S.mode==='atlas'){S.cam=p.camera;S.userCam=true;paint();}
        S.reduced=keep;syncChrome();
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
      var working=JSON.stringify(binding.getWorkingState?binding.getWorkingState():null);
      if(inspector!==S.inspectorOpen||working!==S.workingSig){S.inspectorOpen=inspector;S.workingSig=working;if(!first)renderFolio();}
      if(built&&stage.clientWidth)refit();
    }
    function hide(){S.shown=false;root.hidden=true;}
    syncChrome();
    var api={update:update,show:show,hide:hide,select:function(id,o){select(id,Object.assign({via:'atlas'},o||{}));},
      returnToAtlas:returnToAtlas,deeper:deeper,setTreatment:setTreatment,examine:examine,leaveConstellation:leaveConstellation,
      setReducedMotion:function(on){S.reduced=!!on;syncChrome();},
      fitAtlas:function(){fitAtlas(false);settle();},
      metrics:function(){return S.metrics;},
      setNarrative:setNarrative,
      // Back to the atlas where the author left it: keyboard focus on the selected concept, or the folio.
      returnFocus:function(){var top=root.getBoundingClientRect().top;
        if(top<0||top>global.innerHeight*0.5)root.scrollIntoView({block:'start'});var id=S.focus,b=id&&starEls[id];
        if(b){setRoving(id);b.focus({preventScroll:true});}else focusFolio();},
      snapshot:function(){return {mode:S.mode,treatment:activeTreatment(),research:S.research,focus:S.focus,depth:S.depth,trail:S.trail.slice(),
        narrative:S.narrative,book:{dev:S.dev?{book:S.dev.book,targets:S.dev.targets.slice(),holistic:S.dev.holistic}:null},series:{leaf:S.leaf?{from:S.leaf.from,book:S.leaf.book}:null,status:S.seriesCtx?S.seriesCtx.status:null,
          version:S.seriesCtx&&S.seriesCtx.data?S.seriesCtx.data.version:null,changed:!!(S.seriesCtx&&S.seriesCtx.changed)},revision:S.revision?{keptLayout:S.revision.keptLayout,touched:Object.keys(S.revision.delta.touched),
          reworded:S.revision.delta.reworded.map(function(x){return x.id;}),relationsAdded:S.revision.delta.relationsAdded.map(function(r){return r.sourceRef;}),
          relationsRemoved:S.revision.delta.relationsRemoved.map(function(r){return r.sourceRef;}),removed:S.revision.delta.removed.map(function(x){return x.id;})}:null,storyTime:S.time?{id:S.time.id,phases:S.time.pathway.phases.map(function(p){return {phase:p.phase,status:p.status,
          role:p.phaseRole&&p.phaseRole.role,sources:p.evidence.map(function(e){return e.sourceRef;}),relations:p.relations.slice(),parallel:p.parallel.slice()};})}:null,
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
