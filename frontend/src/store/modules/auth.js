import axios from 'axios'

const API_URL = 'http://localhost:8000/api'

// Настраиваем axios для всех запросов
export const axiosInstance = axios.create({
  baseURL: API_URL,
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

export default {
  namespaced: true,
  
  state: {
    isAuthenticated: false,
    user: null,
    userId: null,
    token: null,
    error: null
  },

  mutations: {
    SET_AUTH(state, auth) {
      state.isAuthenticated = auth.isAuthenticated
      state.user = auth.user
      state.userId = auth.userId
      state.token = auth.token
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    CLEAR_ERROR(state) {
      state.error = null
    }
  },

  actions: {
    async register({ commit }, userData) {
      try {
        commit('CLEAR_ERROR')
        const response = await axiosInstance.post('/register', {
          username: userData.username,
          email: userData.email,
          password: userData.password
        })
        
        console.log('Registration successful:', response.data)
        return response.data
      } catch (error) {
        console.error('Registration error:', error)
        let errorMessage = 'Ошибка при регистрации'
        if (error.response) {
          errorMessage = error.response.data.detail || errorMessage
        }
        commit('SET_ERROR', errorMessage)
        throw new Error(errorMessage)
      }
    },

    async login({ commit }, credentials) {
      try {
        commit('CLEAR_ERROR')
        const formData = new FormData()
        formData.append('username', credentials.username)
        formData.append('password', credentials.password)

        const response = await axiosInstance.post('/login', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        const { access_token, username, user_id } = response.data
        
        commit('SET_AUTH', {
          isAuthenticated: true,
          user: username,
          userId: user_id,
          token: access_token
        })
        
        localStorage.setItem('token', access_token)
        localStorage.setItem('userId', user_id)
        axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        
        return response.data
      } catch (error) {
        console.error('Login error:', error)
        let errorMessage = 'Ошибка при входе'
        if (error.response) {
          errorMessage = error.response.data.detail || errorMessage
        }
        commit('SET_ERROR', errorMessage)
        throw new Error(errorMessage)
      }
    },

    logout({ commit }) {
      localStorage.removeItem('token')
      localStorage.removeItem('userId')
      delete axiosInstance.defaults.headers.common['Authorization']
      commit('SET_AUTH', {
        isAuthenticated: false,
        user: null,
        userId: null,
        token: null
      })
    }
  },

  getters: {
    isAuthenticated: state => state.isAuthenticated,
    currentUser: state => state.user,
    authError: state => state.error
  }
} 