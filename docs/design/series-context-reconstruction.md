# Series Context Reconstruction V1

`SeriesContextSnapshot` is a bounded, read-only projection for a target Book.
It ranks direct dependencies, active unresolved items, requested context, and
recent history, and records why each item was included. Stale items are visible
warnings. The snapshot is derived and never updates Series Identity.
