(() => {
  const chapter = new URLSearchParams(window.location.search).get("chapter") || "1";
  const acceptEndpoint = `/api/beginner/chapters/${chapter}/accept-latest-draft`;
  const status = document.getElementById("status");
  const action = document.getElementById("primary-action");
  fetch(`/api/beginner/chapters/${chapter}/review`)
    .then((response) => response.json())
    .then((review) => {
      status.textContent = review.production_status;
      document.getElementById("next-action").textContent = review.recommended_next_action;
      document.getElementById("evidence").textContent = JSON.stringify({
        blocking_findings: review.blocking_findings,
        warnings: review.warnings,
        plan_alignment: review.plan_alignment,
      }, null, 2);
      action.textContent = review.accepted ? `Plan Chapter ${Number(chapter) + 1}` : "Review candidate draft";
      action.onclick = () => {
        if (review.accepted) window.location.search = `?chapter=${Number(chapter) + 1}`;
        else window.location.hash = "evidence";
      };
    })
    .catch((error) => { status.textContent = `Unable to load review: ${error.message}`; });
})();
