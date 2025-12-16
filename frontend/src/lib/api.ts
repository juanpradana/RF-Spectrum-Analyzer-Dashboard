import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const uploadFile = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

export const getAnalyses = async () => {
  const response = await api.get('/api/analyses')
  return response.data
}

export const getAnalysis = async (id: number) => {
  const response = await api.get(`/api/analyses/${id}`)
  return response.data
}

export const getAutoThreshold = async (
  id: number,
  bandNumber: number,
  marginDb: number = 10.0
) => {
  const response = await api.get(`/api/analyses/${id}/auto-threshold`, {
    params: {
      band_number: bandNumber,
      margin_db: marginDb,
    },
  })
  return response.data
}

export const analyzeSpectrum = async (
  id: number,
  bandNumber: number,
  threshold: number,
  useAutoThreshold: boolean = false,
  marginDb: number = 10.0
) => {
  const formData = new FormData()
  formData.append('band_number', bandNumber.toString())
  formData.append('threshold', threshold.toString())
  formData.append('use_auto_threshold', useAutoThreshold.toString())
  formData.append('margin_db', marginDb.toString())

  const response = await api.post(`/api/analyses/${id}/analyze`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

export const generateReport = async (
  id: number,
  bandNumber: number,
  threshold: number
) => {
  const formData = new FormData()
  formData.append('band_number', bandNumber.toString())
  formData.append('threshold', threshold.toString())

  const response = await api.post(`/api/analyses/${id}/report`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response.data
}

export const getChannels = async (id: number, bandNumber?: number) => {
  const params = bandNumber ? { band_number: bandNumber } : {}
  const response = await api.get(`/api/analyses/${id}/channels`, { params })
  return response.data
}

export const downloadReport = (filename: string) => {
  return `${API_URL}/api/reports/${filename}`
}

export const deleteAnalysis = async (id: number) => {
  const response = await api.delete(`/api/analyses/${id}`)
  return response.data
}

export const deleteAllAnalyses = async () => {
  const response = await api.delete('/api/analyses')
  return response.data
}

export default api
