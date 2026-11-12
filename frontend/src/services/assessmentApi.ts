const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '')

export const FACE_TYPES = ['plane', 'cylinder', 'cone', 'sphere', 'torus', 'other'] as const

export type FaceType = (typeof FACE_TYPES)[number]

export interface AssessmentSubmission {
  question_id: string
  parameters: {
    volume: number
    surface_area: number
    center_of_mass: [number, number, number]
    bounding_box: [number, number, number]
    number_of_solid_bodies: number
    number_of_solid_faces: number
    number_of_edges: number
    face_types: Record<FaceType, number>
  }
}

interface ScalarAssessment {
  error: number
  score: number
}

interface VectorAssessment {
  error: [number, number, number]
  score: number
}

interface CountAssessment {
  error: number
  score: number
}

export interface AssessmentResponse {
  question_id: string
  assessment: {
    volume: ScalarAssessment
    surface_area: ScalarAssessment
    center_of_mass: VectorAssessment
    bounding_box: VectorAssessment
    number_of_solid_bodies: CountAssessment
    number_of_solid_faces: CountAssessment
    number_of_edges: CountAssessment
    face_types: { error: Partial<Record<FaceType, number>>; score: number }
  }
  overall_score: number
}

interface ErrorResponse {
  message: string
  details?: unknown[]
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function toErrorResponse(value: unknown): ErrorResponse | null {
  if (!isRecord(value) || typeof value.message !== 'string') {
    return null
  }
  return {
    message: value.message,
    details: Array.isArray(value.details) ? value.details : [],
  }
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value)
}

function isScore(value: unknown): value is number {
  return isFiniteNumber(value) && value >= 0 && value <= 100
}

function isScalarAssessment(value: unknown): value is ScalarAssessment {
  return isRecord(value) && isFiniteNumber(value.error) && value.error >= 0 && isScore(value.score)
}

function isVectorAssessment(value: unknown): value is VectorAssessment {
  return isRecord(value)
    && Array.isArray(value.error)
    && value.error.length === 3
    && value.error.every((component) => isFiniteNumber(component) && component >= 0)
    && isScore(value.score)
}

function isCountAssessment(value: unknown): value is CountAssessment {
  return isRecord(value)
    && typeof value.error === 'number'
    && Number.isInteger(value.error)
    && value.error >= 0
    && isScore(value.score)
}

function isFaceTypesAssessment(value: unknown): value is AssessmentResponse['assessment']['face_types'] {
  return isRecord(value)
    && isRecord(value.error)
    && Object.entries(value.error).every(
      ([type, count]) => FACE_TYPES.some((faceType) => faceType === type)
        && typeof count === 'number'
        && Number.isInteger(count)
        && count >= 0,
    )
    && isScore(value.score)
}

function isAssessmentResponse(value: unknown): value is AssessmentResponse {
  if (!isRecord(value) || typeof value.question_id !== 'string' || !isScore(value.overall_score)) {
    return false
  }
  const assessment = value.assessment
  return isRecord(assessment)
    && isScalarAssessment(assessment.volume)
    && isScalarAssessment(assessment.surface_area)
    && isVectorAssessment(assessment.center_of_mass)
    && isVectorAssessment(assessment.bounding_box)
    && isCountAssessment(assessment.number_of_solid_bodies)
    && isCountAssessment(assessment.number_of_solid_faces)
    && isCountAssessment(assessment.number_of_edges)
    && isFaceTypesAssessment(assessment.face_types)
}

export class AssessmentApiError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'AssessmentApiError'
  }
}

export async function assessSubmission(
  submission: AssessmentSubmission,
): Promise<AssessmentResponse> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/assessments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(submission),
    })
  } catch {
    throw new AssessmentApiError(
      `Could not connect to the CAD Fun API at ${API_BASE_URL}. Check that the backend is running.`,
    )
  }

  const body: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    const error = toErrorResponse(body)
    const details = error?.details
      ?.filter(isRecord)
      .map((detail) => {
        const location = Array.isArray(detail.loc)
          ? detail.loc.filter((part) => part !== 'body').join('.')
          : ''
        const message = typeof detail.msg === 'string' ? detail.msg : ''
        return [location, message].filter(Boolean).join(': ')
      })
      .filter(Boolean) ?? []
    const message = error
      ? error.message
      : `The API returned an unexpected error (${response.status}).`
    throw new AssessmentApiError(
      [message, ...details].join(' '),
    )
  }

  if (!isAssessmentResponse(body)) {
    throw new AssessmentApiError('The API returned an invalid assessment response.')
  }
  return body
}
