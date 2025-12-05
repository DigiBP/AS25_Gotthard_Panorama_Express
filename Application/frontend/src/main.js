import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router/index.js'
import './styles/base.css'
// Apply saved theme (light/dark) from localStorage if present
const savedTheme = localStorage.getItem('theme')
if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme)
}

// expose a simple toggle helper for quick testing in the console
window.toggleTheme = (t) => {
    const theme = t || (document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark')
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
}

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
