import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import FitWarning from '../components/FitWarning'

vi.mock('../config', () => ({ API_URL: 'http://localhost:8000' }))

describe('FitWarning', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true }))
  })

  it('viser oppsummeringsteksten', () => {
    render(<FitWarning summary="Kandidaten mangler nøkkelkompetanse." sessionId="ses1" />)
    expect(screen.getByText('Kandidaten mangler nøkkelkompetanse.')).toBeInTheDocument()
  })

  it('poster "avbryt" til riktig endepunkt ved klikk på Avbryt', async () => {
    const user = userEvent.setup()
    render(<FitWarning summary="Svak match." sessionId="ses1" />)

    await user.click(screen.getByRole('button', { name: /avbryt/i }))

    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/answer/ses1',
      expect.objectContaining({ body: JSON.stringify({ answer: 'avbryt' }) }),
    )
  })

  it('poster "fortsett" til riktig endepunkt ved klikk på Fortsett', async () => {
    const user = userEvent.setup()
    render(<FitWarning summary="Svak match." sessionId="ses1" />)

    await user.click(screen.getByRole('button', { name: /fortsett/i }))

    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/answer/ses1',
      expect.objectContaining({ body: JSON.stringify({ answer: 'fortsett' }) }),
    )
  })
})
