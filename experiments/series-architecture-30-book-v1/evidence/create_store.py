import sys
from pathlib import Path
from auteur.beginner.studio_store import CanvasStore
root = Path(sys.argv[1]); canvas = sys.argv[2]
store = CanvasStore(root, canvas)
store.create()
vision = (
    "Fixed author brief for a 30-Book epic fantasy Series. Experience: wonder, discovery, "
    "meaningful adventure, everyday belonging, emotionally consequential relationships and an "
    "ultimately hopeful possibility of flourishing. The Series must transform its civilization, "
    "institutions, relationships and narrative concerns across generations. Major victories change "
    "the world rather than restore the initial situation. Some conflicts emerge from consequences of "
    "earlier successes. Several characters, communities or institutions have independent agency. The "
    "Series permits local closure plus continuing long-range questions, and must not depend on "
    "escalating antagonists, arbitrary new threats or indefinitely postponed revelations. Use a fresh "
    "original Series concept; do not reuse the prior Wandering Islands answers, Book 11 prose or crossing mechanism. "
    "Scope of this exercise: an abstract whole-Series architecture only, not manuscripts or per-Book outlines."
)
store.apply("create-item", expected_revision=0, command_id="vision-created",
            payload={"item": {"id": "story-vision", "kind": "note", "title": "Story Vision",
                              "content": vision},
                     "position": {"x": 20, "y": 50}})
print("created", store.canvas_id)
