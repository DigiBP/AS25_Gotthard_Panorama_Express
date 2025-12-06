<template>
    <aside :class="['app-nav', { collapsed }]" aria-label="Main navigation">
        <button class="toggle" @click="collapsed = !collapsed" :aria-expanded="!collapsed">
            <span v-if="collapsed">☰</span>
            <span v-else>✖</span>
        </button>

        <nav class="links">
            <router-link v-for="link in links" :key="link.name" :to="{ name: link.name }" class="nav-link"
                active-class="active">
                <span class="icon">{{ link.icon }}</span>
                <span v-if="!collapsed" class="label">{{ link.label }}</span>
            </router-link>
        </nav>

        <!-- User area at the bottom -->
        <div class="user-area" :title="store && store.currentUser ? store.currentUser.name : 'Not signed in'">
            <div v-if="!collapsed" class="user-controls">
                <label class="sr-only">Switch user</label>
                <select v-model="selectedId" @change="onSwitchUser">
                    <option v-for="u in (store ? store.mockUsers : [])" :key="u.id" :value="u.id">{{ u.name }} — {{
                        u.role }}</option>
                </select>
            </div>
        </div>
    </aside>
</template>

<script>
import { useUserSessionStore } from '../stores/user_session.js';

export default {
    name: 'Navigation',
    data() {
        return {
            collapsed: false,
            links: [
                { name: 'dashboard', label: 'Dashboard', icon: '🏠' },
                { name: 'orderCreation', label: 'Create Order', icon: '📝' },
                { name: 'inventory', label: 'Inventory', icon: '📦' },
                { name: 'Reports and analyse', label: 'Reports', icon: '📊' },
                { name: 'digital carts', label: 'Carts', icon: '🛒' },
                { name: 'chat', label: 'Chat', icon: '💬' },
                { name: 'checklist', label: 'Checklist', icon: '✅' }
            ],
            selectedId: '',
            store: null
        }
    },
    created() {
        this.store = useUserSessionStore()
        this.selectedId = this.store && this.store.currentUser ? this.store.currentUser.id : (this.store && this.store.mockUsers[0] && this.store.mockUsers[0].id) || ''
    },
    methods: {
        onSwitchUser() {
            if (!this.selectedId || !this.store) return
            this.store.switchUser(this.selectedId)
        }
    },
}

</script>
<style scoped>
.app-nav {
    position: fixed;
    right: 0;
    top: 0;
    height: 100vh;
    width: 220px;
    background: color-mix(in srgb, var(--surface) 100%);
    box-shadow: -2px 0 12px rgba(2, 6, 23, 0.06);
    display: flex;
    flex-direction: column;
    align-items: stretch;
    transition: width 180ms ease;
    z-index: 1000;
}

.app-nav.collapsed {
    width: 56px;
}

.app-nav .toggle {
    background: transparent;
    border: none;
    padding: 12px;
    cursor: pointer;
    font-size: 18px;
    align-self: flex-start;
}

.app-nav .links {
    margin-top: 8px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 8px;
    flex: 1 0 auto;
}

.nav-link {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px;
    text-decoration: none;
    color: var(--text);
    border-radius: calc(var(--radius) - 2px);
}

.nav-link:hover {
    background: color-mix(in srgb, var(--primary-200) 8%, transparent);
}

.nav-link .icon {
    width: 24px;
    text-align: center;
}

.nav-link.active {
    background: color-mix(in srgb, var(--primary) 12%, transparent);
    color: var(--primary-600);
}

.user-area {
    padding: 12px;
    border-top: 1px solid var(--border);
    display: flex;
    flex-direction: row;
    gap: 8px;
    align-items: center;
}

.user-controls {
    margin-top: 8px;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.user-controls select {
    padding: 6px 8px;
    border-radius: 6px;
}
</style>
