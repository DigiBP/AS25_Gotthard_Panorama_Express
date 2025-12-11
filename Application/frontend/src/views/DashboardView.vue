<template>
    <div class="view dashboard-view">
        <h1>Dashboard</h1>

        <section class="orders-block">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2>Recent Orders</h2>
                    <p class="muted">Open and inspect recent orders created in the prototype.</p>
                </div>
                <button @click="refreshOrders" :disabled="ordersStore.loading" class="refresh-btn">
                    {{ ordersStore.loading ? 'Refreshing...' : 'Refresh' }}
                </button>
            </div>
            <div v-if="ordersStore.loading && ordersList.length === 0" class="muted">Loading orders...</div>
            <div v-else-if="ordersStore.error" class="error-msg">{{ ordersStore.error }}</div>
            <div v-else-if="ordersList.length === 0" class="muted">No orders yet.</div>
            <ul>
                <li v-for="o in ordersList" :key="o.id">
                    <strong>Order #{{ o.id }}</strong> — Date: {{ o.date }} — {{ o.isRush ? 'RUSH' : 'Normal' }} —
                    Ordered by: {{ o.name }} ({{ o.isInternal ? 'Internal' : 'External' }})
                    <button @click="openOrder(o.id)">Open</button>
                </li>
            </ul>

            <div v-if="showOrderModal" class="modal-backdrop" @click.self="closeOrder">
                <div class="modal">
                    <header class="modal-header">
                        <h3>Order #{{ selectedOrder?.id }}</h3>
                        <button class="close-btn" @click="closeOrder">×</button>
                    </header>
                    <p class="muted">
                        Date: {{ selectedOrder?.date }} —
                        Ordered by: {{ selectedOrder?.name }} ({{ selectedOrder?.isInternal ? 'Internal' : 'External'
                        }}) —
                        {{ selectedOrder?.isRush ? 'Rush' : 'Normal' }}
                    </p>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Medication ID</th>
                                <th>Medication Name</th>
                                <th>Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="med in selectedOrder?.medications || []" :key="med.medicationId">
                                <td>{{ med.medicationId }}</td>
                                <td>{{ getMedicationName(med.medicationId) }}</td>
                                <td>{{ med.amount }}</td>
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
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useMedicationsStore } from '../stores/medications.js'
import { useOrdersStore } from '../stores/orders.js'

const ordersStore = useOrdersStore()
const medicationsStore = useMedicationsStore()

const ordersList = computed(() => ordersStore.orders)
const selectedOrderId = ref(null)
const showOrderModal = ref(false)
const selectedOrder = computed(() => (selectedOrderId.value ? ordersStore.getOrder(selectedOrderId.value) : null))

let autoRefreshInterval = null

function openOrder(id) {
    selectedOrderId.value = id
    showOrderModal.value = true
}
function closeOrder() {
    showOrderModal.value = false
    selectedOrderId.value = null
}

async function refreshOrders() {
    await ordersStore.refresh()
}

function getMedicationName(medicationId) {
    const medication = medicationsStore.medications.find(m => m.medicationId === medicationId)
    return medication ? medication.name : medicationId
}

// Auto-refresh every 30 seconds
onMounted(() => {
    autoRefreshInterval = setInterval(() => {
        ordersStore.fetchOrders()
    }, 30000)
})

onUnmounted(() => {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval)
    }
})
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

.refresh-btn {
    padding: 0.5rem 1rem;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
}

.refresh-btn:hover:not(:disabled) {
    background: #0056b3;
}

.refresh-btn:disabled {
    background: #6c757d;
    cursor: not-allowed;
}

.error-msg {
    color: #dc3545;
    padding: 0.5rem;
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 4px;
    margin: 0.5rem 0;
}
</style>
