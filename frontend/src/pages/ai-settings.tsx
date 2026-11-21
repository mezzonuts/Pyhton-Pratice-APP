import { useState, useEffect } from 'react'
import { useUserStore } from '@/stores/use-user-store'
import { Table, TableHeader, TableRow, TableCell, Input, Button, Badge } from '@/components/uI'

export const AiSettingsPage: React.FC = () => {
  const { aiProviders, setProviders, selectProvider, clearAIHistory } = useUserStore()
  const [baseUrl, setBaseUrl] = useState('')
  const [model, setModel] = useState('')
  const [apiKeyRef, setApiKeyRef] = useState('')
  const [priority, setPriority] = useState(0)
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    // Fetch providers from backend on mount
    // In production, this would be an API call
  }, [])

  const handleAdd = async () => {
    if (!baseUrl || !model) {
      setError('Base URL and model are required')
      return
    }
    const newProvider: any = {
      id: `provider_${Date.now()}`,
      type: 'ollama',
      name: `Ollama ${model}`,
      base_url: baseUrl,
      api_key: apiKeyRef,
      model,
      fallback_models: [],
      timeout: 30.0,
      max_retries: 3,
      is_default: false,
      priority,
    }
    setProviders([...aiProviders, newProvider])
    setShowForm(false)
    setError('')
    setBaseUrl('')
    setModel('')
    setApiKeyRef('')
    setPriority(0)
  }

  const handleEdit = async (id: string) => {
    const provider = aiProviders.find((p) => p.id === id)
    if (!provider) return
    setEditingId(id)
    setBaseUrl(provider.base_url || '')
    setModel(provider.model || '')
    setApiKeyRef(provider.api_key || '')
    setPriority(provider.priority || 0)
    setShowForm(true)
  }

  const handleDelete = async (id: string) => {
    setProviders(aiProviders.filter((p) => p.id !== id))
    if (editingId === id) {
      setEditingId(null)
      setBaseUrl('')
      setModel('')
      setApiKeyRef('')
      setPriority(0)
    }
  }

  const handleTestConnection = async (id: string) => {
    const provider = aiProviders.find((p) => p.id === id)
    if (!provider) return
    try {
      const res = await fetch(
        `/api/v1/ai/providers/${id}/test`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ base_url: provider.base_url, api_key: provider.api_key, model: provider.model }),
        }
      )
      const data = await res.json()
      // Show result in a notification
      if (data.success) {
        // success notification
      } else {
        // error notification
      }
    } catch (e) {
      console.error('Test connection failed', e)
    }
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">AI Provider Settings</h2>

      {error && <p className="text-red-600 mb-4">{error}</p>}

      {aiProviders.length === 0
        ? <p className="text-muted-foreground">No providers configured</p>
        : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Model</TableCell>
                  <TableCell>Base URL</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Default</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHeader>
              {aiProviders.map((provider) => (
                <TableRow key={provider.id}>
                  <TableCell>{provider.name}</TableCell>
                  <TableCell>{provider.type}</TableCell>
                  <TableCell>{provider.model}</TableCell>
                  <TableCell>{provider.base_url || '—'}</TableCell>
                  <TableCell>{provider.priority || 0}</TableCell>
                  <TableCell>
                    <Badge
                      variant={provider.is_default ? 'default' : 'secondary'}
                    >
                      {provider.is_default ? 'Default' : ''}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleEdit(provider.id)}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(provider.id)}
                    >
                      Delete
                    </Button>
                    <Button
                      variant="link"
                      size="sm"
                      onClick={() => handleTestConnection(provider.id)}
                    >
                      Test
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </Table>
          )}

      <Button
        variant="primary"
        onClick={() => setShowForm(true)}
        className="mb-6"
      >
        Add Provider
      </Button>

      {showForm && (
        <div className="max-w-md p-6 border rounded bg-card">
          <h3 className="text-xl font-medium mb-4">
            {editingId ? 'Edit Provider' : 'Add Provider'}
          </h3>

          {error && <p className="text-red-600 mb-4">{error}</p>}

          <Input
            placeholder="Base URL (e.g., http://127.0.0.1:20128/v1)"
            value={baseUrl}
            onChange={(e) => setBaseUrl(e.target.value)}
            disabled={editingId ? false : true}
          />
          <Input
            type="password"
            placeholder="API Key"
            value={apiKeyRef}
            onChange={(e) => setApiKeyRef(e.target.value)}
            masked
          />
          <Input
            placeholder="Model name"
            value={model}
            onChange={(e) => setModel(e.target.value)}
          />
          <Input
            placeholder="Priority (lower = higher priority)"
            value={priority}
            onChange={(e) => setPriority(Number(e.target.value) || 0)}
          />

          <div className="mt-6 flex gap-2">
            <Button
              variant="secondary"
              onClick={() => {
                setShowForm(false)
                setEditingId(null)
                setBaseUrl('')
                setModel('')
                setApiKeyRef('')
                setPriority(0)
              }}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleAdd}
            >
              {editingId ? 'Update' : 'Add'}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

export default AiSettingsPage
