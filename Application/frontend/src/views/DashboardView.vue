<template>
    <div class="view dashboard-view">
        <h1>Dashboard</h1>

        <section class="orders-block">
            <h2>Recent Orders</h2>
            <p class="muted">Open and inspect recent orders created in the prototype.</p>
            <div v-if="ordersList.length === 0" class="muted">No orders yet.</div>
            <ul>
                <li v-for="o in ordersList" :key="o.id">
                    <strong>{{ o.id }}</strong> — Needed by {{ o.neededBy }} — {{ o.isRush ? 'RUSH' : 'Normal' }} —
                    Ordered by {{ o.orderedBy }}
                    <button @click="openOrder(o.id)">Open</button>
                </li>
            </ul>

            <div v-if="showOrderModal" class="modal-backdrop" @click.self="closeOrder">
                <div class="modal">
                    <header class="modal-header">
                        <h3>Order {{ selectedOrder?.id }}</h3>
                        <button class="close-btn" @click="closeOrder">×</button>
                    </header>
                    <p class="muted">Needed by: {{ selectedOrder?.neededBy }} — Ordered by: {{ selectedOrder?.orderedBy
                    }} —
                        {{ selectedOrder?.isRush ? 'Rush' : 'Normal' }}</p>
                    <p>Comment: {{ selectedOrder?.comment || '-' }}</p>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Medication</th>
                                <th>Qty</th>
                                <th>Unit</th>
                                <th>Notes</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="it in selectedOrder?.items || []" :key="it.medicationId">
                                <td>{{ it.name }}</td>
                                <td>{{ it.quantity }}</td>
                                <td>{{ it.unit || '-' }}</td>
                                <td>{{ it.notes || '-' }}</td>
                            </tr>
                        </tbody>
                    </table>
                    <div class="modal-actions">
                        <button @click="closeOrder">Close</button>
                    </div>
                </div>
            </div>
        </section>
    </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useOrdersStore } from '../stores/orders.js'

const ordersStore = useOrdersStore()

const ordersList = computed(() => ordersStore.orders)
const selectedOrderId = ref(null)
const showOrderModal = ref(false)
const selectedOrder = computed(() => (selectedOrderId.value ? ordersStore.getOrder(selectedOrderId.value) : null))

function openOrder(id) {
    selectedOrderId.value = id
    showOrderModal.value = true
}
function closeOrder() {
    showOrderModal.value = false
    selectedOrderId.value = null
}
</script>

<style scoped>
.dashboard-view {
    padding: 1rem
}

.orders-block {
    margin-top: 1rem
}

.muted {
    color: #666
}

.table {
    width: 100%;
    border-collapse: collapse
}

.table th,
.table td {
    border: 1px solid #ddd;
    padding: 0.3rem
}

/* Modal styles */
.modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 2rem;
    z-index: 1001;
}

.modal {
    background: white;
    border-radius: 8px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
    max-width: 700px;
    width: 100%;
    padding: 1rem;
    border: 1px solid #ddd;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.close-btn {
    border: none;
    background: transparent;
    font-size: 1.25rem;
    cursor: pointer;
    line-height: 1;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 0.5rem;
}
</style>
