# Camera Choreography & Motion Recipes

Camera animation subskills provide production-grade, mathematically smooth camera orbits and reveal paths designed for product showcases.

---

## 1. Camera Motion Matrix

| Subskill | Camera Motion Path | Focal / Lens Behavior | Emotional / Narrative Feel | Typical Duration |
| :--- | :--- | :--- | :--- | :---: |
| **`turntable`** | 360° circular horizontal orbit around subject | Fixed focal length (e.g. 50mm) | Standard product showcase, clean and objective | 5s |
| **`slow-zoom`** | Linear push-in toward a hero feature | Subtle dolly zoom (focal compression) | Dramatic reveal, focusing attention on detail or logo | 4–6s |
| **`dolly-rotate`** | Forward spiral / curved push-in while revolving | Smooth depth shift | High energy, dynamic sweep, premium brand promo | 5–8s |
| **`crane-shot`** | Vertical ascent from base up with downward tilt | Continuous subject tracking | Grand unveiling, majestic elevation, pedestal highlight | 5–7s |
| **`dynamic-full-loop`** | Non-linear speed ramped 360° orbit + whip pans | Variable speed bezier curves | Tech showcase, shows top, sides and bottom briskly | 6–8s |
| **`perfect-loop`** | Constant-angular-velocity 360° loop | Frame 0 matches Frame N exactly | Seamless looping banners, eCommerce background video | 4–6s |

---

## 2. Standard Execution Flow

All camera animation subskills follow a three-phase execution pattern:

### Phase 1: Front Face Detection (Interactive / Bounding Box)
Before running the main animation, determine the model's orientation:
1. Calculate the bounding box center of the target object using `Vector` matrix transformations.
2. Render 4 quick low-res preview stills at 0°, 90°, 180°, and 270°.
3. Confirm with the user or select the front-facing angle as angle offset `0°`.

### Phase 2: Keyframing & Interpolation
1. Attach the camera to an empty target (`PLAIN_AXES`) located at the bounding box centroid.
2. Add a `TRACK_TO` constraint to lock the camera's gaze at the target (Note: lock `track_axis='TRACK_NEGATIVE_Z'` and `up_axis='UP_Y'` per [coordinates-and-scene-building.md](coordinates-and-scene-building.md)).
3. Configure the trajectory curve:
   - For `turntable` and `perfect-loop`: Linear interpolation without easing hitches at loop points. (In Blender 5.x, use `set_fcurves_interpolation()` helper for slotted/layered actions).
   - For `dynamic-full-loop`: Custom ease-in / ease-out speed ramps with quick 10-frame whip transitions between faces.
   - For `slow-zoom` / `crane-shot`: Smooth cubic bezier easing for a soft start and settle.

### Phase 3: Headless / Transparent Render
1. Set `render.film_transparent = True`.
2. Output PNG image sequence or stream directly to `ffmpeg`.
3. Encode as Apple ProRes 4444 (`-c:v prores_ks -profile:v 4 -pix_fmt yuva444p10le`) or WebM (`-c:v libvpx-vp9 -pix_fmt yuva420p`).

---

## 3. Parameter Reference

| Parameter | Default | Units / Options | Description |
| :--- | :---: | :--- | :--- |
| `duration` | `5` | seconds | Total animation duration |
| `fps` | `24` | fps (24, 30, 60) | Timeline framerate |
| `camera_distance` | `4.5` | Blender units / meters | Radius from target centroid |
| `camera_height` | `2.0` | Blender units / meters | Altitude above target centroid |
| `camera_lens` | `50` | millimeters (mm) | Focal length (35mm wide, 50mm normal, 85mm portrait) |
| `transparent_bg` | `true` | boolean | Render with transparent alpha channel |
| `output_format` | `mov` | `mov` \| `webm` | Output video codec format |
