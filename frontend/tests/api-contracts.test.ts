import assert from 'node:assert/strict'
import test from 'node:test'
import {
  buildApiUrl,
  extractApiErrorMessage,
  extractConversationId,
  getSseData,
  resolveApiPayload,
  splitSseFrames,
} from '../src/lib/api/contracts.ts'

test('buildApiUrl keeps API calls same-origin and avoids duplicate prefixes', () => {
  assert.equal(buildApiUrl('/ai/chat/stream/'), '/api/ai/chat/stream/')
  assert.equal(buildApiUrl('/api/auth/me/'), '/api/auth/me/')
  assert.equal(buildApiUrl('notifications/'), '/api/notifications/')
})

test('resolveApiPayload unwraps regular envelopes and preserves paging metadata', () => {
  assert.deepEqual(resolveApiPayload({ data: { id: 7 }, error: null }), { id: 7 })

  const paginated = {
    data: [{ id: 1 }],
    error: null,
    paging: { count: 25, next: null, previous: null },
  }
  assert.equal(resolveApiPayload(paginated), paginated)
})

test('extractApiErrorMessage formats nested field validation errors', () => {
  assert.equal(
    extractApiErrorMessage({
      error: { message: { email: ['已经存在'], password: ['长度不足'] } },
    }),
    'email: 已经存在; password: 长度不足',
  )
})

test('conversation ids are accepted from metadata and done events', () => {
  assert.equal(extractConversationId({ type: 'metadata', conversation_id: 42 }), 42)
  assert.equal(extractConversationId({ type: 'done', conversation_id: '43' }), 43)
  assert.equal(extractConversationId({ type: 'error', conversation_id: null }), undefined)
})

test('SSE frames survive chunk boundaries and the final buffer is flushed', () => {
  const first = splitSseFrames('data: {"type":"metadata","conversation_id":9}\n\ndata: {"type"')
  assert.equal(first.frames.length, 1)
  assert.equal(getSseData(first.frames[0]), '{"type":"metadata","conversation_id":9}')

  const final = splitSseFrames(`${first.remainder}:"done","conversation_id":9}`, true)
  assert.equal(final.frames.length, 1)
  assert.equal(getSseData(final.frames[0]), '{"type":"done","conversation_id":9}')
})
