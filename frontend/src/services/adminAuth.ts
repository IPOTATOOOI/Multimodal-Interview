import axios from 'axios'
import type { AuthResponse } from '../types/auth'
import { getApiUrl } from '@/config/api'

const API_URL = getApiUrl('/admin')

export const AdminAuthService = {
  async login(formData: FormData): Promise<AuthResponse> {
    const response = await axios.post<AuthResponse>(`${API_URL}/login`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  async register(formData: FormData): Promise<AuthResponse> {
    const response = await axios.post<AuthResponse>(`${API_URL}/register`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
}
