import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
// Import the template JSON from the repository root
import medicationData from '../../../../medication_data_template.json'

/**
 * Medications store
 * - Loads static prototype data from medication_data_template.json
 * - Exposes the raw list and a lightweight dropdown-friendly options array
 */
export const useMedicationsStore = defineStore('medications', () => {
    const medications = ref(Array.isArray(medicationData) ? medicationData : [])

    const options = computed(() =>
        medications.value.map((m) => {
            const labelParts = [m.name]
            if (m.dosage) labelParts.push(m.dosage)
            if (m.quantity && !m.dosage) labelParts.push(m.quantity)
            return {
                label: labelParts.join(' — '),
                value: m.medicationId,
                meta: m
            }
        })
    )

    function byId(id) {
        return medications.value.find((m) => m.medicationId === id) || null
    }

    function refresh() {
        // For a static JSON import there's nothing to refresh - kept for API parity
        return medications.value
    }

    return { medications, options, byId, refresh }
})
