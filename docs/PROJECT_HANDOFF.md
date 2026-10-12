# Continue the fitness MVP

Repository: https://github.com/robdin/fitness
Pull request: https://github.com/robdin/fitness/pull/2
Branch: codex/blender-mvp (use main after PR #2 is merged).

The user authorized pushing and merging. Continue from GitHub; do not restart the project or regenerate the finished video. Check the PR status and use the branch above if it remains open. If checks pass, finish the authorized merge.

## Finished deliverable

Rep & Reason: “Your workout took an hour. Where did it go?” A 51-second, 1080×1920, 30 fps H.264/AAC vertical MVP with four procedural Blender animations, synthetic narration, 17 captions, and original procedural sound. This is an internal creative MVP, not a public channel upload. The 15/25/8/12-minute breakdown is explicitly illustrative.

The large MP4 upload repeatedly stalled. The exact finished video is retained losslessly in 33 small JavaScript parts under `examples/blender-mvp/media/`, with checksums. No rerender is needed. The offline HTML player reconstructs it in memory.

## Resume

```bash
git clone https://github.com/robdin/fitness.git
cd fitness
# If PR #2 is still open: git switch codex/blender-mvp
python tools/blender/unpack_mvp.py
```

Open `examples/blender-mvp/index.html` to play/download the video offline, or play the unpacked `Rep_and_Reason_Blender_MVP.mp4`. Edit `examples/blender-mvp/time-audit.blend` in Blender. The Python pack/unpack scripts need only the standard library.

## Important paths

- `examples/blender-mvp/README.md`: deliverables and rebuild commands.
- `examples/blender-mvp/build-receipt.json`: source/output fingerprints.
- `content/mvp/time-audit/episode.json`: copy, narration and scene order.
- `tools/blender/`: scene creation, narration, composition, pack and unpack.
- `brand/README.md`: recovered proposed brand direction.
- `brand/RECOVERY_STATUS.md`: earlier unpublished research files could not be fully recovered; do not claim otherwise.

## Verification already completed

All 192 rendered PNG frames verified; full final MP4 decode passed; 1530 frames and 51 seconds confirmed; all 17 captions are within the timeline; 22 repository tests passed. Final video SHA-256: `350a6b3439cf1034a5e8bb6a8fe947b9df23d344ec8b8ae94a1d4c9a142ab947`. Verify GitHub CI for the final PR head before merging.

## Next useful work

Review the actual MP4 for pacing, voice and visual direction. Only revise or produce another episode after the user gives that direction. Do not repeat the build merely because the conversation changed.
