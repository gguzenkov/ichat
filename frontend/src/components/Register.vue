<template>
  <div class="login">
    <h2>Регистрация</h2>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>
    <form @submit.prevent="handleSubmit" v-if="!successMessage">
      <div class="form-group">
        <label>Имя пользователя:</label>
        <input 
          type="text" 
          v-model="username" 
          required
          placeholder="Введите имя пользователя"
          :disabled="loading"
        >
      </div>
      <div class="form-group">
        <label>Email:</label>
        <input 
          type="email" 
          v-model="email" 
          required
          placeholder="Введите email"
          :disabled="loading"
        >
      </div>
      <div class="form-group">
        <label>Пароль:</label>
        <input 
          type="password" 
          v-model="password" 
          required
          placeholder="Введите пароль"
          :disabled="loading"
        >
      </div>
      <div class="form-group">
        <label>Подтверждение пароля:</label>
        <input 
          type="password" 
          v-model="confirmPassword" 
          required
          placeholder="Подтвердите пароль"
          :disabled="loading"
        >
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
      </button>
    </form>
    <div class="form-footer">
      <p>Уже есть аккаунт? <router-link to="/login">Войти</router-link></p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Register',
  data() {
    return {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      error: null,
      successMessage: null,
      loading: false
    }
  },
  methods: {
    async handleSubmit() {
      this.error = null
      this.successMessage = null
      
      if (this.password !== this.confirmPassword) {
        this.error = 'Пароли не совпадают'
        return
      }

      this.loading = true

      try {
        const result = await this.$store.dispatch('auth/register', {
          username: this.username,
          email: this.email,
          password: this.password
        })

        this.successMessage = 'Спасибо за регистрацию! Теперь вы можете войти'
        
        // Очищаем форму
        this.username = ''
        this.email = ''
        this.password = ''
        this.confirmPassword = ''

        // Ждем немного перед редиректом, чтобы пользователь увидел сообщение
        setTimeout(() => {
          this.$router.push({
            path: '/login',
            query: { registered: 'success' }
          })
        }, 2000)
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    }
  },
  // Очищаем сообщения при уничтожении компонента
  beforeUnmount() {
    this.$store.commit('CLEAR_ERROR')
  }
}
</script>

<style scoped>
.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 15px;
}

.success-message {
  color: #28a745;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 15px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.form-group input:disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.form-footer a {
  color: #42b983;
  text-decoration: none;
}

.form-footer a:hover {
  text-decoration: underline;
}
</style> 