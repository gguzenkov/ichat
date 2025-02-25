<template>
  <div class="profile-container">
    <div class="profile-card">
      <div class="avatar-section">
        <div class="avatar">
          <img 
            :src="avatarUrl ? `http://localhost:8000${avatarUrl}` : '/default-avatar.png'" 
            alt="Аватар"
          >
          <div class="avatar-overlay" @click="triggerFileInput">
            <span>Изменить фото</span>
          </div>
        </div>
        <input
          type="file"
          ref="fileInput"
          style="display: none"
          accept="image/*"
          @change="handleAvatarUpload"
        >
      </div>

      <div class="profile-info">
        <h2>Профиль пользователя</h2>
        
        <div class="info-group">
          <label>Логин:</label>
          <span>{{ userInfo.username }}</span>
        </div>

        <div class="info-group">
          <label>E-mail:</label>
          <span>{{ userInfo.email }}</span>
        </div>

        <div class="password-section">
          <h3>Изменить пароль</h3>
          <div class="form-group">
            <label>Текущий пароль:</label>
            <input 
              type="password" 
              v-model="passwordForm.currentPassword"
              placeholder="Введите текущий пароль"
            >
          </div>
          <div class="form-group">
            <label>Новый пароль:</label>
            <input 
              type="password" 
              v-model="passwordForm.newPassword"
              placeholder="Введите новый пароль"
            >
          </div>
          <div class="form-group">
            <label>Подтверждение пароля:</label>
            <input 
              type="password" 
              v-model="passwordForm.confirmPassword"
              placeholder="Подтвердите новый пароль"
            >
          </div>
          <button @click="changePassword" :disabled="loading">
            {{ loading ? 'Сохранение...' : 'Изменить пароль' }}
          </button>
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        <div v-if="success" class="success-message">
          {{ success }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { axiosInstance } from '../store/modules/auth'

export default {
  name: 'Profile',
  data() {
    return {
      userInfo: {
        username: '',
        email: '',
        avatar: null
      },
      passwordForm: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      loading: false,
      error: null,
      success: null,
      avatarUrl: null
    }
  },
  async created() {
    await this.loadUserInfo()
  },
  methods: {
    async loadUserInfo() {
      try {
        const response = await axiosInstance.get(`/users/${this.$store.state.auth.userId}`)
        this.userInfo = response.data
        this.avatarUrl = response.data.avatar_url
      } catch (error) {
        console.error('Error loading user info:', error)
        this.error = 'Ошибка при загрузке информации пользователя'
      }
    },
    
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    
    async handleAvatarUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      
      const formData = new FormData()
      formData.append('avatar', file)
      
      try {
        this.loading = true
        const response = await axiosInstance.post(`/users/${this.$store.state.auth.userId}/avatar`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        this.avatarUrl = response.data.avatar_url
        this.success = 'Аватар успешно обновлен'
        
        setTimeout(() => {
          const img = new Image()
          img.src = `http://localhost:8000${this.avatarUrl}?${new Date().getTime()}`
        }, 100)
      } catch (error) {
        console.error('Error uploading avatar:', error)
        this.error = 'Ошибка при загрузке аватара'
      } finally {
        this.loading = false
      }
    },
    
    async changePassword() {
      if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
        this.error = 'Пароли не совпадают'
        return
      }
      
      try {
        this.loading = true
        await axiosInstance.post(`/users/${this.$store.state.auth.userId}/change-password`, {
          current_password: this.passwordForm.currentPassword,
          new_password: this.passwordForm.newPassword
        })
        
        this.success = 'Пароль успешно изменен'
        this.passwordForm = {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        }
        this.error = null
      } catch (error) {
        console.error('Error changing password:', error)
        if (error.response?.status === 401) {
          this.error = 'Неверный текущий пароль'
        } else {
          this.error = 'Ошибка при изменении пароля'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.profile-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 30px;
  display: flex;
  gap: 40px;
}

.avatar-section {
  flex-shrink: 0;
}

.avatar {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  cursor: pointer;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar-overlay span {
  color: white;
  font-size: 14px;
}

.avatar:hover .avatar-overlay {
  opacity: 1;
}

.profile-info {
  flex-grow: 1;
}

.info-group {
  margin-bottom: 20px;
}

.info-group label {
  display: block;
  color: #666;
  margin-bottom: 5px;
}

.info-group span {
  font-size: 16px;
  color: #333;
}

.password-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #666;
}

input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

button {
  background: #42b983;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error-message {
  margin-top: 20px;
  padding: 10px;
  background: #ffe6e6;
  color: #ff4444;
  border-radius: 4px;
}

.success-message {
  margin-top: 20px;
  padding: 10px;
  background: #e6ffe6;
  color: #42b983;
  border-radius: 4px;
}
</style> 