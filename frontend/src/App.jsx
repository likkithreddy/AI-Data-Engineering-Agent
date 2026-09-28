import { useEffect, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const exampleQuestions = [
  'Which products generated the most revenue last quarter?',
  'Show me refund trends by month and identify the main drivers.',
  'Which customers are at risk of churn based on recent order behavior?',
]

const renderJson = (value) => {
  if (value === null || value === undefined) {
    return '—'
  }

  if (typeof value === 'string') {
    return value
  }

  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value)
  }

  if (Array.isArray(value)) {
    if (!value.length) {
      return 'No data'
    }

    return value.map((item, index) => (
      <li key={`${typeof item}-${index}`} className="text-sm text-slate-300">
        {typeof item === 'object' ? JSON.stringify(item, null, 2) : item}
      </li>
    ))
  }

  return JSON.stringify(value, null, 2)
}

function App() {
  const [question, setQuestion] = useState(exampleQuestions[0])
  const [loading, setLoading] = useState(false)
  const [backendStatus, setBackendStatus] = useState('Checking')
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`)
        if (!response.ok) {
          throw new Error('Backend unavailable')
        }

        const data = await response.json()
        setBackendStatus(data.status === 'ok' ? 'Online' : 'Unreachable')
      } catch {
        setBackendStatus('Offline')
      }
    }

    checkHealth()
  }, [])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${API_BASE_URL}/analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      })

      const payload = await response.json()

      if (!response.ok) {
        throw new Error(payload.detail || 'The backend could not process the request.')
      }

      setResult(payload)
    } catch (submitError) {
      setError(submitError.message)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <header className="mb-8 flex flex-col gap-4 rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-2xl shadow-slate-950/30 backdrop-blur md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-cyan-400">
              AI data engineering agent
            </p>
            <h1 className="mt-2 text-3xl font-bold text-white md:text-4xl">
              Business intelligence assistant
            </h1>
          </div>

          <div className="inline-flex items-center gap-3 self-start rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-sm font-medium text-emerald-300 md:self-auto">
            <span className={`h-2.5 w-2.5 rounded-full ${backendStatus === 'Online' ? 'bg-emerald-400' : 'bg-amber-400'}`} />
            Backend: {backendStatus}
          </div>
        </header>

        <main className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <section className="panel p-6">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-300">Ask a business question</p>
                <h2 className="mt-1 text-xl font-semibold text-white">Data analysis workflow</h2>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <label className="block">
                <span className="mb-2 block text-sm font-medium text-slate-300">Question</span>
                <textarea
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  rows={6}
                  className="w-full rounded-2xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/30"
                  placeholder="Ask about revenue, refunds, order trends, or customer behavior..."
                />
              </label>

              <div className="flex flex-wrap gap-2">
                {exampleQuestions.map((example) => (
                  <button
                    key={example}
                    type="button"
                    className="rounded-full border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 transition hover:border-cyan-500 hover:text-cyan-300"
                    onClick={() => setQuestion(example)}
                  >
                    {example}
                  </button>
                ))}
              </div>

              <button
                type="submit"
                disabled={loading || !question.trim()}
                className="inline-flex w-full items-center justify-center rounded-2xl bg-cyan-500 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
              >
                {loading ? 'Analyzing...' : 'Run analysis'}
              </button>
            </form>

            {error && (
              <div className="mt-5 rounded-2xl border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-200">
                {error}
              </div>
            )}
          </section>

          <aside className="panel p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white">Agent capabilities</h2>
            </div>
            <ul className="space-y-4 text-sm text-slate-300">
              <li className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
                <p className="font-medium text-cyan-300">SQL analysis</p>
                <p className="mt-1">Generates business questions into query plans and validates execution.</p>
              </li>
              <li className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
                <p className="font-medium text-violet-300">Pandas processing</p>
                <p className="mt-1">Runs data transformations and summarization for deeper insights.</p>
              </li>
              <li className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
                <p className="font-medium text-emerald-300">RAG evidence</p>
                <p className="mt-1">Retrieves policy context and supporting documents to ground answers.</p>
              </li>
            </ul>
          </aside>
        </main>

        {result && (
          <section className="mt-8 space-y-6">
            <div className="panel p-6">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-400">Answer</p>
              <h2 className="mt-3 text-2xl font-semibold text-white">{result.question}</h2>
              <p className="mt-4 text-base leading-7 text-slate-200">{result.answer}</p>

              <div className="mt-5 grid gap-3 sm:grid-cols-3">
                <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-3">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Request ID</p>
                  <p className="mt-2 text-sm font-medium text-cyan-200">{result.request_id || '—'}</p>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-3">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Execution time</p>
                  <p className="mt-2 text-sm font-medium text-emerald-200">
                    {result.execution_time_ms !== null && result.execution_time_ms !== undefined
                      ? `${result.execution_time_ms} ms`
                      : '—'}
                  </p>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-3">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Retry count</p>
                  <p className="mt-2 text-sm font-medium text-violet-200">{result.retry_count ?? 0}</p>
                </div>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="panel p-6">
                <h3 className="text-lg font-semibold text-white">Reasoning</h3>
                <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-300">
                  {result.reasoning || 'No reasoning was returned for this request.'}
                </p>
              </div>

              <div className="panel p-6">
                <h3 className="text-lg font-semibold text-white">Selected tools</h3>
                <div className="mt-3 flex flex-wrap gap-2">
                  {result.selected_tools?.length ? (
                    result.selected_tools.map((tool) => (
                      <span key={tool} className="rounded-full border border-cyan-500/40 bg-cyan-500/10 px-3 py-1 text-xs font-medium text-cyan-300">
                        {tool}
                      </span>
                    ))
                  ) : (
                    <span className="text-sm text-slate-400">No tools were selected.</span>
                  )}
                </div>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="panel p-6">
                <h3 className="text-lg font-semibold text-white">Evidence</h3>
                <ul className="mt-3 space-y-3">
                  {result.evidence?.length ? (
                    result.evidence.map((item, index) => (
                      <li key={`${item?.source ?? 'evidence'}-${index}`} className="rounded-xl border border-slate-800 bg-slate-950/55 p-3 text-sm text-slate-300">
                        {renderJson(item)}
                      </li>
                    ))
                  ) : (
                    <li className="text-sm text-slate-400">No evidence was attached.</li>
                  )}
                </ul>
              </div>

              <div className="panel p-6">
                <h3 className="text-lg font-semibold text-white">Observations</h3>
                {result.observations?.length ? (
                  <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-300">
                    {result.observations.map((observation, index) => (
                      <li key={`${observation}-${index}`}>{observation}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-3 text-sm text-slate-400">No observations were recorded.</p>
                )}
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              {result.generated_sql && (
                <div className="panel p-6">
                  <h3 className="text-lg font-semibold text-white">Generated SQL</h3>
                  <pre className="mt-3 overflow-x-auto rounded-xl bg-slate-950/80 p-4 text-xs leading-6 text-cyan-200">
                    {result.generated_sql}
                  </pre>
                </div>
              )}

              {result.execution && (
                <div className="panel p-6">
                  <h3 className="text-lg font-semibold text-white">Execution</h3>
                  <pre className="mt-3 overflow-x-auto rounded-xl bg-slate-950/80 p-4 text-xs leading-6 text-emerald-200">
                    {JSON.stringify(result.execution, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              {result.sql_result && (
                <div className="panel p-6">
                  <h3 className="text-lg font-semibold text-white">SQL result</h3>
                  <pre className="mt-3 overflow-x-auto rounded-xl bg-slate-950/80 p-4 text-xs leading-6 text-violet-200">
                    {JSON.stringify(result.sql_result, null, 2)}
                  </pre>
                </div>
              )}

              {result.pandas_operation && (
                <div className="panel p-6">
                  <h3 className="text-lg font-semibold text-white">Pandas operation</h3>
                  <pre className="mt-3 overflow-x-auto rounded-xl bg-slate-950/80 p-4 text-xs leading-6 text-amber-200">
                    {JSON.stringify(result.pandas_operation, null, 2)}
                  </pre>
                </div>
              )}

              {result.pandas_result && (
                <div className="panel p-6">
                  <h3 className="text-lg font-semibold text-white">Pandas result</h3>
                  <pre className="mt-3 overflow-x-auto rounded-xl bg-slate-950/80 p-4 text-xs leading-6 text-amber-200">
                    {JSON.stringify(result.pandas_result, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            {result.retrieved_documents?.length > 0 && (
              <div className="panel p-6">
                <h3 className="text-lg font-semibold text-white">Retrieved documents</h3>
                <ul className="mt-3 space-y-3">
                  {result.retrieved_documents.map((document, index) => (
                    <li key={`${document?.source ?? 'document'}-${index}`} className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 text-sm text-slate-300">
                      <p className="font-medium text-slate-100">{document.source || 'Document'}</p>
                      <p className="mt-2 whitespace-pre-wrap text-slate-300">{document.content || JSON.stringify(document, null, 2)}</p>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {result.caveats?.length > 0 && (
              <div className="panel p-6">
                <h3 className="text-lg font-semibold text-white">Caveats</h3>
                <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-300">
                  {result.caveats.map((caveat, index) => (
                    <li key={`${caveat}-${index}`}>{caveat}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.validation_errors?.length > 0 && (
              <div className="panel border-rose-500/40 bg-rose-500/5 p-6">
                <h3 className="text-lg font-semibold text-rose-200">Validation errors</h3>
                <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-rose-200/90">
                  {result.validation_errors.map((errorItem, index) => (
                    <li key={`${errorItem}-${index}`}>{errorItem}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}
      </div>
    </div>
  )
}

export default App
