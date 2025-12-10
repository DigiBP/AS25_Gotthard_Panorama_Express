<template>
  <div class="view chat-view">
    <h1>Log</h1>

    <section class="ws-status">
      <span :class="['status-indicator', { connected: isConnected }]"></span>
      <span class="status-text">WebSocket {{ isConnected ? 'Connected' : 'Disconnected' }}</span>
    </section>

    <section class="chat-log" ref="logArea">
      <div v-if="messages.length === 0" class="muted">No messages yet</div>
      <div v-for="(m, idx) in messages" :key="idx" class="chat-message">
        <div class="meta">{{ formatTime(m.time) }}</div>
        <div class="text">{{ m.text }}</div>
      </div>
    </section>

    <section v-if="error" class="error">{{ error }}</section>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import { useWebSocket } from '../composables/useWebSocket'

const messages = ref([])
const error = ref('')
const logArea = ref(null)

// Handler for incoming WebSocket messages
function handleMessage(data) {
  const text = `[${data.event_type}] ${data.message}${data.cart_id ? ` (Cart: ${data.cart_id})` : ''}`
  messages.value.push({ time: new Date().toISOString(), text })

  // Auto-scroll to bottom
  nextTick(() => {
    if (logArea.value) {
      logArea.value.scrollTop = logArea.value.scrollHeight
    }
  })
}

// Initialize WebSocket connection with message handler
const { isConnected } = useWebSocket(handleMessage)

function formatTime(ts) {
  try {
    return new Date(ts).toLocaleString()
  } catch (e) {
    return ts
  }
}
</script>

<style scoped>
.chat-view {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.ws-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: var(--surface, #fafafa);
  border-radius: 6px;
  border: 1px solid var(--border, #eee);
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #d9534f;
  transition: background-color 0.3s ease;
}

.status-indicator.connected {
  background-color: #5cb85c;
}

.status-text {
  font-size: 0.9rem;
  color: var(--text, #333);
  font-weight: 500;
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
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.03);
}

.chat-message .meta {
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 6px;
}

.chat-message .text {
  white-space: pre-wrap;
}

.muted {
  color: #666
}

.error {
  color: #a94442;
  background: #fcebea;
  padding: 8px;
  border-radius: 6px
}
</style>
