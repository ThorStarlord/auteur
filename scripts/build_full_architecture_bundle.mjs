/** Build the Studio classic script from the exact-tested ESM Full Architecture sources. */
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const root=new URL('../',import.meta.url);
const sources=[
 'docs/prototypes/full-architecture/projection.mjs',
 'docs/prototypes/full-architecture/review.mjs',
 'docs/prototypes/focused-unfolding/full-view.mjs',
 'docs/prototypes/focused-unfolding/review-view.mjs'
];
const text=sources.map(path=>readFileSync(new URL(path,root),'utf8').replace(/^export /gm,''));
const fingerprint=createHash('sha256').update(text.join('\n')).digest('hex');
const output=`/* Generated from tested Full Architecture ESM sources. SHA256 ${fingerprint}\n   Regenerate: node scripts/build_full_architecture_bundle.mjs */\n(function(global){\n'use strict';\n${text.join('\n')}\nglobal.AuteurStudioFullArchitecture={project:projectFullArchitecture,review:reviewFullArchitecture,renderFull:renderFullArchitecture,renderReview:renderReviewArchitecture};\n})(window);\n`;
writeFileSync(new URL('../src/auteur/beginner/browser/studio_full_architecture.js',import.meta.url),output);
console.log('Full Architecture browser bundle',output.length,'bytes, SHA256',fingerprint);
