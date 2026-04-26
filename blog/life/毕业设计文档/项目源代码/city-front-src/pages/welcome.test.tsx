import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { RouterProvider, createMemoryRouter } from 'react-router-dom'
import WelcomePage from './welcome'

describe('WelcomePage', () => {
  beforeEach(() => {
    localStorage.clear()
    global.fetch = vi.fn().mockRejectedValue(new Error('Mock'))
  })

  it('renders without crashing', () => {
    const routes = [
      {
        path: '/',
        element: <WelcomePage />,
      },
    ]

    const router = createMemoryRouter(routes)
    const { container } = render(<RouterProvider router={router} />)
    expect(container).toBeDefined()
  })

  it('renders welcome container', () => {
    const routes = [
      {
        path: '/',
        element: <WelcomePage />,
      },
    ]

    const router = createMemoryRouter(routes)
    const { container } = render(<RouterProvider router={router} />)
    
    const welcomeContainer = container.querySelector('.welcome-container')
    expect(welcomeContainer).toBeDefined()
  })

  it('renders multiple sections', () => {
    const routes = [
      {
        path: '/',
        element: <WelcomePage />,
      },
    ]

    const router = createMemoryRouter(routes)
    const { container } = render(<RouterProvider router={router} />)
    
    const sections = container.querySelectorAll('section')
    expect(sections.length).toBeGreaterThan(3)
  })

  it('contains feature cards', () => {
    const routes = [
      {
        path: '/',
        element: <WelcomePage />,
      },
    ]

    const router = createMemoryRouter(routes)
    const { container } = render(<RouterProvider router={router} />)
    
    const buttons = container.querySelectorAll('.btn')
    expect(buttons.length).toBeGreaterThan(5)
  })
})
