/** Read-only presentation routing. URL is restricted to public, synthetic fixture IDs. */
const modes=new Set(['overview','anatomy','comparison','mechanism']);
const ids=/^[a-z0-9_-]{1,80}$/;
const publicStories=new Set(['paladin','hybrid']);
const same=(a,b)=>a?.kind===b?.kind&&a?.id===b?.id;

export function visitRoute(current,destination,viaLinkId=null,snapshot={}) {
  if(current.perspective===destination.perspective && same(current.focus,destination.focus)) return current;
  const {trail=[],returnScrollY,returnFocusLocator,...prior}=current;
  const previous={...prior,scrollY:snapshot.scrollY||0,focusLocator:snapshot.focusLocator||null};
  return {...current,perspective:destination.perspective,focus:destination.focus||null,
    viaLinkId,trail:[...trail,previous].slice(-12),returnScrollY:null,returnFocusLocator:null};
}

export function returnRoute(current) {
  const trail=current.trail||[];
  if(!trail.length)return current;
  const previous=trail[trail.length-1];
  const {scrollY=0,focusLocator=null,...prior}=previous;
  return {...prior,trail:trail.slice(0,-1),returnScrollY:scrollY,returnFocusLocator:focusLocator};
}

export function reconcileRoute(route,model,links=[]) {
  const exists=(f)=>!f || (f.kind==='genre'?model.genres.some(g=>g.id===f.id):
    f.kind==='item'?model.items.some(i=>i.id===f.id):false);
  if(route.storyId!==model.story_id || !modes.has(route.perspective) || !exists(route.focus) ||
      route.viaLinkId && !links.some(l=>l.id===route.viaLinkId)) {
    return {route:{storyId:model.story_id,perspective:'overview',focus:null,viaLinkId:null,trail:[]},
      issue:'This reference or its source is unavailable in this story. Returned to Overview.'};
  }
  const viable=(route.trail||[]).filter(x=>x.storyId===model.story_id && modes.has(x.perspective) && exists(x.focus) &&
    (!x.viaLinkId || links.some(l=>l.id===x.viaLinkId))).slice(-12);
  return {route:{...route,trail:viable},issue:null};
}

export function serializeFixtureRoute(route) {
  if(!publicStories.has(route.storyId)||!modes.has(route.perspective)) throw new Error('Unknown public fixture/view');
  const args=new URLSearchParams({story:route.storyId,view:route.perspective});
  if(route.focus){
    if(!['genre','item'].includes(route.focus.kind)||!ids.test(route.focus.id))throw new Error('Unsafe public fixture reference');
    args.set('kind',route.focus.kind);args.set('key',route.focus.id);
  }
  return '#'+args.toString();
}

export function parseFixtureRoute(hash) {
  if(!hash || !hash.startsWith('#'))return null;
  const args=new URLSearchParams(hash.slice(1));
  const storyId=args.get('story'),perspective=args.get('view'),kind=args.get('kind'),id=args.get('key');
  if(!publicStories.has(storyId)||!modes.has(perspective))return null;
  if((kind||id) && (!['genre','item'].includes(kind)||!ids.test(id||'')))return null;
  return {storyId,perspective,focus:kind?{kind,id}:null,viaLinkId:null,trail:[]};
}
