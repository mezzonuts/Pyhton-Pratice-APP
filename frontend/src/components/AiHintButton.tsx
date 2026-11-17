import { useState, useCallback } from 'react'
import { useUserStore } from '@/stores/use-user-store'
import { useMissionHook } from '@/lib/use-mission-hook'
import { Modal, Button, Badge } from '@/components/uI'
import { useNavigate } from 'react-router-dom'

export const AiHintButton: React.FC = ({
  missionId,
  userCode,
  tier = 0,
  showElI5 = false,
}) => {
  const { addAIHistory, aiHistory } = useUserStore()
  const navigate = useNavigate()
  const [visible, setVisible] = useState(false)
  const [hint, setHint] = useState('')
  const [hintType, setHintType] = useState<'conceptual' | 'analogy' | 'ELI5'>(
    'conceptual'
  )

  const fetchHint = useCallback(async () => {
    try {
      const res = await fetch('/api/v1/ai/hint', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mission_id: missionId,
          user_code: userCode,
          error_type: hintType,
        }),
      })
      const data = await res.json()
      setHint(data.hint || '')
      setHintType(data.hint_type || 'conceptual')
      setVisible(true)
      addAIHistory({
        id: `hint_${Date.now()}`,
        type: 'hint',
        content: data.hint || '',
        created_at: new Date().toISOString(),
      })
    } catch (e) {
      console.error('Failed to fetch hint', e)
    }
  }, [missionId, userCode, hintType, addAIHistory])

  return (
    <Button
      variant="secondary"
      size="sm"
      onClick={fetchHint}
      disabled={visible}
      className="margin-right-2"
    >
      <Badge
        variant="link"
        size="small"
      >
        Hint
      </Badge>
    </Button>

    {visible && (
      <Modal
        open={visible}
        onClose={() => setVisible(false)}
        title="Socratic Hint"
      >
        <p className="text-sm mb-4">{hint}</p>

        <div className="flex gap-2 mb-4">
          <Button
            variant="link"
            size="sm"
            onClick={() => setHintType('conceptual')}
            disabled={hintType === 'conceptual'}
          >
            Conceptual
          </Button>
          <Button
            variant="link"
            size="sm"
            onClick={() => setHintType('analogy')}
            disabled={hintType === 'analogy'}
          >
            Analogy
          </Button>
          <Button
            variant="link"
            size="sm"
            onClick={() => setHintType('ELI5')}
            disabled={hintType === 'ELI5'}
          >
            ELI5
          </Button>
        </div>

        <div>
          <h4 className="text-xs text-muted-foreground">
            Tier {tier} hint{' '}
            {tier === 0 && (
              <Button
                variant="link"
                size="tiny"
                onClick={() => setHintType('ELI5')}
              >
                ELI5
              </Button>
            )}
          </h4>
        </div>

        <Button
          variant="primary"
          onClose={() => setVisible(false)}
          className="mt-4"
        >
          Got it
        </Button>
      </Modal>
    )}
  )
}