import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import InputForm from '../components/InputForm'

vi.mock('../config', () => ({ API_URL: 'http://localhost:8000' }))

describe('InputForm', () => {
  it('onSubmit kalles ikke når feltene er tomme', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<InputForm onSubmit={onSubmit} running={false} />)

    await user.click(screen.getByRole('button', { name: /analyser/i }))

    expect(onSubmit).not.toHaveBeenCalled()
  })

  it('submit-knapp er aktiv når begge felt er fylt ut', async () => {
    const user = userEvent.setup()
    render(<InputForm onSubmit={vi.fn()} running={false} />)

    await user.type(screen.getAllByRole('textbox')[0], 'stillingsannonse')
    await user.type(screen.getAllByRole('textbox')[1], 'cv-tekst')

    expect(screen.getByRole('button', { name: /analyser/i })).toBeEnabled()
  })

  it('kaller onSubmit med jobPosting og cv', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<InputForm onSubmit={onSubmit} running={false} />)

    await user.type(screen.getAllByRole('textbox')[0], 'Min annonse')
    await user.type(screen.getAllByRole('textbox')[1], 'Min CV')
    await user.click(screen.getByRole('button', { name: /analyser/i }))

    expect(onSubmit).toHaveBeenCalledOnce()
    expect(onSubmit).toHaveBeenCalledWith({
      jobPosting: 'Min annonse',
      cv: 'Min CV',
    })
  })

  it('legger tilleggsinfo inn i cv-feltet ved innsending', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<InputForm onSubmit={onSubmit} running={false} />)

    await user.type(screen.getAllByRole('textbox')[0], 'annonse')
    await user.type(screen.getAllByRole('textbox')[1], 'cv')
    await user.click(screen.getByRole('button', { name: /tilleggsinfo/i }))
    await user.type(screen.getAllByRole('textbox')[2], 'ekstra info')
    await user.click(screen.getByRole('button', { name: /analyser/i }))

    const { cv } = onSubmit.mock.calls[0][0]
    expect(cv).toContain('ekstra info')
    expect(cv).toContain('cv')
  })

  it('skjuler feltene og viser "Analyserer..." mens running=true', () => {
    render(<InputForm onSubmit={vi.fn()} running={true} />)
    expect(screen.getByRole('button', { name: /analyserer/i })).toBeDisabled()
    expect(screen.getAllByRole('textbox')[0]).toBeDisabled()
  })
})
