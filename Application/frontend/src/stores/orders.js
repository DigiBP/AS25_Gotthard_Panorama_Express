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

    return { orders, addOrder, getOrder, removeOrder }
})
