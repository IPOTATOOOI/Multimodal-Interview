export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  password: string
  email: string
}

export interface AuthResponse {
  code: number
  msg: string
  data: {
    token?: string
    admin?: {
      id: number
      username: string
      email: string
      status: number
      createTime: string
    }
  }
}
