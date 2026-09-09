# A1-U1 resource binding preparation

Raíz autorizada: `content/resources/a1-u1/`.

El layout futuro es `audio/` para WAV y `visual/` para PNG y MP4. Este
documento define bindings relativos; la capa operativa deberá resolver
`repository_root / relative_path`, rechazar escapes fuera del repositorio y
entregar un `Path` absoluto al contrato de `ResourceBinding`.

| resource_id | relative path |
| --- | --- |
| `audio.a1-u1-l1.i-need-water.en-us.v1` | `audio/i-need-water.en-us.wav` |
| `audio.a1-u1-l1.i-need-water.en-gb.v1` | `audio/i-need-water.en-gb.wav` |
| `audio.a1-u1-l1.i-need-help.en-gb.v1` | `audio/i-need-help.en-gb.wav` |
| `audio.a1-u1-l1.i-need-food.en-gb.v1` | `audio/i-need-food.en-gb.wav` |
| `audio.a1-u1-l1.water.en-us.v1` | `audio/water.en-us.wav` |
| `audio.a1-u1-l1.water.en-gb.v1` | `audio/water.en-gb.wav` |
| `audio.a1-u1-l1.help.en-us.v1` | `audio/help.en-us.wav` |
| `audio.a1-u1-l1.help.en-gb.v1` | `audio/help.en-gb.wav` |
| `audio.a1-u1-l1.food.en-us.v1` | `audio/food.en-us.wav` |
| `audio.a1-u1-l1.food.en-gb.v1` | `audio/food.en-gb.wav` |
| `audio.a1-u1-l1.okay.en-us.v1` | `audio/okay.en-us.wav` |
| `audio.a1-u1-l1.okay.en-gb.v1` | `audio/okay.en-gb.wav` |
| `visual.a1-u1-l1.scene.water.v1` | `visual/scene-water.png` |
| `visual.a1-u1-l1.scene.food.v1` | `visual/scene-food.png` |
| `visual.a1-u1-l1.scene.help.v1` | `visual/scene-help.mp4` |
| `visual.a1-u1-l1.comprehension-option.need.v1` | `visual/option-need.png` |
| `visual.a1-u1-l1.comprehension-option.greeting.v1` | `visual/option-greeting.png` |
| `visual.a1-u1-l1.comprehension-option.farewell.v1` | `visual/option-farewell.png` |

No se han creado assets ni expected identities. Cada expected
`ResourcePhysicalIdentity` se derivará únicamente de los bytes finales,
semánticamente y humanamente aprobados. Si esos bytes cambian, su SHA-256
cambia y B51/B52 deberán verificarse de nuevo. Este mapa no activa contenido,
no publica recursos ni habilita loader.
