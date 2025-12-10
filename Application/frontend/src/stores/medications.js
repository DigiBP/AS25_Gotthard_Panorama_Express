import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

/**
 * Medications store
 * - Fetches medications from backend endpoint
 * - Exposes raw list and dropdown-friendly options
 */
export const useMedicationsStore = defineStore('medications', () => {
    const medications = ref([])
    const inventory = ref([])
    const loading = ref(false)
    const error = ref(null)

    const options = computed(() =>
        medications.value.map((m) => {
            const labelParts = [m.name]
            if (m.dosage) labelParts.push(m.dosage)
            if (m.quantity && !m.dosage) labelParts.push(m.quantity)

            // Calculate total available inventory for this medication
            const totalAmount = inventory.value
                .filter(inv => inv.medicationId === m.medicationId)
                .reduce((sum, inv) => sum + (inv.amount || 0), 0)

            const unit = inventory.value.find(inv => inv.medicationId === m.medicationId)?.unit || ''

            return {
                label: labelParts.join(' — '),
                value: m.medicationId,
                meta: m,
                availableAmount: totalAmount,
                unit: unit
            }
        })
    )

    async function fetchMedicalData() {
        loading.value = true
        error.value = null
        try {
            const res = await fetch('/api/medications', { method: 'GET' })
            if (!res.ok) throw new Error(`Failed to fetch medications (${res.status})`)
            const data = await res.json()
            medications.value = Array.isArray(data) ? data : []
            console.log(data)
            return medications.value
        } catch (err) {
            console.error(err)
            error.value = err?.message || 'Failed to load medications'
            medications.value = []
            return medications.value
        } finally {
            loading.value = false
        }
    }

    async function fetchInventory() {
        loading.value = true
        error.value = null
        try {
            const res = await fetch('/api/inventory', { method: 'GET' })
            if (!res.ok) throw new Error(`Failed to fetch inventory (${res.status})`)
            const data = await res.json()
            inventory.value = Array.isArray(data) ? data : []
            console.log(data)
            return inventory.value
        } catch (err) {
            console.error(err)
            error.value = err?.message || 'Failed to load inventory'
            inventory.value = []
            return inventory.value
        } finally {
            loading.value = false
        }
    }

    // Initial load
    fetchMedicalData()
    fetchInventory()

    function byId(id) {
        return medications.value.find((m) => m.medicationId === id) || null
    }

    function refresh() {
        return Promise.all([fetchMedicalData(), fetchInventory()])
    }

    function getInventoryForMedication(medicationId) {
        return inventory.value.filter(inv => inv.medicationId === medicationId)
    }

    function getTotalAvailable(medicationId) {
        return inventory.value
            .filter(inv => inv.medicationId === medicationId)
            .reduce((sum, inv) => sum + (inv.amount || 0), 0)
    }

    function getFirstInventoryId(medicationId) {
        const inv = inventory.value.find(inv => inv.medicationId === medicationId)
        return inv ? inv.id : null
    }

    return { medications, inventory, options, loading, error, byId, refresh, fetchMedicalData, fetchInventory, getInventoryForMedication, getTotalAvailable, getFirstInventoryId }
})
