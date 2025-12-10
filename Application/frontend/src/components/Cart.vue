<template>
    <article class="cart-card">
        <header class="cart-header">
            <div>
                <h3>Patient: {{ patientId }}</h3>
                <div style="font-size:12px; color:#888">Cart: {{ cartId }} · Room: {{ operationRoom }}</div>
            </div>
            <div class="header-actions">
                <span class="status">{{ status }}</span>
                <button @click="$emit('remove-cart')" class="btn-delete-cart" title="Delete cart">
                    🗑
                </button>
            </div>
        </header>

        <div class="cart-body">
            <p><strong>Operation:</strong> {{ operation }}</p>
            <p><strong>Anaesthesia:</strong> {{ anaesthesia }}</p>
            <p v-if="operationDate"><strong>Date:</strong> {{ operationDate }}</p>

            <table class="medication" v-if="meds.length">
                <thead>
                    <tr>
                        <th class="med-col-name">Medicine</th>
                        <th class="med-col-leftover">Amount</th>
                        <th class="med-col-time">Time critical</th>
                        <th class="med-col-actions">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(medicine, idx) in meds" :key="idx">
                        <td class="med-name">{{ medicine.label }}</td>
                        <td class="med-leftover">{{ medicine.amount }}</td>
                        <td class="med-time">
                            <input type="checkbox" :checked="medicine.timeSensitive"
                                :aria-label="'Time critical for ' + medicine.label" disabled />
                        </td>
                        <td class="med-actions">
                            <button v-if="medicine.id" @click="$emit('remove-medication', medicine.id)"
                                class="btn-remove" title="Remove medication">
                                ×
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>

            <p v-else class="med-empty">No medications listed</p>
        </div>
    </article>
</template>

<script setup>
import { computed, toRef } from 'vue'

const props = defineProps({ cart: { type: Object, required: true } })
const c = toRef(props, 'cart')

// Normalize common key variations present in the sample `carts.js` data
const status = computed(() => c.value.CartStatus ?? c.value.cartStatus ?? c.value.status ?? 'unknown')
const patientId = computed(() => c.value.patientId ?? c.value.patientID ?? c.value.patient ?? '—')
const cartId = computed(() => c.value.CartId ?? c.value.id ?? c.value.cartId ?? '—')
const operation = computed(() => c.value.Operation ?? c.value.plannedOperation ?? c.value.operation ?? '—')
const anaesthesia = computed(() => c.value.FormofAnaesthesia ?? c.value.formOfAnaesthesia ?? c.value.FormOfAnaesthesia ?? '—')
const operationDate = computed(() => c.value.operationDate ?? c.value.date ?? '')
const operationRoom = computed(() => c.value.OperationRoom ?? c.value.operationRoom ?? c.value.room ?? '—')

const medsRaw = computed(() => {
    // Prefer normalized cart.items attached by store; fallback to legacy fields
    if (Array.isArray(c.value.items) && c.value.items.length) return c.value.items
    return c.value.Medications ?? c.value.Medication ?? c.value.medication ?? ''
})

const meds = computed(() => {
    const raw = medsRaw.value
    if (!raw) return []
    // If cart.items array is available
    if (Array.isArray(raw)) {
        return raw.map((m) => ({
            id: m.id,
            label: m.medication_id || m.medicationId || 'unknown',
            amount: m.amount ?? '',
            timeSensitive: Boolean(m.time_sensitive ?? m.timeSensitive),
        }))
    }
    // Legacy string or array of names
    const list = Array.isArray(raw)
        ? raw.map((m) => String(m).trim()).filter(Boolean)
        : String(raw)
            .split(',')
            .map((m) => m.replace(/\s*\'?$|^\'/g, '').trim())
            .filter(Boolean)
    return list.map((name) => ({ label: name, amount: '—', timeSensitive: false }))
})
</script>

<style scoped>
.cart-card {
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 8px;
    padding: 12px;
    background: white;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.cart-header {
    display: flex;
    justify-content: space-between;
    align-items: center
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.cart-header .status {
    font-size: 12px;
    color: #666
}

.cart-body .med {
    font-size: 13px;
    color: #333
}

.cart-header .status {
    font-size: 12px;
    color: #666
}

.cart-body .med {
    font-size: 13px;
    color: #333;
    margin: 0;
}

/* Medication table */
.medication {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    margin-top: 6px;
}

.medication thead th {
    text-align: left;
    padding: 6px 8px;
    border-bottom: 1px solid #eee;
    font-weight: 600;
}

.medication tbody td {
    padding: 6px 8px;
    border-bottom: 1px solid #f5f5f5;
    vertical-align: middle;
}

/* Column widths and alignment */
.med-col-leftover {
    width: 90px;
    text-align: center;
}

.med-col-time {
    width: 110px;
    text-align: center;
}

.med-leftover,
.med-time {
    text-align: center;
}

.med-name {
    /* left aligned by default */
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Checkbox centering */
.med-time input[type="checkbox"] {
    transform: scale(1);
}

/* Actions column */
.med-col-actions {
    width: 80px;
    text-align: center;
}

.med-actions {
    text-align: center;
}

.btn-remove {
    background: grey;
    color: white;
    border: none;
    border-radius: 4px;
    width: 24px;
    height: 24px;
    cursor: pointer;
    font-size: 18px;
    line-height: 1;
    padding: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
}

.btn-remove:hover {
    background: #cc0000;
}

.btn-delete-cart {
    padding: 0.1rem 0.4rem;
    background: grey;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
    transition: all 0.2s;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin: 15px;
}

.btn-delete-cart:hover {
    opacity: 0.8;
    background-color: #cc0000;
}
</style>
