import { createStore } from 'vuex'
import axios from 'axios'
import auth from './modules/auth'

const API_URL = 'http://localhost:8000/api'

export default createStore({
  modules: {
    auth
  },
  state: {
    auth: {
      isAuthenticated: false,
      user: null,
      token: null,
      error: null
    }
  },
  mutations: {
    SET_AUTH(state, auth) {
      state.auth = auth
    },
    SET_ERROR(state, error) {
      state.auth.error = error
    },
    CLEAR_ERROR(state) {
      state.auth.error = null
    }
  },
  actions: {
    async register({ commit }, userData) {
      try {
        commit('CLEAR_ERROR')
        const response = await axios.post(`${API_URL}/register`, {
          username: userData.username,
          email: userData.email,
          password: userData.password
        })
        
        console.log('Registration successful:', response.data)
        return response.data
      } catch (error) {
        const errorMessage = error.response?.data?.detail || 'Ошибка при регистрации'
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

        const response = await axios.post(`${API_URL}/login`, formData)
        const { access_token, username } = response.data
        
        commit('SET_AUTH', {
          isAuthenticated: true,
          user: username,
          token: access_token,
          error: null
        })
        
        // Сохраняем токен
        localStorage.setItem('token', access_token)
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        
        return response.data
      } catch (error) {
        const errorMessage = error.response?.data?.detail || 'Ошибка при входе'
        commit('SET_ERROR', errorMessage)
        throw new Error(errorMessage)
      }
    },
    logout({ commit }) {
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
      commit('SET_AUTH', {
        isAuthenticated: false,
        user: null,
        token: null,
        error: null
      })
    }
  },
  getters: {
    isAuthenticated: state => state.auth.isAuthenticated,
    currentUser: state => state.auth.user,
    authError: state => state.auth.error
  }
}) 