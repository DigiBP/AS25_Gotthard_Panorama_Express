<template>
    <div class="view inventory-view">
        <h1>Inventory</h1>

        <section class="controls">
            <input v-model="search" placeholder="Search by name" class="search" />
            <label>Unit:
                <select v-model="unitFilter">
                    <option value="">All</option>
                    <option v-for="u in units" :key="u" :value="u">{{ u }}</option>
                </select>
            </label>
            <label>Low stock threshold:
                <input type="number" v-model.number="lowStockThreshold" min="0" />
            </label>
        </section>

        <section class="expiring">
            <h2>Expiring soon (on used carts)</h2>
            <p class="muted">Items from carts with status "used". Sorted by soonest expiration.</p>
            <table class="table">
                <thead>
                    <tr>
                        <th>Cart</th>
                        <th @click="toggleExpSort('name')" :class="{ sorted: expSortBy.key === 'name' }">Medication
                            <span class="indicator">{{ sortIndicatorExp('name') }}</span>
                        </th>
                        <th @click="toggleExpSort('expirationDate')"
                            :class="{ sorted: expSortBy.key === 'expirationDate' }">Expires <span class="indicator">{{
                                sortIndicatorExp('expirationDate') }}</span></th>
                        <th @click="toggleExpSort('daysLeft')" :class="{ sorted: expSortBy.key === 'daysLeft' }">Days
                            left <span class="indicator">{{ sortIndicatorExp('daysLeft') }}</span></th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="item in expiringPaginated" :key="item.key">
                        <td>{{ item.cartId }}</td>
                        <td>{{ item.name }}</td>
                        <td>{{ item.expirationDate }}</td>
                        <td :class="{ 'danger': item.daysLeft <= 7 }">{{ item.daysLeft }}</td>
                    </tr>
                    <tr v-if="expiringOnUsedCartsFiltered.length === 0">
                        <td colspan="4" class="muted">No expiring items match the filters.</td>
                    </tr>
                </tbody>
            </table>
            <div class="pagination">
                <label>Page size:
                    <select v-model.number="expPageSize">
                        <option :value="5">5</option>
                        <option :value="10">10</option>
                        <option :value="25">25</option>
                    </select>
                </label>
                <button :disabled="expPage <= 1" @click="expPage = Math.max(1, expPage - 1)">Prev</button>
                <span>Page {{ expPage }} of {{ Math.max(1, Math.ceil(expiringSorted.length / expPageSize)) }}</span>
                <button :disabled="expPage * expPageSize >= expiringSorted.length"
                    @click="expPage = expPage + 1">Next</button>
            </div>
        </section>

        <section class="inventory">
            <h2>Inventory totals</h2>
            <p class="muted">Aggregated by medication name + unit.</p>

            <table class="table">
                <thead>
                    <tr>
                        <th @click="toggleSort('name')" :class="{ sorted: sortBy.key === 'name' }">Name <span
                                class="indicator">{{ sortIndicator('name') }}</span></th>
                        <th @click="toggleSort('quantity')" :class="{ sorted: sortBy.key === 'quantity' }">Total
                            quantity
                            <span class="indicator">{{ sortIndicator('quantity') }}</span>
                        </th>
                        <th>Unit</th>
                        <th>Locations</th>
                        <th>Earliest expiry</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="row in inventoryPaginated" :key="row.key">
                        <td>{{ row.name }}</td>
                        <td :class="{ 'low': row.totalQuantity <= lowStockThreshold }">{{ row.totalQuantity }}</td>
                        <td>{{ row.unit }}</td>
                        <td>{{ row.locations.join(', ') }}</td>
                        <td>{{ row.earliestExpiry || '-' }}</td>
                    </tr>
                    <tr v-if="inventoryFilteredSorted.length === 0">
                        <td colspan="5" class="muted">No inventory items match the filters.</td>
                    </tr>
                </tbody>
            </table>
            <div class="pagination">
                <label>Page size:
                    <select v-model.number="invPageSize">
                        <option :value="10">10</option>
                        <option :value="25">25</option>
                        <option :value="50">50</option>
                    </select>
                </label>
                <button :disabled="invPage <= 1" @click="invPage = Math.max(1, invPage - 1)">Prev</button>
                <span>Page {{ invPage }} of {{ Math.max(1, Math.ceil(inventoryFilteredSorted.length / invPageSize))
                }}</span>
                <button :disabled="invPage * invPageSize >= inventoryFilteredSorted.length"
                    @click="invPage = invPage + 1">Next</button>
            </div>
        </section>
    </div>
</template>

<script>
import { useCartsStore } from '../stores/carts.js';
import { useMedicationsStore } from '../stores/medications.js';

export default {
    name: 'InventoryView',
    data() {
        return {
            meds: null,
            carts: null,
            // UI state
            search: '',
            unitFilter: '',
            lowStockThreshold: 0,
            sortBy: { key: 'name', asc: true },
            // pagination + sort state for expiring table
            expPage: 1,
            expPageSize: 10,
            expSortBy: { key: 'daysLeft', asc: true },
            // pagination for inventory table
            invPage: 1,
            invPageSize: 10
        }
    },
    created() {
        this.meds = useMedicationsStore()
        this.carts = useCartsStore()
    },
    computed: {
        units() {
            return this.meds.medications.map(m => m.unit)

        },
        // Helper: Expiring items on used carts
        expiringOnUsedCarts() {
            const used = (this.carts.carts || []).filter((c) => String(c.CartStatus).toLowerCase() === 'used')
            const items = []
            used.forEach((c) => {
                const medsStr = c.Medications || ''
                const names = medsStr.split(',').map((s) => s.trim()).filter(Boolean)
                names.forEach((n) => {
                    const m = (this.meds.medications || []).find((mm) => String(mm.name).toLowerCase() === String(n).toLowerCase())
                    if (m) {
                        const dl = this.daysUntil(m.expirationDate)
                        items.push({ key: `${c.CartId}-${m.medicationId}`, cartId: c.CartId || c.CartId, name: m.name, expirationDate: m.expirationDate, daysLeft: dl })
                    }
                })
            })
            return items.sort((a, b) => a.daysLeft - b.daysLeft)
        },
        expiringOnUsedCartsFiltered() {
            const q = String(this.search || '').toLowerCase()
            return this.expiringOnUsedCarts.filter((it) => {
                if (q && !it.name.toLowerCase().includes(q)) return false
                if (this.unitFilter) {
                    const m = (this.meds.medications || []).find((mm) => mm.name === it.name)
                    if (!m || (m.unit || '') !== this.unitFilter) return false
                }
                return true
            })
        },
        inventoryTotals() {
            const map = new Map()
                ; (this.meds.medications || []).forEach((m) => {
                    const name = m.name || 'unknown'
                    const unit = m.unit || ''
                    const key = `${name}::${unit}`
                    const qty = Number(m.quantity) || 0
                    const entry = map.get(key) || { name, unit, totalQuantity: 0, locations: new Set(), earliestExpiry: null, key }
                    entry.totalQuantity += qty
                    if (m.location) entry.locations.add(m.location)
                    if (m.expirationDate) {
                        const curr = entry.earliestExpiry ? new Date(entry.earliestExpiry) : null
                        const cand = new Date(m.expirationDate)
                        if (!curr || cand < curr) entry.earliestExpiry = m.expirationDate
                    }
                    map.set(key, entry)
                })
            return Array.from(map.values()).map((e) => ({ key: e.key, name: e.name, unit: e.unit, totalQuantity: e.totalQuantity, locations: Array.from(e.locations), earliestExpiry: e.earliestExpiry }))
        },
        inventoryFilteredSorted() {
            const q = String(this.search || '').toLowerCase()
            let rows = this.inventoryTotals.filter((r) => {
                if (this.unitFilter && r.unit !== this.unitFilter) return false
                if (q && !r.name.toLowerCase().includes(q)) return false
                return true
            })
            rows.sort((a, b) => {
                const k = this.sortBy.key
                let va = a[k]
                let vb = b[k]
                if (k === 'quantity' || k === 'totalQuantity') { va = a.totalQuantity; vb = b.totalQuantity }
                if (va == null) return 1
                if (vb == null) return -1
                if (typeof va === 'string') return this.sortBy.asc ? va.localeCompare(vb) : vb.localeCompare(va)
                return this.sortBy.asc ? (va - vb) : (vb - va)
            })
            return rows
        },
        // Paginated views
        expiringSorted() {
            const rows = [...this.expiringOnUsedCartsFiltered]
            const k = this.expSortBy.key
            rows.sort((a, b) => {
                let va = a[k]
                let vb = b[k]
                if (va == null) return 1
                if (vb == null) return -1
                if (typeof va === 'string') return this.expSortBy.asc ? va.localeCompare(vb) : vb.localeCompare(va)
                return this.expSortBy.asc ? (va - vb) : (vb - va)
            })
            return rows
        },
        expiringPaginated() {
            const p = Math.max(1, this.expPage)
            const size = Math.max(1, this.expPageSize)
            const all = this.expiringSorted
            const start = (p - 1) * size
            return all.slice(start, start + size)
        },
        inventoryPaginated() {
            const p = Math.max(1, this.invPage)
            const size = Math.max(1, this.invPageSize)
            const all = this.inventoryFilteredSorted
            const start = (p - 1) * size
            return all.slice(start, start + size)
        }
    },
    methods: {
        daysUntil(dateStr) {
            if (!dateStr) return Infinity
            const d = new Date(dateStr)
            const diff = d.getTime() - Date.now()
            return Math.ceil(diff / (1000 * 60 * 60 * 24))
        },
        toggleSort(key) {
            if (this.sortBy.key === key) this.sortBy.asc = !this.sortBy.asc
            else { this.sortBy.key = key; this.sortBy.asc = true }
        },
        toggleExpSort(key) {
            if (this.expSortBy.key === key) this.expSortBy.asc = !this.expSortBy.asc
            else { this.expSortBy.key = key; this.expSortBy.asc = true }
        },
        sortIndicator(key) {
            if (this.sortBy.key !== key) return ''
            return this.sortBy.asc ? '▲' : '▼'
        },
        sortIndicatorExp(key) {
            if (this.expSortBy.key !== key) return ''
            return this.expSortBy.asc ? '▲' : '▼'
        }
    },
    watch: {
        search() { this.expPage = 1; this.invPage = 1 },
        unitFilter() { this.expPage = 1; this.invPage = 1 },
        lowStockThreshold() { this.expPage = 1; this.invPage = 1 },
        expPageSize() { this.expPage = 1; this.invPage = 1 },
        invPageSize() { this.expPage = 1; this.invPage = 1 }
    }
}
</script>
<style scoped>
.inventory-view {
    padding: 1rem
}

.controls {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    margin-bottom: 1rem
}

.search {
    padding: 0.4rem;
    flex: 1
}

.table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1rem
}

.table th,
.table td {
    border: 1px solid #ddd;
    padding: 0.4rem;
    text-align: left
}

.muted {
    color: #666
}

.danger {
    color: maroon;
    font-weight: 600
}

.low {
    color: #b33
}

.table th {
    cursor: pointer
}

.table th.sorted {
    background: #f0f8ff
}

.indicator {
    margin-left: 0.4rem;
    color: #333
}

.pagination {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    margin-bottom: 1rem
}
</style>
