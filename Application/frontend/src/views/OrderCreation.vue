<template>
    <div class="view order-creation-view">
        <h1>Create Order</h1>

        <form @submit.prevent="submitOrder" class="order-form">
            <fieldset class="order-meta">
                <label>Needed by: <input type="date" v-model="neededBy" /></label>
                <label>Ordered by: <input type="text" v-model="orderedBy" />
                    <span class="order-type-badge" :class="orderTypeClass" :title="orderTypeTitle">{{ orderTypeShort
                    }}</span>
                    <select class="order-type-select" v-model="orderTypeOverride" title="Order type override">
                        <option value="auto">Auto</option>
                        <option value="internal">Internal</option>
                        <option value="external">External</option>
                    </select>
                </label>
                <label><input type="checkbox" v-model="isRush" /> Rush order</label>
                <label class="wide">Comment: <input type="text" v-model="orderComment"
                        placeholder="Optional comment" /></label>
            </fieldset>
            <div class="rows">
                <div v-for="(row, idx) in rows" :key="row._uid" class="order-row">
                    <select v-model="row.medicationId" class="med-select">
                        <option value="" disabled>Select medication</option>
                        <option v-for="opt in medicationOptions" :key="opt.value" :value="opt.value">
                            {{ opt.label }}
                        </option>
                    </select>

                    <input type="number" v-model.number="row.quantity" min="0" step="1" class="qty"
                        :placeholder="metaPlaceholder(row)" />
                    <div class="spacer">
                        <span class="quantity">{{ metaFor(row.medicationId)?.quantity * row.quantity || '' }}</span>
                        <span class="unit">{{ metaFor(row.medicationId)?.unit || '' }}</span>
                    </div>

                    <input type="text" v-model="row.notes" placeholder="Notes (optional)" class="notes" />

                    <button type="button" class="remove" @click="removeRow(idx)">Remove</button>
                </div>
            </div>

            <div class="controls">
                <button type="button" @click="addRow">Add medicine</button>
                <button type="submit" class="submit">Place order</button>
            </div>
        </form>

        <div v-if="message" class="message">{{ message }}</div>
    </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useCartsStore } from '../stores/carts'
import { useMedicationsStore } from '../stores/medications'
import { useOrdersStore } from '../stores/orders'
import { useUserSessionStore } from '../stores/user_session'

// local reactive rows for ordering multiple medicines
const rows = ref([
    { _uid: Date.now() + '-r0', medicationId: '', quantity: 1, notes: '' }
])

const message = ref('')

const meds = useMedicationsStore()
const carts = useCartsStore()
const orders = useOrdersStore()
const users = useUserSessionStore()

const currentUserName = computed(() => (users.currentUser && users.currentUser.name) ? users.currentUser.name : '')

// live computed orderer name (either typed value or current user)
const ordererName = computed(() => (orderedBy.value && orderedBy.value.trim()) || currentUserName.value || '')

// allow manual override: 'auto' (detect), 'internal', 'external'
const orderTypeOverride = ref('auto')

// determine internal/external based on mockUsers list
const isInternal = computed(() => {
    return users.mockUsers && users.mockUsers.some((u) => u.name === ordererName.value)
})

// effective internal/external taking override into account
const effectiveIsInternal = computed(() => {
    if (orderTypeOverride.value === 'auto') return isInternal.value
    return orderTypeOverride.value === 'internal'
})

const orderTypeShort = computed(() => (effectiveIsInternal.value ? 'INT' : 'EXT'))
const orderTypeTitle = computed(() => (effectiveIsInternal.value ? 'Internal' : 'External'))
const orderTypeClass = computed(() => (effectiveIsInternal.value ? 'internal' : 'external'))

const medicationOptions = computed(() => meds.options)

function metaFor(medId) {
    return medId ? meds.byId(medId) : null
}

function metaPlaceholder(row) {
    const m = metaFor(row.medicationId)
    if (m && m.quantity) return `Amount (e.g. ${m.quantity})`
    if (m && m.dosage) return `Amount (dosage ${m.dosage})`
    return 'Amount'
}

function addRow() {
    rows.value.push({ _uid: Date.now() + '-' + Math.random().toString(36).slice(2, 7), medicationId: '', quantity: 1, notes: '' })
}

// Order-level metadata
const neededBy = ref('')
const orderedBy = ref(currentUserName.value || '')
const isRush = ref(false)
const orderComment = ref('')

function removeRow(index) {
    if (rows.value.length === 1) {
        // keep at least one row
        rows.value[0] = { _uid: Date.now() + '-r0', medicationId: '', quantity: 1, notes: '' }
    } else {
        rows.value.splice(index, 1)
    }
}

function validateRows() {
    for (const r of rows.value) {
        if (!r.medicationId) return { ok: false, reason: 'Please select a medication for each row.' }
        if (r.quantity == null || isNaN(r.quantity) || r.quantity <= 0) return { ok: false, reason: 'Quantity must be greater than 0.' }
    }
    return { ok: true }
}

function submitOrder() {
    message.value = ''
    const v = validateRows()
    if (!v.ok) {
        message.value = v.reason
        return
    }

    if (!neededBy.value) {
        message.value = 'Please provide a needed-by date.'
        return
    }

    // build payload with medication details
    const ordered = rows.value.map((r) => {
        const meta = meds.byId(r.medicationId)
        return {
            medicationId: r.medicationId,
            name: meta ? meta.name : r.medicationId,
            dosage: meta ? meta.dosage : '',
            quantity: r.quantity,
            unit: meta ? (meta.unit || '') : '',
            notes: r.notes || ''
        }
    })

    // Add a simple 'order' entry to carts store for visibility in the prototype app

    try {
        // use computed effective orderer name and effective internal/external (takes override into account)
        const effectiveOrdererName = ordererName.value

        const entry = orders.addOrder({
            neededBy: neededBy.value,
            orderedBy: effectiveOrdererName,
            isRush: Boolean(isRush.value),
            comment: orderComment.value || '',
            items: ordered,
            orderType: effectiveIsInternal.value ? 'internal' : 'external'
        })
        message.value = `Order placed — id ${entry.id}`
        // reset form
        rows.value = [{ _uid: Date.now() + '-r0', medicationId: '', quantity: 1, notes: '' }]
        neededBy.value = ''
        isRush.value = false
        orderComment.value = ''
        // reset override to auto
        orderTypeOverride.value = 'auto'
    } catch (err) {
        console.error(err)
        message.value = 'Failed to place order. See console.'
    }
}
</script>

<style scoped>
.order-creation-view {
    padding: 1rem;
}

.order-form {
    display: grid;
    gap: 0.75rem;
    max-width: 900px;
}

.order-row {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

.med-select {
    flex: 1 1 50%;
    padding: 0.4rem;
}

.qty {
    width: 80px;
    padding: 0.3rem
}

.notes {
    flex: 1 1 30%;
    padding: 0.4rem
}

.remove {
    background: #f8d7da;
    border: 1px solid #f5c2c7;
    padding: 0.3rem 0.5rem
}

.controls {
    display: flex;
    gap: 0.5rem;
}

.order-meta {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 0.5rem
}

.order-meta label {
    display: flex;
    gap: 0.4rem;
    align-items: center
}

.order-meta .wide {
    flex: 1
}

.submit {
    background: #0b5;
    padding: 0.4rem 0.8rem
}

.order-type-badge {
    display: inline-block;
    margin-left: 0.5rem;
    padding: 0.15rem 0.4rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 700;
    color: white;
}

.order-type-badge.internal {
    background: #2b8a3e;
    /* green */
}

.order-type-badge.external {
    background: #8a2b2b;
    /* red/brown */
}

.message {
    margin-top: 1rem;
    color: #064
}

.spacer {
    width: 200px;
    text-align: center;
}
</style>
