import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import FollowUpQuestion from '../components/FollowUpQuestion'

vi.mock('../config', () => ({ API_URL: 'http://localhost:8000' }))

describe('FollowUpQuestion', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true }))
  })

  it('viser spørsmålet', () => {
    render(<FollowUpQuestion question="Har du erfaring med React?" sessionId="s1" />)
    expect(screen.getByText('Har du erfaring med React?')).toBeInTheDocument()
  })

  it('send-knapp er deaktivert når svaret er tomt', () => {
    render(<FollowUpQuestion question="Spørsmål?" sessionId="s1" />)
    expect(screen.getByRole('button', { name: /send svar/i })).toBeDisabled()
  })

  it('send-knapp aktiveres når det skrives et svar', async () => {
    const user = userEvent.setup()
    render(<FollowUpQuestion question="Spørsmål?" sessionId="s1" />)

    await user.type(screen.getByRole('textbox'), 'Ja, fem år')
    expect(screen.getByRole('button', { name: /send svar/i })).toBeEnabled()
  })

  it('poster svaret til riktig endepunkt ved innsending', async () => {
    const user = userEvent.setup()
    render(<FollowUpQuestion question="Spørsmål?" sessionId="s1" />)

    await user.type(screen.getByRole('textbox'), 'Ja, fem år')
    await user.click(screen.getByRole('button', { name: /send svar/i }))

    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/answer/s1',
      expect.objectContaining({ body: JSON.stringify({ answer: 'Ja, fem år' }) }),
    )
  })

  it('poster tomt svar ved klikk på Hopp over', async () => {
    const user = userEvent.setup()
    render(<FollowUpQuestion question="Spørsmål?" sessionId="s1" />)

    await user.click(screen.getByRole('button', { name: /hopp over/i }))

    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/answer/s1',
      expect.objectContaining({ body: JSON.stringify({ answer: '' }) }),
    )
  })
})
