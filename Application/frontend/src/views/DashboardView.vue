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

            <div v-if="selectedOrder" class="order-details">
                <h3>Order {{ selectedOrder.id }}</h3>
                <p>Needed by: {{ selectedOrder.neededBy }} — Ordered by: {{ selectedOrder.orderedBy }} — {{
                    selectedOrder.isRush ? 'Rush' : 'Normal' }}</p>
                <p>Comment: {{ selectedOrder.comment || '-' }}</p>
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
                        <tr v-for="it in selectedOrder.items" :key="it.medicationId">
                            <td>{{ it.name }}</td>
                            <td>{{ it.quantity }}</td>
                            <td>{{ it.unit || '-' }}</td>
                            <td>{{ it.notes || '-' }}</td>
                        </tr>
                    </tbody>
                </table>
                <button @click="closeOrder">Close</button>
            </div>
        </section>
    </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useOrdersStore } from '../stores/orders'

const ordersStore = useOrdersStore()

const ordersList = computed(() => ordersStore.orders)
const selectedOrderId = ref(null)
const selectedOrder = computed(() => (selectedOrderId.value ? ordersStore.getOrder(selectedOrderId.value) : null))

function openOrder(id) { selectedOrderId.value = id }
function closeOrder() { selectedOrderId.value = null }
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
</style>
