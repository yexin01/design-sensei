---
description: Write the art-direction brief for a UI task (no code yet)
argument-hint: "[goal, e.g. landing page for a ceramics studio]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei search *)
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei read *)
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei doctor *)
  - Bash(${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei config show *)
---

Goal: $ARGUMENTS

If the goal above is empty, infer it from the conversation and the project. If you still cannot tell what is being built or for whom, ask exactly one question and stop.

Run steps 0 to 2 of the `design-sensei` skill (toolkit check, inspect, art direction) and then stop. In this command do not write, edit or generate any code, config or file, and do not install anything. The deliverable is a written brief in your reply.

In this file `design-sensei` means `${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/scripts/design-sensei` (quote the path if it contains spaces).

1. **Toolkit and settings.** Run `design-sensei doctor --brief` and `design-sensei config show --project .`. Note the dials (`design_variance`, `motion_intensity`, `visual_density`), `reduced_motion`, `webgl_enabled` and `allowed_dependencies`.
2. **Inspect the project.** Follow the table in step 1 of `${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/SKILL.md`: framework, styling system, existing tokens or `DESIGN.md`, installed motion and 3D libraries, constraints. A `DESIGN.md` or existing token system outranks everything else; only fill the gaps it leaves.
3. **Choose the style.** Search with mood words and the product type, not framework names: `design-sensei search "<mood words>" --category design-style --scope patterns --limit 5`. Read the quick card of the top two or three results (`design-sensei read <style-slug>`, about 400 tokens each; add `--section "Poor fit,Colour"` for detail) and reject any whose "poor fit" matches the product. Pick one primary style and at most one supporting influence.
4. **Write the brief.** Read `design-sensei read ref:art-direction --full` and fill its brief template in the order it gives: design read, audience and emotion, dials, style, typography, colour tokens, layout and spacing, surfaces, motion language, interaction, don'ts, sources. Give every line a one-line reason. Use concrete values (families, scale ratio, hex tokens, easing, durations), not adjectives. Cite each borrowed idea by catalog pattern id with its reuse class. Read the matching files in `${CLAUDE_PLUGIN_ROOT}/skills/design-sensei/references/` (typography, colour systems, layout composition, motion design) only when you need their concrete values.
5. **Check it.** Walk the generic-tells checklist in `art-direction.md` and change at least one default deliberately if the direction looks like one. If a dial pairing conflicts (high variance with high density, high motion with high density), resolve it in the brief.
6. **Ask for approval.** Show the finished brief, then end with a short question: approve it as written, or say what to change? Do not start implementation until the user approves. Never send a questionnaire; state your assumptions and let the user correct them.
