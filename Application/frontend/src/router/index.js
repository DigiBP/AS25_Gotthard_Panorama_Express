import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      name: 'dashboard',
      props: false,
      component: () => import('../views/DashboardView.vue'),
    },
    {
      name: 'orderCreation',
      props: false,
      component: () => import('../views/OrderCreation.vue')
    },
    {
      name: 'inventory',
      props: false,
      component: () => import('../views/InventoryView.vue')
    },
    {
      name: 'Reports and analyse',
      propse: false,
      component: () => import('../views/RapportView.vue')
    },
    {
      name: 'digital carts',
      props: false,
      component: () => import('../views/DigitalCarts.vue')
    }
  ]
})

export default router
