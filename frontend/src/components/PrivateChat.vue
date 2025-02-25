<template>
  <div class="private-chat">
    <div class="chat-header">
      <div class="user-info">
        <div v-if="receiver.avatar_url" class="user-avatar">
          <img :src="`http://localhost:8000${receiver.avatar_url}`" alt="Аватар">
        </div>
        <div v-else class="user-avatar default-avatar">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
          </svg>
        </div>
        <span class="username">{{ receiver.username }}</span>
      </div>
      <button class="close-btn" @click="$router.push('/chat')">✕</button>
    </div>

    <div class="messages" ref="messagesContainer">
      <div v-for="message in messages" :key="message.id" 
           :class="['message', { 'own-message': message.sender_id === currentUserId }]">
        <div class="message-content">{{ message.content }}</div>
        <div class="message-info">
          <span class="timestamp">{{ formatDate(message.created_at) }}</span>
          <span v-if="message.sender_id === currentUserId" class="read-status">
            {{ message.is_read ? '✓✓' : '✓' }}
          </span>
        </div>
      </div>
    </div>

    <div class="input-area">
      <input 
        v-model="newMessage" 
        @keyup.enter="sendMessage"
        placeholder="Введите сообщение..."
        :disabled="loading"
      >
      <button @click="sendMessage" :disabled="!newMessage.trim() || loading">
        {{ loading ? 'Отправка...' : 'Отправить' }}
      </button>
    </div>
  </div>
</template>

<script>
import { axiosInstance } from '../store/modules/auth'

export default {
  name: 'PrivateChat',
  props: {
    receiverId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      messages: [],
      newMessage: '',
      loading: false,
      receiver: {},
      polling: null
    }
  },
  computed: {
    currentUserId() {
      return this.$store.state.auth.userId
    }
  },
  async created() {
    await this.loadReceiverInfo()
    await this.loadMessages()
    this.startPolling()
  },
  beforeUnmount() {
    this.stopPolling()
  },
  methods: {
    async loadReceiverInfo() {
      try {
        const response = await axiosInstance.get(`/users/${this.receiverId}`)
        this.receiver = response.data
      } catch (error) {
        console.error('Error loading receiver info:', error)
      }
    },
    async loadMessages() {
      try {
        const response = await axiosInstance.get(`/private-messages/${this.receiverId}?current_user_id=${this.currentUserId}`)
        this.messages = response.data
        this.$nextTick(() => {
          this.scrollToBottom()
        })
      } catch (error) {
        console.error('Error loading messages:', error)
      }
    },
    async sendMessage() {
      if (!this.newMessage.trim() || this.loading) return

      this.loading = true
      try {
        await axiosInstance.post('/private-messages', {
          content: this.newMessage.trim(),
          receiver_id: parseInt(this.receiverId)
        })
        this.newMessage = ''
        await this.loadMessages()
      } catch (error) {
        console.error('Error sending message:', error)
      } finally {
        this.loading = false
      }
    },
    startPolling() {
      this.polling = setInterval(this.loadMessages, 3000)
    },
    stopPolling() {
      if (this.polling) {
        clearInterval(this.polling)
        this.polling = null
      }
    },
    scrollToBottom() {
      const container = this.$refs.messagesContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.private-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #666;
  cursor: pointer;
}

.messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message {
  max-width: 70%;
  padding: 10px;
  border-radius: 8px;
  background: #f5f5f5;
}

.own-message {
  align-self: flex-end;
  background: #e3f2fd;
}

.message-content {
  margin-bottom: 5px;
}

.message-info {
  display: flex;
  justify-content: flex-end;
  gap: 5px;
  font-size: 0.8em;
  color: #666;
}

.input-area {
  padding: 15px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
}

input {
  flex-grow: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  padding: 10px 20px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.read-status {
  color: #42b983;
}
</style> 