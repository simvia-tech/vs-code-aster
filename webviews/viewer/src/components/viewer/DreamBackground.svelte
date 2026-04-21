<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  let canvas: HTMLCanvasElement;
  let gl: WebGLRenderingContext | null = null;
  let program: WebGLProgram | null = null;
  let uTimeLoc: WebGLUniformLocation | null = null;
  let uResLoc: WebGLUniformLocation | null = null;
  let uThemeLoc: WebGLUniformLocation | null = null;
  let rafHandle: number | null = null;
  let resizeObs: ResizeObserver | null = null;

  const VERT = `
    attribute vec2 aPos;
    void main() {
      gl_Position = vec4(aPos, 0.0, 1.0);
    }
  `;

  const FRAG = `
    precision mediump float;
    uniform vec2 uRes;
    uniform float uTime;
    uniform vec3 uTheme;

    // EDF-ish orange and blue
    const vec3 ORANGE = vec3(1.0, 0.51, 0.16);
    const vec3 BLUE = vec3(0.08, 0.35, 0.78);

    float blob(vec2 p, vec2 c, float r, float soft) {
      float d = length(p - c);
      return smoothstep(r, r * soft, d);
    }

    void main() {
      vec2 uv = gl_FragCoord.xy / uRes.xy;
      float aspect = uRes.x / uRes.y;
      vec2 p = vec2((uv.x - 0.5) * aspect, uv.y - 0.5);

      float t = uTime;

      // Four drifting blobs with independent orbits and independent breathing.
      vec2 c1 = vec2(sin(t * 0.22) * 0.45, cos(t * 0.15) * 0.35);
      float b1 = blob(p, c1, 0.55, 0.0) * (0.55 + 0.45 * sin(t * 0.46));

      vec2 c2 = vec2(sin(t * 0.19 + 1.7) * 0.5, cos(t * 0.29 + 0.9) * 0.4);
      float b2 = blob(p, c2, 0.6, 0.0) * (0.5 + 0.5 * sin(t * 0.36 + 2.0));

      vec2 c3 = vec2(sin(t * 0.14 + 3.2) * 0.5, cos(t * 0.24 + 2.5) * 0.45);
      float b3 = blob(p, c3, 0.5, 0.0) * (0.5 + 0.5 * sin(t * 0.53 + 1.2));

      vec2 c4 = vec2(sin(t * 0.27 + 5.1) * 0.42, cos(t * 0.17 + 4.0) * 0.38);
      float b4 = blob(p, c4, 0.55, 0.0) * (0.45 + 0.55 * sin(t * 0.42 + 3.5));

      float orangeWeight = b1 + b3;
      float blueWeight = b2 + b4;
      float total = orangeWeight + blueWeight;

      // Normalize so overlapping blobs keep their hue instead of muddying to gray.
      vec3 col = ORANGE * orangeWeight + BLUE * blueWeight;
      vec3 hue = total > 0.001 ? col / total : vec3(0.0);
      // Cap the intensity so overlapping blobs at their breathing peak can't
      // fully replace the theme color — at most ~65% blob / 35% theme.
      float intensity = clamp(total * 0.55, 0.0, 0.65);

      // Perceptual theme lightness: > 0.5 = light theme.
      float themeL = dot(uTheme, vec3(0.2126, 0.7152, 0.0722));

      // On dark themes: blend toward the vibrant blob color (brightens).
      // On light themes: blend toward a slightly darkened blob color so the hue
      // stands out against the bright background without washing out to pastel.
      vec3 target = mix(hue, hue * 0.78, smoothstep(0.35, 0.75, themeL));

      vec3 final = mix(uTheme, target, intensity);
      gl_FragColor = vec4(final, 1.0);
    }
  `;

  function compile(gl: WebGLRenderingContext, type: number, src: string): WebGLShader | null {
    const sh = gl.createShader(type);
    if (!sh) return null;
    gl.shaderSource(sh, src);
    gl.compileShader(sh);
    if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) {
      console.error('Shader compile error', gl.getShaderInfoLog(sh));
      gl.deleteShader(sh);
      return null;
    }
    return sh;
  }

  function link(gl: WebGLRenderingContext, vs: WebGLShader, fs: WebGLShader): WebGLProgram | null {
    const p = gl.createProgram();
    if (!p) return null;
    gl.attachShader(p, vs);
    gl.attachShader(p, fs);
    gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) {
      console.error('Program link error', gl.getProgramInfoLog(p));
      return null;
    }
    return p;
  }

  function readTheme(): [number, number, number] {
    const raw = getComputedStyle(document.body)
      .getPropertyValue('--vscode-editor-background')
      .trim();
    const m = raw.match(/^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i);
    if (m) return [parseInt(m[1], 16) / 255, parseInt(m[2], 16) / 255, parseInt(m[3], 16) / 255];
    return [0.12, 0.14, 0.18];
  }

  function resize() {
    if (!canvas || !gl) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.floor(canvas.clientWidth * dpr);
    const h = Math.floor(canvas.clientHeight * dpr);
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
      gl.viewport(0, 0, w, h);
    }
  }

  onMount(() => {
    const scene = document.getElementById('scene');
    if (scene && canvas) {
      scene.insertBefore(canvas, scene.firstChild);
    }
    gl = canvas.getContext('webgl', {
      premultipliedAlpha: true,
      alpha: true,
      preserveDrawingBuffer: true,
    });
    if (!gl) {
      console.error('DreamBackground: no WebGL context');
      return;
    }
    const vs = compile(gl, gl.VERTEX_SHADER, VERT);
    const fs = compile(gl, gl.FRAGMENT_SHADER, FRAG);
    if (!vs || !fs) return;
    program = link(gl, vs, fs);
    if (!program) return;

    const posLoc = gl.getAttribLocation(program, 'aPos');
    uTimeLoc = gl.getUniformLocation(program, 'uTime');
    uResLoc = gl.getUniformLocation(program, 'uRes');
    uThemeLoc = gl.getUniformLocation(program, 'uTheme');

    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(
      gl.ARRAY_BUFFER,
      new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]),
      gl.STATIC_DRAW
    );
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

    resize();

    resizeObs = new ResizeObserver(resize);
    resizeObs.observe(canvas);

    const start = performance.now();
    const loop = () => {
      if (!gl || !program) return;
      const t = (performance.now() - start) / 1000;
      gl.clearColor(0, 0, 0, 0);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.useProgram(program);
      if (uTimeLoc) gl.uniform1f(uTimeLoc, t);
      if (uResLoc) gl.uniform2f(uResLoc, canvas.width, canvas.height);
      if (uThemeLoc) {
        const [r, g, b] = readTheme();
        gl.uniform3f(uThemeLoc, r, g, b);
      }
      gl.drawArrays(gl.TRIANGLES, 0, 6);
      rafHandle = requestAnimationFrame(loop);
    };
    rafHandle = requestAnimationFrame(loop);
  });

  onDestroy(() => {
    if (rafHandle !== null) cancelAnimationFrame(rafHandle);
    resizeObs?.disconnect();
    if (gl && program) {
      gl.deleteProgram(program);
    }
  });
</script>

<canvas bind:this={canvas} class="dream-canvas" aria-hidden="true"></canvas>

<style>
  .dream-canvas {
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    z-index: 0;
    pointer-events: none;
  }
</style>
