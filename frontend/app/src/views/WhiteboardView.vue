<template>
  <div class="card border-0 shadow-sm">
    <div class="card-body">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div>
          <h4 class="fw-semibold mb-0">Collaborative whiteboard</h4>
          <p class="text-muted mb-0">Draw in real time with your classmates.</p>
        </div>
        <div class="d-flex gap-2">
          <input v-model="strokeColor" type="color" class="form-control form-control-color" title="Pick color" />
          <select v-model.number="strokeWidth" class="form-select form-select-sm" style="width: 90px;">
            <option :value="2">Fine</option>
            <option :value="4">Medium</option>
            <option :value="8">Bold</option>
          </select>
          <button class="btn btn-outline-secondary" @click="clearBoard">
            <i class="bi bi-eraser me-1"></i>Clear
          </button>
          <button class="btn btn-primary" @click="saveSnapshot">
            <i class="bi bi-cloud-arrow-up me-1"></i>Save
          </button>
        </div>
      </div>
      <div class="whiteboard-wrapper">
        <canvas ref="canvasRef" class="whiteboard-canvas"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';

type Point = { x: number; y: number };
type Stroke = { points: Point[]; color: string; width: number };

const route = useRoute();
const sessionId = route.params.sessionId as string;
const canvasRef = ref<HTMLCanvasElement | null>(null);

const strokes = ref<Stroke[]>([]);
const strokeColor = ref('#1b6ef3');
const strokeWidth = ref(4);
const drawing = ref(false);
const currentStroke = ref<Stroke | null>(null);
let ctx: CanvasRenderingContext2D | null = null;
let socket: WebSocket | null = null;

function setupCanvas() {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx = canvas.getContext('2d');
  if (ctx) {
    ctx.scale(dpr, dpr);
    ctx.lineCap = 'round';
    redraw();
  }
}

function startDrawing(event: PointerEvent) {
  if (!ctx) return;
  drawing.value = true;
  const point = getCanvasPoint(event);
  currentStroke.value = {
    points: [point],
    color: strokeColor.value,
    width: strokeWidth.value
  };
}

function draw(event: PointerEvent) {
  if (!drawing.value || !ctx || !currentStroke.value) return;
  const point = getCanvasPoint(event);
  currentStroke.value.points.push(point);
  redrawStroke(currentStroke.value);
}

function stopDrawing() {
  if (!drawing.value || !currentStroke.value) return;
  drawing.value = false;
  strokes.value.push(currentStroke.value);
  sendStroke(currentStroke.value);
  currentStroke.value = null;
}

function redraw() {
  if (!ctx) return;
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  const drawnStrokes = [...strokes.value];
  if (currentStroke.value) drawnStrokes.push(currentStroke.value);
  drawnStrokes.forEach(redrawStroke);
}

function redrawStroke(stroke: Stroke) {
  if (!ctx || stroke.points.length < 2) return;
  ctx.strokeStyle = stroke.color;
  ctx.lineWidth = stroke.width;
  ctx.beginPath();
  const [start, ...rest] = stroke.points;
  ctx.moveTo(start.x, start.y);
  rest.forEach((point) => ctx?.lineTo(point.x, point.y));
  ctx.stroke();
}

function getCanvasPoint(event: PointerEvent): Point {
  const canvas = canvasRef.value;
  if (!canvas) return { x: 0, y: 0 };
  const rect = canvas.getBoundingClientRect();
  return {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  };
}

function connectSocket() {
  const baseUrl = import.meta.env.VITE_WS_URL || (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws';
  const url = `${baseUrl.replace(/\/$/, '')}/whiteboard/${sessionId}/`;
  socket = new WebSocket(url);
  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === 'session.init') {
      strokes.value = message.payload.strokes || [];
      redraw();
    } else if (message.type === 'stroke.append') {
      strokes.value.push(message.payload.stroke);
      redraw();
    } else if (message.type === 'board.clear') {
      strokes.value = [];
      redraw();
    } else if (message.type === 'snapshot.save') {
      // ignore for now
    }
  };
}

function sendStroke(stroke: Stroke) {
  socket?.send(
    JSON.stringify({
      action: 'stroke.append',
      payload: { stroke }
    })
  );
}

function clearBoard() {
  strokes.value = [];
  redraw();
  socket?.send(JSON.stringify({ action: 'board.clear' }));
}

function saveSnapshot() {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const dataUrl = canvas.toDataURL('image/png');
  socket?.send(
    JSON.stringify({
      action: 'snapshot.save',
      payload: { snapshot: dataUrl, strokes: strokes.value }
    })
  );
}

function handleResize() {
  setupCanvas();
}

onMounted(() => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  canvas.addEventListener('pointerdown', startDrawing);
  canvas.addEventListener('pointermove', draw);
  window.addEventListener('pointerup', stopDrawing);
  window.addEventListener('resize', handleResize);
  setupCanvas();
  connectSocket();
});

onBeforeUnmount(() => {
  const canvas = canvasRef.value;
  if (canvas) {
    canvas.removeEventListener('pointerdown', startDrawing);
    canvas.removeEventListener('pointermove', draw);
  }
  window.removeEventListener('pointerup', stopDrawing);
  window.removeEventListener('resize', handleResize);
  socket?.close();
});
</script>

<style scoped>
.whiteboard-wrapper {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 0.75rem;
  overflow: hidden;
  height: 520px;
}

.whiteboard-canvas {
  width: 100%;
  height: 100%;
  touch-action: none;
  cursor: crosshair;
  background: repeating-linear-gradient(0deg, rgba(0, 0, 0, 0.03), rgba(0, 0, 0, 0.03) 32px, transparent 32px, transparent 64px),
    #fff;
}
</style>

