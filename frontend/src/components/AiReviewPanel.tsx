import { useState, useCallback } from 'react'
import { useUserStore } from '@/stores/use-user-store'
import { MonacoEditor } from '@/components/MonacoEditor'
import { Modal, Button, Badge } from '@/components/uI'

interface ReviewData {
  review: string
  mission_id: string
  provider: string
}

export const AiReviewPanel: React.FC = ({
  missionId,
  gradedCode,
  grade,
}: {
  missionId: string
  gradedCode: string
  grade: string
}) => {
  const { addAIHistory, aiHistory } = useUserStore()
  const [visible, setVisible] = useState(false)
  const [review, setReview] = useState('')
  const [improvedCode, setImprovedCode] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const loadReview = useCallback(async () => {
    if (grade < 'C'.charCodeAt(0)) {
      setVisible(false)
      return
    }

    setIsLoading(true)
    try {
      const res = await fetch('/api/v1/ai/review', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mission_id: missionId,
          code: gradedCode,
          grader_result: { grade },
        }),
      })
      const data = await res.json()
      setReview(data.review || '')
      setImprovedCode(data.improved_code || '')
      setVisible(true)
      addAIHistory({
        id: `review_${Date.now()}`,
        type: 'review',
        content: data.review || '',
        created_at: new Date().toISOString(),
      })
    } catch (e) {
      console.error('Failed to fetch AI review', e)
    } finally {
      setIsLoading(false)
    }
  }, [missionId, gradedCode, grade, addAIHistory])

  return (
    <>
    <Button
      variant="secondary"
      size="sm"
      onClick={loadReview}
      disabled={visible || grade < 'C'.charCodeAt(0)}
      className="margin-right-2"
    >
      <Badge
        variant="link"
        size="small"
      >
        AI Review
      </Badge>
    </Button>

    {visible && (
      <Modal
        open={visible}
        onClose={() => setVisible(false)}
        title="Senior Engineer Review"
      >
        {isLoading ? (
          <p>Generating review...</p>
        ) : (
          <div>
            <p className="text-sm text-muted-foreground mb-4">
              Grade: <Badge variant="default">{grade}</Badge>
            </p>

            <div className="bg-secondary/20 p-4 rounded mb-4">
              <p className="text-muted-foreground mb-3">{review}</p>

              {improvedCode && (
                <div>
                  <h4 className="text-xs font-medium mb-2">Applied Suggestions</h4>
                  <MonacoEditor
                    defaultValue={improvedCode}
                    language="python"
                    height="200px"
                    onChange={(value) => setImprovedCode(value)}
                  />
                </div>
              )}
            </div>

            <Button
              variant="primary"
          onClick={() => setVisible(false)}
              className="mt-4"
            >
              Close
            </Button>
          </div>
        )}
      </Modal>
    )}
    </>
  )
}
