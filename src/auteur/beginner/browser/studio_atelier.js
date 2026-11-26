/* Living Narrative Atelier — experimental visual study stage (opt-in via ?atelier).
   A is the world: a stable, information-rich atlas of the working Architecture in which selecting a
   concept brings its recorded relationships forward in place; nothing moves and the view is kept.
   B is the magnifying glass: an explicit Focused Constellation that recomposes one neighbourhood for
   close reading and returns to the atlas as it was left. C (contextual unfolding) survives only as a
   research comparison (?atelier=C). Presentation only: layout, camera and focus live in memory;
   nothing is saved or accepted. */
(function(global,document){
  'use strict';
  var M=global.AuteurStudioAtelierModel,X=global.AuteurAtelierSeries,B=global.AuteurAtelierBook,I=global.AuteurAtelierImpact,Q=global.AuteurAtelierQuestions,SVG='http://www.w3.org/2000/svg';
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
      narrative:!!(binding.initial&&binding.initial.narrative),structure:null,time:null,seriesCtx:null,leaf:null,
      // Open questions of the working Architecture: the list (qlist) and one question read in the folio (qv).
      qlist:false,qv:null,qs:null,questionsStale:true};

    /* ---------- Static frame ---------- */
    root.replaceChildren();root.classList.add('atl');
    var bar=el('header','atl-bar');
    var heading=el('div','atl-heading');
    heading.append(el('span','atl-eyebrow','Working Architecture · noncanonical'),
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
    // The coding-agent desk: the question, its answer and any revision review, beside the concept they examine.
    // The studio moves its panel and review in here while the desk is open, and back to the Studio otherwise.
    var desk=el('section','atl-desk');desk.hidden=true;desk.setAttribute('aria-label','Coding-agent desk for the concept you are examining');
    var deskBar=el('div','atl-desk-bar');var deskBack=el('button','atl-desk-back','← Back to the atlas');deskBack.type='button';
    var deskTitle=el('span','atl-desk-title');deskBar.append(deskBack,deskTitle);
    var deskNote=el('p','atl-desk-note');deskNote.setAttribute('role','status');desk.append(deskBar,deskNote);
    deskBack.addEventListener('click',function(){api.returnFocus();});
    function setDeskNote(text){deskNote.textContent=text||'';}
    body.append(stage,folio,desk);
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
      // Choosing a concept leaves the question reading, the list and the opportunities; the concept's folio takes the place.
      S.qv=null;S.qlist=false;if(S.opp)S.opp.open=false;
      if(S.leaf&&S.leaf.from!==id)S.leaf=null;
      if(S.impactReturn&&S.impactReturn.concept!==id)S.impactReturn=null;
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
      var writing=!!(S.leaf&&(S.dev||(S.discovery&&!S.discovery.handedOff)));
      if(root.classList.contains('atl-writing')!==writing){root.classList.toggle('atl-writing',writing);
        folio.setAttribute('data-desk',writing?'writing':'reading');}
      var active=document.activeElement,key=active&&folio.contains(active)&&active.dataset?active.dataset.key:null;
      var onTitle=!!(active&&folio.contains(active)&&active.classList.contains('atl-folio-title')),top=folio.scrollTop;
      // A field the author is typing in survives a re-render as the same element: its words, caret and
      // scroll stay exactly where they were, whatever finishes reading in the meantime.
      var typing=key&&active.tagName==='TEXTAREA'&&!active.readOnly?active:null;
      var caret=typing?[typing.selectionStart,typing.selectionEnd,typing.selectionDirection,typing.scrollTop]:null;
      // Disclosures the author opened stay open across a re-render; a step may ask for one to open once.
      var opened={};folio.querySelectorAll('details[data-key]').forEach(function(x){opened[x.dataset.key]=x.open;});
      renderFolioContent();
      var force=S.openDetails||{};S.openDetails=null;
      folio.querySelectorAll('details[data-key]').forEach(function(x){var k=x.dataset.key;
        if(force[k])x.open=true;else if(opened[k]!==undefined)x.open=opened[k];});
      if(S.folioFor!==S.focus){S.folioFor=S.focus;folio.scrollTop=0;}
      // A re-render under the reader (for example when plans finish reading) keeps the title focused.
      if(onTitle&&!key){var h=folio.querySelector('h3');if(h){h.tabIndex=-1;h.focus({preventScroll:true});folio.scrollTop=top;}}
      if(key){var again=folio.querySelector('[data-key="'+cssEscape(key)+'"]');
        if(again&&typing&&again.tagName==='TEXTAREA'){again.replaceWith(typing);again=typing;}
        if(again){again.focus({preventScroll:true});
          if(again===typing){try{typing.setSelectionRange(caret[0],caret[1],caret[2]);}catch(_){}typing.scrollTop=caret[3];}}
        else focusFolio();}
      // A composer just opened takes the keyboard once it is drawn, after any focus a re-render restores.
      // A note just focused after Apply stays in view while the plans finish reading again.
      if(S.revealKey){var rk=folio.querySelector('[data-key="'+cssEscape(S.revealKey)+'"]');
        if(rk&&document.activeElement===rk)reveal(rk);if(S.seriesCtx&&S.seriesCtx.status!=='loading')S.revealKey=null;}
      var dv=S.dev,field=dv&&dv.focusPending&&folio.querySelector('[data-key="book-instruction:'+dv.book+'"]');
      if(field){dv.focusPending=false;field.focus({preventScroll:false});
        if(dv.caretTop){dv.caretTop=false;try{field.setSelectionRange(0,0);}catch(_){}field.scrollTop=0;}}
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
      // One question read in the folio, or the list of all of them, takes the folio while it is open. The atlas and
      // the focused concept beneath it are unchanged; Back returns to exactly where the author was.
      if(S.opp&&S.opp.open&&Q)return renderOpportunities();
      if(S.qv&&Q)return renderQuestionView();
      if(S.leaf&&X)return renderSeriesLeaf();
      if(S.qlist&&Q)return renderQuestionList();
      if(!S.focus)return renderAtlasFolio(status);
      var cn=S.model.byId[S.focus],model=S.model,examining=S.mode==='constellation';
      folio.setAttribute('aria-label','Reading of '+cn.title);
      if(examining)folio.append(el('p','atl-mode-chip','Focused constellation · close reading'));
      folio.append(el('p','atl-kicker-line atl-facet-'+cn.facet,M.FACET_SINGULAR[cn.facet]+(cn.role?' · '+M.human(cn.role):'')));
      folio.append(el('h3','atl-folio-title'+(cn.title.length>90?' is-long':''),cn.title));
      if(S.impactReturn&&S.impactReturn.concept===cn.id){var ret=el('div','atl-look');
        actionButton(ret,'← Back to the Books that cite it',function(){var r=S.impactReturn;S.impactReturn=null;openLeaf({impact:true});
          if(r.book)showBookEvidence(r.book);},'impact-return');folio.append(ret);}
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
      if(Q&&binding.getArchitectureQuestions)renderQuestionsEntry();
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
      var books=impactLine();if(books)wrap.append(books);
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
      // A Book or Series read may have changed what the Books record about the questions, so those are read again too.
      if(force)S.questionsStale=true;
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
          (bad.length?'; a Book that could not be read might.':'. That does not show that no Book depends on it.')));
      }else if(cn&&!cn.nodeId&&wbs.length){
        wrap.append(el('p','atl-note','Working Book architectures refer only to recorded Architecture nodes, so none can refer to this '+
          M.FACET_SINGULAR[cn.facet].toLowerCase()+' directly.'));
      }
      // Said for a concept; the atlas reading's Working Books line already counts unreadable Books.
      if(cn)bad.forEach(function(t){wrap.append(toneLine({tone:'bad',text:t}));});
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
      // A Book opened from an open question remembers that question, and Back returns to it.
      S.leaf={from:S.focus,book:opts&&opts.book||null,impact:!!(opts&&opts.impact),opener:a&&folio.contains(a)&&a.dataset?a.dataset.key:null,scroll:folio.scrollTop,
        returnQuestion:opts&&opts.question||null};
      S.qv=null;S.qlist=false;if(S.opp)S.opp.open=false;
      readSeries(true,false);renderFolio();folio.scrollTop=0;focusFolio();
      var from=S.focus&&S.model.byId[S.focus];
      announce((S.leaf.impact?'Working Books after the Architecture changes.':'Series and Book context.')+
        (S.leaf.returnQuestion?' Back returns to the open question.':
        from?' Back returns to “'+from.title+'”; the atlas keeps your place.':' Back returns to the atlas; it keeps your place.'));
    }
    function closeLeaf(){
      var l=S.leaf;if(!l)return;S.leaf=null;
      if(l.returnQuestion){S.qv=l.returnQuestion;renderFolio();folio.scrollTop=l.returnQuestion.ownScroll||0;focusFolio();
        announce('Back to the open question. Nothing was changed.');return;}
      renderFolio();
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
      folio.append(el('h3','atl-folio-title',l.impact?'Working Books after the Architecture changes':
        recorded?'Plans that record “'+from.title+'”':'Book and Series plans in this canvas and project'));
      if(from&&!recorded)folio.append(el('p','atl-folio-detail','Opened from “'+from.title+'”. '+(d&&X.unreadableBooks(d).length?
        'No readable plan here records a reference to it; a Book that could not be read might.':'No plan here records a reference to it.')));
      var nav=el('div','atl-look');
      var bk=actionButton(nav,l.returnQuestion?'← Back to the open question':from?'← Back to '+from.name:'← Back to the atlas',closeLeaf,'series-back');bk.classList.add('atl-action-primary');
      bk.setAttribute('aria-keyshortcuts','Escape');
      actionButton(nav,'Read again',function(){readSeries(true,true);},'series-reread').classList.add('atl-action-quiet');
      folio.append(nav);
      var status=!c||c.status==='loading'?(d?'Reading the plans again… (showing the read of '+readTime(c)+')':'Reading the plans…'):c.status==='error'?'Could not read the plans: '+c.error:
        (c.changed?'Changed since you last read them. ':'')+'Read at '+readTime(c)+'.';
      folio.append(el('p','atl-note atl-series-status',status));
      folio.append(el('p','atl-note','Reading a plan here changes nothing. Each plan keeps its own owner, revision and acceptance; a working Book changes only when you apply a revision you reviewed.'));
      if(!d)return;
      // What the author opened comes first: the Book they asked for, or the overview when they asked for it.
      var bookFirst=!!(l.book&&!l.impact);
      if(!bookFirst)renderImpactOverview(d,from,l);
      renderLeafBooks(d,from,l);
      if(bookFirst)renderImpactOverview(d,from,l);renderLeafPlan(d,from);renderLeafDirections(d,from);
      if(d.separate_owners_note)folio.append(el('p','atl-note',d.separate_owners_note));
      var s=d.sources,missing=[];
      if(s.working_books.state==='absent')missing.push('working Book architectures for this canvas');
      if(s.series_plan.state==='absent')missing.push('a Series plan (series_identity.yaml)');
      if(s.series_direction.state==='absent')missing.push('Series or Book Directions');
      if(missing.length)folio.append(el('p','atl-note','Not kept here: '+missing.join(' · ')+'.'));
      var end=el('div','atl-actions');
      var bk2=actionButton(end,l.returnQuestion?'← Back to the open question':from?'← Back to '+from.name:'← Back to the atlas',closeLeaf,'series-back-end');bk2.classList.add('atl-action-primary');
      folio.append(end);
    }
    /* ---------- Open questions of the working Architecture (read-only) ----------
       The Architecture owner's read projection: each question as the revisions record it, its identity where one is
       recorded, its earlier formulations with the reason each revision records, and the Working Book decisions that
       refer to it by identity. Reading changes nothing. Asking opens the coding-agent desk on the question; an alternative
       becomes a revision only when the author chooses it, and only Apply changes the Architecture. */
    var QUESTIONS_MAX_AGE=20000;
    function readQuestions(force){
      if(!Q||!binding.getArchitectureQuestions)return;
      var c=S.qs,key=canvasKey()+'|'+(binding.getRequestSha()||'');
      // A failed read is not retried by the render it causes: "Try again" asks for it.
      if(c&&c.key===key&&!force&&!S.questionsStale&&(c.status==='loading'||c.status==='error'||
        (c.status==='ready'&&Date.now()-c.readAt.getTime()<QUESTIONS_MAX_AGE)))return;
      var seq=(S.qSeq||0)+1;S.qSeq=seq;S.questionsStale=false;
      // Data is kept only for the same canvas and revision: another canvas's or revision's questions are never shown as these.
      S.qs={key:key,status:'loading',data:c&&c.key===key&&c.data||null};
      var call;try{call=Promise.resolve(binding.getArchitectureQuestions());}catch(error){call=Promise.reject(error);}
      call.then(function(data){
        if(seq!==S.qSeq)return;
        S.qs={key:key,status:'ready',data:data,readAt:new Date()};renderFolio();
      },function(error){
        if(seq!==S.qSeq)return;
        S.qs={key:key,status:'error',error:error&&error.message||String(error),data:null};renderFolio();
      });
    }
    // Open questions only: a question no longer open is not counted as one.
    function questionsCount(){var c=S.qs,d=c&&c.data;
      return d&&d.available?(d.questions||[]).length:null;}
    function questionsData(){var c=S.qs;return c&&c.status!=='error'&&c.data?c.data:null;}
    // One question as a row in a list: its wording, then what the record says about it, in short.
    function questionItem(q){
      var li=el('li','atl-question-row'),b=el('button','atl-question-item');b.type='button';b.dataset.key=Q.keyOf(q);
      b.append(el('span','atl-question-text',Q.clip(q.text,150)));
      var chips=el('span','atl-question-chips');
      Q.chipsFor(q).forEach(function(c){chips.append(chip(c.text,c.tone==='warn'?'removed':c.tone==='ok'?'ok':null));});
      b.append(chips);
      b.setAttribute('aria-label',Q.clip(q.text,200)+'. '+Q.chipsFor(q).map(function(c){return c.text;}).join(', '));
      b.addEventListener('click',function(){openQuestion({id:q.id,index:q.index});});
      li.append(b);return li;
    }
    function renderQuestionOverview(){
      readQuestions(false);
      var c=S.qs,sec=el('section','atl-questions');sec.setAttribute('aria-label','Open questions of the working Architecture');
      sec.append(el('h4','atl-section-title','Open questions'));
      if(!c||(c.status==='loading'&&!c.data)){sec.append(el('p','atl-note','Reading the open questions…'));folio.append(sec);return;}
      if(c.status==='error'){sec.append(el('p','atl-note','Could not read the open questions: '+c.error));
        actionButton(sec,'Try again',function(){readQuestions(true);},'questions-retry');folio.append(sec);return;}
      var d=c.data;
      if(!d.available){sec.append(el('p','atl-note','No working Architecture is recorded, so there are no open questions to read.'));folio.append(sec);return;}
      var g=Q.groups(d),live=g.continuing.concat(g.wording);
      sec.append(el('p','atl-note',Q.overviewNote(d)));
      if(!live.length)sec.append(el('p','atl-note','The working Architecture records no open questions.'));
      else{var ul=el('ul','atl-question-list');live.slice(0,5).forEach(function(q){ul.append(questionItem(q));});sec.append(ul);}
      var total=live.length+g.gone.length;
      if(total)actionButton(sec,'All questions · '+total,openQuestionList,'questions-all').classList.add('atl-action-quiet');
      // Looking for opportunities is the author's explicit invitation; nothing runs until a request is prepared.
      if(d.available)actionButton(sec,'Look for opportunities',openOpportunities,'discover-open').classList.add('atl-action-quiet');
      if(g.gone.length)sec.append(el('p','atl-note',Q.plural(g.gone.length,'question')+' recorded in earlier revisions '+(g.gone.length===1?'is':'are')+
        ' no longer open. Removing one is not an answer.'));
      folio.append(sec);
    }
    // The concept's folio points to the open questions without moving the atlas or changing the focused concept.
    function renderQuestionsEntry(){
      readQuestions(false);
      var n=questionsCount(),sec=el('section','atl-questions-entry');
      sec.append(el('p','atl-series-kicker','Working Architecture'));
      actionButton(sec,'Open questions'+(n===null?'':' · '+n),openQuestionList,'questions-open').classList.add('atl-action-quiet');
      folio.append(sec);
    }
    function listBackLabel(){var cn=S.focus&&S.model&&S.model.byId[S.focus];return cn?'Back to “'+M.shorten(cn.name,40)+'”':'Back to the atlas';}
    function openQuestionList(){
      S.qlistOpener=(document.activeElement&&folio.contains(document.activeElement)&&document.activeElement.dataset)?document.activeElement.dataset.key:null;
      S.qlistScroll=folio.scrollTop;
      S.qlist=true;S.qv=null;S.leaf=null;
      readQuestions(false);renderFolio();folio.scrollTop=0;focusFolio();
      announce('All open questions of the working Architecture. Nothing is changed by reading them.');
    }
    function closeQuestionList(){
      S.qlist=false;renderFolio();folio.scrollTop=S.qlistScroll||0;
      var again=S.qlistOpener&&folio.querySelector('[data-key="'+cssEscape(S.qlistOpener)+'"]');
      if(again)again.focus({preventScroll:false});else focusFolio();
      var cn=S.focus&&S.model.byId[S.focus];
      announce(cn?'Back to “'+cn.title+'”. Your place in the atlas is unchanged.':'Back to the atlas.');
    }
    function renderQuestionList(){
      var d=questionsData(),c=S.qs;
      folio.setAttribute('aria-label','Open questions of the working Architecture');
      folio.append(el('p','atl-kicker-line','Open questions · working Architecture'));
      folio.append(el('h3','atl-folio-title','The questions this Architecture records'));
      var nav=el('div','atl-look');
      actionButton(nav,'← '+listBackLabel(),closeQuestionList,'questions-back').classList.add('atl-action-primary');
      folio.append(nav);
      if(!d){folio.append(el('p','atl-note',c&&c.status==='error'?'Could not read the open questions: '+c.error:'Reading the open questions…'));return;}
      folio.append(el('p','atl-note',Q.overviewNote(d)));
      var g=Q.groups(d);
      if(!g.continuing.length&&!g.wording.length)folio.append(el('p','atl-note','The working Architecture records no open questions.'));
      if(g.continuing.length){
        folio.append(el('h4','atl-section-title','Continuing · identity recorded · '+g.continuing.length));
        var u1=el('ul','atl-question-list');g.continuing.forEach(function(q){u1.append(questionItem(q));});folio.append(u1);}
      if(g.wording.length){
        folio.append(el('h4','atl-section-title','Wording only · no identity yet · '+g.wording.length));
        folio.append(el('p','atl-note','These questions have no recorded identity, so they cannot be followed across revisions or asked about as continuing questions.'));
        var u2=el('ul','atl-question-list');g.wording.forEach(function(q){u2.append(questionItem(q));});folio.append(u2);}
      if(g.gone.length){
        folio.append(el('h4','atl-section-title','No longer open · '+g.gone.length));
        folio.append(el('p','atl-note','Removing a question is not an answer. Each keeps the formulations it was recorded with.'));
        var u3=el('ul','atl-question-list');g.gone.forEach(function(q){u3.append(questionItem(q));});folio.append(u3);}
      renderComparisonSection(null);
      var status=el('p','atl-note atl-series-status',c&&c.status==='loading'?'Reading again…':'Read at '+readTime(c)+'.');
      folio.append(status);
      actionButton(folio,'Read again',function(){readQuestions(true);},'questions-reread').classList.add('atl-action-quiet');
    }
    // The question as the folio reads it: where it stands, how it has been recorded, the Books that refer to it.
    function openQuestion(view){
      S.qv={id:view.id||null,index:view.index===undefined?null:view.index,
        opener:(document.activeElement&&folio.contains(document.activeElement)&&document.activeElement.dataset)?document.activeElement.dataset.key:null,
        scroll:folio.scrollTop,returnLeaf:S.leaf||null,returnList:!!S.qlist};
      S.leaf=null;S.qlist=false;
      readQuestions(false);renderFolio();folio.scrollTop=0;focusFolio();
      announce(questionReturnWords(S.qv)+' Nothing is changed by reading it.');
    }
    function questionBackLabel(v){
      if(v.returnLeaf)return 'Back to the Series and Book context';
      if(v.returnList)return 'Back to all open questions';
      return listBackLabel();
    }
    function questionReturnWords(v){
      return 'Open question. Back returns to '+(v.returnLeaf?'the Series and Book context':v.returnList?'all open questions':
        (S.focus&&S.model.byId[S.focus]?'“'+S.model.byId[S.focus].title+'”':'the atlas'))+'.';
    }
    function closeQuestion(){
      var v=S.qv;if(!v)return;S.qv=null;
      if(v.returnLeaf)S.leaf=v.returnLeaf;
      else if(v.returnList)S.qlist=true;
      renderFolio();folio.scrollTop=v.scroll||0;
      var again=v.opener&&folio.querySelector('[data-key="'+cssEscape(v.opener)+'"]');
      if(again)again.focus({preventScroll:false});else focusFolio();
      announce(v.returnLeaf?'Back to the Series and Book context. Nothing was changed.':v.returnList?'Back to all open questions. Nothing was changed.':
        (S.focus&&S.model.byId[S.focus]?'Back to “'+S.model.byId[S.focus].title+'”. Your place in the atlas is unchanged.':'Back to the atlas.'));
    }
    function renderQuestionView(){
      var v=S.qv,c=S.qs,d=questionsData();
      folio.setAttribute('aria-label','Open question of the working Architecture');
      folio.append(el('p','atl-kicker-line','Open question · working Architecture'));
      var nav=el('div','atl-look');
      var back=actionButton(nav,'← '+questionBackLabel(v),closeQuestion,'question-back');back.classList.add('atl-action-primary');
      back.setAttribute('aria-keyshortcuts','Escape');
      folio.append(nav);
      readQuestions(false);
      // A heading even while reading, so the focus that opened the question stays on it when the reading arrives.
      if(!d){folio.append(el('h3','atl-folio-title','Open question'),
        el('p','atl-note',c&&c.status==='error'?'Could not read the open questions: '+c.error:'Reading the open question…'));return;}
      var q=Q.find(d,v);
      if(!q){folio.append(el('h3','atl-folio-title','This question is no longer recorded'),
        el('p','atl-folio-detail','The working Architecture does not record it under this identity or position now. Nothing has been changed.'));return;}
      folio.append(el('h3','atl-folio-title'+(q.text.length>90?' is-long':''),q.text));
      Q.standing(q,d).forEach(function(t){folio.append(toneLine(t));});
      // The question's own story first: how it has been recorded, then the Books that refer to it, then investigation.
      renderQuestionFormulations(q);
      renderQuestionBooks(q,d);
      renderQuestionInvestigation(q,d);
      renderComparisonSection(q);
      renderQuestionSource(q,d);
      var end=el('div','atl-actions');
      actionButton(end,'← '+questionBackLabel(v),closeQuestion,'question-back-end').classList.add('atl-action-primary');
      folio.append(end);
    }
    // A wording change, shown as what it was and what it is now, word by word. Same wording is said, not drawn.
    function wordDiffBlock(before,after,was){
      var box=el('div','atl-qdiff');
      if(!B.wordDiff||before===after){box.append(el('p','atl-qspan-text',after));return box;}
      var d=B.wordDiff(before,after);
      var a=el('p','atl-qspan-text atl-qspan-was');a.append(el('span','atl-series-kind',(was||'Was')+' · '));
      d.before.forEach(function(part){a.append(part[1]?el('del','',part[0]):document.createTextNode(part[0]));});
      var n=el('p','atl-qspan-text');n.append(el('span','atl-series-kind','Now · '));
      d.after.forEach(function(part){n.append(part[1]?el('ins','',part[0]):document.createTextNode(part[0]));});
      box.append(a,n);return box;
    }
    function renderQuestionFormulations(q){
      var sec=el('section','atl-qhistory');sec.setAttribute('aria-label','How this question has been recorded');
      if(q.standing==='wording_only'){
        sec.append(el('h4','atl-section-title','Recorded wording'),el('p','atl-qspan-text',q.text),
          el('p','atl-note','No identity is recorded for it yet. Earlier revisions named no identity for any question, so no earlier formulation is attached to it.'));
        folio.append(sec);return;
      }
      sec.append(el('h4','atl-section-title',q.standing==='no_longer_open'?'How it was recorded':'How it has changed'));
      if(!q.spans||!q.spans.length){sec.append(el('p','atl-note','No readable revision records this question.'));folio.append(sec);return;}
      var ol=el('ol','atl-qspans');
      q.spans.forEach(function(span,i){
        var li=el('li','atl-qspan atl-qspan-'+span.kind),head=Q.spanHead(span);
        li.append(el('p','atl-qspan-head atl-tone atl-tone-'+head.tone,head.text));
        if(span.kind==='present'){
          var before=span.previous&&span.previous.text;
          li.append(before!==undefined&&before!==null&&before!==span.text?wordDiffBlock(before,span.text,'Was'):el('p','atl-qspan-text',span.text));
          Q.reasonLines(span.reason).forEach(function(line){li.append(el('p','atl-qspan-reason',line));});
        }else if(span.kind==='absent'&&span.previous){
          li.append(el('p','atl-qspan-text atl-qspan-was','Last recorded as: “'+span.previous.text+'”'));
        }else if(span.kind==='no_identity'){
          li.append(el('p','atl-note','Revisions before the identities were recorded name no identity for this question. The wording they held is not attached to it.'));
        }
        var vs=Q.spanVersions(span);
        var det=el('details','atl-series-how');det.dataset.key='qspan:'+(q.id||q.index)+':'+i;
        det.append(el('summary','',vs.length===1?'The version this records':vs.length+' versions this span covers'));
        var list=el('ul','atl-qversions');
        vs.forEach(function(v){var item=el('li','',v.label+' · ');item.append(el('code','',v.sha));list.append(item);});
        det.append(list);li.append(det);
        ol.append(li);
      });
      sec.append(ol);folio.append(sec);
    }
    function renderQuestionBooks(q,d){
      var books=Q.booksOf(q),u=d.books||{};
      var sec=el('section','atl-qbooks');sec.setAttribute('aria-label','Working Books that record a decision about this question');
      sec.append(el('h4','atl-section-title','Working Books that record a decision about it · '+books.length));
      if(!books.length)sec.append(el('p','atl-note',q.standing==='wording_only'?
        'Decisions in the Books refer to wording without an identity, so none is connected to this question here.':
        'No working Book records a decision about this question. That shows only that no Book records one.'));
      books.forEach(function(ref){sec.append(bookRow(q,ref));});
      (u.unreadable||[]).forEach(function(b){sec.append(toneLine({tone:'bad',text:'Book '+b.book_number+' could not be read, so whether it records a decision about this question cannot be told.'}));});
      var loose=(u.wording_only_references||[]).length;
      if(loose&&q.standing!=='wording_only')sec.append(el('p','atl-note',Q.plural(loose,'decision')+' in the Books refer to wording without an identity. They are not connected to this question.'));
      // Decisions whose named version cannot be read, or no longer matches them, cannot be attached to any question.
      var unattached=(u.unattributed_references||[]).length;
      if(unattached)sec.append(el('p','atl-note',Q.plural(unattached,'decision')+' in the Books refer to an Architecture version that cannot be read or no longer matches the decision, so none can be attached to a question here.'));
      folio.append(sec);
    }
    // A Book's decision that refers to this question. Its own words, what the reference now means, and the wording it
    // was written against when that differs. The recorded identity and version sit behind a disclosure.
    function bookRow(q,ref){
      var box=el('article','atl-qbook');box.dataset.book=String(ref.book_number);
      box.append(el('p','atl-series-book','Book '+ref.book_number+(ref.title?' · '+ref.title:'')));
      if(ref.decision_text)box.append(el('p','atl-series-text','The Book keeps this decision open: “'+ref.decision_text+'”'));
      var rel=Q.bookRelation(ref);if(rel)box.append(toneLine(rel));
      var rec=ref.recorded||{};
      if(rec.text&&q.text!==rec.text&&q.standing!=='no_longer_open')
        box.append(el('p','atl-qspan-was','Earlier formulation it refers to · '+Q.label({revision_number:rec.revision_number,request_sha256:rec.version_request_sha256})+': “'+rec.text+'”'));
      var fresh=Q.bookFreshnessNote(ref);if(fresh)box.append(el('p','atl-note',fresh));
      var tech=el('details','atl-series-how');tech.dataset.key='question-book-source:'+ref.book_number+':'+ref.decision_id;
      tech.append(el('summary','','Source details'));
      var dl=el('dl','atl-facts');
      fact(dl,'Question identity',ref.question_id?(ref.records_identity?ref.question_id:
        ref.question_id+' · resolved from the version the decision names; the decision itself records no identity'):'none');
      fact(dl,'Recorded question version',rec.version_request_sha256?Q.label({revision_number:rec.revision_number,request_sha256:rec.version_request_sha256})+' · '+rec.version_request_sha256:null);
      fact(dl,'Decision',ref.decision_id);
      fact(dl,'Recorded position',rec.index!==null&&rec.index!==undefined?String(rec.index+1):null);
      tech.append(dl);box.append(tech);
      var row=el('div','atl-look');
      actionButton(row,'Read Book '+ref.book_number,function(){openBookFromQuestion(ref.book_number);},
        'question-book:'+ref.book_number+':'+ref.decision_id).classList.add('atl-action-quiet');
      if(binding.onDevelop&&binding.books&&ref.anchorable)actionButton(row,'Ask about this decision’s question',function(){
        askQuestion(ref.book_number,Q.bookAskRef(ref));},'question-book-ask:'+ref.book_number+':'+ref.decision_id).classList.add('atl-action-quiet');
      box.append(row);
      return box;
    }
    function openBookFromQuestion(n){
      var v=S.qv;S.qv=null;
      // The question's own place is kept, so Back returns the author to where they were reading it.
      v.ownScroll=folio.scrollTop;
      openLeaf({book:n,question:v});
    }
    // Investigation is offered where the author has read the question. Each operation is an inquiry in the existing desk;
    // no alternative is applied, and nothing is accepted, by asking.
    function renderQuestionInvestigation(q,d){
      var sec=el('section','atl-qinvestigate');sec.setAttribute('aria-label','Investigate this question with your coding agent');
      sec.append(el('h4','atl-section-title','Investigate with your coding agent'));
      if(Q.isAskable(q,d)){
        var row=el('div','atl-look atl-question-ask');
        Q.OPERATIONS.forEach(function(op){actionButton(row,op[1],function(){askArchitectureQuestion(q,op[0]);},'question-ask:'+op[0]).classList.add('atl-action-quiet');});
        sec.append(row,el('p','atl-note','Opens the coding-agent desk on this question. Asking changes nothing. An alternative becomes a revision only if you choose it, and then you review it and apply it yourself.'));
      }else{var note=Q.askNote(q,d);sec.append(el('p','atl-note',note||'This question cannot be asked about here.'));}
      folio.append(sec);
    }
    function renderQuestionSource(q,d){
      var det=el('details','atl-series-how');det.dataset.key='question-source:'+(q.id||'index-'+q.index);
      det.append(el('summary','','Source details'));
      var dl=el('dl','atl-facts');
      fact(dl,'Identity',q.id||'none recorded: wording only');
      fact(dl,q.standing==='no_longer_open'?'Last recorded position':'Position in the current revision',String(q.index+1));
      fact(dl,'Wording digest (sha256)',q.text_sha256?q.text_sha256.slice(0,16)+'…':null);
      if(d.current)fact(dl,'Current revision',Q.label({revision_number:d.current.revision_number,request_sha256:d.current.request_sha256})+' · '+d.current.request_sha256);
      if(d.history)fact(dl,'Revision history read',(d.history.chain_complete?'the whole chain':'part of the chain')+' · '+d.history.versions_read+' readable · '+d.history.unreadable_versions+' unreadable');
      det.append(dl,el('p','atl-note','Identities are the Architecture’s own declarations and are never inferred from wording. Each formulation is kept as the revision that recorded it.'));
      folio.append(det);
    }
    function askArchitectureQuestion(q,operation){
      if(!binding.onDevelop){announce('The coding-agent desk is not available here, so nothing was asked.');return;}
      binding.onDevelop({conceptId:null,title:q.text,anchor:{kind:'question',id:q.id},precision:'question',subject:'Open question',
        quote:q.text,sourceRef:'open_questions/'+q.index,operation:operation,draft:Q.SUGGEST[operation]||''});
    }
    /* Opportunity discovery, in the folio. The agent chooses what deserves a closer look; the author decides what to
       investigate. Looking changes nothing. Preparing a request only writes the request the author will copy; a
       possibility is investigated only through the same comparison and desk the author uses for their own questions. */
    function oppState(){return S.opp||(S.opp={open:false,goal:'',response:'',pending:null,projection:null,loading:false,error:null});}
    function openOpportunities(){
      var d=oppState();d.open=true;S.qlist=false;S.qv=null;S.leaf=null;
      readOpportunities(false);renderFolio();folio.scrollTop=0;focusFolio();
      announce('Look for opportunities. Nothing runs until you prepare a request and give it to your coding agent. Looking changes nothing.');
    }
    function closeOpportunities(){var d=oppState();d.open=false;renderFolio();folio.scrollTop=0;focusFolio();announce('Back to the open questions. Nothing was changed.');}
    function readOpportunities(force){
      var d=oppState();
      if(!binding.getDiscoveries){d.error='Opportunity discovery is not available here.';return;}
      if(d.loading||(!force&&(d.projection||d.error)))return;
      d.loading=true;
      binding.getDiscoveries().then(function(p){d.projection=p;d.pending=p.pending||null;d.loading=false;d.error=null;renderFolio();})
        .catch(function(e){d.loading=false;d.error='Could not read the earlier discoveries: '+e.message;renderFolio();});
    }
    function oppKey(row,p){return 'discover:'+row.request_sha256.slice(0,12)+':'+p.id;}
    function questionTitleFor(id){
      var data=questionsData()||{};var all=(data.questions||[]).concat(data.no_longer_open||[]);
      var q=all.find(function(x){return x.id===id;});return q?q.text:id;
    }
    function prepareOpportunityRequest(){
      var d=oppState();d.error=null;
      binding.prepareDiscovery((d.goal||'').trim()||null).then(function(p){
        d.projection=p;d.pending=p.pending||null;d.response='';
        announce('Discovery request prepared. Copy it to your coding agent. Nothing has run.');renderFolio();
      }).catch(function(e){d.error='The discovery request was not prepared: '+e.message;renderFolio();});
    }
    function validateOpportunityResponse(){
      var d=oppState();var parsed;
      try{parsed=JSON.parse(d.response);}catch(e){d.error='The answer is not JSON: '+e.message;renderFolio();return;}
      binding.completeDiscovery(parsed).then(function(p){
        d.projection=p;d.pending=p.pending||null;d.response='';d.error=null;
        announce('Discovery answer accepted. Its possibilities are listed below. Nothing has been changed.');renderFolio();
      }).catch(function(e){d.error='The answer was not accepted: '+e.message;renderFolio();});
    }
    function decideOpportunity(row,p,decision){
      var d=oppState();
      binding.decideDiscovery(row.request_sha256,p.id,decision,null).then(function(next){
        d.projection=next;d.error=null;announce(decision==='declined'?'Declined. Nothing in the Architecture or a Book was changed.':'Reopened. Nothing was changed.');renderFolio();
      }).catch(function(e){d.error='The decision was not recorded: '+e.message;announce(d.error);renderFolio();});
    }
    function investigatePossibility(row,p){
      if(!binding.onDevelop){announce('The coding-agent desk is not available here, so nothing was asked.');return;}
      var data=questionsData()||{};
      var list=(p.questions||[]).map(function(qid){var q=(data.questions||[]).find(function(x){return x.id===qid;});
        return {id:qid,title:q?q.text:qid,index:q?q.index:null};});
      var replaced=(S.qcompare||[]).length>0;S.qcompare=list.slice();
      if(replaced)announce('The comparison now holds this possibility’s questions. Your earlier selection was replaced.');
      var anchors=list.map(function(x){return {kind:'question',id:x.id};});
      binding.onDevelop({conceptId:null,title:'Possibility: '+p.title,anchor:anchors[0],anchors:anchors,precision:'question',
        subject:'Discovered possibility',quote:'',sourceRef:'',operation:'compare',draft:p.next_investigation||'',
        fromDiscovery:{requestSha256:row.request_sha256,possibilityId:p.id,title:p.title,questions:(p.questions||[]).slice()}});
    }
    function renderOpportunities(){
      var d=oppState();
      folio.setAttribute('aria-label','Look for opportunities in the working Architecture');
      folio.append(el('p','atl-kicker-line','Opportunities · working Architecture'));
      var nav=el('div','atl-look');
      actionButton(nav,'← Back to the open questions',closeOpportunities,'discover-back').classList.add('atl-action-primary');
      folio.append(nav);
      folio.append(el('h3','atl-folio-title','Look for opportunities'));
      folio.append(el('p','atl-note','The coding agent reads the whole working Architecture and its open questions, and chooses what deserves a closer look. Each possibility is advisory. Nothing is accepted, and nothing changes unless you choose to investigate one.'));
      var req=el('section','atl-discover-request');req.setAttribute('aria-label','Ask the coding agent for opportunities');
      var goal=el('label','atl-note','Optional: a goal or area of concern, in your words');
      var field=document.createElement('textarea');field.setAttribute('aria-label','Optional goal for the discovery');
      field.maxLength=600;field.rows=2;field.value=d.goal||'';field.dataset.key='discover-goal';field.addEventListener('input',function(){d.goal=field.value;});
      goal.append(field);req.append(goal);
      actionButton(req,'Prepare the discovery request',prepareOpportunityRequest,'discover-prepare').classList.add('atl-action-primary');
      if(d.pending&&d.pending.request){
        var pk=el('label','atl-note','Prepared discovery request: copy it to your coding agent. Nothing has been executed.');
        var pre=document.createElement('textarea');pre.readOnly=true;pre.rows=5;pre.setAttribute('aria-label','Prepared discovery request');
        pre.value=JSON.stringify(d.pending.request,null,2);pk.append(pre);
        var rl=el('label','atl-note','Paste the signed host-agent response JSON from your coding agent');
        var rt=document.createElement('textarea');rt.rows=4;rt.setAttribute('aria-label','Discovery response');rt.value=d.response||'';rt.dataset.key='discover-response';
        rt.addEventListener('input',function(){d.response=rt.value;});rl.append(rt);
        req.append(pk,rl);
        actionButton(req,'Validate the response',validateOpportunityResponse,'discover-validate').classList.add('atl-action-quiet');
      }
      if(d.error){var err=el('p','atl-note atl-tone-bad',d.error);err.setAttribute('role','alert');req.append(err);}
      actionButton(req,'Read again',function(){readOpportunities(true);},'discover-reread').classList.add('atl-action-quiet');
      folio.append(req);
      renderOpportunityResults(d);
    }
    function renderOpportunityResults(d){
      var p=d.projection;
      if(!p){folio.append(el('p','atl-note',d.loading?'Reading the earlier discoveries…':'No discovery has been read yet.'));
        if(!d.loading&&!d.error)readOpportunities(false);return;}
      if(!p.discoveries||!p.discoveries.length){folio.append(el('p','atl-note','No discovery has been run on this Architecture yet.'));return;}
      p.discoveries.forEach(function(row,index){
        var box=index===0?el('section','atl-discover-run'):el('details','atl-discover-run');
        if(index!==0)box.append(el('summary','','Earlier discovery · '+row.created_at));
        else box.append(el('h4','atl-section-title','Latest discovery'));
        if(row.baseline!=='current')box.append(el('p','atl-note','Recorded against an earlier working Architecture. Each possibility says whether it can still be investigated.'));
        if(row.author_goal)box.append(el('p','atl-note','Your goal: '+row.author_goal));
        if(row.coverage_note){var cov=el('details','atl-series-how');cov.append(el('summary','','What the agent surveyed'),el('p','atl-note',row.coverage_note));box.append(cov);}
        if(!row.possibilities.length)box.append(el('p','atl-note',row.no_possibility_reason||'No possibility was worth recording.'));
        row.possibilities.forEach(function(item){box.append(opportunityCard(row,item));});
        folio.append(box);
      });
    }
    function opportunityCard(row,item){
      var D=global.AuteurAtelierDiscovery;var art=el('article','atl-discover-card');
      art.setAttribute('aria-label','Possibility: '+item.title);
      art.append(el('h4','atl-discover-title',item.title));
      var st=D.statusWords(item.status);
      art.append(el('p','atl-discover-meta',['Agent proposal',D.kindLabel(item.kind),item.basis==='grounded'?'Grounded in recorded mechanisms':'Speculative, labelled as such',st.label].filter(Boolean).join(' · ')));
      art.append(el('p','atl-discover-text',item.possibility),el('p','atl-discover-why',item.significance));
      var qs=el('ul','atl-discover-questions');
      item.questions.forEach(function(qid){qs.append(el('li','',questionTitleFor(qid)));});
      art.append(el('p','atl-note','Concerns these questions:'),qs);
      if(item.status&&item.status.note)art.append(el('p','atl-note',item.status.note));
      art.append(el('p','atl-discover-next','Next: '+item.next_investigation));
      var ev=el('details','atl-series-how');ev.dataset.key=oppKey(row,item)+':evidence';
      ev.append(el('summary','','Evidence and provenance'));
      var evl=el('ul','');item.evidence.forEach(function(e){evl.append(el('li','',D.evidenceLine(e)));});ev.append(evl);art.append(ev);
      var un=el('details','atl-series-how');un.dataset.key=oppKey(row,item)+':uncertainty';
      un.append(el('summary','','Interpretation, assumptions and counterevidence'));
      un.append(el('p','atl-note','This is the agent’s proposal, not established fact. Its grounding is the evidence above.'));
      if(item.assumptions&&item.assumptions.length)un.append(el('p','atl-note','Assumes: '+item.assumptions.join(' · ')));
      if(item.counterevidence&&item.counterevidence.length)un.append(el('p','atl-note','Counterevidence: '+item.counterevidence.join(' · ')));
      if(item.gains)un.append(el('p','atl-note','Could gain: '+item.gains));
      if(item.costs)un.append(el('p','atl-note','Would cost: '+item.costs));
      art.append(un);
      var acts=el('div','atl-look atl-question-ask');
      if(item.decision&&item.decision.decision==='declined'){
        art.append(el('p','atl-note','Declined. Nothing in the Architecture or a Book was changed.'));
        actionButton(acts,'Reopen',function(){decideOpportunity(row,item,'reopened');},'discover-decision:'+item.id).classList.add('atl-action-quiet');
      }else{
        if(D.canInvestigate(item))actionButton(acts,'Investigate these questions',function(){investigatePossibility(row,item);},'discover-investigate:'+item.id).classList.add('atl-action-primary');
        actionButton(acts,'Decline',function(){decideOpportunity(row,item,'declined');},'discover-decision:'+item.id).classList.add('atl-action-quiet');
      }
      art.append(acts);
      if(item.investigations&&item.investigations.length)art.append(el('p','atl-note','Investigated '+item.investigations.length+' time'+(item.investigations.length===1?'':'s')+(item.applied?'; a revision made from it has been applied':'; no revision applied from it yet')+'.'));
      return art;
    }
    /* Comparing open questions: up to three, chosen in the folio and investigated together through the desk. Choosing
       changes nothing; the desk's prepared request is the only thing that is ever sent, and only when the author asks. */
    function comparison(){return S.qcompare||(S.qcompare=[]);}
    function renderComparisonSection(q){
      var d=questionsData(),list=comparison();
      // Only questions the owner says may be asked about stay in the comparison, and each takes its current wording.
      if(d&&d.available){var live={};(d.questions||[]).forEach(function(x){if(Q.isAskable(x,d))live[x.id]=x;});
        list=list.filter(function(x){return live[x.id];}).map(function(x){return {id:x.id,title:live[x.id].text,index:live[x.id].index};});
        S.qcompare=list;}
      var sec=el('section','atl-qcompare');sec.setAttribute('aria-label','Compare open questions');
      sec.append(el('h4','atl-section-title',list.length?'Comparing · '+list.length+' of 3':'Compare open questions'));
      if(q&&q.id){
        var inList=list.some(function(x){return x.id===q.id;});
        if(inList||Q.isAskable(q,d))actionButton(sec,inList?'Remove this question from the comparison':'Add this question to a comparison',
          function(){toggleCompare(q);},'question-compare:'+q.id).classList.add('atl-action-quiet');
        else sec.append(el('p','atl-note','This question cannot be compared here: the Architecture does not record it as an open question you can ask about.'));
      }
      if(!list.length)sec.append(el('p','atl-note','Add two or three open questions to investigate how they relate. Nothing is sent until you choose an operation.'));
      else{
        var ul=el('ul','atl-question-list');
        list.forEach(function(x){var li=el('li','atl-qcompare-item');li.append(el('p','atl-question-text',x.title));
          actionButton(li,'Remove “'+M.shorten(x.title,40)+'”',function(){removeCompare(x.id);},'compare-remove:'+x.id).classList.add('atl-action-quiet');
          ul.append(li);});
        sec.append(ul);
        if(list.length<2)sec.append(el('p','atl-note','Add one more question to compare.'));
        else{
          var row=el('div','atl-look atl-question-ask');
          Q.compareOperations(list.length).forEach(function(op){
            actionButton(row,op[1],function(){investigateTogether(op[0]);},'compare-ask:'+op[0]).classList.add('atl-action-quiet');});
          sec.append(row,el('p','atl-note','Opens the coding-agent desk on these questions, with their recorded history. Asking changes nothing. An alternative becomes a revision only if you choose it, and then you review it and apply it yourself.'));
        }
        actionButton(sec,'Clear comparison',clearComparison,'compare-clear').classList.add('atl-action-quiet');
      }
      folio.append(sec);
    }
    function rerenderKeeping(key){
      renderFolio();
      var again=key&&folio.querySelector('[data-key="'+cssEscape(key)+'"]');
      // Otherwise the comparison's own heading takes focus, so a keyboard user stays in the section they acted in.
      if(!again){again=folio.querySelector('.atl-qcompare .atl-section-title');if(again)again.setAttribute('tabindex','-1');}
      if(again)again.focus({preventScroll:true});else focusFolio();
    }
    function toggleCompare(q){
      var r=Q.toggleComparison(comparison(),q);S.qcompare=r.list;
      announce(r.full?'Three questions is the most one comparison can hold. Remove one to add another.':
        (r.list.some(function(x){return x.id===q.id;})?'Added to the comparison. ':'Removed from the comparison. ')+'Nothing is changed by comparing them.');
      rerenderKeeping('question-compare:'+q.id);
    }
    function removeCompare(id){S.qcompare=comparison().filter(function(x){return x.id!==id;});announce('Removed from the comparison. Nothing is changed.');
      rerenderKeeping(S.qcompare.length?'compare-remove:'+S.qcompare[0].id:null);}
    function clearComparison(){S.qcompare=[];announce('The comparison is cleared. Nothing is changed.');rerenderKeeping(null);}
    function investigateTogether(operation){
      var list=comparison();if(list.length<2)return;
      if(!binding.onDevelop){announce('The coding-agent desk is not available here, so nothing was asked.');return;}
      var anchors=list.map(function(x){return {kind:'question',id:x.id};});
      binding.onDevelop({conceptId:null,title:'Comparing '+list.length+' open questions',anchor:anchors[0],anchors:anchors,
        precision:'question',subject:'Open questions compared',quote:'',sourceRef:'open_questions/'+list[0].index,
        operation:operation,draft:Q.COMPARE_SUGGEST[operation]||''});
    }
    /* What Architecture changes mean for the working Books. Read from each Book's own record: the concepts
       it cites by node id, judged against the fingerprint it kept, and its own freshness. The overview says
       which Books cite a concept that changed or is gone and which are only out of date; each Book's record
       shows the exact evidence. Nothing is inferred from wording, and reconciling goes through the Book's
       own owner: a whole-Book revision the author reviews and applies. */
    function impactLine(){
      if(!I||!binding.getSeriesContext)return null;
      readSeries(false);
      var c=S.seriesCtx,sum=c&&c.data&&I.summarize(c.data);if(!I.noteworthy(sum))return null;
      var box=el('div','atl-impact-line'),parts=[];
      if(sum.flagged.length)parts.push(I.andList(sum.flagged.map(function(e){return 'Book '+e.number;}))+(sum.flagged.length===1?' cites':' cite')+
        ' Architecture concepts that changed or are gone');
      var archOnly=sum.outOfDateOnly.filter(function(e){return e.architectureChanged&&!e.noArchitecture;}),
        srcOnly=sum.outOfDateOnly.filter(function(e){return !e.architectureChanged;});
      if(archOnly.length)parts.push(I.plural(archOnly.length,'Book')+(archOnly.length===1?' was':' were')+
        ' written against an earlier Architecture, with every concept cited unchanged');
      if(srcOnly.length)parts.push(I.plural(srcOnly.length,'Book')+(srcOnly.length===1?' has':' have')+' its own source changed since it was written');
      if(sum.unreadable.length||sum.state==='unreadable')parts.push(sum.state==='unreadable'?'the working Books could not be read':
        I.plural(sum.unreadable.length,'Book')+' could not be read');
      box.append(el('p','atl-series-kicker','Working Books'),el('p','atl-note',parts.join('; ')+'.'));
      var go=actionButton(box,'Review the working Books',function(){openLeaf({impact:true});},'impact-open');go.classList.add('atl-action-quiet');
      return box;
    }
    function renderImpactOverview(d,from,l){
      if(!I)return;
      var sum=I.summarize(d);if(!sum||(!I.noteworthy(sum)&&!l.impact))return;
      var sec=leafSection('Architecture changes and the working Books',I.OVERVIEW_NOTE);sec.classList.add('atl-impact');
      if(sum.state==='unreadable'){sec.append(toneLine({tone:'bad',text:'The working Book architectures could not be read ('+sum.reason+'), so which Books are affected cannot be told.'}));return;}
      if(sum.state==='absent'&&!sum.without.length){sec.append(el('p','atl-note','This canvas keeps no working Book architectures, so no Book records a reference to the Architecture.'));return;}
      // While one Book's evidence is open the other Books shrink to one line each.
      var focusOn=l.evidence||null;
      function group(title,entries,compact){
        if(!entries.length)return;compact=compact||!!focusOn;
        sec.append(el('p','atl-series-kicker',title+' · '+entries.length));
        var ul=el('ul','atl-impact-list'),rest=null;
        entries.forEach(function(e,i){var li=el('li','atl-impact-book-row');
          if(focusOn===e.number)li.classList.add('is-current');
          li.append(el('p','atl-series-book','Book '+e.number+(e.book.title?' · '+e.book.title:'')));
          if(!compact)I.lines(e,nodeName).forEach(function(t){li.append(toneLine(t));});
          if(e.state!=='working'&&e.reason&&!compact){var tech=el('details','atl-series-how');tech.dataset.key='impact-tech:'+e.number;
            tech.append(el('summary','','Technical detail'),el('p','atl-note',e.reason));li.append(tech);}
          if(e.state==='working'){var since=I.sinceLine(e);if(since&&!compact)li.append(el('p','atl-note',since));
            var dl=e.book.development&&B.phaseLine(e.book.development.phase,e.number);if(dl)li.append(toneLine(dl));
            if(focusOn!==e.number)actionButton(li,'Show Book '+e.number+'’s evidence',function(){showBookEvidence(e.number);},'impact-show:'+e.number).classList.add('atl-action-quiet');}
          if(i<8)ul.append(li);else{if(!rest){rest=el('details','atl-series-how');rest.dataset.key='impact-more:'+title;
            rest.append(el('summary','',(entries.length-8)+' more'));rest.append(el('ul','atl-impact-list'));}rest.lastChild.append(li);}});
        sec.append(ul);if(rest)sec.append(rest);
      }
      group('Cite concepts that changed or are gone',sum.flagged,false);
      group('Out of date, with every cited concept unchanged',sum.outOfDateOnly,false);  // the rows say why: Architecture or source
      group('Could not be read',sum.unreadable,false);
      if(sum.current.length)sec.append(el('p','atl-tone atl-tone-ok','Written against the current working Architecture: '+
        I.andList(sum.current.map(function(e){return 'Book '+e.number;}))+'.'));
      if(sum.concepts.length){
        sec.append(el('p','atl-series-kicker','Concepts behind this'));
        var row=el('div','atl-revised-index');
        sum.concepts.forEach(function(c){var target=c.status==='changed'?conceptForNode(c.node_id):null,name=I.refName(c.ref,nodeName);
          var who=' · '+I.citedBy(c.books);
          if(target){var b=el('button','atl-index-item',target.name+' · changed'+who);b.type='button';b.title=target.title;b.dataset.key='impact-node:'+c.node_id;
            b.addEventListener('click',function(){S.impactReturn={concept:target.id,book:null};select(target.id,{via:'series'});focusFolio();});row.append(b);}
          else row.append(chip(name+(c.status==='removed'?' · no longer in the Architecture':' · changed')+who,c.status==='removed'?'removed':'proposal'));});
        sec.append(row,el('p','atl-note','A changed concept opens in the atlas. A concept that is gone is not in the atlas; each Book’s evidence shows it as that Book recorded it.'));
      }
      if(sum.without.length)sec.append(el('p','atl-note',I.andList(sum.without.map(function(w){return 'Book '+w.book_number+(w.requested?' (a develop request is prepared)':'');}))+
        (sum.without.length===1?' has':' have')+' source items in this canvas but no working Book architecture, so nothing '+(sum.without.length===1?'it':'they')+
        ' might depend on is recorded.'));
      if(sum.requestedOnly.length)sec.append(el('p','atl-note',I.andList(sum.requestedOnly.map(function(n){return 'Book '+n;}))+' has a prepared develop request and no working Book yet.'));
    }
    // Bring a folio element into view by scrolling whatever holds it: the folio where it scrolls (desktop),
    // else the page (a phone, where the folio is part of the page). The atlas never moves.
    function reveal(t){
      if(!t)return;
      if(folio.scrollHeight>folio.clientHeight+1&&global.getComputedStyle(folio).overflowY!=='visible')
        folio.scrollTop+=t.getBoundingClientRect().top-folio.getBoundingClientRect().top-8;
      else t.scrollIntoView({block:'start'});
    }
    function focusAndReveal(key){global.setTimeout(function(){var t=folio.querySelector('[data-key="'+cssEscape(key)+'"]');
      if(t){t.focus({preventScroll:true});reveal(t);}},0);}
    function showBookEvidence(n){
      if(!S.leaf)return;S.leaf.book=n;S.leaf.evidence=n;renderFolio();
      var t=folio.querySelector('[data-key="impact-evidence:'+n+'"]');if(t){t.focus({preventScroll:true});reveal(t);}
      announce('Book '+n+'’s evidence. Escape returns to all the Books.');
    }
    function changeBlock(parent,r){
      var c=I.conceptChange(r);
      if(!c.known){parent.append(el('p','atl-note','The version the Book was written against is not kept in any record here, so what changed cannot be shown.'));return;}
      if(c.status==='removed'){var p=el('p','atl-series-text');p.append(el('span','atl-series-kind','As the Book recorded it · '),document.createTextNode(c.was.summary||''));
        parent.append(p);return;}
      if(c.titleChanged){var t=el('p','atl-series-text');t.append(el('span','atl-series-kind','Name · '),el('del','',c.was.title),document.createTextNode(' → '),el('ins','',c.now.title));parent.append(t);}
      if(c.summary){var was=el('p','atl-book-before'),now=el('p','atl-book-after');
        was.append(el('span','atl-series-kind','When the Book was written · '));now.append(el('span','atl-series-kind','Now · '));
        c.summary.before.forEach(function(p){was.append(p[1]?el('del','',p[0]):document.createTextNode(p[0]));});
        c.summary.after.forEach(function(p){now.append(p[1]?el('mark','',p[0]):document.createTextNode(p[0]));});
        parent.append(was,now);}
      else if(c.fields.length)parent.append(el('p','atl-note','Its '+I.andList(c.fields)+' changed.'));
    }
    function renderBookImpact(det,b,from){
      var e=I.entry(b),n=b.book_number,box=el('section','atl-impact-book');box.setAttribute('aria-label','Since Book '+n+' was written');
      var h=el('h5','atl-series-subtitle','Since Book '+n+' was written');h.tabIndex=-1;h.dataset.key='impact-evidence:'+n;box.append(h);
      var since=I.sinceLine(e);if(since)box.append(el('p','atl-note',since));
      function refList(title,refs,tone){
        if(!refs.length)return;
        box.append(el('p','atl-series-kicker',title+' · '+refs.length));
        var ul=el('ul','atl-series-elements');
        refs.forEach(function(r){var li=el('li','atl-impact-ref'),target=r.present?conceptForNode(r.node_id):null;
          li.append(el('p','atl-series-book','“'+I.refName(r,nodeName)+'”'+(r.present?'':' · no longer in the working Architecture')));
          changeBlock(li,r);
          var cites=el('details','atl-series-how');cites.dataset.key='impact-cites:'+n+':'+r.node_id;
          cites.append(el('summary','','Cited by '+X.refSummary(r)+' of Book '+n));
          var cl=el('ul','atl-series-elements');I.citing(r).forEach(function(t){cl.append(el('li','',t));});cites.append(cl);li.append(cites);
          var row=el('div','atl-actions');
          if(target)actionButton(row,'Show it in the atlas',function(){S.impactReturn={concept:target.id,book:n};select(target.id,{via:'series'});focusFolio();},'impact-select:'+n+':'+r.node_id).classList.add('atl-action-quiet');
          if(target&&binding.onDevelop&&r.status==='changed')inquiryButton(row,target,e,r);
          if(row.childNodes.length)li.append(row);
          ul.append(li);});
        box.append(ul);
      }
      refList('Changed since it was written',e.changed,'warn');
      refList('No longer in the working Architecture',e.removed,'bad');
      I.lines(e,nodeName).filter(function(t){return !/^Cites /.test(t.text);}).forEach(function(t){box.append(toneLine(t));});
      var nc=I.notCited(e);
      if(nc&&e.flagged&&I.notCitedNames(e,6))box.append(el('p','atl-note','Also changed in the Architecture since, and not cited by Book '+n+': '+I.notCitedNames(e,6)+'.'));
      if(e.unchanged.length)box.append(el('p','atl-note',(e.flagged?I.plural(e.unchanged.length,'other cited concept'):'All '+I.plural(e.unchanged.length,'cited concept'))+
        (e.unchanged.length===1&&!e.flagged?' is':'')+' unchanged as the Book recorded them. '+
        'A Book records each concept it cites (its name, kind, description, scope and parent), not its relationships, so a changed relationship is not shown here.'));
      var la=b.last_applied;
      if(la&&la.currentness==='kept_baseline')box.append(el('p','atl-note','Working Book revision '+la.revision_number+' changed only part of this Book while it was out of date, so it is still recorded against its earlier Architecture and source.'));
      if(binding.books&&e.outOfDate&&!e.noArchitecture&&!b.development&&!devFor(n)){
        var go=actionButton(box,e.architectureChanged?'Reconcile Book '+n+' with the working Architecture':'Bring Book '+n+' up to date with its source',function(){
          S.leaf.book=n;openDevelop(n,[],true,from,{instruction:I.reconcileDraft(e,nodeName),caretTop:true});},'impact-reconcile:'+n);
        go.classList.add('atl-action-primary');
        box.append(el('p','atl-note','A whole-Book revision through Book '+n+'’s own owner, starting from words you can change. Preparing changes nothing; only Apply changes the Book.'));
      }
      det.append(box);
    }
    // Investigating instead of revising is a question in the existing coding-agent panel, never sent for the author.
    function inquiryButton(parent,target,e,r){
      var s=M.sourceAnchor(S.model,target.id);if(!s.anchor)return;
      var offered=binding.developOperations?binding.developOperations(s.anchor):['explore'];
      var op=['explore','challenge','explain'].filter(function(o){return offered.indexOf(o)>=0;})[0];if(!op)return;
      actionButton(parent,'Ask your coding agent what this may mean',function(){
        binding.onDevelop({conceptId:target.id,title:target.title,anchor:JSON.parse(JSON.stringify(s.anchor)),precision:s.precision,
          subject:s.subject,quote:s.quote,sourceRef:s.sourceRef,operation:op,draft:I.inquiryDraft(e,r,nodeName)});
      },'impact-ask:'+e.number+':'+r.node_id).classList.add('atl-action-quiet');
    }
    /* A working Book discovery, considered for the Architecture. What the Book records is shown as the Book
       records it: its own words, its standing, and the Architecture concepts it cites by node id. Whether it
       matters beyond the Book is not established; asking the coding agent is an inquiry that changes nothing,
       and keeping it in the Book is a complete outcome. An Architecture revision is only ever prepared from an
       alternative the author chooses in the inquiry, reviewed and applied through the Architecture's owner. */
    var BEYOND={unresolved:1,series_consequences:1,alternatives:1,later_possibilities:1,assumptions:1};
    // The element's kind as a noun in a sentence ("records this open question").
    var NOUN={unresolved:'open question',series_consequences:'consequence for the Series',alternatives:'alternative',
      later_possibilities:'later possibility',assumptions:'assumption',engines:'engine',agents:'agent',inherited:'inherited Series condition',
      local_resolution:'local resolution',typed_edges:'link'};
    function noun(collection){return NOUN[collection]||B.kind(collection).toLowerCase();}
    function discoveryFor(n){var d=S.discovery;return d&&d.canvas===canvasKey()&&d.book===n?d:null;}
    function discoverButton(parent,b,e,from,list){
      if(!binding.onDevelop||!binding.books||e.collection==='open_author_decisions')return;
      var x=actionButton(parent,'Consider for the Architecture',function(){openDiscovery(b.book_number,e.id,from);},
        (list?'book-discover-list:':'book-discover:')+b.book_number+':'+e.id);
      x.classList.add('atl-action-quiet');
      x.setAttribute('aria-label','Consider this '+(X.COLLECTION[e.collection]||'element').toLowerCase()+' of Book '+b.book_number+' for the Architecture: '+B.clip(e.text||'',60));
    }
    function openDiscovery(n,id,from){
      S.discovery={canvas:canvasKey(),book:n,element:id,from:from?from.id:null,operation:'explore',anchor:null,focusPending:true};
      if(S.leaf)S.leaf.book=n;
      readBook(n,true);renderFolio();
      announce('Considering a Book '+n+' element for the Architecture. Nothing is prepared or changed until you ask.');
    }
    function closeDiscovery(n,kept){
      var d=discoveryFor(n);S.discovery=null;renderFolio();
      if(d)focusAndReveal(folio.querySelector('[data-key="book-discover:'+n+':'+d.element+'"]')?'book-discover:'+n+':'+d.element:'book-discover-list:'+n+':'+d.element);
      announce(kept?'Kept in Book '+n+'. Nothing was prepared or changed.':'Closed; nothing was prepared.');
    }
    function discoveryDraft(d){S.discoveryDrafts=S.discoveryDrafts||{};var k=canvasKey()+'#'+d.book+'|'+d.element;
      return S.discoveryDrafts[k]||(S.discoveryDrafts[k]={text:''});}
    function citedStatus(r){
      if(!r)return 'recorded';
      return r.status==='removed'?'recorded, but no longer in the working Architecture: historical, and it cannot be asked about':
        r.status==='changed'?'recorded; changed since the Book was written':r.status==='unrecorded'?'recorded; its version when the Book was written is not kept':
        'recorded, unchanged since the Book was written';
    }
    function renderDiscovery(det,b,from){
      var n=b.book_number,d=discoveryFor(n);if(!d)return;
      // A changed Architecture clears every Book read; the card reads its Book again rather than wait on nothing.
      if(!bookState(n))readBook(n,false);
      var st=bookState(n),data=st&&st.data,box=el('section','atl-discovery');box.setAttribute('aria-label','Consider for the Architecture');
      var h=el('h5','atl-series-subtitle','Consider for the Architecture');h.tabIndex=-1;h.dataset.key='book-discovery-h:'+n;box.append(h);
      if(!data){box.append(el('p','atl-note',st&&st.status==='error'?'Could not read Book '+n+': '+st.error:'Reading Book '+n+'…'));det.append(box);return;}
      var row=(data.elements||[]).filter(function(x){return x.id===d.element;})[0];
      if(data.state!=='working'||!row){box.append(toneLine({tone:'bad',text:data.state==='unreadable'?
          'Book '+n+'’s working record cannot be read, so there is nothing current to consider. Nothing was prepared.':
          'Book '+n+' no longer records this element, so there is nothing current to consider. Nothing was prepared.'}));
        actionButton(box,'Close',function(){closeDiscovery(n,false);},'book-keep:'+n);det.append(box);return;}
      var kind=B.kind(row.collection),said=noun(row.collection),refs={};(b.references||[]).forEach(function(r){refs[r.node_id]=r;});
      box.append(el('p','atl-series-kicker','What Book '+n+' records'));
      var rr=actionButton(box,'Read Book '+n+' again',function(){readBook(n,true);},'book-reread:'+n);rr.classList.add('atl-action-quiet');
      var what=el('div','atl-book-target');
      what.append(el('p','atl-series-line',kind),el('p','atl-series-text',row.text||row.title||''));
      var standing=el('p','atl-provenance');
      standing.append(chip('Working Book proposal · '+(X.AUTHORITY[row.commitment_authority]||M.human(row.commitment_authority||'element')),'proposal'),
        chip(M.human(row.epistemic_status||'')+(row.attribution?' · '+M.human(row.attribution).toLowerCase():''),'proposal'));
      what.append(standing,el('p','atl-note','Book '+n+(b.title?' · '+b.title:'')+' · working revision '+data.book.revision_number+' · element '+row.id));
      box.append(what);
      var cited=(row.series_refs||[]).map(function(id){return {id:id,ref:refs[id]};});
      var present=cited.filter(function(c){return c.ref&&c.ref.present&&conceptForNode(c.id);});
      box.append(el('p','atl-series-kicker','Architecture concepts it records'));
      var ul=el('ul','atl-series-elements');
      cited.forEach(function(c){ul.append(el('li','','“'+(c.ref?I.refName(c.ref,nodeName):c.id)+'” · '+citedStatus(c.ref)));});
      if(!cited.length)ul.append(el('li','','None. It names no Architecture concept by a recorded reference.'));
      box.append(ul);
      box.append(toneLine({tone:'ok',text:'Established: Book '+n+' records this '+said+(present.length?' and a reference to '+
        I.andList(present.map(function(c){return '“'+nodeName(c.id)+'”';})):'')+'.'}));
      box.append(el('p','atl-note','Not established: whether it matters beyond Book '+n+', or what, if anything, the Architecture should do about it. '+
        'Asking gives your coding agent’s interpretation; the decision stays yours, and keeping it in this Book is a complete outcome.'));
      var asked=binding.getBookInquiry&&binding.getBookInquiry();
      if(asked&&asked.book_number===n&&asked.element_id===row.id){
        box.append(toneLine({tone:'warn',text:asked.status==='ready'?'Asked: your coding agent’s answer is in the coding-agent panel'+
          (asked.evidence==='changed'||asked.evidence==='unreadable'?'; the Book has changed since, so its evidence there is historical.':'.'):
          asked.status==='awaiting_host_agent'?'Asked: a request with this element is waiting for your coding agent.':
          'An earlier request with this element no longer matches its sources; ask again if you still want an answer.'}));
        if(binding.showInquiry)actionButton(box,'Go to the coding-agent panel',function(){binding.showInquiry();},'book-panel:'+n).classList.add('atl-action-quiet');
      }else if(d.revisionApplied)box.append(toneLine({tone:'ok',text:'An Architecture revision was applied after you asked. Nothing in Book '+n+
          ' changed; whether it now cites a changed concept is shown in its record.'}));
      else if(d.handedOff)box.append(el('p','atl-note','Taken to the coding-agent panel; send it from there when you are ready.'));
      var row2=el('div','atl-actions');
      var keep=actionButton(row2,'Keep it in Book '+n,function(){closeDiscovery(n,true);},'book-keep:'+n);keep.classList.add('atl-action-quiet');
      if(!present.length){
        box.append(toneLine({tone:'warn',text:'This element records no reference to a concept the current working Architecture has, so there is no recorded concept to ask about. '+
          'A concept it names only in its wording is not a recorded reference.'}));
        box.append(row2);det.append(box);return;
      }
      if(!d.anchor||!present.some(function(c){return c.id===d.anchor;}))d.anchor=(from&&present.some(function(c){return c.id===from.nodeId;}))?from.nodeId:present[0].id;
      var ask=el('fieldset','atl-book-scope');ask.append(el('legend','','Investigate with your coding agent'));
      [['explore','Explore alternatives for the Architecture'],['challenge','Challenge how the Architecture reads it'],['explain','Explain what the Architecture records']].forEach(function(o){
        var lab=el('label','atl-book-choice'),r=el('input');r.type='radio';r.name='discovery-op-'+n;r.value=o[0];r.checked=d.operation===o[0];
        r.dataset.key='book-discovery-op:'+n+':'+o[0];r.addEventListener('change',function(){if(r.checked){d.operation=o[0];}});
        lab.append(r,el('span','',o[1]));ask.append(lab);});
      if(present.length>1){ask.append(el('p','atl-note','About which concept it records?'));
        present.forEach(function(c){var lab=el('label','atl-book-choice'),r=el('input');r.type='radio';r.name='discovery-anchor-'+n;r.value=c.id;r.checked=d.anchor===c.id;
          r.dataset.key='book-discovery-anchor:'+n+':'+c.id;r.addEventListener('change',function(){if(r.checked)d.anchor=c.id;});
          lab.append(r,el('span','','“'+nodeName(c.id)+'”'));ask.append(lab);});}
      var draft=discoveryDraft(d);
      // The suggested question points to the evidence; the Book's own words travel only as Book evidence.
      if(!draft.text)draft.text='Does Book '+n+'’s '+said+' about “'+nodeName(d.anchor)+'” (attached as Book evidence) point to something '+
        'the Architecture should decide or change, or does it belong to Book '+n+' alone?';
      var label=el('label','atl-bookdev-label','Your question'),ta=el('textarea','atl-book-text');ta.id='atl-discovery-q-'+n;label.htmlFor=ta.id;
      ta.rows=4;ta.maxLength=4000;ta.value=draft.text;ta.dataset.key='book-discovery-q:'+n;
      ta.addEventListener('input',function(){draft.text=ta.value;});
      ask.append(label,ta);
      var go=actionButton(ask,'Take it to your coding agent',function(){d.handedOff=true;investigate(n,d,row,data);},'book-investigate:'+n);go.classList.add('atl-action-primary');
      ask.append(el('p','atl-note','Opens the coding-agent panel with your question and this element as Book evidence; you send it from there. '+
        'Sending prepares a request and changes nothing. If an answer suggests a change, you can develop one alternative into an Architecture revision, '+
        'review it and apply it yourself, or leave the Architecture as it is.'));
      box.append(ask,row2);det.append(box);
      if(d.focusPending){d.focusPending=false;global.setTimeout(function(){var t=folio.querySelector('[data-key="book-discovery-h:'+n+'"]');if(t){t.focus({preventScroll:true});reveal(t);}},0);}
    }
    // A decision's question is asked as the question itself. The Book's evidence is the decision element as its own
    // owner reads it now; the author writes the question. Asking changes neither the Architecture nor the Book.
    function askQuestion(n,q){
      if(!binding.onDevelop||!binding.books){refusal(n,'The Book cannot be read here, so its question cannot be asked about.');return;}
      binding.books.read(n).then(function(result){
        var data=result.data,row=(data.elements||[]).find(function(e){return e.id===q.decision_id;});
        if(!row){refusal(n,'The decision this question comes from is no longer in Book '+n+', so it cannot be asked about.');return;}
        var anchor={kind:'question',id:q.question_id};
        binding.onDevelop({conceptId:null,title:q.current_text||q.recorded_text||'Open question',anchor:anchor,
          precision:'question',subject:'Open question',quote:q.current_text||'',sourceRef:'open_questions/'+q.current_index,
          operation:'explore',draft:'',bookEvidence:{book_number:n,element_id:row.id,
            expected_book_request_sha256:data.book.request_sha256,expected_element_content_sha256:row.content_sha256,
            kind:B.kind(row.collection),text:row.text||'',revision_number:data.book.revision_number,
            standing:X.AUTHORITY[row.commitment_authority]||row.commitment_authority,
            epistemic_status:row.epistemic_status,attribution:row.attribution,anchors:[anchor]}});
      }).catch(function(error){refusal(n,'Could not read Book '+n+' to ask about its question: '+error.message);});
    }
    function investigate(n,d,row,data){
      var cn=conceptForNode(d.anchor),draft=discoveryDraft(d);
      if(!cn){refusal(n,'“'+d.anchor+'” is not in the working Architecture any more, so it cannot be asked about.');return;}
      var s=M.sourceAnchor(S.model,cn.id);
      if(!s.anchor||s.anchor.kind!=='node'||s.anchor.id!==d.anchor){refusal(n,'“'+cn.title+'” is not a recorded Architecture node here, so it cannot carry Book evidence.');return;}
      if(!draft.text.trim()){refusal(n,'Write your question first.');return;}
      binding.onDevelop({conceptId:cn.id,title:cn.title,anchor:JSON.parse(JSON.stringify(s.anchor)),precision:s.precision,subject:s.subject,quote:s.quote,
        sourceRef:s.sourceRef,operation:d.operation,draft:draft.text,
        bookEvidence:{book_number:n,element_id:row.id,expected_book_request_sha256:data.book.request_sha256,
          expected_element_content_sha256:row.content_sha256,kind:B.kind(row.collection),text:row.text||row.title||'',
          revision_number:data.book.revision_number,standing:X.AUTHORITY[row.commitment_authority]||row.commitment_authority,
          epistemic_status:row.epistemic_status,attribution:row.attribution,anchors:[d.anchor]}});
    }
    // Questions and consequences a Book records that cite a current Architecture concept: listed only, collapsed,
    // never pressed on the author. Each is the Book's own record; considering one is the author's choice.
    function renderBeyondBook(det,b,from){
      if(!binding.onDevelop||!binding.books||b.state!=='working')return;
      var seen={},items=[],open=discoveryFor(b.book_number);
      if(open)seen[open.element]=1;
      (b.references||[]).slice().sort(function(x,y){return (y.node_id===(from&&from.nodeId))-(x.node_id===(from&&from.nodeId));})
        .forEach(function(r){if(!r.present)return;(r.elements||[]).forEach(function(e){
        if(BEYOND[e.collection]&&!seen[e.id]){seen[e.id]=1;items.push({e:e,nodes:[]});}
        var it=items.filter(function(x){return x.e.id===e.id;})[0];if(it&&it.nodes.indexOf(r.node_id)<0)it.nodes.push(r.node_id);});});
      if(!items.length)return;
      var dd=el('details','atl-series-how');dd.dataset.key='book-beyond:'+b.book_number;
      dd.append(el('summary','','Questions and consequences Book '+b.book_number+' records about the Architecture · '+items.length));
      dd.append(el('p','atl-note','Listed from Book '+b.book_number+'’s own record: each cites a current Architecture concept. None is a finding; consider one only if it interests you.'));
      var ul=el('ul','atl-series-elements');
      items.slice(0,12).forEach(function(it){var li=el('li','');
        li.append(el('span','atl-series-kind',(X.COLLECTION[it.e.collection]||M.human(it.e.collection))+' · cites '+I.andList(it.nodes.map(function(id){return '“'+nodeName(id)+'”';}))));
        li.append(el('span','atl-series-text',B.clip(it.e.text||'',200)));
        discoverButton(li,b,it.e,from,true);ul.append(li);});
      dd.append(ul);if(items.length>12)dd.append(el('p','atl-note',(items.length-12)+' more in the Book record.'));
      det.append(dd);
    }
    function renderLeafBooks(d,from,l){
      var wb=d.sources.working_books;if(!wb||wb.state==='absent')return;
      var sec=leafSection('Working Book architectures · this canvas',wb.authority_note);
      if(wb.state==='unreadable'){sec.append(toneLine({tone:'bad',text:'The working Book architectures could not be read ('+wb.reason+'). Nothing from them is shown.'}));return;}
      var list=wb.books.slice().sort(function(a,b){return (b.book_number===l.book)-(a.book_number===l.book)||a.book_number-b.book_number;});
      list.forEach(function(b){
        var det=el('details','atl-series-record');det.dataset.book=String(b.book_number);
        det.open=b.book_number===l.book||list.length===1||!!b.development||!!devFor(b.book_number)||!!discoveryFor(b.book_number);
        det.append(el('summary','','Book '+b.book_number+(b.title?' · '+b.title:'')));
        if(b.state!=='working'){det.append(toneLine({tone:'bad',text:'Its working record is damaged and cannot be read, so nothing from it is shown.'}));
          if(b.reason){var tech=el('details','atl-series-how');tech.dataset.key='book-tech:'+b.book_number;
            tech.append(el('summary','','Technical detail'),el('p','atl-note',b.reason));det.append(tech);}
          sec.append(det);return;}
        var chips=el('p','atl-provenance');chips.append(chip('Working · agent proposal · not accepted','proposal'));det.append(chips);
        if(I&&I.entry(b).architectureChanged||I&&I.entry(b).sourceChanged||I&&I.entry(b).unrecorded.length)renderBookImpact(det,b,from);
        else X.bookFreshness(b).forEach(function(f){det.append(toneLine(f));});
        det.append(factList([['Question',b.question],['Pressure',b.pressure]]));
        if(from){
          var ref=from.nodeId&&(b.references||[]).filter(function(r){return r.node_id===from.nodeId;})[0];
          if(ref){
            var box=el('div','atl-series-about');
            box.append(el('h5','atl-series-subtitle','What Book '+b.book_number+' records about “'+from.title+'”'));
            var st=X.refStanding(ref);if(st)box.append(toneLine(st));
            var ul=el('ul','atl-series-elements');
            var la=b.last_applied,touched=la?la.changed.concat(la.added):[],gone=la&&la.withdrawal?la.withdrawal.element_id:null;
            ref.elements.forEach(function(e){var li=el('li','');
              li.append(el('span','atl-series-kind',(X.COLLECTION[e.collection]||M.human(e.collection))+(e.via==='name_source'?' · takes its name from this concept':'')));
              li.append(el('span','atl-series-text',e.text));
              li.append(chip(X.AUTHORITY[e.commitment_authority]||M.human(e.commitment_authority),'proposal'));
              // A Book revision is marked as a change to the working Book, never to the Architecture concept.
              if(gone===e.id)li.append(chip('Withdrawn in working Book revision '+la.revision_number,'book-changed'));
              else if(touched.indexOf(e.id)>=0)li.append(chip('Changed in working Book revision '+la.revision_number,'book-changed'));
              if(binding.books&&e.collection!=='open_author_decisions'){var dv=actionButton(li,'Develop this element',function(){openDevelop(b.book_number,[e.id],false,from);},'book-dev:'+b.book_number+':'+e.id);
                dv.classList.add('atl-action-quiet');dv.setAttribute('aria-label','Develop this '+(X.COLLECTION[e.collection]||'element').toLowerCase()+' of Book '+b.book_number);}
              discoverButton(li,b,e,from);
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
        renderDiscovery(det,b,from);
        renderBeyondBook(det,b,from);
        var others=(b.references||[]).filter(function(r){return !from||r.node_id!==from.nodeId;});
        if(others.length){
          var o=el('div','atl-series-others');
          o.append(el('h5','atl-series-subtitle',(from?'Other Architecture concepts it refers to · ':'Architecture concepts it refers to · ')+others.length));
          var row=el('div','atl-revised-index');
          others.forEach(function(r){var target=conceptForNode(r.node_id),label=target?target.name:(I?I.refName(r):(r.title||r.node_id));
            var btn=el('button','atl-index-item',label+(r.present?'':' · no longer in the Architecture'));btn.type='button';
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
        if((b.question_references||[]).length){
          var qbox=el('div','atl-decision-questions');
          qbox.append(el('h5','atl-series-subtitle','Open questions these decisions refer to'));
          var qul=el('ul','atl-series-elements');
          var QSTAND={current_wording:'The question as it now stands; the decision refers to it.',
            moved:'Same wording, now at another position.',
            reworded:'Wording changed since the decision was written; the question keeps its identity. It may warrant reconsideration.',
            moved_and_reworded:'Moved and reworded since the decision was written. It may warrant reconsideration.',
            removed:'No longer open in the Architecture. Removing it is not an answer.',
            identity_not_established:'A recorded wording reference; this question has no identity yet.',
            version_unavailable:'The Architecture version this decision was written against cannot be read.',
            binding_mismatch:'The recorded wording does not match the version the Book names.'};
          b.question_references.forEach(function(q){
            var li=el('li','');
            li.append(el('span','atl-series-text',q.current_text||q.recorded_text||'(no recorded wording)'));
            li.append(el('span','atl-series-kind',QSTAND[q.state]||q.state));
            if(q.recorded_text&&q.current_text&&q.recorded_text!==q.current_text)
              li.append(el('span','atl-series-kind','Earlier wording: '+q.recorded_text));
            li.append(el('span','atl-technical',(q.question_id?q.question_id+' · ':'')+'decision '+q.decision_id));
            if(Q&&binding.getArchitectureQuestions&&q.question_id){
              // The question as the Architecture records it, with its history; Back returns to this Book.
              actionButton(li,'Read this question',function(){openQuestion({id:q.question_id});},'book-read-question:'+b.book_number+':'+q.decision_id).classList.add('atl-action-quiet');}
            if(binding.onDevelop&&q.question_id&&q.decision_id&&['current_wording','moved','reworded','moved_and_reworded'].indexOf(q.state)>=0){
              var askQ=actionButton(li,'Ask about this question',function(){askQuestion(b.book_number,q);},'book-question:'+b.book_number+':'+q.decision_id);
              askQ.classList.add('atl-action-quiet');
            }
            qul.append(li);
          });
          qbox.append(qul);det.append(qbox);
        }
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
    // Unsent words belong to what they were written for: one draft per Book and scope.
    function scopeKey(dev){return dev.holistic?'whole':dev.targets.slice().sort().join(',');}
    function bookDraft(n,key){S.drafts=S.drafts||{};var k=bookKey(n)+'|'+key;return S.drafts[k]||(S.drafts[k]={instruction:''});}
    function responseDraft(n){S.responses=S.responses||{};var k=bookKey(n);return S.responses[k]||(S.responses[k]={text:''});}
    function bookNote(n,tone,text,phase){S.notes=S.notes||{};S.notes[bookKey(n)]=tone?{tone:tone,text:text,phase:phase||null}:null;}
    // A refusal is said where the author is looking and announced, so the live region never says the opposite.
    function refusal(n,text){bookNote(n,'bad',text);announce(text);}
    function busy(n){S.busy=S.busy||{};return S.busy[bookKey(n)]||null;}
    function setBusy(n,what){S.busy=S.busy||{};S.busy[bookKey(n)]=what;}
    function devFor(n){var d=S.dev;return d&&d.canvas===canvasKey()&&d.book===n?d:null;}
    function openOnce(key){S.openDetails=S.openDetails||{};S.openDetails[key]=true;}
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
        (mine.then||[]).forEach(function(f){f(r.data,mine.data);});
      },function(error){
        var mine=S.books[k];if(!mine||mine.seq!==seq)return;
        S.books[k]={status:'error',error:error&&error.message||String(error),data:mine.data,readAt:mine.readAt,seq:seq};renderFolio();
      });
    }
    function focusKey(key){global.setTimeout(function(){var t=folio.querySelector('[data-key="'+cssEscape(key)+'"]');
      if(t){t.focus({preventScroll:false});}},0);}
    function requestScope(n,dev){
      if(dev.holistic||!dev.targets.length||!binding.books.scope||dev.scope)return;
      Promise.resolve(binding.books.scope(n,dev.targets)).then(function(r){
        if(S.dev!==dev||r.canvasId!==canvasKey())return;dev.scope=r.data;renderFolio();
      },function(error){if(S.dev!==dev)return;dev.scopeError=error&&error.message||String(error);renderFolio();});
    }
    function openDevelop(n,targets,holistic,from,seed){
      S.dev={canvas:canvasKey(),book:n,targets:(targets||[]).slice(),holistic:!!holistic,from:from?from.id:null,
        replace:!!(seed&&seed.replace),scope:null,focusPending:true,caretTop:!!(seed&&seed.caretTop)};
      var dev=S.dev,d=bookDraft(n,scopeKey(dev));
      // The author's own unsent words for this target come first; an earlier request's words fill only an empty draft.
      if(seed&&seed.instruction&&!d.instruction)d.instruction=seed.instruction;
      bookNote(n,null);
      readBook(n,true);requestScope(n,dev);renderFolio();
      announce('Developing Book '+n+'. Write what should change; preparing calls no model and changes nothing in the Book.');
    }
    function closeDevelop(n){var dev=devFor(n);S.dev=null;renderFolio();
      focusKey(dev&&dev.targets.length===1?'book-dev:'+n+':'+dev.targets[0]:'series-back');}
    function nodeName(nodeId){var c=conceptForNode(nodeId);return c?c.title:nodeId;}
    function renderBookDevelopment(det,b,from){
      if(!binding.books)return;
      var n=b.book_number,summary=b.development,dev=devFor(n),st=bookState(n),k=bookKey(n),note=S.notes&&S.notes[k];
      if(!summary&&!dev&&!note)return;
      if(!st)readBook(n,false);
      // The context and this Book's own read can disagree only for a moment: the newer read decides.
      else if(st.status==='ready'&&S.seriesCtx&&S.seriesCtx.readAt&&st.readAt<S.seriesCtx.readAt&&
        (((summary&&summary.request_sha256)||null)!==(st.data.pending&&st.data.phase!=='none'?st.data.pending.request_sha256:null)||
         (st.data.book&&st.data.book.revision_number!==b.revision_number)))readBook(n,true);
      st=bookState(n);
      var data=st&&st.data,box=el('section','atl-book-dev');box.setAttribute('aria-label','Developing Book '+n);
      box.append(el('h5','atl-series-subtitle','Developing Book '+n+(data&&data.book?' · working revision '+data.book.revision_number:'')));
      if(note&&note.phase&&data&&data.phase!==note.phase)note=null;
      if(note){var np=toneLine(note,'atl-book-note');np.tabIndex=-1;np.dataset.key='book-note:'+n;box.append(np);}
      if(!data){box.append(el('p','atl-note',st&&st.status==='error'?'Could not read Book '+n+'’s revision state: '+st.error:'Reading Book '+n+'’s revision state…'));
        if(st&&st.status==='error')actionButton(box,'Try again',function(){readBook(n,true);},'book-retry:'+n);det.append(box);return;}
      if(data.state==='unreadable'){box.append(toneLine({tone:'bad',text:'Book '+n+' could not be read ('+data.reason+'). Nothing can be prepared for it here.'}));det.append(box);return;}
      if(data.state!=='working'){box.append(el('p','atl-note','Book '+n+' has no working architecture to revise.'));det.append(box);return;}
      if(st.status==='error')box.append(toneLine({tone:'bad',text:'Could not read Book '+n+' again: '+st.error+'. Showing the read of '+readTime(st)+'.'}));
      var phase=data.phase,line=B.phaseLine(phase,n);
      // The phase is said once: a note about this same step already says it.
      if(line&&!dev&&!(note&&note.phase===phase))box.append(toneLine(line));
      if(phase==='stale'&&!dev)renderStale(box,n,data,from);
      else if(phase==='awaiting_coding_agent'&&!dev)renderAwaiting(box,n,data,from);
      else if((phase==='review_ready'||phase==='review_blocked')&&!dev)renderBookReview(box,n,data,from);
      if(dev)renderComposer(box,n,b,data,dev,from);
      det.append(box);
    }
    function scopeWords(n,pending,data){
      if(!pending)return '';
      if(pending.mode==='holistic')return 'Any element of Book '+n+'.';
      var chosen=B.labels(data.elements,pending.targets),rest=B.labels(data.elements,(pending.dependents||[]));
      return chosen.join('; ')+(rest.length?'; and, so their references stay true, '+rest.join('; '):'')+'. Every other element stays as it is.';
    }
    function targetLines(parent,n,data,dev,from){
      var map={};data.elements.forEach(function(e){map[e.id]=e;});
      var card=el('div','atl-book-target');
      card.append(el('p','atl-series-book','Book '+n+(data.book.title?' · '+data.book.title:'')+' · working revision '+data.book.revision_number));
      if(dev.holistic)card.append(el('p','atl-series-line','The whole Book: your coding agent may change any of its elements.'));
      dev.targets.forEach(function(id){var e=map[id];if(!e)return;
        card.append(el('p','atl-series-line',B.kind(e.collection)+(dev.holistic?' you started from':'')));
        if(e.text)card.append(el('p','atl-series-text',e.text));
        var p=el('p','atl-provenance');p.append(chip('Working · '+(X.AUTHORITY[e.commitment_authority]||M.human(e.commitment_authority||'element')),'proposal'));card.append(p);
        if(from&&from.nodeId)card.append(el('p','atl-note',e.series_refs.indexOf(from.nodeId)>=0?
          'It records a reference to “'+from.title+'”, the concept you came from.':'It records no reference to “'+from.title+'” itself.'));
      });
      X.bookFreshness(data.book).forEach(function(f){if(f.tone!=='ok')card.append(toneLine(f));});
      var ids=el('details','atl-series-how');ids.dataset.key='book-ids:'+n;ids.append(el('summary','','Exact identifiers'));
      ids.append(factList([['Elements',dev.targets.join(', ')||'whole Book'],['Book request',data.book.request_sha256],
        ['Book content',data.book.content_sha256],['Architecture node',from&&from.nodeId||''],['Architecture request',data.book.series_request_sha256]]));
      card.append(ids);parent.append(card);
    }
    function renderComposer(box,n,b,data,dev,from){
      var busyNow=busy(n),outOfDate=data.book.freshness!=='ready';
      if(outOfDate)dev.holistic=true;
      var d=bookDraft(n,scopeKey(dev));
      var form=el('div','atl-book-compose');
      form.append(el('p','atl-kicker-line',dev.holistic?'Revise the whole Book':'Revise one element'));
      targetLines(form,n,data,dev,from);
      var scope=el('fieldset','atl-book-scope');scope.append(el('legend','','How far may the revision reach?'));
      function radio(value,label,detail){var lab=el('label','atl-book-choice'),r=el('input');r.type='radio';r.name='book-scope-'+n;r.value=value;
        r.checked=value==='holistic'?dev.holistic:!dev.holistic;r.dataset.key='book-scope:'+n+':'+value;
        r.addEventListener('change',function(){if(!r.checked)return;
          // The words move with the author to the other scope, unless that scope already has words of its own.
          var was=bookDraft(n,scopeKey(dev));dev.holistic=value==='holistic';var now=bookDraft(n,scopeKey(dev));
          if(!now.instruction&&was.instruction){now.instruction=was.instruction;was.instruction='';}
          requestScope(n,dev);renderFolio();});
        lab.append(r,el('span','',label));scope.append(lab);if(detail)scope.append(el('p','atl-note',detail));}
      if(outOfDate)scope.append(toneLine({tone:'warn',text:'Book '+n+(data.book.series_changed&&data.book.source_changed?
        ' was written against an earlier working Architecture, and its own source changed since. ':data.book.source_changed?
        '’s own source changed after it was written. ':' was written against an earlier working Architecture. ')+
        'Only a revision of the whole Book can bring it up to date, so a revision here covers the whole Book: '+
        'your coding agent may then bring every element up to date, and the review shows each one.'}));
      if(dev.targets.length&&!outOfDate){
        var map={};data.elements.forEach(function(e){map[e.id]=e;});
        radio('targeted',dev.targets.length===1?'Only this element':'Only these elements',dev.scope?B.scopeSentence(dev.scope,map)+
          (dev.scope.dependents.length?' They are: '+B.labels(map,dev.scope.dependents).join('; ')+'.':''):dev.scopeError?'Could not check which elements refer to it: '+dev.scopeError:'Checking which elements refer to it…');
      }
      radio('holistic','The whole Book',outOfDate?'':'Use this only when the change cannot stay inside the chosen element. Your coding agent may then change any element of Book '+n+', and the review shows each one.');
      form.append(scope);
      var label=el('label','atl-bookdev-label','What should change?'),ta=el('textarea','atl-book-text');ta.id='atl-book-instruction-'+n;label.htmlFor=ta.id;
      ta.rows=Math.max(4,Math.min(12,(d.instruction.match(/\n/g)||[]).length+3));ta.maxLength=4000;ta.value=d.instruction;ta.dataset.key='book-instruction:'+n;
      ta.placeholder='For example: make the cost of refusing the count visible inside this mechanism.';
      var count=el('p','atl-note atl-book-count');count.setAttribute('aria-live','polite');
      function counted(){count.textContent=ta.value.length>3500?ta.value.length+' of 4000 characters':'';}
      ta.addEventListener('input',function(){d.instruction=ta.value;counted();});counted();
      form.append(label,ta,count);
      if(data.pending){
        var rp=el('label','atl-book-choice'),cb=el('input');cb.type='checkbox';cb.checked=!!dev.replace;cb.dataset.key='book-replace:'+n;
        cb.addEventListener('change',function(){dev.replace=cb.checked;});
        var waiting=data.pending.instruction?' (“'+B.clip(data.pending.instruction,80)+'”)':'';
        rp.append(cb,el('span','',data.phase==='stale'?'Replace the request that no longer matches the Book'+waiting:
          data.pending.completed?'Replace the waiting request'+waiting+', whose review is ready; that review can then no longer be applied':
          'Replace the request that is already waiting'+waiting+'; it can then no longer be applied'));
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
      var d=bookDraft(n,scopeKey(dev)),st=bookState(n),data=st&&st.data,k=bookKey(n),canvas=canvasKey();
      if(busy(n)||!data||data.state!=='working')return;
      if(!d.instruction.trim()){refusal(n,'Write what should change first. Nothing was prepared.');renderFolio();focusKey('book-instruction:'+n);return;}
      var body={instruction:d.instruction,targets:dev.holistic?[]:dev.targets,holistic:!!dev.holistic,
        expected_book_request_sha256:data.book.request_sha256};
      if(data.pending){if(!dev.replace){refusal(n,'A request for Book '+n+' is already waiting. Tick “Replace…” to prepare this one instead; nothing was prepared.');
        renderFolio();focusKey('book-replace:'+n);return;}
        body.replace_pending_request_sha256=data.pending.request_sha256;body.replace_pending_reviewed=!!data.pending.completed;}
      setBusy(n,'prepare');renderFolio();
      var call;try{call=Promise.resolve(binding.books.prepare(n,body));}catch(error){call=Promise.reject(error);}
      call.then(function(r){
        setBusy(n,null);if(r.canvasId!==canvas||canvasKey()!==canvas)return;
        S.books[k]={status:'ready',data:r.data,readAt:new Date(),seq:S.bookSeq=(S.bookSeq||0)+1};
        d.instruction='';if(S.dev===dev)S.dev=null;
        bookNote(n,'ok','Prepared for your coding agent. Nothing in Book '+n+' has changed. Give it the message below, then check for its response.','awaiting_coding_agent');
        openOnce('book-agent:'+n);
        readSeries(true,false,true);renderFolio();focusKey('book-copy:'+n);
        announce('Request prepared for your coding agent. Nothing in Book '+n+' has changed.');
      },function(error){
        setBusy(n,null);if(error.canvasId&&error.canvasId!==canvasKey())return;
        var message=error&&error.message||String(error);
        // A waiting request whose review arrived meanwhile is replaced only after the author has seen that.
        if(/review of it is now ready/.test(message))dev.replace=false;
        refusal(n,'Not prepared: '+message+'. Your words are kept.');
        readBook(n,true);renderFolio();focusKey('book-note:'+n);
      });
    }
    // A partial request prepared elsewhere on an out-of-date Book: it cannot bring the Book up to date, and while
    // the Book cites a concept the Architecture no longer has, an answer outside those citing elements cannot pass.
    function partialOnStale(box,n,p,from){
      var b=I&&S.seriesCtx&&S.seriesCtx.data?X.workingBooks(S.seriesCtx.data).filter(function(x){return x.book_number===n;})[0]:null;
      var e=b?I.entry(b):null,allowed=p.permitted_ids||[],blocking=[];
      if(e)e.removed.forEach(function(r){(r.elements||[]).forEach(function(x){if(allowed.indexOf(x.id)<0&&blocking.indexOf(x.id)<0)blocking.push(x.id);});});
      box.append(toneLine({tone:'warn',text:'This request revises only part of Book '+n+', which was already out of date when it was prepared. Applying it would '+
        'leave the Book out of date.'+(blocking.length?' Elements outside it still cite a concept the Architecture no longer has ('+blocking.join(', ')+
        '), and every reference in the revised Book must resolve, so no answer to this request can pass.':'')}));
      if(e&&e.outOfDate&&!devFor(n))actionButton(box,'Prepare a whole-Book reconciliation instead',function(){
        S.leaf.book=n;openDevelop(n,[],true,from,{instruction:I.reconcileDraft(e,nodeName),caretTop:true,replace:true});},'impact-replace:'+n);
    }
    function renderAwaiting(box,n,data,from){
      var p=data.pending;
      if(p.instruction){box.append(el('p','atl-series-kicker','You asked'),el('p','atl-book-asked',p.instruction));
        box.append(el('p','atl-series-kicker','It may change'),el('p','atl-note',scopeWords(n,p,data)));}
      if(p.stale_response_kept)box.append(toneLine({tone:'warn',text:'A response arrived for an earlier state of this Book and was kept as evidence; it was not reviewed.'}));
      if(p.baseline_out_of_date&&p.mode!=='holistic')partialOnStale(box,n,p,from);
      var give=el('details','atl-series-how');give.dataset.key='book-agent:'+n;
      give.append(el('summary','','What to give your coding agent'));
      var msg=el('textarea','atl-book-text');msg.readOnly=true;msg.rows=7;msg.value=B.agentMessage(data.handoff,n,data.canvas_id,p);
      msg.setAttribute('aria-label','Message for your coding agent');give.append(msg);
      var copy=actionButton(give,'Copy the message',function(){
        function selectIt(){msg.focus();msg.select();announce('The message is selected; copy it with your keyboard.');}
        try{global.navigator.clipboard.writeText(msg.value).then(function(){announce('Message copied. Give it to your coding agent.');},selectIt);}catch(_){selectIt();}
      },'book-copy:'+n);copy.classList.add('atl-action-quiet');
      give.append(el('p','atl-note','The Studio does not run your coding agent. It fulfils the request with the Working Book owner’s own commands; submitting stores a review and changes nothing in the Book.'));
      if(data.request){var exact=el('details','atl-series-how');exact.dataset.key='book-exact:'+n;
        exact.append(el('summary','','The exact request · '+B.shortSha(p.request_sha256)));
        var raw=el('textarea','atl-book-text');raw.readOnly=true;raw.rows=6;raw.value=JSON.stringify(data.request,null,2);
        raw.setAttribute('aria-label','Exact host-agent request');exact.append(raw);give.append(exact);}
      var manual=el('details','atl-series-how');manual.dataset.key='book-manual:'+n;
      manual.append(el('summary','','Paste the coding agent’s response yourself'));
      var d=responseDraft(n),resp=el('textarea','atl-book-text');resp.rows=4;resp.value=d.text;resp.dataset.key='book-response:'+n;
      resp.setAttribute('aria-label','Your coding agent’s response (JSON)');resp.placeholder='The complete response JSON your coding agent produced for this request.';
      resp.addEventListener('input',function(){d.text=resp.value;});
      var v=actionButton(manual,busy(n)==='complete'?'Checking…':'Check this response',function(){completeBook(n);},'book-validate:'+n);v.disabled=!!busy(n);
      manual.insertBefore(resp,v);give.append(manual);box.append(give);
      var row=el('div','atl-actions');
      var chk=actionButton(row,'Check for your coding agent’s response',function(){checkResponse(n);},'book-check:'+n);chk.classList.add('atl-action-primary');
      actionButton(row,'Prepare a different request',function(){openDevelop(n,p.targets,p.mode==='holistic',from,{instruction:p.instruction,replace:true});},'book-redo:'+n);
      box.append(row);
    }
    function checkResponse(n){
      var before=bookState(n),was=before&&before.data&&before.data.phase,wasSha=before&&before.data&&before.data.pending&&before.data.pending.request_sha256;
      readSeries(true,false,true);
      readBook(n,true,function(data){
        var now=data.phase,nowSha=data.pending&&data.pending.request_sha256;
        if(wasSha&&nowSha&&wasSha!==nowSha){
          bookNote(n,'warn','Another request replaced the one shown here before; what it asks is shown below. Your earlier request can no longer be completed.');
          announce('Another request replaced the one shown here before.');renderFolio();return;}
        announce(now===was?(now==='awaiting_coding_agent'?'No response yet. Nothing in Book '+n+' has changed.':'Nothing changed.'):
          (B.phaseLine(now,n)||{text:'Book '+n+' was read again.'}).text);
        if(now!==was)focusKey(now==='review_ready'||now==='review_blocked'?'book-review:'+n:'book-check:'+n);
      });
    }
    function completeBook(n){
      var d=responseDraft(n),k=bookKey(n),canvas=canvasKey(),payload;
      if(busy(n))return;
      try{payload=JSON.parse(d.text);}catch(_){refusal(n,'The response must be one JSON object, exactly as your coding agent produced it. Nothing was submitted.');renderFolio();focusKey('book-note:'+n);return;}
      setBusy(n,'complete');renderFolio();
      Promise.resolve(binding.books.complete(n,payload)).then(function(r){
        setBusy(n,null);if(r.canvasId!==canvas||canvasKey()!==canvas)return;
        d.text='';S.books[k]={status:'ready',data:r.data,readAt:new Date(),seq:S.bookSeq=(S.bookSeq||0)+1};
        bookNote(n,null);readSeries(true,false,true);renderFolio();focusKey('book-review:'+n);
        announce((B.phaseLine(r.data.phase,n)||{text:'Response checked.'}).text);
      },function(error){
        setBusy(n,null);if(error.canvasId&&error.canvasId!==canvasKey())return;
        refusal(n,'The Working Book owner refused the response: '+String(error&&error.message||error).replace(/[.;\s]*$/,'')+'. Nothing was stored; the request is still open.');
        readBook(n,true);renderFolio();focusKey('book-note:'+n);
      });
    }
    function renderStale(box,n,data,from){
      var p=data.pending;
      box.append(el('p','atl-folio-detail','Why: '+B.staleReason(p)+'.'));
      if(p.instruction){box.append(el('p','atl-series-kicker','You asked'),el('p','atl-book-asked',p.instruction));}
      if(p.completed)box.append(el('p','atl-note','Its review was made against that earlier state, so it is not shown as applicable.'));
      var row=el('div','atl-actions');
      var again=actionButton(row,'Prepare it again against the current Book',function(){
        openDevelop(n,p.targets,p.mode==='holistic',from,{instruction:p.operation==='revise'?p.instruction:'',replace:true});},'book-redo:'+n);
      again.classList.add('atl-action-primary');box.append(row);
    }
    function wordedLine(parent,w){
      var head=w.key==='text'?'':w.field[0].toUpperCase()+w.field.slice(1)+' · ',parts=B.wordDiff(w.before,w.after);
      if(w.before!==null){var bl=el('span','atl-book-before',head+'Before: ');
        parts.before.forEach(function(p){bl.append(p[1]?el('del','',p[0]):document.createTextNode(p[0]));});parent.append(bl);}
      var al=el('span','atl-book-after',head+(w.before===null?'Now: ':'After: '));
      if(w.after===null)al.append(document.createTextNode('(removed)'));
      else parts.after.forEach(function(p){al.append(p[1]?el('mark','',p[0]):document.createTextNode(p[0]));});
      parent.append(al);
    }
    function reviewActions(n,data,from,g,end){
      var r=data.review,row=el('div','atl-actions'),ready=data.phase==='review_ready';
      if(ready){var ap=actionButton(row,busy(n)==='apply'?'Applying…':'Apply this revision to working Book '+n,function(){applyBook(n,r.request_sha256);},end?'book-apply-end:'+n:'book-apply:'+n);
        ap.classList.add('atl-action-primary');ap.disabled=!!busy(n);
        if(!end)row.append(el('p','atl-note','Applying changes this working Book only. It accepts nothing, and the Architecture, the Series plan and the Directions stay as they are.'));}
      else if(!end){var wide=B.widenedTargets(r,data.elements),seed=data.pending.operation==='revise'?r.instruction:'';
        if(wide.length&&r.mode!=='holistic'){var w=actionButton(row,'Prepare again, allowing those elements too',function(){
          openDevelop(n,wide,false,from,{instruction:seed,replace:true});},'book-widen:'+n);w.classList.add('atl-action-primary');}
        actionButton(row,'Prepare again for the whole Book',function(){openDevelop(n,[],true,from,{instruction:seed,replace:true});},'book-holistic:'+n);}
      if(!end){var seedText=data.pending.operation==='revise'?r.instruction:'';
        actionButton(row,'Prepare a different request',function(){openDevelop(n,data.pending.targets,data.pending.mode==='holistic',from,{instruction:seedText,replace:true});},'book-redo:'+n);}
      return row;
    }
    function renderBookReview(box,n,data,from){
      var r=data.review,g=B.reviewDigest(r,data.elements,nodeName,data.review_elements),ready=data.phase==='review_ready';
      var sec=el('div','atl-book-review');sec.setAttribute('aria-label','Review of the revision of Book '+n);
      var h=el('h5','atl-series-subtitle','Review · working revision '+g.fromRevision+' → '+g.toRevision);h.tabIndex=-1;h.dataset.key='book-review:'+n;sec.append(h);
      // The summary and the decision first; the detail below.
      sec.append(el('p','atl-book-summary',[g.changed.length+' changed',g.added.length+' added',g.removed.length+' removed',g.preserved+' unchanged'].join(' · ')+
        (g.unexpected.length?' · '+g.unexpected.length+' outside what you allowed':'')));
      sec.append(el('p','atl-series-kicker','You asked'),el('p','atl-book-asked',g.instruction));
      sec.append(el('p','atl-series-kicker','It could change'),el('p','atl-note',g.mode==='holistic'?'Any element of Book '+n+'.':scopeWords(n,data.pending,data)));
      if(data.pending&&data.pending.baseline_out_of_date&&g.mode!=='holistic')sec.append(toneLine({tone:'warn',text:'Book '+n+' was already out of date with the '+
        'working Architecture or its source when this was prepared, and it changes only part of the Book. Applying it changes those elements; the Book stays '+
        'recorded against its earlier Architecture and source, so it is still out of date afterwards.'}));
      if(g.unexpected.length){var u=el('div','atl-book-block');u.append(el('p','atl-tone atl-tone-bad','Outside what you allowed — this blocks Apply:'));
        var ul=el('ul','atl-series-elements');g.unexpected.forEach(function(x){ul.append(el('li','',x.text));});u.append(ul);sec.append(u);}
      sec.append(reviewActions(n,data,from,g,false));
      if(g.changed.length){sec.append(el('p','atl-series-kicker','Changed · '+g.changed.length));
        var cl=el('ul','atl-series-elements'),more=null;
        g.changed.forEach(function(c,i){var li=el('li','');
          li.append(el('span','atl-series-kind',c.label),el('span','atl-note',c.kind+'.'));
          c.worded.forEach(function(w){wordedLine(li,w);});
          if(c.status)li.append(el('span','atl-note','Working status: '+c.status.before+' → '+c.status.after+'.'));
          if(c.restated)li.append(el('span','atl-note','Restated in the explicit form, as every changed element written in the older form must be.'));
          if(c.other.length)li.append(el('span','atl-note','Also changed: '+c.other.join(', ')+'.'));
          if(i<6)cl.append(li);else{if(!more){more=el('details','atl-series-how');more.dataset.key='book-more:'+n;
            more.append(el('summary','','Show '+(g.changed.length-6)+' more changed elements'));more.append(el('ul','atl-series-elements'));}
            more.lastChild.append(li);}});
        sec.append(cl);if(more)sec.append(more);}
      if(g.added.length){sec.append(el('p','atl-series-kicker','Added · '+g.added.length));var al=el('ul','atl-series-elements');
        g.added.forEach(function(a){var li=el('li','');li.append(el('span','atl-series-kind',a.label));
          if(a.text)li.append(el('span','atl-book-after','New: '+a.text));
          if(a.refersTo.length)li.append(el('span','atl-note','Refers to '+a.refersTo.join('; ')+'.'));al.append(li);});sec.append(al);}
      if(g.removed.length){sec.append(el('p','atl-series-kicker','Removed · '+g.removed.length));var rl=el('ul','atl-series-elements');
        g.removed.forEach(function(x){rl.append(el('li','',x.label));});sec.append(rl);}
      sec.append(el('p','atl-note',X.plural(g.preserved,'other element')+' stay exactly as they are; the owner compared every element by content.'));
      if(g.rereadItems.length){sec.append(el('p','atl-series-kicker','To re-read · '+g.rereadItems.length));
        sec.append(el('p','atl-note','Each refers to an element this revision changes. The reference is recorded; whether it still holds is not.'));
        var ll=el('ul','atl-series-elements');g.rereadItems.forEach(function(t){ll.append(el('li','',t.label+' → '+t.via.join('; ')));});sec.append(ll);}
      if(g.seriesItems.length){sec.append(el('p','atl-series-kicker','Architecture concepts these elements cite · '+g.seriesItems.length));
        sec.append(el('p','atl-note','The Architecture is unchanged; check that the Book still fits each concept.'));
        var sl=el('ul','atl-series-elements');g.seriesItems.forEach(function(t){sl.append(el('li',t.exists?'':'atl-tone-bad',
          (t.exists?'“'+t.name+'”':t.name+' — no longer recorded in the working Architecture')+' · cited by '+t.citedBy.join('; ')));});sec.append(sl);}
      g.decisions.forEach(function(t){sec.append(toneLine({tone:'warn',text:t}));});
      if(g.authority.length)sec.append(el('p','atl-note','Standing changes: '+g.authority.join(' ')));
      if(g.unresolvedLabels.length)sec.append(el('p','atl-note','Reworded with no recorded dependency, so what follows from the change is not established: '+g.unresolvedLabels.join('; ')+'.'));
      var ids=el('details','atl-series-how');ids.dataset.key='book-reqid:'+n;ids.append(el('summary','','Request identity and baseline'));ids.append(factList(g.identity));
      if(g.note)ids.append(el('p','atl-note','The owner’s note: '+g.note));sec.append(ids);
      if(ready&&g.changed.length+g.added.length>3)sec.append(reviewActions(n,data,from,g,true));
      box.append(sec);
    }
    function applyBook(n,sha){
      var k=bookKey(n),canvas=canvasKey();
      if(busy(n))return;
      setBusy(n,'apply');renderFolio();
      var call;try{call=Promise.resolve(binding.books.apply(n,sha));}catch(error){call=Promise.reject(error);}
      call.then(function(r){
        setBusy(n,null);if(r.canvasId!==canvas||canvasKey()!==canvas)return;
        if(S.leaf){S.leaf.book=n;S.leaf.evidence=null;}
        var data=r.data,a=data.application||{},la=data.book&&data.book.last_applied;
        S.books[k]={status:'ready',data:data,readAt:new Date(),seq:S.bookSeq=(S.bookSeq||0)+1};
        if(a.result==='already_applied')bookNote(n,'note','That revision was already applied. Nothing changed.','none');
        else{var what=la?[].concat(la.changed.length?['changed '+B.labels(data.elements,la.changed).join('; ')]:[],
            la.added.length?['added '+B.labels(data.elements,la.added).join('; ')]:[],la.removed.length?['removed '+la.removed.join(', ')]:[]).join(', and '):'';
          var now=a.currentness==='kept_baseline'?' It changed only part of a Book that was out of date, so the Book is still recorded against its earlier Architecture and source.':
            data.book.freshness==='ready'?' Book '+n+' is now recorded as written against the current working Architecture.':'';
          bookNote(n,'ok','Applied to working Book '+n+', now working revision '+data.book.revision_number+(what?': '+what:'')+'.'+now+
            ' Only this working Book changed. The Architecture and its concepts, the Series plan and the Directions are unchanged, and nothing was accepted.','none');}
        S.revealKey='book-note:'+n;readSeries(true,false,true);renderFolio();focusAndReveal('book-note:'+n);
        announce(a.result==='already_applied'?'Already applied; nothing changed.':'Applied to working Book '+n+'.'+
          (a.currentness==='kept_baseline'?' It changed only part of the Book, which stays out of date.':data.book.freshness==='ready'?' It is now up to date.':'')+
          ' Only the working Book changed; the atlas is unchanged.');
      },function(error){
        setBusy(n,null);if(error.canvasId&&error.canvasId!==canvasKey())return;
        if(S.leaf)S.leaf.book=n;
        refusal(n,'Not applied: '+(error&&error.message||error)+'. Working Book '+n+' is unchanged.');
        S.revealKey='book-note:'+n;readBook(n,true);readSeries(true,false,true);renderFolio();focusAndReveal('book-note:'+n);
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
      else if(I){var books=impactLine();if(books)folio.append(books);}
      if(Q&&binding.getArchitectureQuestions)renderQuestionOverview();
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
      ribbon.append(el('span','atl-ribbon-note',' Selecting reveals in place; your records change only when you apply a reviewed revision.'));
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
      if(!desk.hidden&&e.target&&desk.contains(e.target)){
        // Escape in the desk's text fields does nothing, as in the folio; anywhere else it returns to the atlas.
        if(e.target.tagName==='TEXTAREA'||(e.target.tagName==='INPUT'&&/^(text|search)$/.test(e.target.type)))return;
        e.preventDefault();api.returnFocus();return;}
      // Escape first closes the read-only Series and Book context, back to the concept it was opened from.
      // Escape in a text field never closes the view around the words being written.
      if(e.target&&(e.target.tagName==='TEXTAREA'||(e.target.tagName==='INPUT'&&/^(text|search)$/.test(e.target.type)))&&folio.contains(e.target))return;
      // Escape closes an open question, then the list of them, back to where the author came from.
      if(S.opp&&S.opp.open&&!S.leaf&&!S.qv&&!S.qlist&&!(e.target.closest&&e.target.closest('details[open] summary'))){e.preventDefault();closeOpportunities();return;}
      if(S.qv&&!S.leaf&&!(e.target.closest&&e.target.closest('details[open] summary'))){e.preventDefault();closeQuestion();return;}
      if(S.qlist&&!S.leaf&&!S.qv&&!(e.target.closest&&e.target.closest('details[open] summary'))){e.preventDefault();closeQuestionList();return;}
      if(S.leaf&&S.discovery&&discoveryFor(S.discovery.book)&&!(e.target.closest&&e.target.closest('details[open] summary'))){
        e.preventDefault();closeDiscovery(S.discovery.book,false);return;}
      if(S.leaf&&S.leaf.evidence&&!(e.target.closest&&e.target.closest('details[open] summary'))){e.preventDefault();
        var n=S.leaf.evidence;S.leaf.evidence=null;S.leaf.book=null;renderFolio();
        global.setTimeout(function(){var t=folio.querySelector('[data-key="impact-show:'+n+'"]');if(t)t.focus({preventScroll:false});else focusFolio();},0);
        announce('Back to all the Books.');return;}
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
      var keepLeaf=S.leaf;S.leaf=null;if(sha!==prevSha){S.seriesStale=true;S.books={};S.questionsStale=true;}
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
        if(S.discovery&&S.discovery.handedOff)S.discovery.revisionApplied=true;
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
    // The desk is open only while a question, its answer or a revision review is being worked on. The folio steps
    // aside (inert, not removed), so the atlas keeps its selection, trail and orientation.
    function narrowLayout(){return !!(global.matchMedia&&global.matchMedia('(max-width:900px)').matches);}
    function setDesk(open,label,opts){
      open=!!open;opts=opts||{};
      if(label)deskTitle.textContent=label;
      root.classList.toggle('atl-desk-open',open);
      desk.hidden=!open;folio.inert=open;
      if(!open)return;
      if(narrowLayout()){if(!opts.quiet)desk.scrollIntoView({block:'start'});}
      else{
        // Beside the desk the concept under examination must stay in the open part of the atlas.
        var f=S.focus&&S.pos[S.focus],v=view(),clear=v.width-desk.offsetWidth-16;
        var sx=f&&S.cam?(f.x-S.cam.cx)*S.cam.z+v.width/2:0;
        if(f&&S.cam&&clear>0&&sx>clear*0.8){
          var target=clear*0.5;
          animate({camera:{cx:f.x-(target-v.width/2)/S.cam.z,cy:S.cam.cy,z:S.cam.z},cameraDuration:S.reduced?0:420});
          if(S.reduced)flushInstant();
        }
      }
      if(opts.reveal&&!opts.reveal.hidden)opts.reveal.scrollIntoView({block:'start'});
      if(opts.moveFocus)deskBack.focus({preventScroll:true});
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
    var api={setDesk:setDesk,setDeskNote:setDeskNote,deskHost:desk,deskOpen:function(){return !desk.hidden;},update:update,show:show,hide:hide,select:function(id,o){select(id,Object.assign({via:'atlas'},o||{}));},
      returnToAtlas:returnToAtlas,deeper:deeper,setTreatment:setTreatment,examine:examine,leaveConstellation:leaveConstellation,
      setReducedMotion:function(on){S.reduced=!!on;syncChrome();},
      fitAtlas:function(){fitAtlas(false);settle();},
      metrics:function(){return S.metrics;},
      setNarrative:setNarrative,
      // Back to the atlas where the author left it: keyboard focus on the selected concept, or the folio.
      // The author asked to check again: Book reads are refreshed, so an open card never shows an old revision.
      rereadBooks:function(){S.books={};S.questionsStale=true;if(S.leaf)readSeries(true,false,true);renderFolio();},
      returnFocus:function(){if(!desk.hidden)setDesk(false);var top=root.getBoundingClientRect().top;
        // Where the folio stacks below the atlas (narrow screens) the author must land on the atlas, where the applied
        // change is marked; focusing the discovery heading without revealing it keeps that view.
        var stacked=!!(global.matchMedia&&global.matchMedia('(max-width:900px)').matches);
        if(stacked||top<0||top>global.innerHeight*0.5)root.scrollIntoView({block:'start'});
        var dc=S.leaf&&S.discovery&&folio.querySelector('[data-key="book-discovery-h:'+S.discovery.book+'"]');
        // Focus follows what is on screen: on narrow screens the discovery sits below the atlas, so the atlas concept takes focus.
        if(dc&&!stacked){dc.focus({preventScroll:true});reveal(dc);announce('Back to Book '+S.discovery.book+'’s discovery. The atlas kept your place.');return;}
        var id=S.focus,b=id&&starEls[id];
        if(b){setRoving(id);b.focus({preventScroll:true});}else focusFolio();
        if(dc)announce('Back to the atlas. Book '+S.discovery.book+'’s discovery is below it.');},
      snapshot:function(){return {mode:S.mode,treatment:activeTreatment(),research:S.research,focus:S.focus,depth:S.depth,trail:S.trail.slice(),
        narrative:S.narrative,questions:{list:!!S.qlist,view:S.qv?{id:S.qv.id,index:S.qv.index,from:S.qv.returnLeaf?'book':S.qv.returnList?'list':'folio'}:null,
          status:S.qs?S.qs.status:null,version:S.qs&&S.qs.data?S.qs.data.current&&S.qs.data.current.request_sha256:null},book:{dev:S.dev?{book:S.dev.book,targets:S.dev.targets.slice(),holistic:S.dev.holistic}:null,
          discovery:S.discovery?{book:S.discovery.book,element:S.discovery.element,operation:S.discovery.operation,anchor:S.discovery.anchor}:null},series:{leaf:S.leaf?{from:S.leaf.from,book:S.leaf.book}:null,status:S.seriesCtx?S.seriesCtx.status:null,
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
