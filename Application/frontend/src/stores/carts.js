import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

/**
 * Carts store - prototype data loaded from OnCart.xlsx
 * Exposes carts array and basic helpers for the UI.
 */
export const useCartsStore = defineStore('carts', () => {
  const carts = ref([])
  const cart_items = ref([])
  const loading = ref(false)
  const error = ref(null)

  const count = computed(() => carts.value.length)


  async function fetchCarts() {
    try {
      const res = await fetch('/api/carts', { method: 'GET' })
      if (!res.ok) throw new Error(`Failed to fetch carts (${res.status})`)
      const data = await res.json()
      carts.value = Array.isArray(data) ? data : []
      return carts.value
    } catch (err) {
      console.error(err)
      error.value = err?.message || 'Failed to load carts'
      carts.value = []
      return carts.value
    }
  }

  async function fetchCartItems() {
    try {
      const res = await fetch('/api/cart-items', { method: 'GET' })
      if (!res.ok) throw new Error(`Failed to fetch cart-items (${res.status})`)
      const data = await res.json()
      cart_items.value = Array.isArray(data) ? data : []
      return cart_items.value
    } catch (err) {
      console.error(err)
      error.value = err?.message || 'Failed to load cart-items'
      cart_items.value = []
      return cart_items.value
    }
  }

  async function initialLoad() {
    loading.value = true
    error.value = null
    try {
      await Promise.all([fetchCartItems(), fetchCarts()])
      // Create new array with items attached to trigger reactivity
      carts.value = carts.value.map(cart => ({
        ...cart,
        items: cart_items.value.filter((row) => row.cart_id === cart.id)
      }))
      console.log('Carts loaded with items:', carts.value)
    } catch (err) {
      // error already recorded in fetch helpers
    } finally {
      loading.value = false
    }
  }

  // Initial load
  initialLoad()

  async function addCart(cart) {
    try {
      const res = await fetch('/api/carts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(cart)
      })
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        const errorMsg = errorData.detail || `Failed to create cart (${res.status})`
        throw new Error(errorMsg)
      }
      const newCart = await res.json()
      carts.value.push(newCart)
      return newCart
    } catch (err) {
      console.error(err)
      throw err
    }
  }

  async function addMedicationToCart(cartId, medicationData) {
    try {
      const medData = {
        cart_id: cartId,
        ...medicationData
      }
      const res = await fetch('/api/cart-items/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(medData)
      })
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        const errorMsg = errorData.detail || `Failed to add medication (${res.status})`
        throw new Error(errorMsg)
      }
      const cartItem = await res.json()
      return cartItem
    } catch (err) {
      console.error(err)
      throw err
    }
  }

  async function addCartWithMedications(cartData, medications = []) {
    try {
      // Create the cart first
      const createdCart = await addCart(cartData)

      // Add medications to the cart if any
      if (medications.length > 0) {
        for (const med of medications) {
          if (med.medication_id) {
            await addMedicationToCart(createdCart.id, {
              medication_id: med.medication_id,
              amount: med.amount,
              inventory_id: med.inventory_id,
              time_sensitive: med.time_sensitive
            })
          }
        }
        // Refresh to show medications
        await refresh()
      }

      return createdCart
    } catch (err) {
      console.error(err)
      throw err
    }
  }

  async function updateCart(cartId, newStatus) {
    try {
      const res = await fetch(`/api/carts/${cartId}/status`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ new_status: newStatus })
      })
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        const errorMsg = errorData.detail || `Failed to update cart status (${res.status})`
        throw new Error(errorMsg)
      }
      const updatedCart = await res.json()
      const idx = carts.value.findIndex((c) => c.id === cartId)
      if (idx !== -1) {
        carts.value[idx] = updatedCart
      }
      return updatedCart
    } catch (err) {
      console.error(err)
      throw err
    }
  }

  function getCart(id) {
    return carts.value.find((c) => c.id === id) || null
  }

  async function refresh() {
    loading.value = true
    try {

      await initialLoad()
      return carts.value
    } finally {
      loading.value = false
    }
  }

  async function removeMedicationFromCart(cartItemId) {
    try {
      const res = await fetch(`/api/cart-items/${cartItemId}`, {
        method: 'DELETE',
      })
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        const errorMsg = errorData.detail || 'Failed to remove medication'
        throw new Error(errorMsg)
      }
      await refresh()
    } catch (err) {
      console.error('Remove medication error:', err)
      error.value = err.message
      throw err
    }
  }

  async function removeCart(cartId) {
    try {
      const res = await fetch(`/api/carts/${cartId}`, {
        method: 'DELETE',
      })
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        const errorMsg = errorData.detail || 'Failed to remove cart'
        throw new Error(errorMsg)
      }
      // Remove from local state
      carts.value = carts.value.filter(c => c.id !== cartId)
      cart_items.value = cart_items.value.filter(item => item.cart_id !== cartId)
    } catch (err) {
      console.error('Remove cart error:', err)
      error.value = err.message
      throw err
    }
  }

  return { carts, cart_items, count, loading, error, addCart, addMedicationToCart, addCartWithMedications, updateCart, getCart, fetchCarts, fetchCartItems, refresh, removeMedicationFromCart, removeCart }
})
