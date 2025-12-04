<script setup>
import Navigation from './components/Navigation.vue';
</script>

<template>
  <div id="app" class="app-shell">
    <main class="content">
      <router-view />
    </main>

    <!-- Right-side navigation (collapsible) -->
    <Navigation />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  align-items: stretch;
}

.content {
  flex: 1 1 auto;
  padding: 1rem;
  /* Add right padding so content isn't hidden under the nav */
  padding-right: 240px;
  /* matches nav width; when collapsed the nav covers less */
  transition: padding-right 180ms ease;
}
</style>
