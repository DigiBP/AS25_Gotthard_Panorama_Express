import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * User session store (prototype)
 * - Holds the current user object
 * - Exposes mock users for switching during prototyping
 * - Provides simple helpers: switchUser, setUser, logout, updatePreferences
 */
export const useUserSessionStore = defineStore('user_session', () => {
  // Prototype/mock users (replace with real backend data later)
  const mockUsers = ref([
    {
      id: '1',
      name: 'Merel',
      role: 'admin',
      preferences: { theme: 'light' }
    },
    {
      id: '2',
      name: 'Dj',
      role: 'backend',
      preferences: { theme: 'dark' }
    },
    {
      id: '3',
      name: 'Donna',
      role: 'viewer',
      preferences: { theme: 'light' }
    },
    {
      id: '4',
      name: 'Viktorija',
      role: 'viewer',
      preferences: { theme: 'light' }
    },
    {
      id: '4',
      name: 'Janosh',
      role: 'viewer',
      preferences: { theme: 'light' }
    }
  ])

  // Active user (null if signed out)
  const currentUser = ref(mockUsers.value[0])

  function switchUser(id) {
    const found = mockUsers.value.find((u) => u.id === String(id))
    if (found) currentUser.value = { ...found }
    return currentUser.value
  }

  function setUser(user) {
    currentUser.value = user ? { ...user } : null
  }

  function updatePreferences(patch = {}) {
    if (!currentUser.value) return
    currentUser.value.preferences = {
      ...(currentUser.value.preferences || {}),
      ...patch
    }
  }

  return {
    mockUsers,
    currentUser,
    switchUser,
    setUser,
    updatePreferences
  }
})
