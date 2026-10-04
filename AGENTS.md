# Repository hygiene

- Inspect `git status`, the staged file list, and staged sizes before committing.
  Never force-add ignored scratch files, caches, build output, or bulk recordings.
- Put disposable task output in an ignored `tmp/`, `.tmp/`, or `build/` directory,
  or a task directory under `/tmp` inside the managed development container.
  Reuse one scratch directory per task. Remove task-created disposable files
  when finished, including on failure; use `finally` blocks or shell traps.
- Ignore rules prevent commits but do not reclaim disk space. Before deleting a
  scratch directory, resolve its absolute path, verify it stays inside the
  intended workspace or container scratch directory, and check for symlinks,
  junctions, tracked files, and active processes using it.
- Reports, source snapshots, checkpoints, hashes, and verification receipts are
  retained evidence, not trash. Preserve existing evidence and its recorded
  bytes. Do not make recursive copies of whole report bundles for temporary QA.
- Keep new Droid Blocks bulk transition recordings, physical snapshot streams,
  and headroom playback exports local and ignored. Commit source, report
  summaries, and compact provenance records; document which local assets a
  fresh checkout needs for full replay.
- Clean only known disposable files created by the task, or duplicates whose
  retained copies have been verified. Do not delete dependency environments,
  active service builds, experiment data, or Docker objects as generic cleanup.
- Develop, build, test, and run project services in their documented managed
  Linux containers. Host PowerShell is limited to filesystem inspection,
  orchestration, and operating-system integration.
