<template>
    <div class="view dashboard-view">
        <div class="header">
            <h1>Digital carts</h1>
            <div class="controls">
                <button @click="refreshCarts" :disabled="loading" class="btn-refresh">
                    {{ loading ? 'Loading...' : '🔄 Refresh' }}
                </button>
                <button @click="showAddCartForm = !showAddCartForm" class="btn-add">
                    {{ showAddCartForm ? '✖ Cancel' : '+ Add Cart' }}
                </button>
            </div>
        </div>

        <form v-if="showAddCartForm" @submit.prevent="handleAddCart" class="add-cart-form">
            <h2>Create New Cart</h2>
            <div class="form-grid">
                <label>
                    Patient ID:
                    <input v-model="newCart.patientId" type="text" required />
                </label>
                <label>
                    Operation:
                    <input v-model="newCart.operation" type="text" required />
                </label>
                <label>
                    Operation Date:
                    <input v-model="newCart.operationDate" type="date" required />
                </label>
                <label>
                    Anaesthesia Type:
                    <input v-model="newCart.anaesthesiaType" type="text" required />
                </label>
                <label>
                    Room Number:
                    <input v-model="newCart.roomNumber" type="text" required />
                </label>
                <label>
                    Status:
                    <select v-model="newCart.status" required>
                        <option value="Prepared">Prepared</option>
                        <option value="In-Use">In-Use</option>
                        <option value="Closed">Closed</option>
                    </select>
                </label>
            </div>

            <div class="medications-section">
                <h3>Medications</h3>
                <p class="hint">Select medications from the inventory to add to this cart</p>
                <div v-for="(medItem, idx) in newCart.medications" :key="idx" class="medication-row">
                    <select v-model="medItem.medication_id" required>
                        <option value="" disabled>Select medication</option>
                        <option v-for="med in medications" :key="med.value" :value="med.value">
                            {{ med.label }} (Available: {{ med.availableAmount }} {{ med.unit }})
                        </option>
                    </select>
                    <input v-model.number="medItem.amount" type="number" min="0.1" step="0.1" placeholder="Amount"
                        required />
                    <button type="button" @click="removeMedicationFromCart(idx)" class="btn-remove-med">✖</button>
                </div>
                <button type="button" @click="addMedicationToCartForm" class="btn-add-med-inline">+ Add
                    Medication</button>
            </div>

            <div class="form-actions">
                <button type="submit" class="btn-submit" :disabled="loading">Create Cart</button>
                <button type="button" @click="resetForm" class="btn-cancel">Reset</button>
            </div>
            <div v-if="message" class="message" :class="messageType">{{ message }}</div>
        </form>

        <form v-if="showAddMedicationForm" @submit.prevent="handleAddMedication" class="add-cart-form">
            <h2>Add Existing Medication to Cart #{{ selectedCartId }}</h2>
            <p class="hint">Select from the medications</p>
            <div class="form-grid">
                <label>
                    Medication:
                    <select v-model="newMedication.medication_id" required>
                        <option value="" disabled>Select medication</option>
                        <option v-for="med in medications" :key="med.value" :value="med.value">
                            {{ med.label }} (Available: {{ med.availableAmount }} {{ med.unit }})
                        </option>
                    </select>
                </label>
                <label>
                    Amount:
                    <input v-model.number="newMedication.amount" type="number" min="0.1" step="0.1" required />
                    <span class="available-hint" v-if="selectedMedicationAvailable">
                        Available: {{ selectedMedicationAvailable.amount }} {{ selectedMedicationAvailable.unit }}
                    </span>
                </label>
            </div>
            <div class="form-actions">
                <button type="submit" class="btn-submit" :disabled="loading">Add Medication</button>
                <button type="button" @click="showAddMedicationForm = false; resetMedicationForm()"
                    class="btn-cancel">Cancel</button>
            </div>
            <div v-if="message" class="message" :class="messageType">{{ message }}</div>
        </form>

        <section class="carts-grid">
            <div v-for="cart in carts" :key="cart.id" class="cart-wrapper">
                <Cart :cart="cart" @remove-medication="handleRemoveMedication"
                    @remove-cart="handleRemoveCart(cart.id)" />
                <button @click="openAddMedicationForm(cart.id)" class="btn-add-med">
                    + Add Medication
                </button>
            </div>
        </section>

        <div v-if="carts.length === 0 && !loading" class="empty-state">
            No carts found. Create one using the "Add Cart" button above.
        </div>
    </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import Cart from '../components/Cart.vue'
import { useCartsStore } from '../stores/carts.js'
import { useMedicationsStore } from '../stores/medications.js'

const store = useCartsStore()
const medsStore = useMedicationsStore()

const carts = computed(() => store.carts)
const loading = computed(() => store.loading)
const medications = computed(() => medsStore.options)
const selectedMedicationAvailable = computed(() => {
    if (!newMedication.value.medication_id) return null
    const med = medications.value.find(m => m.value === newMedication.value.medication_id)
    return med ? { amount: med.availableAmount, unit: med.unit } : null
})

const showAddCartForm = ref(false)
const showAddMedicationForm = ref(false)
const selectedCartId = ref(null)
const message = ref('')
const messageType = ref('success')

const newCart = ref({
    patientId: '',
    operation: '',
    operationDate: '',
    anaesthesiaType: '',
    roomNumber: '',
    status: 'Prepared',
    medications: []
})

const newMedication = ref({
    cart_id: null,
    medication_id: '',
    amount: 1,
    inventory_id: 1,
    time_sensitive: false
})

const resetForm = () => {
    newCart.value = {
        patientId: '',
        operation: '',
        operationDate: '',
        anaesthesiaType: '',
        roomNumber: '',
        status: 'Prepared',
        medications: []
    }
    message.value = ''
}

const addMedicationToCartForm = () => {
    newCart.value.medications.push({
        medication_id: '',
        amount: 1,
        inventory_id: 1,
        time_sensitive: false
    })
}

const removeMedicationFromCart = (index) => {
    newCart.value.medications.splice(index, 1)
}

const resetMedicationForm = () => {
    newMedication.value = {
        cart_id: selectedCartId.value,
        inventory_id: 1,
        medication_id: '',
        amount: 1,
        time_sensitive: false
    }
}

const handleAddCart = async () => {
    try {
        message.value = ''

        // Validate and add inventory_id to all medications
        const medicationsWithInventory = newCart.value.medications.map(med => {
            const inventoryId = medsStore.getFirstInventoryId(med.medication_id)
            if (!inventoryId) {
                throw new Error(`Medication ${med.medication_id} not found in inventory`)
            }
            return {
                ...med,
                inventory_id: inventoryId
            }
        })

        const cartData = {
            patientId: newCart.value.patientId,
            operation: newCart.value.operation,
            operationDate: newCart.value.operationDate,
            anaesthesiaType: newCart.value.anaesthesiaType,
            roomNumber: newCart.value.roomNumber,
            status: newCart.value.status
        }

        await store.addCartWithMedications(cartData, medicationsWithInventory)

        message.value = 'Cart created successfully!'
        messageType.value = 'success'
        resetForm()
        setTimeout(() => {
            showAddCartForm.value = false
            message.value = ''
        }, 2000)
    } catch (err) {
        message.value = `Failed to create cart: ${err.message}`
        messageType.value = 'error'
    }
}

const openAddMedicationForm = (cartId) => {
    selectedCartId.value = cartId
    newMedication.value.cart_id = cartId
    showAddMedicationForm.value = true
    message.value = ''
}

const handleAddMedication = async () => {
    try {
        message.value = ''

        // Get the correct inventory_id for the selected medication
        const inventoryId = medsStore.getFirstInventoryId(newMedication.value.medication_id)
        if (!inventoryId) {
            message.value = 'Selected medication not found in inventory'
            messageType.value = 'error'
            return
        }

        await store.addMedicationToCart(selectedCartId.value, {
            medication_id: newMedication.value.medication_id,
            amount: newMedication.value.amount,
            inventory_id: inventoryId,
            time_sensitive: newMedication.value.time_sensitive
        })

        message.value = 'Medication added to cart successfully!'
        messageType.value = 'success'
        resetMedicationForm()

        // Refresh carts to show updated medications
        await store.refresh()

        setTimeout(() => {
            showAddMedicationForm.value = false
            message.value = ''
        }, 2000)
    } catch (err) {
        message.value = `Failed to add medication: ${err.message}`
        messageType.value = 'error'
    }
}

const handleRemoveMedication = async (cartItemId) => {
    if (!confirm('Are you sure you want to remove this medication from the cart?')) {
        return
    }
    try {
        await store.removeMedicationFromCart(cartItemId)
        message.value = 'Medication removed successfully!'
        messageType.value = 'success'
        setTimeout(() => {
            message.value = ''
        }, 2000)
    } catch (err) {
        message.value = `Failed to remove medication: ${err.message}`
        messageType.value = 'error'
    }
}

const handleRemoveCart = async (cartId) => {
    if (!confirm('Are you sure you want to delete this cart? This will also remove all medications in it.')) {
        return
    }
    try {
        message.value = ''
        await store.removeCart(cartId)
        message.value = 'Cart deleted successfully!'
        messageType.value = 'success'
        setTimeout(() => {
            message.value = ''
        }, 2000)
    } catch (err) {
        message.value = `Failed to delete cart: ${err.message}`
        messageType.value = 'error'
    }
}

const refreshCarts = async () => {
    try {
        message.value = ''
        await store.refresh()
    } catch (err) {
        message.value = `Failed to refresh: ${err.message}`
        messageType.value = 'error'
    }
}
</script>

<style scoped>
.dashboard-view {
    padding: 1rem;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.header h1 {
    margin: 0;
}

.controls {
    display: flex;
    gap: 0.5rem;
}

.btn-refresh,
.btn-add {
    padding: 0.5rem 1rem;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--surface);
    color: var(--text);
    cursor: pointer;
    font-size: 0.9rem;
}

.btn-refresh:hover,
.btn-add:hover {
    background: color-mix(in srgb, var(--primary-200) 12%, transparent);
}

.btn-refresh:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.add-cart-form {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.add-cart-form h2 {
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1.25rem;
}

.form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin-bottom: 1rem;
}

.form-grid label {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    font-size: 0.9rem;
    font-weight: 500;
}

.form-grid input,
.form-grid select {
    padding: 0.5rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    background: var(--surface);
    color: var(--text);
    font-size: 0.9rem;
}

.form-actions {
    display: flex;
    gap: 0.5rem;
}

.btn-submit {
    padding: 0.6rem 1.2rem;
    background: var(--primary-600);
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
}

.btn-submit:hover {
    background: var(--primary);
}

.btn-submit:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-cancel {
    padding: 0.6rem 1.2rem;
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
    cursor: pointer;
}

.btn-cancel:hover {
    background: color-mix(in srgb, var(--muted) 10%, transparent);
}

.message {
    margin-top: 1rem;
    padding: 0.75rem;
    border-radius: 6px;
    font-size: 0.9rem;
}

.message.success {
    background: color-mix(in srgb, var(--success) 10%, transparent);
    color: var(--success);
    border: 1px solid var(--success);
}

.message.error {
    background: color-mix(in srgb, var(--danger) 10%, transparent);
    color: var(--danger);
    border: 1px solid var(--danger);
}

.hint {
    margin: 0 0 1rem 0;
    font-size: 0.85rem;
    color: var(--muted);
}

.available-hint {
    display: block;
    margin-top: 0.25rem;
    font-size: 0.8rem;
    color: var(--success);
    font-weight: 500;
}

.medications-section {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
}

.medications-section h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
}

.medication-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1.5fr auto;
    gap: 0.5rem;
    align-items: center;
    margin-bottom: 0.75rem;
}

.medication-row select,
.medication-row input {
    padding: 0.5rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    background: var(--surface);
    color: var(--text);
    font-size: 0.9rem;
}

.checkbox-inline {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.85rem;
    font-weight: 400;
}

.checkbox-inline input[type="checkbox"] {
    width: auto;
    margin: 0;
}

.btn-remove-med {
    padding: 0.4rem 0.6rem;
    background: var(--danger);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
}

.btn-remove-med:hover {
    opacity: 0.8;
}

.btn-add-med-inline {
    padding: 0.5rem 1rem;
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85rem;
    margin-top: 0.5rem;
}

.btn-add-med-inline:hover {
    background: color-mix(in srgb, var(--accent-1) 12%, transparent);
    border-color: var(--accent-1);
}

.checkbox-label {
    display: flex;
    flex-direction: row !important;
    align-items: center;
    gap: 0.5rem;
}

.checkbox-label input[type="checkbox"] {
    width: auto;
    margin: 0;
}

.carts-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    align-items: start;
}

.cart-wrapper {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.btn-add-med {
    padding: 0.5rem;
    border: 1px solid var(--border);
    border-radius: 6px;
    background: var(--surface);
    color: var(--text);
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.2s;
}

.btn-add-med:hover {
    background: color-mix(in srgb, var(--accent-1) 12%, transparent);
    border-color: var(--accent-1);
}

.empty-state {
    text-align: center;
    padding: 3rem;
    color: var(--muted);
    font-size: 1rem;
}

@media (max-width: 900px) {
    .form-grid {
        grid-template-columns: 1fr;
    }

    .medication-row {
        grid-template-columns: 1fr;
    }

    .btn-remove-med {
        width: 100%;
    }
}

@media (max-width: 700px) {
    .carts-grid {
        grid-template-columns: 1fr;
    }

    .header {
        flex-direction: column;
        align-items: flex-start;
    }
}
</style>
