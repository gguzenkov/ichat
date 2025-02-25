<template>
  <div class="user-profile">
    <div class="profile-card">
      <div class="profile-header">
        <div class="avatar-section">
          <div v-if="user.avatar_url" class="avatar">
            <img :src="`http://localhost:8000${user.avatar_url}`" alt="Аватар">
          </div>
          <div v-else class="avatar default-avatar">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
          </div>
        </div>
        <h2>{{ user.username }}</h2>
      </div>

      <div class="profile-info">
        <div class="info-group">
          <label>Логин:</label>
          <span>{{ user.username }}</span>
        </div>
        <div class="info-group">
          <label>E-mail:</label>
          <span>{{ user.email }}</span>
        </div>
        <div class="info-group">
          <label>Дата регистрации:</label>
          <span>{{ formatDate(user.created_at) }}</span>
        </div>
      </div>

      <div class="actions">
        <button @click="startChat" class="action-btn">
          <i class="fas fa-envelope"></i> Написать сообщение
        </button>
        <button @click="$router.push('/chat')" class="back-btn">
          <i class="fas fa-arrow-left"></i> Вернуться в чат
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { axiosInstance } from '../store/modules/auth'

export default {
  name: 'UserProfile',
  props: {
    userId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      user: {}
    }
  },
  async created() {
    await this.loadUserInfo()
  },
  methods: {
    async loadUserInfo() {
      try {
        const response = await axiosInstance.get(`/users/${this.userId}`)
        this.user = response.data
      } catch (error) {
        console.error('Error loading user info:', error)
      }
    },
    startChat() {
      this.$router.push(`/chat/${this.userId}`)
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }
  }
}
</script>

<style scoped>
.user-profile {
  max-width: 600px;
  margin: 40px auto;
  padding: 20px;
}

.profile-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.avatar-section {
  position: relative;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.default-avatar {
  background-color: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.default-avatar svg {
  width: 60px;
  height: 60px;
  color: #757575;
}

.profile-info {
  margin-bottom: 30px;
}

.info-group {
  margin-bottom: 15px;
  display: flex;
  gap: 10px;
}

.info-group label {
  font-weight: bold;
  color: #666;
  min-width: 150px;
}

.actions {
  display: flex;
  gap: 10px;
  justify-content: flex-start;
  margin-top: 20px;
}

.action-btn, .back-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  background: #42b983;
  color: white;
}

.back-btn {
  background: #666;
  color: white;
}

.action-btn:hover {
  background: #3aa876;
}

.back-btn:hover {
  background: #555;
}
</style> 