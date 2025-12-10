import { onMounted, onUnmounted, ref } from 'vue'

export function useWebSocket(onMessage) {
    const socket = ref(null)
    const isConnected = ref(false)
    let reconnectTimeout = null

    /**
     * Determine the WebSocket protocol based on the current location protocol
     */
    function getWebSocketProtocol() {
        return window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    }

    /**
     * Connect to the WebSocket endpoint
     */
    function connect() {
        const protocol = getWebSocketProtocol()
        const wsUrl = `${protocol}//${window.location.host}/api/notifications/ws`

        console.log('Connecting to WebSocket:', wsUrl)

        socket.value = new WebSocket(wsUrl)

        socket.value.onopen = () => {
            console.log('WebSocket connected')
            isConnected.value = true
        }

        socket.value.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                console.log('Received WebSocket message:', data)

                // Call the message handler callback if provided
                if (onMessage) {
                    onMessage(data)
                }
            } catch (err) {
                console.error('Failed to parse WebSocket message:', err)
                if (onMessage) {
                    onMessage({
                        event_type: 'error',
                        message: `Failed to parse message: ${event.data}`,
                        cart_id: null
                    })
                }
            }
        }

        socket.value.onerror = (error) => {
            console.error('WebSocket error:', error)
            isConnected.value = false
        }

        socket.value.onclose = () => {
            console.log('WebSocket disconnected')
            isConnected.value = false

            // Auto-reconnect after 3 seconds
            reconnectTimeout = setTimeout(() => {
                console.log('Attempting to reconnect...')
                connect()
            }, 3000)
        }
    }

    /**
     * Disconnect and clean up
     */
    function disconnect() {
        if (reconnectTimeout) {
            clearTimeout(reconnectTimeout)
            reconnectTimeout = null
        }

        if (socket.value) {
            socket.value.close()
            socket.value = null
        }

        isConnected.value = false
    }

    onMounted(() => {
        connect()
    })

    onUnmounted(() => {
        disconnect()
    })

    return {
        socket,
        isConnected,
        connect,
        disconnect,
    }
}
