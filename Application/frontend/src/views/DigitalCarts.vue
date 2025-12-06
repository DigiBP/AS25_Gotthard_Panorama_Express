<template>
    <div class="view dashboard-view">
        <h1>Digital carts</h1>

        <section class="carts-grid">
            <Cart v-for="cart in carts" :key="cart.id" :cart="cart" />
        </section>
    </div>
</template>

<script>
import { computed } from 'vue';
import Cart from '../components/Cart.vue';
import { useCartsStore } from '../stores/carts.js';

export default {
    name: 'DigitalCartsView',
    components: { Cart },

    setup() {
        const store = useCartsStore()
        const carts = computed(() => store.carts)
        return { carts }
    }
}
</script>

<style scoped>
.carts-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    align-items: start;
}

@media (max-width: 700px) {
    .carts-grid {
        grid-template-columns: 1fr
    }
}

.dashboard-view {
    padding: 1rem
}
</style>
