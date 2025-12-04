import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

/**
 * Carts store - prototype data loaded from OnCart.xlsx
 * Exposes carts array and basic helpers for the UI.
 */
export const useCartsStore = defineStore('carts', () => {
  const carts = ref([
    {
      "CartId": "001",
      "CartStatus": "in-use",
      "patientId": "12345",
      "Operation": "Dekompression",
      "operationDate": "2025-12-29",
      "FormofAnaesthesia": "General",
      "Medications": "lidocain, propofol, fentanyl, remifentanyl, phenylephrin, ephedrin, Novalgin, Ondansetron, Ringer, NaCl'",
      "OperationRoom": "01"
    },
    {
      "CartId": "002",
      "CartStatus": "used",
      "patientId": "12245",
      "Operation": "Port-Einlage",
      "operationDate": "2025-12-28",
      "FormofAnaesthesia": "Standyby",
      "Medication": "ephedrin, phenylephrin",
      "OperationRoom": "11"
    }
  ])

  const count = computed(() => carts.value.length)

  function addCart(cart) {
    const nextId = carts.value.length ? Math.max(...carts.value.map((c) => c.id)) + 1 : 1
    carts.value.push({ id: nextId, ...cart })
  }

  function updateCart(id, patch) {
    const idx = carts.value.findIndex((c) => c.id === id)
    if (idx === -1) return null
    carts.value[idx] = { ...carts.value[idx], ...patch }
    return carts.value[idx]
  }

  function getCart(id) {
    return carts.value.find((c) => c.id === id) || null
  }

  return { carts, count, addCart, updateCart, getCart }
})
