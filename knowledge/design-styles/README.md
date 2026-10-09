# Design styles

Original, project-authored guidance for 40 design styles. Each note covers visual traits, fit and poor fit, typography, colour, layout, motion, accessibility cautions, common mistakes (including typical AI-generated ones) and how to build the style with catalog patterns and verified local code. Pick one primary style and at most one supporting influence; the last column suggests combinations that tend to work. The taxonomy is not derived from any article or website (see `../website-references/`).

| Style | Group | One-line summary | Pairs well with |
| --- | --- | --- | --- |
| [Editorial](editorial.md) | Type and layout | Magazine hierarchy: kicker, headline, standfirst, measure, captions, rules. | minimalism, swiss-international-typographic, grain-and-texture |
| [Swiss / International Typographic](swiss-international-typographic.md) | Type and layout | Explicit grid, one neo-grotesque, flush-left text, a single signal colour. | minimalism, editorial, generative-design |
| [Minimalism](minimalism.md) | Type and layout | Reduction with purpose: one typeface, neutral palette, designed quiet states. | swiss-international-typographic, editorial, product-led-saas |
| [Brutalism](brutalism.md) | Type and layout | Raw exposed structure, default or heavy type, hard borders, no gloss. | swiss-international-typographic, generative-design, cyberpunk |
| [Neo-brutalism](neo-brutalism.md) | Type and layout | Thick outlines, hard offset shadows, flat bright fills, pressable controls. | bento-layouts, product-led-saas, kinetic-typography |
| [Maximalism](maximalism.md) | Type and layout | Layered collage and clashing colour held by a hidden grid and rest areas. | retro-vintage, y2k, kinetic-typography |
| [Bento layouts](bento-layouts.md) | Type and layout | Modular grid of rounded tiles whose size signals priority. | product-led-saas, minimalism, dark-technical-developer-tools |
| [Kinetic typography](kinetic-typography.md) | Type and layout | Type as moving material, with real text and a static reduced-motion state. | editorial, brutalism, motion-led-storytelling |
| [Bauhaus](bauhaus.md) | Type and layout | Primary colours, basic geometry, diagonal asymmetry and function-first type. | swiss-international-typographic, minimalism, memphis |
| [Memphis](memphis.md) | Type and layout | 1980s squiggles, zigzags and confetti on calm panels, in bounded clashing colour. | maximalism, y2k, retro-vintage |
| [Collage and cutout](collage-cutout.md) | Type and layout | Paper cutouts, tape and stickers on a zine-page layer stack. | maximalism, grain-and-texture, editorial |
| [Japanese minimalism](japanese-minimalism.md) | Type and layout | Ma, yohaku and wabi-sabi: designed pauses, asymmetry, material warmth. | minimalism, organic-tactile, editorial |
| [High-fashion and luxury](high-fashion-luxury.md) | Era and mood | Restraint, slowness, art-directed imagery, muted metals, no discount devices. | editorial, minimalism, art-deco |
| [Retro and vintage](retro-vintage.md) | Era and mood | Print and analogue logic: spot inks, halftone, badges, one era per design. | grain-and-texture, editorial, organic-tactile |
| [Y2K](y2k.md) | Era and mood | Glossy millennium optimism: chrome, bubbles, holographic foils, pastel bases. | liquid-materials, maximalism, vaporwave |
| [Art Deco](art-deco.md) | Era and mood | Symmetry, sunbursts and stepped forms, gold on dark, tall capitals. | high-fashion-luxury, editorial, retro-vintage |
| [Vaporwave](vaporwave.md) | Era and mood | Ironic 80s-90s nostalgia: pastel neon, grids, sunsets, retro-OS windows. | y2k, retro-vintage, maximalism |
| [Cyberpunk](cyberpunk.md) | Era and mood | Neon dystopia: glitch, CRT, terminal and signage, used in short bursts. | dark-technical-developer-tools, futurism, grain-and-texture |
| [Futurism (digital sci-fi)](futurism.md) | Era and mood | Cool dark stage, luminous accents, HUD framing, spatial depth. | experimental-3d, generative-design, dark-technical-developer-tools |
| [Pixel art and 8-bit](pixel-art-8bit.md) | Era and mood | Sprites, small palettes and bitmap type with integer scaling. | retro-vintage, cyberpunk, vaporwave |
| [Glitch](glitch.md) | Era and mood | Signal failure as short bursts over a clean base, within flash limits. | cyberpunk, dark-technical-developer-tools, grain-and-texture |
| [Glassmorphism](glassmorphism.md) | Surface and material | Translucent blurred panels over rich backdrops, with contrast and fallbacks. | aurora-gradient-mesh, bento-layouts, futurism |
| [Neumorphism](neumorphism.md) | Surface and material | Soft extruded controls; needs borders and indicators to be usable. | minimalism, claymorphism, organic-tactile |
| [Claymorphism](claymorphism.md) | Surface and material | Puffy matte shapes with inner highlights in friendly pastels. | organic-tactile, bento-layouts, y2k |
| [Skeuomorphism](skeuomorphism.md) | Surface and material | Real materials and objects, lit consistently, with proper control semantics. | retro-vintage, organic-tactile, grain-and-texture |
| [Liquid materials](liquid-materials.md) | Surface and material | Chrome, oil and gel surfaces from shaders, PBR or SVG, with fallbacks. | experimental-3d, futurism, high-fashion-luxury |
| [Aurora and gradient mesh](aurora-gradient-mesh.md) | Surface and material | Soft drifting colour fields from CSS to WebGL, with text-safe layouts. | glassmorphism, grain-and-texture, product-led-saas |
| [Grain and texture](grain-and-texture.md) | Surface and material | Film grain, paper and halftone as a finishing layer that stays legible. | editorial, aurora-gradient-mesh, retro-vintage |
| [Organic and tactile](organic-tactile.md) | Surface and material | Earthy palettes, soft shapes and bounded spring interactions. | claymorphism, grain-and-texture, retro-vintage |
| [Flat design](flat-design.md) | Surface and material | Solid colour planes and geometric icons with type-led hierarchy. | minimalism, product-led-saas, bento-layouts |
| [Material design](material-design.md) | Surface and material | Layered surfaces, elevation, state overlays and purposeful motion. | product-led-saas, flat-design, minimalism |
| [Isometric and 3D illustration](isometric-illustration.md) | Surface and material | 30-degree grid objects, three tonal faces, one light direction. | product-led-saas, bento-layouts, flat-design |
| [Hand-drawn and doodle](hand-drawn-doodle.md) | Surface and material | Wobbly outlines, marker underlines and handwriting accents. | organic-tactile, collage-cutout, editorial |
| [Line art and outline](line-art-outline.md) | Surface and material | One stroke weight everywhere: outlined icons, contours, hairline rules. | minimalism, japanese-minimalism, editorial |
| [Duotone and monochrome](duotone-monochrome.md) | Surface and material | Two inks or one hue: gradient-mapped photos and tonal ramps. | editorial, grain-and-texture, minimalism |
| [Generative design](generative-design.md) | Motion and technology | Rule-based, seeded visuals with palettes as data and static posters. | swiss-international-typographic, grain-and-texture, futurism |
| [Experimental 3D](experimental-3d.md) | Motion and technology | Real-time 3D as the experience, with one canvas, fallbacks and keyboard access. | motion-led-storytelling, liquid-materials, futurism |
| [Motion-led storytelling](motion-led-storytelling.md) | Motion and technology | Scroll-driven chapters with a mandatory static and reduced-motion version. | editorial, experimental-3d, kinetic-typography |
| [Product-led SaaS](product-led-saas.md) | Product context | The real product as hero: clear promise, proof, restrained polish. | minimalism, bento-layouts, dark-technical-developer-tools |
| [Dark technical / developer tools](dark-technical-developer-tools.md) | Product context | Dark-first, dense, keyboard-centric UI with measured muted text. | minimalism, swiss-international-typographic, bento-layouts |

Notes about combining: avoid pairing opposites (for example minimalism with maximalism, or glassmorphism with brutalism); each note lists styles that conflict with it. Every animated style requires a reduced-motion alternative, and every WebGL style requires a static fallback.
