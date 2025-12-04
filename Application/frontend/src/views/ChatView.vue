<template>
  <div class="view chat-view">
    <h1>Chat Log</h1>

    <section class="chat-controls">
      <label for="endpoint">API endpoint</label>
      <input id="endpoint" v-model="endpoint" placeholder="/api/chat/message" />
      <button @click="fetchMessage">Fetch message</button>
      <button @click="clearMessages">Clear</button>
      <label class="auto-label"><input type="checkbox" v-model="autoPoll" /> Auto-poll</label>
    </section>

    <section class="chat-log" ref="logArea">
      <div v-if="messages.length === 0" class="muted">No messages yet. Click "Fetch message" to load one.</div>
      <div v-for="(m, idx) in messages" :key="idx" class="chat-message">
        <div class="meta">{{ formatTime(m.time) }}</div>
        <div class="text">{{ m.text }}</div>
      </div>
    </section>

    <section v-if="error" class="error">{{ error }}</section>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const messages = ref([])
const endpoint = ref('/api/chat/message')
const error = ref('')
const autoPoll = ref(false)
const pollInterval = ref(5000)
let timer = null
const logArea = ref(null)

function formatTime(ts) {
  try {
    return new Date(ts).toLocaleString()
  } catch (e) {
    return ts
  }
}

async function fetchMessage() {
  error.value = ''
  try {
    const res = await fetch(endpoint.value, { cache: 'no-store' })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const payload = await res.json()
    // Try to extract a message string from common shapes
    let text = ''
    if (typeof payload === 'string') text = payload
    else if (payload.message) text = payload.message
    else if (payload.data && payload.data.message) text = payload.data.message
    else text = JSON.stringify(payload)

    messages.value.push({ time: new Date().toISOString(), text })
    await nextTick()
    if (logArea.value) logArea.value.scrollTop = logArea.value.scrollHeight
  } catch (err) {
    error.value = 'Failed to fetch: ' + (err.message || err)
  }
}

function clearMessages() {
  messages.value = []
}

function startPolling() {
  stopPolling()
  timer = setInterval(() => fetchMessage(), pollInterval.value)
}

function stopPolling() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

watch(autoPoll, (v) => {
  if (v) startPolling()
  else stopPolling()
})

onMounted(() => {
  if (autoPoll.value) startPolling()
})

onBeforeUnmount(() => {
  stopPolling()
})
</script>

<style scoped>
.chat-view {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.chat-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}
.chat-controls input[type="text"], .chat-controls input {
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid var(--border, #ddd);
}
.chat-log {
  background: var(--surface, #fafafa);
  border: 1px solid var(--border, #eee);
  padding: 12px;
  border-radius: 8px;
  height: 420px;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.chat-message {
  background: white;
  padding: 8px 10px;
  border-radius: 6px;
  box-shadow: 0 1px 0 rgba(0,0,0,0.03);
}
.chat-message .meta {
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 6px;
}
.chat-message .text {
  white-space: pre-wrap;
}
.muted { color: #666 }
.error { color: #a94442; background: #fcebea; padding: 8px; border-radius: 6px }
.auto-label { margin-left: 8px; font-size: 0.9rem }
</style>
