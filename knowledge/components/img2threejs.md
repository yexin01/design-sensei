---
title: "img2threejs image-to-Three.js skill"
kind: component-library
summary: "Agent skill and stdlib Python tooling that rebuilds the object in one reference image as a code-only, quality-gated procedural Three.js model. Covers the staged forge pipeline, gates, outputs, requirements, documented limits and Apache-2.0 reuse terms."
source_ids: [img2threejs]
pattern_ids: [image-to-3d-img2threejs-pipeline, image-to-3d-review-gates-and-correction-loop, image-to-3d-procedural-rig-animation-gates]
updated: "2026-10-09"
---

# img2threejs image-to-Three.js skill

## What it is and who maintains it

- An agent skill plus deterministic Python tooling. Given one reference image it produces a TypeScript `THREE.Group` factory built from primitives, procedural shaders and generated geometry, together with a JSON spec and a review history. It is reconstruction by code, not photogrammetry, mesh extraction or downloaded art (`img2threejs:SKILL.md`, `img2threejs:README.md`).
- Skill version 2.0.0 (front matter of `SKILL.md`), Apache-2.0. The npm installer is a separate package, `img2threejs` 0.1.1, whose version is independent of the skill (`img2threejs:package.json`, `img2threejs:CONTRIBUTING.md`).
- Maintained by the `img2threejs` GitHub project; the LICENSE names `hoainho` as copyright holder. The live gallery (`img2threejs-showcase`), the `img2` plugin harness and the plugins (cs2, character, environment, img2glb, hello-cube) are separate repositories that are not part of this source.
- Agent-agnostic: Claude Code, Codex and OpenCode; the installer also detects Hermes (`img2threejs:bin/img2threejs.mjs`).

## Install and invocation (as documented)

Installer commands, quoted from `img2threejs:README.md`:

```bash
npx --yes img2threejs@latest install --dry-run
npx --yes img2threejs@latest install
npx --yes img2threejs@latest doctor
```

- Needs Node.js 18 or newer and Git for the installer, and Python 3.10 or newer for the scripts. The installer fetches the skill from GitHub at tag `v2.0.0` by default; `--ref` takes a semantic tag or a full commit SHA, never a branch.
- Manual alternative: clone the repository into the host skills folder (for example `~/.claude/skills/img2threejs`). Keep one checkout and symlink it per host so hosts do not drift (`img2threejs:SKILL.md`, `img2threejs:CLAUDE.md`).
- Restart the agent after installing. In Claude Code, attach or name the image and run `/img2threejs` with a request that states the quality bar and asks for output files, render-review evidence and inferred regions. Other hosts: ask the agent to use the installed skill.
- The agent's first command at every start, resume and correction is `python3 forge/next.py --state .img2threejs/state.json`. Exit code 3 or `status=stopped` is a hard stop (`img2threejs:SKILL.md`, `img2threejs:forge/next.py`, `img2threejs:forge/state.py`).
- Installing the `img2` harness does not install the base skill, and `img2 add` must not be used for it (`img2threejs:README.md`).

## Staged pipeline

| Stage | Directory | Role | Representative scripts |
|---|---|---|---|
| 1 intake | `img2threejs:forge/stage1_intake/` | validate the reference and extract evidence | `probe_image.py`, `check_reference_admission.py`, `build_detail_inventory.py`, `extract_pbr_evidence.py`, `analyze_texture.py`, `solve_camera_pose.py`, `delight_albedo.py`, optional `run_vision_adapter.py` |
| 2 spec | `img2threejs:forge/stage2_spec/` | classify, write the quality contract, author and validate the spec | `new_pre_spec_assessment.py`, `new_sculpt_spec.py`, `validate_sculpt_spec.py`, `apply_material_analysis.py` |
| 3 build | `img2threejs:forge/stage3_build/` | locked pass-by-pass TypeScript generation | `orchestrate_passes.py`, `generate_threejs_factory.py`, `bake_projected_texture.py`, `decimate.py`, `emit_target.py` |
| 4 review | `img2threejs:forge/stage4_review/` | deterministic gates and the review record | `diagnose_render.py`, `diagnose_render_multi_angle.py`, `make_comparison_sheet.py`, `append_review.py`, `check_part_coverage.py`, `turntable_gate.py`, `self_intersection.py` |
| 5 rig | `img2threejs:forge/stage5_rig/` | skeleton, skinning and animation gates for characters | `rig_spec.py`, `geodesic_skinning.py`, `validate_rig_payload.py`, `clip_features.py`, `rig_gates.py`, `emit_animation_runtime.py` |

- The checklist lives in `img2threejs:forge/_shared/workflow_state.py`: 11 setup steps (image analysis, suitability, admission, local spec search, pre-spec assessment, detail inventory, projection route, spec authoring, material evidence, material wiring, strict validation), 8 steps per pass (build, render capture, read review contract, Tier 1 diagnostics, multi-angle review, pass gate check, AI review recorded, sync) and 4 final steps (part coverage, action-ready, emission target, plugin gates).
- Build passes, from `orchestrate_passes.py`: blockout, structural-pass, form-refinement, material-pass, surface-pass, lighting-pass, interaction-pass, optimization-pass. `img2threejs:grimoire/scripts.md` lists seven and omits surface-pass; the code and `img2threejs:docs/ARCHITECTURE.md` list eight.
- Stage 5 stays in the repo as a library: the `animated-character` checklist and rig gates come from the separately installed plugin-character (`img2threejs:docs/ARCHITECTURE.md`). Base profiles are `generic` and `character`; CHANGELOG "Unreleased" plans to move `character` into the plugin in v2.1.
- Scripts enforce and package evidence; they never score visuals. The acceptance score comes from the agent looking at one reference-versus-render comparison sheet (`img2threejs:SKILL.md`).

## Quality gates

| Gate | Where | Rule |
|---|---|---|
| Reference admission | `img2threejs:forge/stage1_intake/check_reference_admission.py` | foreground coverage 0.05 to 0.97, short side at least 64 px, largest blob at least 60 percent of foreground, duplicates rejected at pHash distance 6 or less |
| Suitability | `img2threejs:grimoire/intake/validation_rubric.md` | pass, conditional or reject before planning |
| Strict quality | `img2threejs:forge/stage2_spec/validate_sculpt_spec.py` | `--strict-quality` blocks shallow specs; the generator repeats it and is fail-closed (`BLOCKED`, exit 2, no file written) |
| Pass lock | `img2threejs:forge/stage3_build/orchestrate_passes.py` | a pass unlocks only after the previous one has `continue` backed by a render, a comparison sheet, an AI score at or above the threshold (0.7 by default) and every critical feature at its own threshold |
| Tier 1 diagnostics | `img2threejs:forge/stage4_review/diagnose_render.py` | silhouette IoU 0.85, aspect delta 0.05, scale delta 0.08, symmetry error 0.10, colour delta E 20 (colour only from material-pass onward) |
| Geometry before pixels | `turntable_gate.py`, `self_intersection.py`, `attachment_anchor.py` in stage 4 | at least two angles, no folded surfaces, no floating attachments |
| Interior difference | `img2threejs:forge/stage4_review/interior_difference.py` | the docs say outline IoU reads about 11 percent of figure cells and scored a deleted face like a finished one |
| Assembly | `img2threejs:forge/stage4_review/check_part_coverage.py` | fails on specified parts never built and on fused parts |
| Bounded loop | `img2threejs:forge/state.py` | 3 corrections per pass and 6 total by default; one action per pass: continue, refine-spec, refine-code, request-input or stop |
| Rig and animation | `img2threejs:forge/stage5_rig/rig_gates.py` | gates G1 to G10; an unmeasured gate reports `unevaluated`, never a pass (`img2threejs:grimoire/readiness/animation_contract.md`) |

## Outputs

- `object-sculpt-spec.json`: component tree, materials, repetition systems, sockets, review history.
- A TypeScript module. The generator emits `create<TargetName>Model(options)` returning a `THREE.Group` with `root.userData.sculptRuntime = { nodes, meshes, sockets, colliders, destructionGroups }`. `SKILL.md` and the README write `createObjectNameModel(spec, options)`; the emitter in `img2threejs:forge/stage3_build/generate_threejs_factory.py` takes only `options` (`wireframe`, `castShadow`, `receiveShadow`, `textureSize`, `textureAnisotropy`, `qualityPriority`).
- Companion exports in the same module: `create<Name>Environment(renderer)` (a PMREM room environment), `frame<Name>Camera`, `create<Name>LookDevLights`, `create<Name>PresentationComposer`, `configure<Name>Renderer`, `create<Name>InspectControls`. The module imports `three` and several `three/examples/jsm` modules.
- Comparison sheets, `.img2threejs/state.json`, and for characters `root.userData.rig` (bones, one shared skeleton, a computed `bound` flag).

## Requirements and limits

- One image cannot show hidden sides; unseen faces are inferred by mirroring and reported as low confidence. "This cannot reach the requested fidelity" is a valid result (`img2threejs:README.md`).
- Strong for hard-surface objects and props; characters are stylized figures, not likenesses (`img2threejs:CONTRIBUTING.md`). The rubric rejects ambiguous targets, scenes, hidden or blurred shapes, manufacturing-grade dimensions, and smoke, liquid, caustics or lace.
- Not shipped: hair profile compiler, IK, pose-sweep gating, clothing (`img2threejs:ROADMAP.md`). The character template has 61 anatomy components and no garments (`img2threejs:docs/standard-prompts/build.md`). Environments (v2.2) and engine exporters (v2.3) are roadmap items. The ROADMAP gap table is dated 2026-07-22 and partly superseded.
- Needs an image-capable agent and a browser or screenshot tool (browser MCP, the project preview, or user screenshots). The docs say not to install Playwright just for the skill (`img2threejs:grimoire/feedback/render_capture.md`). Optional SAM2, MediaPipe and Depth Anything adapters install separately (`img2threejs:docs/integrations/reference_fidelity_tooling.md`).
- Typecheck gates skip without a showcase checkout (`IMG2THREEJS_SHOWCASE_ROOT`), so a green test run does not prove the emitted code compiles (`img2threejs:CLAUDE.md`). The docs target three r169.
- Cost: estimates, not measurements, of roughly 80k to 180k model tokens per object and 150k to 350k per character, dominated by review cycles (`img2threejs:docs/TOKEN_COST.md`).
- `img2threejs:LAB-FINDINGS.md` records a structural experiment on the img2 harness (v0.2.0): a placeholder-policy mismatch and a `capabilities` query that returned success for rows `doctor` rejected. It states that no reconstruction was run and no baseline recorded, so the repository has no quality benchmark.
- `SKILL.md` tells agents to run `runtime/scripts/export_mesh_geometry.mjs`, but `runtime/` is gitignored and absent from the clone (`img2threejs:docs/STAGE_R_BACKLOG.md`, item H-1).

## Relation to Design Sensei's image-to-3D use case

Guidance, not upstream text. Use it when a site needs a 3D hero or prop derived from a reference image, an approximate stylized result is acceptable, and the project can afford a long agent session with screenshot review. Prefer a supplied GLB (loaded with `useLoader`, see `knowledge/implementation-recipes/r3f-product-showcase-scene.md`) when exact geometry matters, and a static image or video when WebGL cannot be budgeted. The factory drops into a React Three Fiber scene as a `<primitive>`; see `knowledge/implementation-recipes/image-to-3d-with-img2threejs.md`.

## Directory map

| Path | Contents |
|---|---|
| `img2threejs:SKILL.md` | always-loaded router: order of operations and hard rules |
| `img2threejs:forge/` | stdlib Python tooling: `stage1_intake/` to `stage5_rig/`, `_shared/`, `materials/`, `state.py`, `next.py`, about 100 test files |
| `img2threejs:grimoire/` | routed reference docs: `intake/`, `build/`, `review/`, `feedback/`, `readiness/`, `character/`, `glossary/` |
| `img2threejs:docs/` | architecture, token cost, standard prompts, material registry, render-profile schema |
| `img2threejs:integrations/` | optional `vision/`, `mesh3d/` (hosted TRELLIS reference mesh) and `glb_character_pipeline/` |
| `img2threejs:bin/img2threejs.mjs` | installer CLI |
| `img2threejs:scripts/` | Playwright capture adapter, audit and release helpers |

## Notable modules

| Module | What it does | File | Pattern |
|---|---|---|---|
| Local state gate | ordered checklist, correction ceilings, next command | `img2threejs:forge/_shared/workflow_state.py` | `image-to-3d-img2threejs-pipeline` |
| Factory generator | emits the pass-gated `THREE.Group` factory | `img2threejs:forge/stage3_build/generate_threejs_factory.py` | `image-to-3d-img2threejs-pipeline` |
| Tier 1 diagnostics | cheap deterministic render checks | `img2threejs:forge/stage4_review/diagnose_render.py` | `image-to-3d-review-gates-and-correction-loop` |
| Comparison sheet | one reference-versus-render image | `img2threejs:forge/stage4_review/make_comparison_sheet.py` | `image-to-3d-review-gates-and-correction-loop` |
| Rig gates | G1 to G10 runner | `img2threejs:forge/stage5_rig/rig_gates.py` | `image-to-3d-procedural-rig-animation-gates` |
| Animation runtime emitter | mixer controller, ticker collection | `img2threejs:forge/stage5_rig/emit_animation_runtime.py` | `image-to-3d-procedural-rig-animation-gates` |

## Performance and accessibility observations

- Repetition systems are emitted as `InstancedMesh`, one draw call per cluster (`img2threejs:ROADMAP.md` gap G3, `img2threejs:forge/stage3_build/generate_threejs_factory.py`). Tessellation follows `performanceBudget.targetTriangles`: up to 6,000 low, up to 60,000 standard, otherwise hero, which is also the default (`img2threejs:forge/_shared/subdivision.py`).
- Every material is a `MeshPhysicalMaterial`. Unless declared textureless, a material gets a reference texture set when one exists, otherwise five procedural canvas maps (albedo, roughness, height, normal, ao) of 256 to 2048 px. The default is 1024, or 512 with `qualityPriority: 'balanced'`, unless the spec sets `textureResolution`. At 1024 px each canvas is about 4 MiB before GPU copies (arithmetic, not measured).
- Texture generation uses `document.createElement('canvas')` and returns nothing when `document` is undefined, so build the model in the browser.
- The presentation composer (depth of field, bloom) is for hero renders only. The generated code keeps the evaluation render composer-free so bloom and blur cannot distort the gates (comments in `img2threejs:forge/stage3_build/generate_threejs_factory.py`, `img2threejs:ROADMAP.md`).
- Output is static unless you animate it. If you use the rig track, skip clip playback under `prefers-reduced-motion` and show the rest pose; that is this catalog's guidance.

## Pitfalls

- A fresh scaffold fails strict quality with about 89 causes. They are fields to fill, not defects (`img2threejs:docs/standard-prompts/build.md`).
- Against a photograph, silhouette IoU and SSIM mostly measure framing and lighting. Do not chase the Divine Eye score; judge each pass with agent vision (`img2threejs:grimoire/review/self_correction.md`).
- A passing 2D gate is not "done": check a three-quarter render for flat, toy-like edges.
- Disable orbit controls and fix the viewport and camera during review capture (`img2threejs:grimoire/feedback/render_capture.md`).
- Scene edits made through an MCP inspector do not count until they are written back to the spec or TypeScript (`img2threejs:docs/integrations/reference_fidelity_tooling.md`).
- Carry hand refinements back into the spec before regenerating with `--force`; never use `--allow-nonstrict` for production output (`img2threejs:SKILL.md`).

## Licence and reuse

Apache-2.0, Copyright 2026 hoainho (`img2threejs:LICENSE`). Attribution: img2threejs contributors (https://github.com/img2threejs/img2threejs). Section 4 requires giving recipients a copy of the licence, marking modified files with prominent change notices, and keeping copyright and attribution notices. The repository has no NOTICE file at the pin, so there is nothing to carry from one. Sponsor logos in `img2threejs:assets/sponsors/` are third-party marks and are not reusable here, and the licence grants no rights to the project's own marks beyond describing origin (section 6). The licensing of generated output is not stated in the repository (not verified); the showcase repository and any plugin have their own licences that were not examined. This note describes the project and cites paths; it copies no code.

## Related patterns

`image-to-3d-img2threejs-pipeline`, `image-to-3d-review-gates-and-correction-loop`, `image-to-3d-procedural-rig-animation-gates`. Recipe: `knowledge/implementation-recipes/image-to-3d-with-img2threejs.md`. R3F side: `knowledge/components/react-three-fiber.md`.
