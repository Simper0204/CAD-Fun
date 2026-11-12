import { useState, type FormEvent } from 'react'
import {
  FACE_TYPES,
  assessSubmission,
  AssessmentApiError,
  type AssessmentResponse,
} from './services/assessmentApi'

const criteria: { key: keyof AssessmentResponse['assessment']; label: string; unit: string }[] = [
  { key: 'volume', label: 'Volume', unit: '' },
  { key: 'surface_area', label: 'Surface area', unit: '' },
  { key: 'center_of_mass', label: 'Center of mass', unit: 'mm' },
  { key: 'bounding_box', label: 'Bounding box', unit: 'mm' },
  { key: 'number_of_solid_bodies', label: 'Solid bodies', unit: 'count' },
  { key: 'number_of_solid_faces', label: 'Solid faces', unit: 'count' },
  { key: 'number_of_edges', label: 'Edges', unit: 'count' },
  { key: 'face_types', label: 'Face types', unit: 'count' },
]

function readNumber(data: FormData, name: string): number {
  const value = Number(data.get(name))
  if (!Number.isFinite(value)) {
    throw new Error(`Enter a valid number for ${name.replaceAll('_', ' ')}.`)
  }
  return value
}

function formatError(error: number | number[] | Partial<Record<string, number>>): string {
  if (Array.isArray(error)) {
    return error.map((value) => value.toLocaleString(undefined, { maximumFractionDigits: 6 })).join(', ')
  }
  if (typeof error === 'object') {
    const entries = Object.entries(error)
    return entries.length
      ? entries.map(([name, value]) => `${name}: ${value}`).join(', ')
      : 'No difference'
  }
  return error.toLocaleString(undefined, { maximumFractionDigits: 6 })
}

function App() {
  const [result, setResult] = useState<AssessmentResponse | null>(null)
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setResult(null)
    setIsSubmitting(true)

    try {
      const data = new FormData(event.currentTarget)
      const counts = [
        ['number_of_solid_bodies', 'solid bodies'],
        ['number_of_solid_faces', 'solid faces'],
        ['number_of_edges', 'edges'],
        ...FACE_TYPES.map((type) => [`face_${type}`, `${type} faces`]),
      ] as const

      for (const [field, label] of counts) {
        const value = readNumber(data, field)
        if (!Number.isInteger(value) || value < 0) {
          throw new Error(`${label} must be a non-negative whole number.`)
        }
      }

      const response = await assessSubmission({
        question_id: 'CAD001',
        parameters: {
          volume: readNumber(data, 'volume'),
          surface_area: readNumber(data, 'surface_area'),
          center_of_mass: ['x', 'y', 'z'].map((axis) => readNumber(data, `center_of_mass_${axis}`)) as [number, number, number],
          bounding_box: ['x', 'y', 'z'].map((axis) => readNumber(data, `bounding_box_${axis}`)) as [number, number, number],
          number_of_solid_bodies: readNumber(data, 'number_of_solid_bodies'),
          number_of_solid_faces: readNumber(data, 'number_of_solid_faces'),
          number_of_edges: readNumber(data, 'number_of_edges'),
          face_types: Object.fromEntries(
            FACE_TYPES.map((type) => [type, readNumber(data, `face_${type}`)]),
          ) as Record<(typeof FACE_TYPES)[number], number>,
        },
      })
      setResult(response)
    } catch (submissionError) {
      if (submissionError instanceof AssessmentApiError) {
        setError(submissionError.message)
      } else if (submissionError instanceof Error) {
        setError(submissionError.message)
      } else {
        setError('Something went wrong while submitting your assessment.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label="CAD Fun home">
          <span className="brand-mark" aria-hidden="true">C</span>
          <span>CAD<span className="brand-accent">FUN</span></span>
        </a>
        <span className="version-pill">VERSION 1</span>
      </header>

      <main>
        <section className="intro">
          <p className="eyebrow"><span className="eyebrow-line" /> BUILD. MEASURE. LEARN.</p>
          <h1>Make your model.<br /><span>Know your numbers.</span></h1>
          <p className="intro-copy">
            Enter the measurements from your CAD model and get a detailed assessment.
            Your model stays in your CAD software; CAD Fun scores the values you submit.
          </p>
        </section>

        <div className="workspace">
          <section className="panel exercise-panel" aria-labelledby="exercise-heading">
            <div className="panel-heading">
              <div>
                <p className="section-kicker">CURRENT EXERCISE</p>
                <h2 id="exercise-heading">Sample block</h2>
              </div>
              <span className="question-id">CAD001</span>
            </div>
            <div className="notice">
              <span className="notice-icon" aria-hidden="true">i</span>
              <p>
                This is the only question configured on the backend right now. Exercise
                instructions and drawings are not available through the current API.
              </p>
            </div>
            <div className="divider" />

            <form onSubmit={handleSubmit}>
              <fieldset disabled={isSubmitting}>
                <legend className="form-section-title">
                  <span className="step-number">01</span>
                  Model measurements
                </legend>
                <p className="form-hint">Use millimetres (mm), mm², and mm³ as labelled.</p>

                <div className="field-grid two-columns">
                  <NumberField label="Volume" name="volume" unit="mm³" min="0" required />
                  <NumberField label="Surface area" name="surface_area" unit="mm²" min="0" required />
                </div>

                <VectorFields title="Center of mass" prefix="center_of_mass" unit="mm" />
                <VectorFields title="Bounding box" prefix="bounding_box" unit="mm" min="0" />

                <div className="field-grid three-columns">
                  <NumberField label="Solid bodies" name="number_of_solid_bodies" min="0" step="1" required />
                  <NumberField label="Solid faces" name="number_of_solid_faces" min="0" step="1" required />
                  <NumberField label="Edges" name="number_of_edges" min="0" step="1" required />
                </div>

                <div className="face-type-section">
                  <div className="subsection-heading">
                    <span>Faces by type</span>
                    <span className="unit-label">non-negative counts</span>
                  </div>
                  <div className="field-grid three-columns face-grid">
                    {FACE_TYPES.map((type) => (
                      <NumberField
                        key={type}
                        label={type[0].toUpperCase() + type.slice(1)}
                        name={`face_${type}`}
                        min="0"
                        step="1"
                        required
                      />
                    ))}
                  </div>
                </div>

                {error && (
                  <div className="error-message" role="alert">
                    <strong>Assessment not submitted</strong>
                    <span>{error}</span>
                  </div>
                )}

                <button className="submit-button" type="submit">
                  {isSubmitting ? 'Submitting assessment…' : 'Assess my model'}
                  {!isSubmitting && <span aria-hidden="true">↗</span>}
                </button>
                <p className="privacy-note">Your values are assessed by the CAD Fun backend.</p>
              </fieldset>
            </form>
          </section>

          <aside className="side-column">
            {result ? (
              <section className="panel result-panel" aria-live="polite">
                <p className="section-kicker">ASSESSMENT COMPLETE</p>
                <div className="score-display">
                  <span className="score-number">{result.overall_score.toFixed(2)}</span>
                  <span className="score-out-of">/ 100</span>
                </div>
                <p className="score-caption">Overall score</p>
                <div className="divider" />
                <h3 className="result-heading">Criterion breakdown</h3>
                <ul className="result-list">
                  {criteria.map(({ key, label, unit }) => {
                    const item = result.assessment[key]
                    return (
                      <li key={key} className="result-item">
                        <div className="result-item-top">
                          <span>{label}</span>
                          <strong>{item.score.toFixed(2)}<small> / 100</small></strong>
                        </div>
                        <div className="result-track" aria-hidden="true">
                          <span style={{ width: `${item.score}%` }} />
                        </div>
                        <p className="result-error">
                          Error{unit ? ` (${unit})` : ''}: {formatError(item.error)}
                        </p>
                      </li>
                    )
                  })}
                </ul>
                <p className="result-footnote">
                  Scores and error values are returned by the backend. Scalar error units
                  follow the criterion configured for this question.
                </p>
              </section>
            ) : (
              <section className="panel guide-panel">
                <p className="section-kicker">YOUR WORKFLOW</p>
                <h2>From CAD to feedback</h2>
                <ol className="workflow-list">
                  <li><span>1</span><p><strong>Build</strong> your model in your CAD program.</p></li>
                  <li><span>2</span><p><strong>Measure</strong> its dimensions and topology.</p></li>
                  <li><span>3</span><p><strong>Submit</strong> the values to see your assessment.</p></li>
                </ol>
                <div className="divider" />
                <p className="guide-note">
                  CAD Fun compares your submitted measurements. It does not inspect or
                  verify your CAD file.
                </p>
              </section>
            )}
            <div className="side-caption">
              <span className="status-dot" />
              <span>Assessment powered by CAD Fun API</span>
            </div>
          </aside>
        </div>
      </main>

      <footer className="footer">
        <span>CAD FUN <span className="footer-muted">· A better way to learn by building</span></span>
        <span>Measurements in metric units</span>
      </footer>
    </div>
  )
}

function NumberField({
  label,
  name,
  unit,
  min,
  step,
  required = false,
}: {
  label: string
  name: string
  unit?: string
  min?: string
  step?: string
  required?: boolean
}) {
  return (
    <label className="field">
      <span className="field-label">{label}{unit && <span className="unit-label">{unit}</span>}</span>
      <input
        type="number"
        name={name}
        min={min}
        step={step ?? 'any'}
        required={required}
        placeholder="0"
      />
    </label>
  )
}

function VectorFields({
  title,
  prefix,
  unit,
  min,
}: {
  title: string
  prefix: string
  unit: string
  min?: string
}) {
  return (
    <div className="vector-section">
      <div className="subsection-heading">
        <span>{title}</span>
        <span className="unit-label">{unit} · X, Y, Z</span>
      </div>
      <div className="field-grid three-columns">
        {(['x', 'y', 'z'] as const).map((axis) => (
          <NumberField key={axis} label={axis.toUpperCase()} name={`${prefix}_${axis}`} min={min} required />
        ))}
      </div>
    </div>
  )
}

export default App
