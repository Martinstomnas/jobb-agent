import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import AgentPipeline from '../components/AgentPipeline'
import type { AgentStates } from '../types'

const AGENTS = ['Kravleser', 'Research', 'Match', 'Writer']

describe('AgentPipeline', () => {
  it('viser alle agentnavnene', () => {
    render(<AgentPipeline agents={AGENTS} states={{}} />)
    AGENTS.forEach(name => expect(screen.getByText(name)).toBeInTheDocument())
  })

  it('viser ikke teller når ingen agenter er startet', () => {
    render(<AgentPipeline agents={AGENTS} states={{}} />)
    expect(screen.queryByText(/\/ 4/)).not.toBeInTheDocument()
  })

  it('viser ferdig-teller når agenter er done', () => {
    const states: AgentStates = {
      Kravleser: { status: 'done' },
      Research: { status: 'done' },
    }
    render(<AgentPipeline agents={AGENTS} states={states} />)
    expect(screen.getByText('2 / 4')).toBeInTheDocument()
  })

  it('setter agent-card-klassen basert på status', () => {
    const states: AgentStates = {
      Kravleser: { status: 'done' },
      Research: { status: 'running' },
    }
    const { container } = render(<AgentPipeline agents={AGENTS} states={states} />)
    expect(container.querySelector('.agent-done')).toBeInTheDocument()
    expect(container.querySelector('.agent-running')).toBeInTheDocument()
    expect(container.querySelector('.agent-idle')).toBeInTheDocument()
  })

  it('viser hake-ikon for done-agenter', () => {
    const states: AgentStates = { Kravleser: { status: 'done' } }
    render(<AgentPipeline agents={AGENTS} states={states} />)
    expect(screen.getByText('✓')).toBeInTheDocument()
  })
})
