---
title: "Image to 3D with img2threejs and React Three Fiber"
kind: recipe
summary: "Workflow for rebuilding the object in one reference image as a code-only Three.js model with the img2threejs skill, then mounting the generated factory in a React Three Fiber page with disposal, environment, framing and a static fallback."
source_ids: [img2threejs, react-three-fiber]
pattern_ids: [image-to-3d-img2threejs-pipeline]
updated: "2026-10-09"
---

# Image to 3D with img2threejs and React Three Fiber

## Goal

Turn one reference image of an object, for example a product photo, into a procedural Three.js model with review evidence, then show it in an R3F page. Only steps found in the img2threejs docs are used for the generation half; the R3F half is original glue code.

## When to use

- Hard-surface objects and props where a stylized, approximate, diffable TypeScript model is acceptable, the photo is clean, and the project can run a long agent session with browser screenshots.
- Not for exact geometry or CAD fidelity, photoreal likeness of people, smoke, liquid, glass caustics or lace (the suitability rubric rejects them), mostly-cloth characters, scenes, or setups with no screenshot tooling.
- Already have a GLB? Load it with `useLoader` instead (`knowledge/implementation-recipes/r3f-product-showcase-scene.md`). The README also lists an optional `img2glb` plugin that returns a mesh through a hosted TRELLIS space; it is explicitly not the default code-only route and was not reviewed here (`img2threejs:README.md`).
- Budget: the docs estimate roughly 80k to 180k model tokens per object, dominated by review cycles. These are estimates, not measurements (`img2threejs:docs/TOKEN_COST.md`).

## Prerequisites

| Item | Requirement | Source |
|---|---|---|
| Agent host | Claude Code, Codex or OpenCode, with image reading | `img2threejs:README.md` |
| Installer | Node.js 18 or newer and Git | `img2threejs:package.json`, `img2threejs:README.md` |
| Scripts | Python 3.10 or newer, standard library only | `img2threejs:forge/requirements.txt` |
| Review preview | a browser tool (browser MCP, project preview, or user screenshots) | `img2threejs:grimoire/feedback/render_capture.md` |
| R3F page | React `>=19 <19.4`, `@react-three/fiber` 9.x, `three >=0.156` | `react-three-fiber:packages/fiber/package.json` |
| three version | img2threejs targets three r169; pick one version satisfying both and typecheck the generated file | `img2threejs:docs/integrations/reference_fidelity_tooling.md` |

Reference image: one obvious object filling the frame, strong silhouette, neutral background. Ask for front, side and back views, higher resolution and material close-ups when you can (`img2threejs:grimoire/intake/validation_rubric.md`).

## Steps

**1. Install the base skill** and restart the agent session. Commands from the README (`img2threejs:README.md`): `npx --yes img2threejs@latest install --dry-run`, then `install`, then `doctor`. The manual alternative is cloning the repository into the host's skills folder. The plugin harness is optional and does not install the base skill.

**2. Check suitability.** The rubric returns pass, conditional or reject. Conditional covers cases such as a single view of a symmetric object, partial occlusion, accepted stylization, or no need for exact logo or text fidelity; if the missing information cannot be inferred, mark the spec conditional and list the missing views or close-ups. Record the verdict before planning.

**3. Start the run.** In Claude Code attach the image and invoke `/img2threejs` with a request in your own words: rebuild the object as a procedural Three.js model for a web page, keep proportions, silhouette and colours, run strict quality, do not advance a pass until the side-by-side review passes, and report inferred regions with per-region confidence. State a triangle budget so the spec's `performanceBudget.targetTriangles` selects a tessellation tier (up to 6,000 low, up to 60,000 standard, otherwise hero). Behind the scenes the agent initialises the local state and asks it for the next command:

```bash
python3 forge/state.py init --state .img2threejs/state.json --reference <image> --profile generic --spec object-sculpt-spec.json
python3 forge/next.py --state .img2threejs/state.json
```

Use `generic` for objects; `character` is for humanoids. Exit code 3 or `status=stopped` is a hard stop: report and ask (`img2threejs:SKILL.md`).

**4. Let the staged pipeline run.** The README quick start gives the script order (quoted, `img2threejs:README.md`):

```bash
python3 forge/stage1_intake/probe_image.py <image>
python3 forge/stage2_spec/new_pre_spec_assessment.py "Name" --image <image> --out assessment.json
python3 forge/stage2_spec/new_sculpt_spec.py "Name" --image <image> --assessment assessment.json --out spec.json
python3 forge/stage2_spec/validate_sculpt_spec.py spec.json --strict-quality
python3 forge/stage3_build/generate_threejs_factory.py spec.json --out src/createObjectModel.ts
```

- Scripts only scaffold. The agent must fill the assessment (class, complexity scores, detail inventory) before strict validation can pass; about 89 failures on a fresh scaffold are fields to fill, not defects (`img2threejs:docs/standard-prompts/build.md`).
- The generator emits only the currently unlocked pass and refuses to write a file when strict quality fails. Never use `--allow-nonstrict`.
- Each of the eight passes repeats: generate the pass, render and capture the fixed review view plus orbit views, run `diagnose_render.py` and `diagnose_render_multi_angle.py`, `orchestrate_passes.py check`, package one comparison sheet with `make_comparison_sheet.py`, inspect it with agent vision, record exactly one action with `append_review.py` (continue, refine-spec, refine-code, request-input or stop), then `orchestrate_passes.py sync`. Corrections are capped at 3 per pass and 6 total. Finish with `check_part_coverage.py`.

**5. Give the review loop a deterministic preview.** The review route can be a page in your R3F app. The docs require a fixed named camera, controls disabled during capture, the reference viewport, and a framing close to the reference (`img2threejs:grimoire/feedback/render_capture.md`). Their showcase route also sets `window.__IMG2THREEJS_READY__` when assets are ready, and the Playwright adapter expects a capture contract on the page; whether your own route satisfies a given capture tool is not covered by the docs, so the agent has to adapt. Original sketch of the readiness flag:

```tsx
function ReadyFlag() {
  const done = useRef(false)
  useFrame(() => {
    if (!done.current) { done.current = true; (window as any).__IMG2THREEJS_READY__ = true }
  })
  return null
}
```

Render with `<Canvas dpr={1}>`, no controls, and a camera set from the named review view. Do not judge the model from a single front view.

**6. Mount the generated factory in R3F.** The generator emits `create<Name>Model(options)` returning a `THREE.Group`, plus `create<Name>Environment(renderer)` and `frame<Name>Camera(camera, object, { margin, azimuthDeg, elevationDeg })` (`img2threejs:forge/stage3_build/generate_threejs_factory.py`). `<primitive>` objects are never disposed by R3F (`react-three-fiber:docs/API/objects.mdx`), and the factory builds canvas textures through the DOM, so create the model in an effect (never on the server) and dispose it yourself. Replace `Talon` with the generated name:

```tsx
import { useEffect, useState } from 'react'
import { useThree, type ThreeElements } from '@react-three/fiber'
import * as THREE from 'three'
import { createTalonModel, createTalonEnvironment, frameTalonCamera } from './generated/createTalonModel'

function disposeObject(root: THREE.Object3D) {
  root.traverse((node) => {
    const mesh = node as THREE.Mesh
    mesh.geometry?.dispose()
    const materials = Array.isArray(mesh.material) ? mesh.material : mesh.material ? [mesh.material] : []
    for (const material of materials) {
      for (const value of Object.values(material)) {
        if ((value as THREE.Texture | undefined)?.isTexture) (value as THREE.Texture).dispose()
      }
      material.dispose()
    }
    if ((node as THREE.InstancedMesh).isInstancedMesh) (node as THREE.InstancedMesh).dispose()
  })
}

export function GeneratedModel(props: ThreeElements['group']) {
  const gl = useThree((s) => s.gl)
  const scene = useThree((s) => s.scene)
  const camera = useThree((s) => s.camera)
  const invalidate = useThree((s) => s.invalidate)
  const [model, setModel] = useState<THREE.Group | null>(null)

  useEffect(() => {
    const created = createTalonModel({ qualityPriority: 'balanced', castShadow: false, receiveShadow: false })
    setModel(created)
    return () => { disposeObject(created); setModel(null) }
  }, [])

  useEffect(() => {
    const env = createTalonEnvironment(gl)
    scene.environment = env
    invalidate()
    return () => { scene.environment = null; env.dispose() }
  }, [gl, scene, invalidate])

  useEffect(() => {
    if (model && (camera as THREE.PerspectiveCamera).isPerspectiveCamera) {
      frameTalonCamera(camera as THREE.PerspectiveCamera, model, { margin: 1.15, azimuthDeg: 25, elevationDeg: 12 })
      invalidate()
    }
  }, [model, camera, invalidate])

  return model ? <primitive object={model} {...props} /> : null
}
```

- Build the effect-based model inside the lazy chunk of `knowledge/implementation-recipes/r3f-canvas-in-a-page-with-fallback.md` so the page keeps its poster, WebGL check, error boundary and `frameloop="demand"` behaviour. Reuse the same wrapper for an interactive view.
- Options verified in the generator: `wireframe`, `castShadow`, `receiveShadow`, `textureSize`, `textureAnisotropy`, `qualityPriority`. `balanced` or `textureSize: 512` shrinks the generated canvas textures.
- The generated `create<Name>LookDevLights` configures a 4096 px shadow map on its key light. R3F leaves shadows off unless you set `shadows`, but prefer your own lights for production.
- If you add orbit controls, set their target to the model's bounding-box centre; the framing helper calls `lookAt` on the camera, which controls will override.
- Animate or move parts through `model.userData.sculptRuntime` (`nodes`, `sockets`, `colliders`, `destructionGroups`) from `useFrame`, using deltas as in the animation note.

**7. Record provenance.** Keep `object-sculpt-spec.json`, the generated TypeScript, review sheets and the licence notice together. Carry any hand edits to the generated code back into the spec before regenerating with `--force` (`img2threejs:SKILL.md`).

## Verification checklist

- Gates: strict quality exits 0, every pass has a recorded `continue`, `check_part_coverage.py` passes, and the agent's report names inferred regions and what still does not match.
- Compile: run `tsc --noEmit` on the generated file with your installed `three`; the upstream typecheck gates skip without a showcase checkout (`img2threejs:CLAUDE.md`).
- Budget: log `gl.info.render.triangles` and draw calls after the first frame and compare them with the spec's triangle budget.
- Responsive and reduced motion: static by default; do not start idle animation when `prefers-reduced-motion` is set.
- Console: no errors on mount, unmount and route change; check for leaked textures after repeated mounts.
- Fallback: the poster shows when WebGL is missing, the factory throws, or the context is lost.
- Honesty: do not present the model as an exact copy; the project itself says a single image cannot show hidden sides.

## Upstream references

`img2threejs:README.md`, `img2threejs:SKILL.md`, `img2threejs:docs/ARCHITECTURE.md`, `img2threejs:docs/standard-prompts/build.md`, `img2threejs:forge/stage3_build/orchestrate_passes.py`, `img2threejs:forge/_shared/workflow_state.py`, `react-three-fiber:docs/API/objects.mdx`, `react-three-fiber:docs/API/hooks.mdx`.

## Licence notes

img2threejs is Apache-2.0 (Copyright 2026 hoainho, `img2threejs:LICENSE`). Using the tool and writing your own code needs no extra steps. If you copy or adapt upstream files or docs into your repository, include the licence text, mark modified files with a change notice and keep the copyright notices; there is no NOTICE file at the pin. Sponsor logos in `img2threejs:assets/sponsors/` are third-party marks. The repository does not state licensing for generated output (not verified), so keep the reference image's rights in mind. React Three Fiber is MIT (Copyright (c) 2019-2025 Poimandres). The glue code above is original and covered by this repository's MIT licence.
