<template>
  <div class="login">
    <h2>Вход в систему</h2>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>Имя пользователя:</label>
        <input 
          type="text" 
          v-model="username"
          required
          placeholder="Введите имя пользователя"
        >
      </div>
      <div class="form-group">
        <label>Пароль:</label>
        <input 
          type="password" 
          v-model="password"
          required
          placeholder="Введите пароль"
        >
      </div>
      <button type="submit">Войти</button>
    </form>
    <div class="form-footer">
      <p>Нет аккаунта? <router-link to="/register">Зарегистрироваться</router-link></p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: ''
    }
  },
  methods: {
    async handleSubmit() {
      try {
        await this.$store.dispatch('auth/login', {
          username: this.username,
          password: this.password
        })
        this.$router.push('/chat')
      } catch (error) {
        console.error('Ошибка входа:', error)
      }
    }
  }
}
</script>

<style scoped>
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

button {
  width: 100%;
  margin-top: 10px;
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