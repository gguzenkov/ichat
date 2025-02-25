<template>
  <div id="app">
    <nav v-if="isLoggedIn" class="navigation">
      <router-link to="/chat">Чат</router-link>
      <router-link to="/profile">Профиль</router-link>
      <a href="#" @click.prevent="logout">Выйти</a>
    </nav>
    <div class="container">
      <router-view/>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  created() {
    // Проверяем наличие токена при загрузке приложения
    const token = localStorage.getItem('token')
    const userId = localStorage.getItem('userId')
    if (token && userId) {
      this.$store.commit('auth/SET_AUTH', {
        isAuthenticated: true,
        token: token,
        userId: userId,
        user: null // Можно добавить запрос данных пользователя
      })
    }
  },
  computed: {
    isLoggedIn() {
      return this.$store.getters['auth/isAuthenticated']
    }
  },
  methods: {
    logout() {
      this.$store.dispatch('auth/logout')
      this.$router.push('/login')
    }
  }
}
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
}

#app {
  min-height: 100vh;
}

.navigation {
  background-color: #2c3e50;
  padding: 1rem;
  text-align: center;
}

.navigation a {
  color: white;
  text-decoration: none;
  margin: 0 10px;
}

.navigation a.router-link-active {
  color: #42b983;
}

/* Добавим стиль для разделителя */
.navigation a:not(:last-child):after {
  content: '|';
  color: #666;
  margin-left: 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.login {
  max-width: 400px;
  margin: 40px auto;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.login form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.login input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #3aa876;
}
</style> 