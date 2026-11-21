/* Living Narrative Atelier — experimental visual study (opt-in, presentation only).
   Pure model, stable atlas layout and local compositions for three unfolding treatments.
   Concepts and relationships come only from the source-qualified explanation packet and
   from recorded candidate fields; no edge is ever inferred from position, proximity or text.
   Nothing here writes the canvas, the candidate or any story artifact. */
(function(global){
  'use strict';
  var FACETS=['genres','emotions','timeline','tropes','structure','other'];
  var FACET_LABEL={genres:'Genres',emotions:'Reader emotions',timeline:'Story time',
    tropes:'Tropes',structure:'Structure & engines',other:'Themes, aesthetics & threads'};
  var FACET_SINGULAR={genres:'Genre',emotions:'Reader emotion',timeline:'Phase',
    tropes:'Trope',structure:'Structure',other:'Narrative idea'};
  var COVERED={genre:'genres',trope:'tropes',structure:'structure',engine:'structure',reader_experience:'emotions'};
  var TREATMENTS={A:'Progressive revelation',B:'Spatial choreography',C:'Contextual unfolding'};
  // A is the world, B the magnifying glass; C is kept only as a research comparison.
  var MODES={atlas:'Living atlas',constellation:'Focused constellation'};

  function hash(text){var h=2166136261;text=String(text);
    for(var i=0;i<text.length;i++){h^=text.charCodeAt(i);h=Math.imul(h,16777619);}return (h>>>0)/4294967295;}
  function clamp(v,a,b){return Math.max(a,Math.min(b,v));}
  function shorten(text,limit){
    text=String(text||'').replace(/\s+/g,' ').trim();limit=limit||42;
    if(text.length<=limit)return text;
    var cut=text.slice(0,limit),space=cut.lastIndexOf(' ');
    return (space>limit*0.55?cut.slice(0,space):cut).replace(/[,;:.\s]+$/,'')+'…';
  }
  function capital(text){text=String(text||'');return text.charAt(0).toUpperCase()+text.slice(1);}
  function human(text){return String(text||'').replace(/_/g,' ');}
  /* Presentation names drop a leading kind that only repeats what the interface already shows
     ("Trope: The Bought Seal" in the Tropes band). The recorded title is never changed and stays
     available to the folio, call-outs and assistive names. */
  var KIND_WORDS={genres:['genre'],emotions:['reader experience','reader emotion','emotion'],timeline:['phase'],
    tropes:['trope'],structure:['structure'],other:[]};
  function presentedName(title,facet,category){
    var m=/^([^:]{2,40}):\s+(\S.*)$/.exec(String(title||''));if(!m)return String(title||'');
    var kind=m[1].trim().toLowerCase();
    return kind===human(category).toLowerCase()||(KIND_WORDS[facet]||[]).indexOf(kind)>=0?m[2]:String(title);
  }
  /* A recorded Book scope as a heading: "opening_books_duration_unknown" reads "Opening Books"
     (its unknown duration stays in the folio), "book_12" reads "Book 12", "books_13_14" "Books 13–14". */
  function bookLabel(scope){
    var raw=String(scope||'whole_story'),unknown=/_duration_unknown$/.test(raw),s=raw.replace(/_duration_unknown$/,'');
    var m=/^books?_(\d+)(?:_(\d+))?$/.exec(s);
    var text=m?(m[2]?'Books '+m[1]+'–'+m[2]:'Book '+m[1]):capital(human(s)).replace(/\bbooks\b/g,'Books').replace(/\bbook\b/g,'Book');
    return {text:text,durationUnknown:unknown};
  }

  /* ---------- Model: concepts and recorded relationships ---------- */
  function buildModel(candidate,requestSha){
    var api=global.AuteurStudioExplanations;
    if(!api||typeof api.project!=='function')throw Error('Explanation contract unavailable');
    var c=candidate||{},packet=api.project(c,requestSha||null,null);
    var nodes=c.nodes||[],nmap={},phaseMap={},contracts=c.genre_contracts||[];
    nodes.forEach(function(n){nmap[n.id]=n;});
    (c.phases||[]).forEach(function(p){phaseMap[p.id]=p;});
    var concepts=[],byId={},relations=[],relById={};
    function tierOf(facet,entry){
      if(entry.nodeId||facet==='timeline'||facet==='other')return 1;
      return /^(genre:|emotion:|complex:)/.test(entry.key)?1:2;
    }
    function scopeOf(entry){
      if(entry.nodeId&&nmap[entry.nodeId])return nmap[entry.nodeId].scope||'whole_story';
      if(entry.phaseId&&phaseMap[entry.phaseId])return phaseMap[entry.phaseId].scope||'whole_story';
      return null;
    }
    function add(facet,entry,extra){
      var id=facet+'|'+entry.key;if(byId[id])return byId[id];
      var tier=tierOf(facet,entry),title=String(entry.title||entry.key);
      var concept={id:id,facet:facet,key:entry.key,title:title,label:shorten(title,tier===1?40:46),
        detail:entry.detail||'',role:entry.role||'',sourceRef:entry.sourceRef||null,
        nodeId:entry.nodeId||null,phaseId:entry.phaseId||null,ownerGenreId:entry.ownerGenreId||null,
        tier:tier,scope:scopeOf(entry),entry:entry,coverage:entry.coverageMessage||null};
      if(extra)Object.keys(extra).forEach(function(k){concept[k]=extra[k];});
      if(!concept.name)concept.name=presentedName(concept.title,facet,concept.category||(nmap[concept.nodeId]||{}).category);
      if(!(extra&&extra.label))concept.label=shorten(concept.name,tier===1?40:46);
      concepts.push(concept);byId[id]=concept;return concept;
    }
    ['genres','emotions','timeline','tropes','structure'].forEach(function(facet){
      (packet[facet]||[]).forEach(function(entry){
        var extra=null;
        if(facet==='emotions'&&/^emotion:/.test(entry.key)){
          var target=(c.emotion_targets||[]).find(function(t){return 'emotion:'+t.id===entry.key;});
          var shown=capital(entry.title)+(entry.role?' · '+entry.role:'');extra={title:capital(entry.title),name:shown,label:shown,record:target||null};
        }
        if(facet==='timeline'){var ph=phaseMap[entry.phaseId];extra={order:ph?ph.order:0,record:ph||null};}
        if(entry.nodeId&&nmap[entry.nodeId])extra=Object.assign(extra||{},{record:nmap[entry.nodeId],category:nmap[entry.nodeId].category});
        if(facet==='genres'&&entry.contract)extra=Object.assign(extra||{},{record:entry.contract});
        add(facet,entry,extra);
      });
    });
    // Complex emotions are recorded components the explanation packet does not list.
    (c.complex_emotions||[]).forEach(function(ce){
      add('emotions',{key:'complex:'+ce.id,title:ce.title,detail:ce.context||'',role:'complex emotion',
        sourceRef:'complex_emotions/'+ce.id},{record:ce,label:shorten(ce.title,40)});
    });
    // Candidate nodes outside the five explanation facets keep their recorded category.
    nodes.forEach(function(n){
      if(COVERED[n.category])return;
      add('other',{key:'node:'+n.id,title:n.title,detail:n.summary||'',role:human(n.category),
        nodeId:n.id,sourceRef:'nodes/'+n.id},{record:n,category:n.category});
    });
    function relate(from,to,verb,sourceRef,sourceKind,reason,reverseVerb,id){
      if(!byId[from]||!byId[to]||from===to||!verb||!sourceRef)return;
      id=id||(requestSha+':'+sourceRef+':'+from+':'+to);
      if(relById[id])return;
      var r={id:id,from:from,to:to,verb:verb,reverseVerb:reverseVerb||null,reason:reason||null,
        sourceRef:sourceRef,sourceKind:sourceKind||'architecture_proposal'};
      relations.push(r);relById[id]=r;
    }
    // Grammatical inversions of the contract's own fixed verbs (never of agent-written link text).
    var INVERSE={'targets reader emotion':'targeted by','lists trope function':'a trope function of',
      'describes narrative engine':'the narrative engine of','describes structural pattern':'the structural pattern of',
      'uses local trope function':'a local trope function of','uses local structural function':'a local structural function of'};
    (packet.links||[]).forEach(function(l){
      relate(l.fromFacet+'|'+l.fromKey,l.targetFacet+'|'+l.targetKey,l.relationVerb,l.sourceRef,
        l.sourceKind,l.reason,l.reverseVerb||(l.sourceKind!=='proposal_edge'&&INVERSE[l.relationVerb])||null,l.id);
    });
    function nodeConcept(nodeId){
      var n=nmap[nodeId];if(!n)return null;
      var facet=COVERED[n.category];
      if(!facet)return 'other|node:'+nodeId;
      if(facet==='genres')return contracts.some(function(x){return x.genre_node_id===nodeId;})?
        'genres|genre:'+nodeId:'genres|genre-node:'+nodeId;
      return facet+'|'+({tropes:'trope-node:',emotions:'emotion-node:'}[facet]||'structure-node:')+nodeId;
    }
    // Proposal edges the packet cannot express (an endpoint outside its facets).
    (c.links||[]).forEach(function(e,i){
      var a=nodeConcept(e.source),b=nodeConcept(e.target);
      if(a&&b&&e.function&&(a.indexOf('other|')===0||b.indexOf('other|')===0))
        relate(a,b,e.function,'links/'+i,'proposal_edge');
    });
    contracts.forEach(function(ct){
      (ct.complex_emotion_ids||[]).forEach(function(ceId,i){
        relate('genres|genre:'+ct.genre_node_id,'emotions|complex:'+ceId,'targets complex emotion',
          'genre_contracts/'+ct.genre_node_id+'/complex_emotion_ids/'+i,'genre_contract',null,'targeted by');
      });
    });
    nodes.forEach(function(n){
      if(!n.parent_id)return;
      var a=nodeConcept(n.id),b=nodeConcept(n.parent_id);
      if(a&&b)relate(a,b,'is part of','nodes/'+n.id+'/parent_id','node_hierarchy',null,'contains');
    });
    (c.phases||[]).forEach(function(p){
      (p.parallel_with||[]).forEach(function(other,j){
        relate('timeline|phase:'+p.id,'timeline|phase:'+other,'runs parallel with',
          'phases/'+p.id+'/parallel_with/'+j,'phase',null,'runs parallel with');
      });
    });
    var adjacency={};concepts.forEach(function(x){adjacency[x.id]=[];});
    relations.forEach(function(r){
      adjacency[r.from].push({relation:r,other:r.to,direction:'forward',verb:r.verb});
      adjacency[r.to].push({relation:r,other:r.from,direction:'reverse',
        verb:r.reverseVerb||('related through “'+r.verb+'”')});
    });
    // Prominence is the count of documented relationships, a recorded fact rather than a judgement.
    var maxDegree=1;concepts.forEach(function(x){x.degree=adjacency[x.id].length;maxDegree=Math.max(maxDegree,x.degree);});
    var timeline=concepts.filter(function(x){return x.facet==='timeline';})
      .sort(function(a,b){return (a.order||0)-(b.order||0)||a.id.localeCompare(b.id);});
    return {requestSha:requestSha||null,summary:c.summary||'',concepts:concepts,byId:byId,
      relations:relations,relById:relById,adjacency:adjacency,timeline:timeline,maxDegree:maxDegree,packet:packet,candidate:c};
  }

  /* ---------- Atlas: a stable "narrative score" ----------
     Bands hold kinds of narrative idea; the story-time spine runs left to right in recorded
     phase order. A concept's horizontal place follows the phases it is recorded as related to,
     so nearness reflects recorded phase activity only — never an inferred relationship.
     The score is laid out for the stage it is first read on: rows are spaced so that resting
     names have room at the whole-story view, then the layout never changes while exploring. */
  var BAND_ORDER=['genres','emotions','timeline','tropes','structure','other'];
  var LABEL_W=176,ROW_H=32,MOTE_GAP=15,REST_LABEL_PX=128,REST_ROW_PX=34,MOTE_PX=8;
  var GUTTER_WIDE=172,GUTTER_NARROW=96,ATLAS_LEFT=150;
  // Phone constellation list: first row below the focus, then one row per first- and second-order concept.
  var PHONE_LIST={start:84,near:50,far:44};
  // Minimal squared displacement with a minimum gap (isotonic regression, pool adjacent violators).
  function spread(wanted,gap,minX){
    var blocks=[];
    wanted.forEach(function(d,i){
      blocks.push({sum:d-i*gap,n:1});
      while(blocks.length>1){var b=blocks[blocks.length-1],a=blocks[blocks.length-2];
        if(a.sum/a.n<=b.sum/b.n)break;a.sum+=b.sum;a.n+=b.n;blocks.pop();}
    });
    var out=[],i=0;
    blocks.forEach(function(b){var v=b.sum/b.n;for(var k=0;k<b.n;k++){out.push(v+i*gap);i++;}});
    if(out.length&&out[0]<minX){var shift=minX-out[0];out=out.map(function(x){return x+shift;});}
    return out;
  }
  // The whole-story view: band names keep a gutter, the score fills the rest of the stage.
  // On a phone the score fits its height and the author travels along story time.
  function restCamera(atlas,view){
    var narrow=view.width<600,gutter=narrow?GUTTER_NARROW:GUTTER_WIDE,z;
    if(narrow){
      z=clamp((view.height-24)/atlas.height,0.3,1.05);
      return {cx:ATLAS_LEFT+(view.width/2-gutter)/z,cy:atlas.height/2,z:z};
    }
    var room=view.width-gutter-24;
    z=clamp(Math.min(room/(atlas.width-ATLAS_LEFT),(view.height-24)/atlas.height),0.2,1.05);
    var spare=Math.max(0,room-(atlas.width-ATLAS_LEFT)*z)/2;
    return {cx:ATLAS_LEFT-(gutter+spare-view.width/2)/z,cy:atlas.height/2,z:z};
  }
  function layoutAtlas(model,options){
    options=options||{};
    var view=options.view&&options.view.width>0&&options.view.height>0?options.view:null;
    var narrow=!!(view&&view.width<600);
    var o={labelW:LABEL_W,rowH:ROW_H,moteGap:MOTE_GAP,aspect:narrow?0:options.aspect};
    // On a phone the score is travelled along story time at a fixed reading zoom; it only has to fit
    // the stage's height, so its spacing is set once for that zoom.
    if(narrow){var zr=0.4;o.labelW=REST_LABEL_PX/zr;o.rowH=REST_ROW_PX/zr*0.9;o.moteGap=MOTE_PX/zr;}
    var atlas=layoutOnce(model,o);
    // A few deterministic passes settle the spacing that suits the whole-story zoom. When the stage
    // is wider than the score, story time is given the width: phases spread apart rather than leaving
    // the right of the stage empty, so phase and landmark names have room.
    for(var k=0;view&&!narrow&&k<6;k++){
      var z=restCamera(atlas,view).z,room=view.width-GUTTER_WIDE-24,span=Math.max(1,atlas.width-ATLAS_LEFT);
      var fill=span*z/room,heightBound=(view.height-24)/atlas.height<room/span;
      var want={labelW:clamp(REST_LABEL_PX/z,LABEL_W*0.94,LABEL_W*2.6),rowH:clamp(REST_ROW_PX/z,ROW_H,ROW_H*2.8),
        moteGap:clamp(MOTE_PX/z,MOTE_GAP,MOTE_GAP*2.2),
        phaseGap:heightBound&&fill<0.95?clamp(atlas.phaseGap/fill*0.97,atlas.basePhaseGap,atlas.basePhaseGap*2.6):atlas.phaseGap};
      if(Math.abs(want.labelW-o.labelW)<4&&Math.abs(want.rowH-o.rowH)<1.5&&Math.abs(want.phaseGap-atlas.phaseGap)<6)break;
      o.labelW=want.labelW;o.rowH=want.rowH;o.moteGap=want.moteGap;o.phaseGap=want.phaseGap;
      atlas=layoutOnce(model,o);
    }
    atlas.design={labelW:Math.round(o.labelW),rowH:Math.round(o.rowH),narrow:narrow,
      view:view?{width:view.width,height:view.height}:null};
    return atlas;
  }
  function layoutOnce(model,o){
    var positions={},rooms={},margin={left:200,right:150,top:44+o.rowH*1.25,bottom:70},LW=o.labelW,RH=o.rowH,MG=o.moteGap;
    var phases=model.timeline,groups=[],basePhaseGap=phases.length>8?238:phases.length>4?262:300,phaseGap=o.phaseGap||basePhaseGap,groupGap=70;
    phases.forEach(function(p){
      var scope=p.scope||'whole_story',last=groups[groups.length-1];
      if(!last||last.scope!==scope)groups.push(last={scope:scope,phases:[]});
      last.phases.push(p);
    });
    var x=margin.left+40;
    groups.forEach(function(g,gi){
      if(gi)x+=phaseGap+groupGap;
      g.x0=x;g.phases.forEach(function(p,i){if(i)x+=phaseGap;positions[p.id]={x:x,y:0};});
      g.x1=x;
    });
    var spanEnd=phases.length?x:margin.left+40+Math.max(900,Math.ceil(model.concepts.length/4)*LABEL_W*0.6);
    // Desired x: recorded phase relations first, then recorded neighbours, then an even spread.
    var desired={};phases.forEach(function(p){desired[p.id]=positions[p.id].x;});
    function mean(list){return list.length?list.reduce(function(s,v){return s+v;},0)/list.length:null;}
    model.concepts.forEach(function(cn){
      if(desired[cn.id]!==undefined)return;
      if(cn.phaseId&&model.byId['timeline|phase:'+cn.phaseId]){desired[cn.id]=desired['timeline|phase:'+cn.phaseId];return;}
      var m=mean(model.adjacency[cn.id].filter(function(a){return model.byId[a.other].facet==='timeline';})
        .map(function(a){return desired[a.other];}));
      if(m!==null)desired[cn.id]=m;
    });
    for(var pass=0;pass<3;pass++){
      model.concepts.forEach(function(cn){
        if(desired[cn.id]!==undefined)return;
        if(cn.ownerGenreId&&desired['genres|genre:'+cn.ownerGenreId]!==undefined){
          desired[cn.id]=desired['genres|genre:'+cn.ownerGenreId];return;}
        var m=mean(model.adjacency[cn.id].map(function(a){return desired[a.other];})
          .filter(function(v){return v!==undefined;}));
        if(m!==null)desired[cn.id]=m;
      });
    }
    var x0=margin.left+40,x1=Math.max(spanEnd,x0+600);
    BAND_ORDER.forEach(function(facet){
      var rest=model.concepts.filter(function(cn){return cn.facet===facet&&desired[cn.id]===undefined;})
        .sort(function(a,b){return a.title.localeCompare(b.title);});
      rest.forEach(function(cn,i){desired[cn.id]=x0+(x1-x0)*(rest.length===1?0.5:i/(rest.length-1));});
    });
    // Bands stack top to bottom; landmarks take staggered rows, motes gather in small
    // sunflower clouds around the place they belong to.
    var y=margin.top,bands=[],maxX=x1;
    BAND_ORDER.forEach(function(facet){
      var members=model.concepts.filter(function(cn){return cn.facet===facet;});
      if(!members.length)return;
      var band={facet:facet,label:FACET_LABEL[facet],y0:y,count:members.length};
      if(facet==='timeline'){
        var spineY=y+Math.max(46,RH*1.3);members.forEach(function(p){positions[p.id]={x:desired[p.id],y:spineY};rooms[p.id]=phaseGap;});
        band.y1=spineY+Math.max(64,RH*2.1);band.spineY=spineY;bands.push(band);y=band.y1+26;return;
      }
      var landmarks=members.filter(function(cn){return cn.tier===1;})
        .sort(function(a,b){return desired[a.id]-desired[b.id]||a.id.localeCompare(b.id);});
      // Few rows, each spread with minimal displacement from where its concepts want to be.
      var gap=LW*(facet==='genres'?1.3:0.94),span=Math.max(x1-x0+LW*1.2,640),rowTop=facet==='genres'?Math.max(30,RH*1.85):30;
      var rowCount=landmarks.length?Math.max(1,Math.ceil(landmarks.length*gap/span)):0;
      for(var r=0;r<rowCount;r++){
        var row=landmarks.filter(function(_,i){return i%rowCount===r;});
        // Use the room the band offers: a looser row keeps more of each name readable.
        var rowGap=Math.max(gap,Math.min(gap*1.7,span/Math.max(row.length,1)));
        var xs=spread(row.map(function(cn){return desired[cn.id]-LW*0.42;}),rowGap,margin.left);
        row.forEach(function(cn,i){positions[cn.id]={x:xs[i],y:y+rowTop+r*RH};
          rooms[cn.id]=i<row.length-1?Math.min(xs[i+1]-xs[i],LW*1.3):LW*1.3;
          maxX=Math.max(maxX,xs[i]+LW);});
      }
      var cloudTop=y+rowTop+Math.max(rowCount,landmarks.length?1:0)*RH+(landmarks.length?6:-10);
      var motes=members.filter(function(cn){return cn.tier===2;}),clouds={},order=[];
      motes.forEach(function(cn){
        var owner=cn.phaseId?'phase:'+cn.phaseId:cn.ownerGenreId?'genre:'+cn.ownerGenreId:'free:'+cn.id;
        if(!clouds[owner]){clouds[owner]={x:desired[cn.id],items:[]};order.push(owner);}
        clouds[owner].items.push(cn);
      });
      order.sort(function(a,b){return clouds[a].x-clouds[b].x||a.localeCompare(b);});
      var placedClouds=[],cloudDepth=0;
      order.forEach(function(key){
        var cloud=clouds[key],n=cloud.items.length,radius=MG*Math.sqrt(n)*0.62+6;
        var cx=cloud.x,cy=cloudTop+radius;
        placedClouds.forEach(function(o2){
          if(Math.abs(o2.x-cx)<o2.r+radius+14)cx=o2.x+o2.r+radius+14;
        });
        placedClouds.push({x:cx,r:radius});
        cloud.items.forEach(function(cn,i){
          var angle=i*2.39996323,dist=i?MG*0.62*Math.sqrt(i+0.5):0;
          positions[cn.id]={x:cx+Math.cos(angle)*dist,y:cy+Math.sin(angle)*dist};
        });
        cloudDepth=Math.max(cloudDepth,radius*2);maxX=Math.max(maxX,cx+radius);
      });
      band.y1=motes.length?cloudTop+cloudDepth+14:cloudTop+16;
      bands.push(band);y=band.y1+30;
    });
    var width=maxX+margin.right,height=y+margin.bottom-30;
    // A wide score is given vertical air to match the stage's proportions (computed once, then stable).
    var aspect=o.aspect>0?o.aspect:0,stretch=aspect?Math.min(2.4,Math.max(1,width/aspect/height)):1;
    if(stretch>1.02){
      Object.keys(positions).forEach(function(id){positions[id]={x:positions[id].x,y:positions[id].y*stretch};});
      bands.forEach(function(b){b.y0*=stretch;b.y1*=stretch;if(b.spineY)b.spineY*=stretch;});
      height*=stretch;
    }
    var books=groups.map(function(g){var bl=bookLabel(g.scope);return {scope:g.scope,label:bl.text,durationUnknown:bl.durationUnknown,x0:g.x0,x1:g.x1};});
    return {positions:positions,rooms:rooms,width:width,height:height,bands:bands,books:books,phaseGap:phaseGap,basePhaseGap:basePhaseGap,
      spine:phases.map(function(p){return positions[p.id];})};
  }

  /* ---------- Label placement around fixed glyphs ----------
     Cartographic point labelling: each label tries a few positions around its glyph, most
     important labels first. A label that cannot be set without overprinting another label, a
     glyph or the stage furniture stays quiet (its glyph remains; hover, focus and the folio name it).
     Glyphs never move to make room. Pure and deterministic, in screen pixels. */
  function placeRect(place,x,y,g,w,h){
    var d=g*0.62;
    switch(place){
      case 'e':return {x0:x+g,y0:y-h/2,x1:x+g+w,y1:y+h/2};
      case 'w':return {x0:x-g-w,y0:y-h/2,x1:x-g,y1:y+h/2};
      case 's':return {x0:x-w/2,y0:y+g,x1:x+w/2,y1:y+g+h};
      case 'n':return {x0:x-w/2,y0:y-g-h,x1:x+w/2,y1:y-g};
      case 'ne':return {x0:x+d,y0:y-d-h,x1:x+d+w,y1:y-d};
      case 'se':return {x0:x+d,y0:y+d,x1:x+d+w,y1:y+d+h};
      case 'nw':return {x0:x-d-w,y0:y-d-h,x1:x-d,y1:y-d};
      case 'sw':return {x0:x-d-w,y0:y+d,x1:x-d,y1:y+d+h};
      default:return {x0:x-w/2,y0:y-h/2,x1:x+w/2,y1:y+h/2};
    }
  }
  function placeLabels(items,obstacles,bounds){
    var CELL=64,grid={},result={};
    function cells(r,fn){
      for(var cx=Math.floor(r.x0/CELL);cx<=Math.floor(r.x1/CELL);cx++)
        for(var cy=Math.floor(r.y0/CELL);cy<=Math.floor(r.y1/CELL);cy++)fn(cx+','+cy);
    }
    function add(r,owner,soft){var box={r:r,owner:owner,soft:soft===true||soft==='hood'?soft:false};cells(r,function(k){(grid[k]||(grid[k]=[])).push(box);});}
    // soft:true obstacles (faint glyphs) may be covered by an item that allows it; soft:'hood' ones
    // (furniture already faded behind a focus) only by the focus neighbourhood itself.
    function hit(r,item,allowSoft){
      var found=false;
      cells(r,function(k){if(found||!grid[k])return;
        found=grid[k].some(function(b){
          if(b.owner===item.id)return false;
          if(b.soft===true&&allowSoft)return false;
          if(b.soft==='hood'&&item.overSoft===true)return false;
          return r.x0<b.r.x1&&b.r.x0<r.x1&&r.y0<b.r.y1&&b.r.y0<r.y1;});});
      return found;
    }
    (obstacles||[]).forEach(function(o){add(o.rect,o.owner||null,o.soft);});
    var b=bounds||{x0:-Infinity,y0:-Infinity,x1:Infinity,y1:Infinity};
    items.slice().sort(function(p,q){return q.priority-p.priority||(p.id<q.id?-1:p.id>q.id?1:0);}).forEach(function(item){
      var anchors=item.anchors||[{x:item.x,y:item.y}],chosen=null;
      function search(allowSoft){
        for(var v=0;v<item.variants.length;v++){
          var variant=item.variants[v];
          for(var a=0;a<anchors.length;a++)for(var p=0;p<item.places.length;p++){
            var r=placeRect(item.places[p],anchors[a].x,anchors[a].y,item.gap||0,variant.w,variant.h);
            if(r.x0<b.x0||r.y0<b.y0||r.x1>b.x1||r.y1>b.y1)continue;
            if(hit(r,item,allowSoft))continue;
            return {place:item.places[p],variant:variant.key,anchor:a,rect:r};
          }
        }
        return null;
      }
      // A label first looks for a place that covers nothing; only then may it cover a faint glyph.
      chosen=search(false)||(item.overSoft?search(true):null);
      if(!chosen&&item.required){
        var v0=item.variants[0],a0=anchors[0];
        chosen={place:item.places[0],variant:v0.key,anchor:0,rect:placeRect(item.places[0],a0.x,a0.y,item.gap||0,v0.w,v0.h),forced:true};
      }
      if(chosen)add(chosen.rect,item.id,false);
      result[item.id]=chosen;
    });
    return result;
  }

  /* ---------- Neighbourhoods and compositions ---------- */
  function neighbourhood(model,focusId,depth){
    var levels={},order=[];levels[focusId]=0;order.push(focusId);
    var first=[];
    model.adjacency[focusId].forEach(function(a){if(levels[a.other]===undefined){levels[a.other]=1;first.push(a.other);order.push(a.other);}});
    var second=[],hidden=0;
    if(depth>=2){
      var counts={};
      first.forEach(function(id){model.adjacency[id].forEach(function(a){
        if(levels[a.other]===undefined)counts[a.other]=(counts[a.other]||0)+1;});});
      second=Object.keys(counts).sort(function(a,b){return counts[b]-counts[a]||a.localeCompare(b);});
      hidden=Math.max(0,second.length-36);second=second.slice(0,36);
      second.forEach(function(id){levels[id]=2;order.push(id);});
    }
    var edges=model.relations.filter(function(r){return levels[r.from]!==undefined&&levels[r.to]!==undefined;})
      .map(function(r){var a=levels[r.from],b=levels[r.to];
        return {relation:r,level:Math.min(a,b)===0?1:(a===1&&b===1?1.5:2)};});
    return {focus:focusId,levels:levels,first:first,second:second,hiddenSecond:hidden,order:order,edges:edges};
  }
  function bandIndex(atlas,facet){var i=atlas.bands.findIndex(function(b){return b.facet===facet;});return i<0?0:i;}
  function bearing(model,atlas,focusId,id){
    var f=atlas.positions[focusId],p=atlas.positions[id];
    var dx=(p.x-f.x)/260,dy=(bandIndex(atlas,model.byId[id].facet)-bandIndex(atlas,model.byId[focusId].facet))*0.9+(p.y-f.y)/900;
    if(Math.abs(dx)<0.05&&Math.abs(dy)<0.05){dx=hash(id)-0.5;dy=hash(id+'y')-0.5;}
    return Math.atan2(dy,dx);
  }
  function labelWidth(model,id){var cn=model.byId[id];return Math.min(208,34+7*cn.label.length);}
  // The focus wears its title centred beneath its glyph, like the name under a constellation.
  // Labels keep their on-screen size at every zoom, so their world footprint is scaled by s = 1/zoom.
  function labelRect(model,id,pos,side,focusId,s){
    s=s||1;
    if(id===focusId)return {x0:pos.x-132*s,x1:pos.x+132*s,y0:pos.y-16*s,y1:pos.y+64*s};
    // Rail names alternate below and above the rail and wrap to at most 196px, so a half-width of 98px.
    if(side==='rail-s'||side==='rail-n'){var hw=Math.min(98,17+3.5*model.byId[id].label.length)*s;
      return side==='rail-s'?{x0:pos.x-hw,x1:pos.x+hw,y0:pos.y+10*s,y1:pos.y+48*s}:{x0:pos.x-hw,x1:pos.x+hw,y0:pos.y-48*s,y1:pos.y-10*s};}
    var w=labelWidth(model,id)*s,h=22*s;
    return side==='left'?{x0:pos.x-w,x1:pos.x+10*s,y0:pos.y-h/2,y1:pos.y+h/2}:
      {x0:pos.x-10*s,x1:pos.x+w,y0:pos.y-h/2,y1:pos.y+h/2};
  }
  function overlaps(a,b){return a.x0<b.x1&&b.x0<a.x1&&a.y0<b.y1&&b.y0<a.y1;}
  // Separate overlapping labels vertically; fixed items never move.
  function relax(model,items,targets,sides,fixed,focusId,s){
    for(var it=0;it<60;it++){
      var moved=false;
      for(var i=0;i<items.length;i++)for(var j=i+1;j<items.length;j++){
        var a=items[i],b=items[j];if(fixed[a]&&fixed[b])continue;
        var ra=labelRect(model,a,targets[a],sides[a],focusId,s),rb=labelRect(model,b,targets[b],sides[b],focusId,s);
        if(!overlaps(ra,rb))continue;
        var push=(Math.min(ra.y1,rb.y1)-Math.max(ra.y0,rb.y0))/2+2,down=targets[b].y>=targets[a].y?1:-1;
        if(targets[b].y===targets[a].y)down=a<b?1:-1;
        if(!fixed[a]&&!fixed[b]){targets[a]={x:targets[a].x,y:targets[a].y-push*down};targets[b]={x:targets[b].x,y:targets[b].y+push*down};}
        else if(fixed[a])targets[b]={x:targets[b].x,y:targets[b].y+push*2*down};
        else targets[a]={x:targets[a].x,y:targets[a].y-push*2*down};
        moved=true;
      }
      if(!moved)break;
    }
  }
  /* Two balanced arcs either side of the focus. Each concept keeps the side it lies on in the
     atlas (west or east); within a side, kinds of idea stay together in the atlas's band order. */
  function arcs(ids,angles,center,opts,targets,sides){
    var east=[],west=[];
    ids.forEach(function(id){(Math.cos(angles[id])>=0?east:west).push(id);});
    function vertical(id){return Math.abs(Math.cos(angles[id]));}
    while(Math.abs(east.length-west.length)>1+(opts.slack||0)){
      var from=east.length>west.length?east:west,to=from===east?west:east;
      from.sort(function(a,b){return vertical(a)-vertical(b)||a.localeCompare(b);});to.push(from.shift());
    }
    [[east,1],[west,-1]].forEach(function(pair){
      var col=pair[0],dir=pair[1];
      col.sort(function(a,b){return (opts.order?opts.order(a)-opts.order(b):Math.sin(angles[a])-Math.sin(angles[b]))||a.localeCompare(b);});
      var n=col.length,h=(n-1)*opts.gap,ry=Math.max(h/2+opts.gap*1.4,opts.ry),mid=opts.midY!==undefined?opts.midY:center.y;
      col.forEach(function(id,i){
        var dy=mid-center.y-h/2+i*opts.gap,t=Math.sqrt(Math.max(0,1-(dy/ry)*(dy/ry)));
        targets[id]={x:center.x+dir*(opts.minDx+(opts.rx-opts.minDx)*t),y:center.y+dy};
        sides[id]=dir>0?'right':'left';
      });
    });
  }
  function parentOf(model,hood,id){
    return hood.first.find(function(p){return model.adjacency[id].some(function(a){return a.other===p;});});
  }
  /* A — every concept keeps its atlas place. B — the neighbourhood is recomposed into a balanced
     constellation around the focus: phases it is recorded with run in recorded story order along a
     story-time rail beneath it, as in the atlas, and the other kinds of idea, which have no recorded
     order, keep to two arcs grouped by kind. C — relationships are revealed in place, and only
     neighbours whose place hurts readability (far away or colliding) move into the same oriented arcs. */
  function storyOrder(model,id){var i=model.timeline.indexOf(model.byId[id]);return i<0?Infinity:i;}
  function compose(model,atlas,hood,treatment,view){
    var targets={},sides={},moved=[],home=atlas.positions,focus=hood.focus,f=home[focus];
    Object.keys(home).forEach(function(id){targets[id]={x:home[id].x,y:home[id].y};});
    var visible=hood.order;
    visible.forEach(function(id){sides[id]='right';});
    var angles={};visible.forEach(function(id){if(id!==focus)angles[id]=bearing(model,atlas,focus,id);});
    // Compositions are designed in screen pixels at the zoom they will be read at (s = 1/zoom).
    var view0=view||{width:1100,height:640,z:1},n1=hood.first.length,s=1/(view0.z||1);
    var narrow=view0.width<600;
    var rx=clamp(140+n1*7,190,Math.max(190,Math.min(330,view0.width/2-235)));
    var inner={rx:rx*s,minDx:Math.min(140,rx-40)*s,gap:30*s,ry:150*s};
    var outerOpts=function(){return {rx:(rx+210)*s,minDx:(rx+60)*s,gap:26*s,ry:200*s,slack:2,
      order:function(id){var p=parentOf(model,hood,id);return p&&targets[p]?targets[p].y:f.y;}};};
    var fixed={};fixed[focus]=true;
    function kindThenBearing(id){return BAND_ORDER.indexOf(model.byId[id].facet)*10+Math.sin(angles[id]);}
    function place(ids,outer){
      if(!ids.length)return;
      if(narrow){
        // Narrow screens: one list beneath the focus title, read top to bottom, grouped by kind and
        // with phases in story order; each item hangs from a single trunk below the focus.
        var pitch=outer?PHONE_LIST.far:PHONE_LIST.near;
        ids.slice().sort(function(a,b){var fa=BAND_ORDER.indexOf(model.byId[a].facet),fb=BAND_ORDER.indexOf(model.byId[b].facet);
          return fa-fb||(storyOrder(model,a)-storyOrder(model,b))||(outer?0:Math.sin(angles[a])-Math.sin(angles[b]))||a.localeCompare(b);})
          .forEach(function(id,i){targets[id]={x:f.x+(outer?44:22)*s,y:f.y+(stemY+i*pitch)*s};sides[id]='right';});
        stemY+=ids.length*pitch;return;
      }
      if(outer){ids.forEach(function(id){var p=parentOf(model,hood,id),t=targets[p]||f;angles[id]=Math.atan2(t.y-f.y,t.x-f.x);});
        arcs(ids,angles,f,outerOpts(),targets,sides);}
      else arcs(ids,angles,f,Object.assign({order:kindThenBearing},inner,railIds.length?{midY:f.y-46*s}:{}),targets,sides);
    }
    // The story-time rail: recorded phases in recorded order, left to right, beneath the focus.
    function rail(ids){
      var n=ids.length,avail=Math.max(260,(view0.width-150)),step=n>1?clamp(avail/(n-1),96,190):0;
      ids.forEach(function(id,i){targets[id]={x:f.x+(i-(n-1)/2)*step*s,y:f.y+176*s};sides[id]=i%2?'rail-n':'rail-s';});
    }
    var stemY=PHONE_LIST.start,railIds=[];
    if(treatment==='B'){
      var others=hood.first;
      if(!narrow&&model.byId[focus].facet!=='timeline'){
        railIds=hood.first.filter(function(id){return model.byId[id].facet==='timeline';})
          .sort(function(a,b){return storyOrder(model,a)-storyOrder(model,b)||a.localeCompare(b);});
        if(railIds.length<2)railIds=[];
        others=hood.first.filter(function(id){return railIds.indexOf(id)<0;});
      }
      place(others,false);
      if(railIds.length){rail(railIds);railIds.forEach(function(id){fixed[id]=true;});}
      place(hood.second,true);
      if(!narrow)relax(model,visible,targets,sides,fixed,focus,s);
    }else if(treatment==='C'){
      var keepRadius=Math.min(view0.width,view0.height*1.6)*(narrow?0.3:0.42)*s;
      var placedRects=[labelRect(model,focus,f,'right',focus,s)],movers=[];
      // Nearest first: the closest readable neighbours anchor the composition in their atlas place.
      hood.first.slice().sort(function(a,b){return dist(home[a],f)-dist(home[b],f)||a.localeCompare(b);}).forEach(function(id){
        var rect=labelRect(model,id,home[id],'right',focus,s);
        var crowded=placedRects.some(function(r){return overlaps(r,rect);});
        if(dist(home[id],f)<=keepRadius&&!crowded){fixed[id]=true;placedRects.push(rect);}
        else movers.push(id);
      });
      place(movers,false);
      var outerMovers=[];
      hood.second.forEach(function(id){
        var rect=labelRect(model,id,home[id],'right',focus,s);
        var crowded=placedRects.some(function(r){return overlaps(r,rect);});
        if(dist(home[id],f)<=keepRadius*1.2&&!crowded){fixed[id]=true;placedRects.push(rect);}
        else outerMovers.push(id);
      });
      place(outerMovers,true);
      relax(model,visible,targets,sides,fixed,focus,s);
    }
    visible.forEach(function(id){
      if(dist(targets[id],home[id])>1)moved.push(id);
    });
    return {targets:targets,sides:sides,moved:moved,rail:railIds};
  }
  function dist(a,b){var dx=a.x-b.x,dy=a.y-b.y;return Math.sqrt(dx*dx+dy*dy);}

  /* ---------- Machine-readable study measures ---------- */
  function measure(model,atlas,hood,composition,z){
    var t=composition.targets,home=atlas.positions,visible=hood.order;
    var moves=composition.moved.map(function(id){return dist(t[id],home[id]);});
    var rects=visible.map(function(id){return labelRect(model,id,t[id],composition.sides[id],hood.focus,1/(z||1));});
    var overlapsCount=0;
    for(var i=0;i<rects.length;i++)for(var j=i+1;j<rects.length;j++)if(overlaps(rects[i],rects[j]))overlapsCount++;
    var xs=visible.map(function(id){return t[id].x;}),ys=visible.map(function(id){return t[id].y;});
    var firstEdges=hood.edges.filter(function(e){return e.level===1;}),crossings=0;
    function seg(e){return [t[e.relation.from],t[e.relation.to]];}
    for(var a=0;a<firstEdges.length;a++)for(var b=a+1;b<firstEdges.length;b++)
      if(cross(seg(firstEdges[a]),seg(firstEdges[b])))crossings++;
    var reach=hood.first.map(function(id){return dist(t[id],t[hood.focus]);});
    return {visible:visible.length,first:hood.first.length,second:hood.second.length,
      moved:composition.moved.length,meanMove:Math.round(avg(moves)),maxMove:Math.round(Math.max.apply(null,moves.concat([0]))),
      labelOverlaps:overlapsCount,firstEdgeCrossings:crossings,
      extent:{width:Math.round(Math.max.apply(null,xs)-Math.min.apply(null,xs)+LABEL_W),
        height:Math.round(Math.max.apply(null,ys)-Math.min.apply(null,ys)+22)},
      meanReach:Math.round(avg(reach)),maxReach:Math.round(Math.max.apply(null,reach.concat([0])))};
  }
  function avg(list){return list.length?list.reduce(function(s,v){return s+v;},0)/list.length:0;}
  function cross(s,t){
    function o(a,b,c){return Math.sign((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x));}
    var p=s[0],q=s[1],r=t[0],u=t[1];
    if(p===r||p===u||q===r||q===u)return false;
    return o(p,q,r)!==o(p,q,u)&&o(r,u,p)!==o(r,u,q);
  }

  global.AuteurStudioAtelierModel={FACETS:FACETS,FACET_LABEL:FACET_LABEL,FACET_SINGULAR:FACET_SINGULAR,
    TREATMENTS:TREATMENTS,MODES:MODES,buildModel:buildModel,layoutAtlas:layoutAtlas,restCamera:restCamera,
    neighbourhood:neighbourhood,compose:compose,measure:measure,labelRect:labelRect,placeRect:placeRect,
    placeLabels:placeLabels,shorten:shorten,human:human,capital:capital,presentedName:presentedName,bookLabel:bookLabel,
    PHONE_LIST:PHONE_LIST};
})(window);
