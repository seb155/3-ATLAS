import { useEffect, useRef } from 'react'
import { useDevConsoleStore } from '../store/useDevConsoleStore'

export const useWebSocketConnection = () => {
    const wsRef = useRef<WebSocket | null>(null)
    const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
    const reconnectAttempts = useRef(0)

    const { addLog, setConnected, setConnectionError } = useDevConsoleStore()

    const connect = () => {
        try {
            // Get API URL from environment
            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8001'
            const wsUrl = apiUrl.replace('http', 'ws') + '/ws/logs'

            console.log('[WebSocket] Connecting to:', wsUrl)

            const ws = new WebSocket(wsUrl)

            ws.onopen = () => {
                console.log('[WebSocket] Connected')
                setConnected(true)
                setConnectionError(null)
                reconnectAttempts.current = 0
            }

            ws.onmessage = (event) => {
                try {
                    const log = JSON.parse(event.data)
                    addLog(log)
                } catch (error) {
                    console.error('[WebSocket] Failed to parse message:', error)
                }
            }

            ws.onerror = (error) => {
                console.error('[WebSocket] Error:', error)
                setConnectionError('WebSocket connection error')
            }

            ws.onclose = () => {
                console.log('[WebSocket] Disconnected')
                setConnected(false)

                // Reconnect with exponential backoff
                const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000)
                reconnectAttempts.current++

                console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current})`)

                reconnectTimeoutRef.current = setTimeout(() => {
                    connect()
                }, delay)
            }

            wsRef.current = ws
        } catch (error) {
            console.error('[WebSocket] Connection failed:', error)
            setConnectionError('Failed to establish WebSocket connection')
        }
    }

    const disconnect = () => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current)
        }

        if (wsRef.current) {
            wsRef.current.close()
            wsRef.current = null
        }

        setConnected(false)
    }

    useEffect(() => {
        connect()

        return () => {
            disconnect()
        }
    }, [])

    return {
        isConnected: useDevConsoleStore((state) => state.isConnected),
        connectionError: useDevConsoleStore((state) => state.connectionError),
        reconnect: connect,
    }
}
