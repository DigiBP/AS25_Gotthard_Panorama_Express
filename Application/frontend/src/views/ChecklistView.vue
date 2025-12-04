<template>
    <div class="view checklist-view">
        <h1>Checklist</h1>

        <section class="controls">
            <label for="endpoint">API endpoint</label>
            <input id="endpoint" v-model="endpoint" placeholder="/api/checklist" />
            <button @click="loadChecklist">Load</button>
            <button @click="saveChecklist" :disabled="saving">Save All</button>
            <span v-if="saving" class="muted">Saving…</span>
        </section>

        <section class="list">
            <div v-if="error" class="error">{{ error }}</div>
            <div v-if="items.length === 0 && !error" class="muted">No items loaded. Click Load.</div>

            <ul>
                <li v-for="(it, idx) in items" :key="idx" class="item">
                    <label class="row">
                        <input type="checkbox" v-model="it.check" />
                        <span class="name">{{ it.name }}</span>
                        <span class="amount">{{ it.amount }}</span>
                    </label>
                </li>
            </ul>
        </section>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import checklist from './checklist.json'

const endpoint = ref('/api/checklist')
const items = ref([])
const error = ref('')
const saving = ref(false)

async function loadChecklist() {
    error.value = ''
    items.value = []
    try {

        const data = checklist
        // Expect an array of { name, amount, check }
        if (Array.isArray(data)) {
            // Normalize items: ensure fields exist
            items.value = data.map((d) => ({
                name: d.name ?? '',
                amount: d.amount ?? '',
                check: !!d.check,
            }))
        } else {
            throw new Error('Invalid payload: expected an array')
        }
    } catch (err) {
        error.value = `Failed to load: ${err.message || err}`
    }
}

async function saveChecklist() {
    error.value = ''
    saving.value = true
    try {
        const res = await fetch(endpoint.value, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(items.value),
        })
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
    } catch (err) {
        error.value = `Failed to save: ${err.message || err}`
    } finally {
        saving.value = false
    }
}
</script>

<style scoped>
.checklist-view {
    padding: 1rem
}

.controls {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-bottom: 12px
}

.controls input {
    padding: 6px 8px;
    border-radius: 6px;
    border: 1px solid var(--border, #ddd)
}

.list ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 8px
}

.item {
    background: var(--surface, #fff);
    border: 1px solid var(--border, #eee);
    border-radius: 6px;
    padding: 8px
}

.row {
    display: flex;
    align-items: center;
    gap: 12px
}

.name {
    flex: 1
}

.amount {
    width: 80px;
    text-align: right;
    color: #333
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
