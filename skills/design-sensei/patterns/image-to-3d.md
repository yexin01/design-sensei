# Image to 3D playbook

Decide whether to rebuild the object in a reference image as a code-only Three.js model (img2threejs), load a supplied model, or fall back to a photo, and run that workflow with gates.

## When to use / when not

- Use when a site needs a 3D hero or prop derived from one reference image, an approximate stylized result is acceptable, the object is hard-surface (product, tool, prop), and the project can afford a long agent session with screenshot review.
- Do not use when exact geometry or CAD fidelity matters, for photoreal likeness of people, smoke, liquid, caustics or lace (the upstream suitability rubric rejects them), mostly-cloth characters, scenes, or when no screenshot tool is available.
- A GLB already exists: load it (see [3D scenes](three-dimensional-scenes.md), [[r3f-gltf-loading-suspense]], [[r3f-product-showcase-scene]]). If WebGL cannot be budgeted, use a photo or a turntable video.
- Cost warning: upstream estimates roughly 80k-180k model tokens per object (estimate, not a measurement), dominated by review cycles. Tell the user before starting.
- Dials: `webgl_enabled: false` or `allowed_dependencies` none: do not start. `source_acquisition_mode: offline`: the installer needs network (npx and Git); ask first, do not run it silently. A single image can never show hidden sides: unseen faces are inferred and reported as low confidence; never present the model as an exact copy.
- Not the same thing: [[taste-skill-image-to-code-workflow]] turns generated reference images into page layouts, not 3D models.

## Pick the approach

| Situation | Pattern | Reuse class | Notes |
| --- | --- | --- | --- |
| Rebuild one object from a reference image as a TypeScript `THREE.Group` factory | [[image-to-3d-img2threejs-pipeline]] | copy_with_attribution (Apache-2.0) | Staged pipeline: intake, spec, locked pass-by-pass build, review. Apache-2.0: keep licence text, mark modified files, keep notices if you copy upstream files. |
| Decide, after each pass, whether the render matches the reference | [[image-to-3d-review-gates-and-correction-loop]] | copy_with_attribution | Deterministic diagnostics + multi-angle checks + one side-by-side sheet judged by agent vision; one action per pass; corrections capped (3 per pass, 6 total by default). Reference only. |
| Character or animated figure | [[image-to-3d-procedural-rig-animation-gates]] | copy_with_attribution | Rig and animation gates G1-G10; unmeasured gate reports `unevaluated`. Characters are stylized figures, not likenesses. Reference only; part of the rig track lives in a separate plugin. |
| Mount the generated factory in a page | [[r3f-lazy-canvas-webgl-fallback]], [[r3f-canvas-setup]] | copy_with_attribution | Lazy chunk, poster, error boundary; the factory builds canvas textures through the DOM, so create it in an effect, never on the server. |
| Product viewer around the result | [[r3f-product-showcase-scene]] | copy_with_attribution | See [product showcases](product-showcases.md). |
| Logo or flat artwork instead of an object | [[liquid-metal-logo]], [[image-background-removal-for-logos]] | copy_with_attribution | 2D shader route; see [background shaders](background-shaders.md). |

## Search commands

```bash
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "image to 3d" --category image-to-3d
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "reference image three.js model" --scope all --limit 5
${CLAUDE_SKILL_DIR}/scripts/design-sensei sources show img2threejs
${CLAUDE_SKILL_DIR}/scripts/design-sensei search "img2threejs" --content   # only if the source is downloaded
```

## Implementation steps

1. Check the reference: one obvious object filling the frame, strong silhouette, neutral background; ask for front, side, back views and material close-ups when available. Confirm rights to the image.
2. Install the base skill (from the [recipe](../../../knowledge/implementation-recipes/image-to-3d-with-img2threejs.md): Node 18+, Git, Python 3.10+; installer via `npx img2threejs`; restart the agent session). The installer fetches from GitHub at a pinned tag: network and permission needed. Never run install scripts from downloaded upstream folders without the user's approval.
3. Suitability: record pass, conditional or reject before planning. Conditional means list missing views or close-ups.
4. Run with a stated quality bar and triangle budget (upstream tessellation tiers: up to 6,000 low, up to 60,000 standard, otherwise hero). The first command at every start, resume and correction is the upstream `forge/next.py` against its state file; exit code 3 or `status=stopped` is a hard stop: report and ask.
5. Let the staged pipeline run. Scripts scaffold only; the agent fills the assessment and spec until strict quality passes. Never use `--allow-nonstrict`. Each of the eight build passes needs a render, a comparison sheet, agent-vision review and exactly one recorded action. Do not chase pixel scores against a photograph; judge with agent vision. Finish with part-coverage.
6. Review capture needs a deterministic preview: fixed named camera, controls disabled, reference viewport, framing close to the reference. Never judge from a single front view.
7. Mount in the page per the recipe step 6: create the model in an effect; dispose geometries, textures and materials yourself (`<primitive>` is not auto-disposed); environment from the factory; frame the camera with the generated helper; `frameloop="demand"` for static views. Use `qualityPriority: 'balanced'` or smaller textures on phones. Prefer your own lights for production.
8. Record provenance: keep the spec JSON, generated TypeScript, review sheets and licence notice together; carry hand edits back into the spec before regenerating. Add a third-party notice if upstream files were copied.

## Accessibility and performance gates

- [ ] Strict quality exits 0, every pass has a recorded `continue`, part coverage passes, and the report names inferred regions and what still does not match.
- [ ] `tsc --noEmit` on the generated file with the project's installed `three` (upstream typecheck gates skip without their showcase checkout, so green upstream tests do not prove it compiles).
- [ ] Budget: log `gl.info.render.triangles` and draw calls after the first frame; compare with the spec's budget. Repeats are instanced upstream (one draw call per cluster).
- [ ] Texture memory: generated canvas textures are 256-2048 px per map (default 1024; five maps per material when procedural); test on a mid-range phone.
- [ ] Poster/fallback when WebGL is missing, the factory throws or context is lost; no console errors across mount/unmount/route change; no leaked textures after repeated mounts.
- [ ] Static by default; no idle animation under `prefers-reduced-motion`; rig clips skipped, rest pose shown.
- [ ] Alt/label for the canvas and the information also in DOM text; keyboard-operable viewer.
- [ ] LCP <= 2.5 s with the poster as the candidate; the 3D chunk loads lazily.
- [ ] Licence: Apache-2.0 obligations met if upstream files were copied; the licensing of generated output is not stated upstream (not verified), so respect the reference image's rights.

## Common mistakes

- Promising an exact copy from one photograph; hiding the low-confidence regions.
- Starting a long pipeline without telling the user the token and time cost, or without screenshot tooling.
- Skipping suitability and feeding cluttered, blurred or multi-object images.
- Accepting a passing 2D gate without a three-quarter render check (flat, toy-like edges).
- Reviewing with orbit controls enabled or a moving camera.
- Using `--allow-nonstrict` for production output; hand-editing generated code without carrying it back into the spec.
- Building the model during server render (it needs `document`); forgetting to dispose on unmount.
- Mismatched three versions: upstream targets r169; R3F 9 needs a recent `three`. Pick one satisfying both and typecheck.
- Confusing it with a mesh-extraction or photogrammetry tool. It is reconstruction by code.

## Where to read more

- [img2threejs note](../../../knowledge/components/img2threejs.md) (pipeline, gates, limits, licence), [workflow recipe](../../../knowledge/implementation-recipes/image-to-3d-with-img2threejs.md), [R3F note](../../../knowledge/components/react-three-fiber.md), [canvas fallback recipe](../../../knowledge/implementation-recipes/r3f-canvas-in-a-page-with-fallback.md)
- [three-dimensional-design reference](../references/three-dimensional-design.md), [source usage](../references/source-usage.md), [performance](../references/performance.md); related playbooks [3D scenes](three-dimensional-scenes.md), [product showcases](product-showcases.md)
