import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * Orders store - simple in-memory store for prototype
 * Each order: { id, createdAt, neededBy, orderedBy, isRush, comment, items: [{ medicationId, name, dosage, quantity, unit, notes }], orderType }
 *
 * orderType: 'internal' | 'external' — set by the UI based on whether the ordering person
 * is a known/internal user (prototype uses `user_session.mockUsers` to check this).
 */
export const useOrdersStore = defineStore('orders', () => {
    const orders = ref([])
    const loading = ref(false)
    const error = ref(null)

    async function fetchOrders() {
        loading.value = true
        error.value = null
        try {
            const res = await fetch('/api/orders', { method: 'GET' })
            if (!res.ok) throw new Error(`Failed to fetch orders (${res.status})`)
            const data = await res.json()
            console.log('Fetched orders:', data)
            orders.value = Array.isArray(data) ? data : []
            return orders.value
        } catch (err) {
            console.error(err)
            error.value = err?.message || 'Failed to load orders'
            orders.value = []
            return orders.value
        } finally {
            loading.value = false
        }
    }

    // Initial load
    fetchOrders()

    function addOrder(order) {
        const id = `ord-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`
        const createdAt = new Date().toISOString()
        const entry = { id, createdAt, ...order }
        orders.value.unshift(entry)
        return entry
    }

    function getOrder(id) {
        return orders.value.find((o) => o.id === id) || null
    }

    function getOrdersByType(type) {
        if (!type) return []
        return orders.value.filter((o) => o.orderType === type)
    }

    function removeOrder(id) {
        const idx = orders.value.findIndex((o) => o.id === id)
        if (idx !== -1) orders.value.splice(idx, 1)
    }

    async function refresh() {
        return await fetchOrders()
    }

    return { orders, loading, error, addOrder, getOrder, removeOrder, fetchOrders, refresh }
})
