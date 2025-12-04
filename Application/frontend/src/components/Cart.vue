<template>
    <article class="cart-card">
        <header class="cart-header">
            <div>
                <h3>Patient: {{ patientId }}</h3>
                <div style="font-size:12px; color:#888">Cart: {{ cartId }} · Room: {{ operationRoom }}</div>
            </div>
            <span class="status">{{ status }}</span>
        </header>

        <div class="cart-body">
            <p><strong>Operation:</strong> {{ operation }}</p>
            <p><strong>Anaesthesia:</strong> {{ anaesthesia }}</p>
            <p v-if="operationDate"><strong>Date:</strong> {{ operationDate }}</p>

            <table class="medication" v-if="meds.length">
                <thead>
                    <tr>
                        <th class="med-col-name">Medicine</th>
                        <th class="med-col-leftover">Leftover</th>
                        <th class="med-col-time">Time critical</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(medicine, idx) in meds" :key="idx">
                        <td class="med-name">{{ medicine }}</td>
                        <td class="med-leftover">—</td>
                        <td class="med-time">
                            <input type="checkbox" :aria-label="'Time critical for ' + medicine" disabled />
                        </td>
                    </tr>
                </tbody>
            </table>

            <p v-else class="med-empty">No medications listed</p>
        </div>
    </article>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ cart: { type: Object, required: true } })
const c = props.cart || {}

// Normalize common key variations present in the sample `carts.js` data
const status = computed(() => c.CartStatus ?? c.cartStatus ?? c.status ?? 'unknown')
const patientId = computed(() => c.patientId ?? c.patientID ?? c.patient ?? '—')
const cartId = computed(() => c.CartId ?? c.id ?? c.cartId ?? '—')
const operation = computed(() => c.Operation ?? c.plannedOperation ?? c.operation ?? '—')
const anaesthesia = computed(() => c.FormofAnaesthesia ?? c.formOfAnaesthesia ?? c.FormOfAnaesthesia ?? '—')
const operationDate = computed(() => c.operationDate ?? c.date ?? '')
const operationRoom = computed(() => c.OperationRoom ?? c.operationRoom ?? c.room ?? '—')

const medsRaw = computed(() => {
    // carts.js shows both "Medications" and (inconsistent) "Medication"
    return c.Medications ?? c.Medication ?? c.medication ?? ''
})

const meds = computed(() => {
    if (!medsRaw.value) return []
    // If already an array, use it; if string, split on commas
    if (Array.isArray(medsRaw.value)) return medsRaw.value.map(m => String(m).trim()).filter(Boolean)
    return String(medsRaw.value)
        .split(',')
        .map(m => m.replace(/\s*\'?$|^\'/g, '').trim())
        .filter(Boolean)
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

.cart-header .status {
    font-size: 12px;
    color: #666
}

.cart-body .med {
    font-size: 13px;
    color: #333
}

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
</style>
