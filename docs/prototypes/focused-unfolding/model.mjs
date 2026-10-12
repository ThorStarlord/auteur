/** Pure, noncanonical illustration of source-scoped, author-governed unfolding. */
const catalogue = Object.freeze({
  emotion: [
    ['earned-breakthrough','Earned breakthrough','trope','might turn sustained effort into cathartic joy','A possible expression of achievement, not a reliable prediction of the audience'],
    ['generosity-empowers','Generosity empowers others','trope','might make care and mutual growth emotionally desirable','Potentially uplifting, but generosity needs concrete consequences'],
    ['restoration-after-loss','Restoration after loss','trope','might deliver relief and renewed possibility','Restoration works only if loss and recovery are earned'],
    ['community-belonging','Belonging to a community','relationship','might provide warmth through shared accomplishment','Belonging needs lived scenes, not only declarations']
  ],
  premise: [
    ['living-stakes','Hope and stakes','emotion','asks which reader experience the premise aims to support','A suggested intention, not an automatic effect'],
    ['opposing-force','A credible opposing force','conflict','might expose what makes the premise difficult','Do not invent a villain as if one is already established'],
    ['unusual-choice','The protagonist’s defining choice','structure','could turn the premise into a repeatable story engine','Actual character agency must be authored'],
    ['social-meaning','Whose daily life changes?','theme','could reveal the premise’s human consequences','A prompt for exploration, not a canonical fact']
  ],
  character: [
    ['emotional-need','Emotional need','emotion','could expose a reader-facing reason to care','A character desire is not itself a guaranteed reader emotion'],
    ['internal-contradiction','Internal contradiction','conflict','could create meaningful difficult choices','A contradiction is one option, not an obligatory flaw'],
    ['relationship-mirror','A meaningful relationship','relationship','could challenge the character’s values','A proposed dynamic, not an established connection'],
    ['heroic-decision','A defining decision','structure','could give the character agency in the plot','The actual arc remains to be authored']
  ],
  trope: [
    ['challenge-growth','Challenge → Growth → Responsibility','structure','might turn the trope into a renewable narrative engine','A pattern proposal, not a proven genre requirement'],
    ['test-of-values','Test of values','conflict','could make adopting the trope morally consequential','The conflict must fit the actual story'],
    ['relational-payoff','Shared payoff','relationship','might link personal progress to a community','Avoid assuming every progress arc includes this'],
    ['unexpected-cost','Unexpected cost of success','structure','could prevent advancement from becoming automatic','An optional complication, not an inevitability']
  ],
  genre: [
    ['reader-promise','Reader promise','emotion','asks what experience this genre might invite','Absent verified Genre Pack rules remain unknown'],
    ['genre-mechanism','Genre mechanism','structure','asks which repeatable narrative pattern the story needs','Do not invent a verified morphology'],
    ['trope-possibility','Adapted convention','trope','could reinterpret a familiar convention for this story','Not a claim of a mandatory trope']
  ],
  structure: [
    ['pressure','Escalating pressure','conflict','might create stakes that transform over time','Not all stories need escalation in the same form'],
    ['emotional-result','Reader payoff','emotion','asks what the mechanism is intended to make possible','Intended impact is not measured reader response'],
    ['thematic-choice','Thematic decision','theme','could connect mechanics with meaning','An optional causal hypothesis']
  ],
  setting: [
    ['everyday-habitat','Everyday life worth protecting','theme','might make the world emotionally habitable','An optional worldbuilding emphasis'],
    ['pressure-on-place','Place under pressure','conflict','could connect setting to plot','Not every setting needs external destruction'],
    ['resident-relationship','Community relationships','relationship','might reveal why the place matters','A proposed social dimension']
  ],
  theme: [
    ['action-that-tests','Choice that tests the idea','structure','could dramatize rather than declare the theme','An illustrative structure option'],
    ['moral-tension','Competing values','conflict','might keep the theme from becoming a lecture','Not a required binary opposition'],
    ['human-connection','Relationship embodiment','relationship','could show the theme in daily life','A hypothesis about expression']
  ],
  conflict: [
    ['cost-of-action','Meaningful consequence','structure','could make the conflict matter beyond spectacle','Consequences need authorial design'],
    ['feeling-under-pressure','Emotional intention under pressure','emotion','asks what feeling the struggle aims to evoke','Not a guaranteed effect'],
    ['affected-others','People affected','relationship','could broaden the stakes','Do not invent relationships as accepted facts']
  ],
  relationship: [
    ['bond-effect','What this bond changes','structure','might give the relationship narrative consequence','A suggested structural question'],
    ['care-and-conflict','Care under pressure','conflict','could test mutual commitments','A possibility, not required drama'],
    ['shared-affect','Shared emotional payoff','emotion','might create warmth or tension for the reader','Only an intended effect']
  ],
  other: [
    ['reader-question','Intended reader response','emotion','could clarify why this idea belongs in the story','A proposed question rather than a fact'],
    ['narrative-role','Narrative role','structure','could locate how this idea contributes','No relationship is accepted without author review']
  ]
});

const roles = new Set(Object.keys(catalogue));
const limitHistory = h => h.slice(-12);
const clone = state => ({...state, nodes:[...state.nodes], edges:[...state.edges], history:[...state.history], dismissed:[...state.dismissed], collapsed:[...state.collapsed]});
const findNode = (state,id) => state.nodes.find(node=>node.id===id);
const templatesFor = role => catalogue[role] || catalogue.other;
const keyFor=(state,focus,template)=>`ghost:${focus.id}:${template[0]}:${state.revision}:${focus.intentRevision||0}`;

export function createDemoState(story='paladin') {
  return {story, revision:`demo-${story}-v1`,nodes:[],edges:[],focusId:null,inspectedGhostId:null,
    dismissed:[],collapsed:[],history:[],nextSerial:1};
}
export function createAnchor(state,role,title) {
  if(!roles.has(role))throw new Error(`Unknown role ${role}`);
  const clean=String(title||'').trim();if(!clean||clean.length>120)throw new Error('Title must be 1–120 characters');
  const next=clone(state),id=`author-${next.nextSerial++}`;
  next.nodes.push({id,title:clean,role,authority:'author_working',canonical:false,
    origin:null,intentRevision:0,sourceFocusId:null,needsReview:false});
  next.history=next.focusId?limitHistory([...next.history,next.focusId]):[];
  next.focusId=id;next.inspectedGhostId=null;return next;
}
function allSuggestions(state) {
  const focus=findNode(state,state.focusId);if(!focus)return [];
  const adopted=new Set(state.nodes.flatMap(n=>n.origin?[n.origin.ghostId]:[]));
  return templatesFor(focus.role).map(template=>({
    id:keyFor(state,focus,template),templateKey:template[0],title:template[1],targetRole:template[2],
    why:template[3],caveat:template[4],sourceRef:`demo-fixture/${state.story}/${focus.role}/${template[0]}`,
    sourceKind:'illustrative_model_hypothesis',supportStatus:'hypothesis',requestSha:state.revision,
    originFocusId:focus.id,canonical:false,authority:'agent_proposal'}))
    .filter(g=>!adopted.has(g.id)&&!state.dismissed.includes(g.id));
}
export function suggestForFocus(state,limit=3,offset=0) {
  const count=Math.max(0,Math.min(3,Number.isFinite(limit)?Math.floor(limit):0));
  const start=Math.max(0,Math.floor(offset)||0);
  return allSuggestions(state).slice(start,start+count);
}
export function selectFocus(state,id) {
  if(!findNode(state,id))throw new Error(`Unknown focus ${id}`);
  if(state.focusId===id)return state;
  const next=clone(state);
  next.history=state.focusId?limitHistory([...next.history,state.focusId]):next.history;
  next.focusId=id;next.inspectedGhostId=null;return next;
}
export function returnFocus(state){
  if(!state.history.length)return state;
  const next=clone(state),id=next.history.pop();
  if(!findNode(next,id))return {...next,inspectedGhostId:null};
  next.focusId=id;next.inspectedGhostId=null;return next;
}
export function inspectGhost(state,ghostId) {
  if(!allSuggestions(state).some(g=>g.id===ghostId))throw new Error('Suggestion unavailable or stale');
  return {...state,inspectedGhostId:ghostId};
}
export function adoptGhost(state,ghostId) {
  const prior=state.nodes.find(n=>n.origin?.ghostId===ghostId);
  if(prior){if(prior.origin.requestSha!==state.revision)throw new Error('Suggestion source is stale');return state;}
  const ghost=allSuggestions(state).find(g=>g.id===ghostId);
  if(!ghost)throw new Error('Suggestion unavailable or stale');
  const next=clone(state),id=`author-${next.nextSerial++}`;
  next.nodes.push({id,title:ghost.title,role:ghost.targetRole,authority:'author_working',canonical:false,
    origin:{ghostId,sourceRef:ghost.sourceRef,requestSha:ghost.requestSha,sourceKind:ghost.sourceKind},
    sourceFocusId:ghost.originFocusId,intentRevision:0,needsReview:false});
  next.inspectedGhostId=null;return next;
}
export function dismissGhost(state,ghostId){
  if(!allSuggestions(state).some(g=>g.id===ghostId))throw new Error('Suggestion unavailable or stale');
  return {...state,dismissed:[...state.dismissed,ghostId],inspectedGhostId:null};
}
export function collapseCluster(state,id,collapsed=true){
  if(!findNode(state,id))throw new Error(`Unknown group focus ${id}`);
  return {...state,collapsed:collapsed?[...new Set([...state.collapsed,id])]:state.collapsed.filter(x=>x!==id)};
}
export function replaceSourceRevision(state,revision){
  if(!revision||revision===state.revision)return state;
  return {...state,revision,dismissed:[],inspectedGhostId:null};
}
export function editWorkingNode(state,id,title){
  const clean=String(title||'').trim();if(!clean||clean.length>120)throw new Error('Title must be 1–120 characters');
  if(!findNode(state,id))throw new Error(`Unknown working item ${id}`);
  return {...state,nodes:state.nodes.map(n=>n.id===id?{...n,title:clean,intentRevision:n.intentRevision+1}:
    n.sourceFocusId===id?{...n,needsReview:true}:n),inspectedGhostId:null};
}
