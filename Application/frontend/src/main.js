import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router/index.js'
import './styles/base.css'

// Centralized theme helper so UI + console share the same logic
const applyTheme = (theme) => {
    const next = theme === 'dark' ? 'dark' : 'light'
    document.documentElement.setAttribute('data-theme', next)
    localStorage.setItem('theme', next)
    return next
}

// Boot with saved theme (fallback to light)
applyTheme(localStorage.getItem('theme') || 'light')

// Expose for quick manual testing in the browser console
window.toggleTheme = (t) => {
    const current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'
    const next = t || (current === 'dark' ? 'light' : 'dark')
    applyTheme(next)
}

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
