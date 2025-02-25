<template>
  <div class="popup-chat" :class="{ minimized }">
    <div class="chat-header" @click="toggleMinimize">
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
      <div class="chat-controls">
        <button class="minimize-btn">
          {{ minimized ? '△' : '▽' }}
        </button>
        <button class="close-btn" @click.stop="closeChat">✕</button>
      </div>
    </div>

    <div v-if="!minimized" class="chat-content">
      <div class="messages" ref="messagesContainer">
        <div v-for="message in messages" :key="message.id" 
             :class="['message', { 'own-message': message.sender_id === currentUserId }]">
          <div class="message-content" v-html="formatMessageWithLinks(message.content)"></div>
          <div class="message-info">
            <span class="timestamp">{{ formatDate(message.created_at) }}</span>
            <button 
              class="delete-btn"
              @click="confirmDelete(message)"
            >
              ✕
            </button>
            <span v-if="message.sender_id === currentUserId" class="read-status">
              {{ message.is_read ? '✓✓' : '✓' }}
            </span>
          </div>
        </div>
      </div>

      <div class="input-area">
        <div v-if="showEmojiPicker" class="emoji-picker" ref="emojiPicker">
          <div class="emoji-categories">
            <button 
              v-for="(category, name) in emojiCategories" 
              :key="name"
              @click="currentCategory = name"
              :class="{ active: currentCategory === name }"
            >
              {{ category.icon }}
            </button>
          </div>
          <div class="emoji-list">
            <button 
              v-for="emoji in currentEmojis" 
              :key="emoji"
              @click="addEmoji(emoji)"
              class="emoji-button"
            >
              {{ emoji }}
            </button>
          </div>
        </div>

        <div v-if="selectedFiles.length > 0" class="selected-files">
          <div v-for="(file, index) in selectedFiles" :key="index" class="file-preview">
            <i class="fas fa-paperclip"></i>
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">({{ formatFileSize(file.size) }})</span>
            <button class="remove-file" @click="removeFile(index)">✕</button>
          </div>
        </div>

        <div class="input-wrapper">
          <input 
            v-model="newMessage" 
            @keyup.enter="sendMessage"
            @input="handleInput"
            @keydown="handleKeydown"
            placeholder="Введите сообщение..."
            :disabled="loading"
            ref="messageInput"
          >
          <label class="attachment-trigger" title="Прикрепить файлы">
            <i class="fas fa-paperclip"></i>
            <input 
              type="file" 
              multiple 
              @change="handleFileSelect" 
              ref="fileInput"
              accept="*/*"
              style="display: none;"
            >
          </label>
          <span 
            class="emoji-trigger"
            @click.stop="toggleEmojiPicker"
            title="Добавить эмодзи"
          >
            <i class="far fa-smile"></i>
          </span>
        </div>

        <button 
          @click="sendMessage" 
          :disabled="(newMessage.trim() === '' && selectedFiles.length === 0) || loading"
        >
          <i class="fas fa-paper-plane"></i>
        </button>
      </div>
    </div>

    <!-- Модальное окно подтверждения удаления -->
    <div v-if="showDeleteModal" class="modal">
      <div class="modal-content">
        <h3>Подтверждение удаления</h3>
        <p>Вы действительно хотите удалить это сообщение?</p>
        <p class="warning">Сообщение будет удалено для всех участников переписки</p>
        <div class="modal-buttons">
          <button @click="deleteMessage" class="delete-confirm-btn">Удалить</button>
          <button @click="cancelDelete" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { axiosInstance } from '../store/modules/auth'
import { emojiCategories } from '../utils/emojis'

export default {
  name: 'PopupChat',
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
      polling: null,
      minimized: false,
      showDeleteModal: false,
      messageToDelete: null,
      showMentionPopup: false,
      mentionFilter: '',
      mentionStartIndex: -1,
      activeUsers: [],
      showEmojiPicker: false,
      currentCategory: 'smileys',
      emojiCategories,
      selectedFiles: [],
      notificationSound: null,
      unreadMessagesCount: 0,
      originalTitle: document.title,
      titleInterval: null
    }
  },
  computed: {
    currentUserId() {
      return this.$store.state.auth.userId
    },
    filteredUsers() {
      if (!this.mentionFilter) return this.activeUsers
      const filter = this.mentionFilter.toLowerCase()
      return this.activeUsers.filter(user => 
        user.username.toLowerCase().includes(filter)
      )
    },
    currentEmojis() {
      return this.emojiCategories[this.currentCategory].emojis
    }
  },
  async created() {
    await this.loadReceiverInfo()
    await this.loadMessages()
    await this.loadActiveUsers()
    this.startPolling()
    this.notificationSound = new Audio('/sounds/notification.mp3')
    this.originalTitle = document.title
  },
  beforeUnmount() {
    this.stopPolling()
    this.clearTitleNotification()
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
        const response = await axiosInstance.get(
          `/private-messages/${this.receiverId}`, 
          { 
            headers: {
              'X-Current-User-Id': this.currentUserId
            }
          }
        )
        
        // Проверяем, есть ли новые сообщения
        const newMessages = response.data.filter(
          msg => !this.messages.some(existingMsg => existingMsg.id === msg.id) && 
                msg.sender_id !== this.currentUserId
        )
        
        // Если есть новые сообщения и чат не активен, воспроизводим звук
        if (newMessages.length > 0 && this.minimized) {
          this.playNotificationSound()
          this.showTitleNotification()
        }
        
        this.messages = response.data
        
        // Отмечаем непрочитанные сообщения как прочитанные, если чат открыт
        if (!this.minimized) {
          const unreadMessages = this.messages.filter(
            msg => msg.receiver_id === this.currentUserId && !msg.is_read
          )
          
          for (const msg of unreadMessages) {
            await this.markAsRead(msg.id)
          }
          
          // Если чат открыт и мы прочитали сообщения, убираем уведомление
          if (unreadMessages.length > 0) {
            this.clearTitleNotification()
          }
        } else {
          // Если чат свернут, считаем непрочитанные сообщения
          this.unreadMessagesCount = this.messages.filter(
            msg => msg.receiver_id === this.currentUserId && !msg.is_read
          ).length
        }
        
        // Прокручиваем к последнему сообщению при первой загрузке
        if (this.isFirstLoad) {
          this.$nextTick(() => {
            this.scrollToBottom()
            this.isFirstLoad = false
          })
        }
      } catch (error) {
        console.error('Error loading messages:', error)
      }
    },
    async sendMessage() {
      if ((this.newMessage.trim() === '' && this.selectedFiles.length === 0) || this.loading) return

      this.loading = true
      try {
        let attachments = []
        
        if (this.selectedFiles.length > 0) {
          const formData = new FormData()
          this.selectedFiles.forEach(file => {
            formData.append('files', file)
          })

          const response = await axiosInstance.post('/messages/attachments', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
              'X-Current-User-Id': this.currentUserId
            }
          })
          attachments = response.data.attachments
        }

        await axiosInstance.post('/private-messages', {
          content: this.newMessage.trim() || '',
          receiver_id: parseInt(this.receiverId),
          sender_id: parseInt(this.currentUserId),
          attachments: attachments
        }, {
          headers: {
            'X-Current-User-Id': this.currentUserId
          }
        })

        this.newMessage = ''
        this.selectedFiles = []
        if (this.$refs.fileInput) {
          this.$refs.fileInput.value = ''
        }
        await this.loadMessages()
        this.scrollToBottom()
      } catch (error) {
        console.error('Error sending message:', error)
        alert('Ошибка при отправке сообщения')
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
    },
    toggleMinimize() {
      this.minimized = !this.minimized
      
      // Если открываем чат, отмечаем сообщения как прочитанные
      if (!this.minimized) {
        this.markAllAsRead()
        this.clearTitleNotification()
      }
    },
    closeChat() {
      this.$emit('close')
    },
    confirmDelete(message) {
      this.messageToDelete = message
      this.showDeleteModal = true
    },
    cancelDelete() {
      this.messageToDelete = null
      this.showDeleteModal = false
    },
    async deleteMessage() {
      if (!this.messageToDelete) return

      try {
        await axiosInstance.delete(
          `/private-messages/${this.messageToDelete.id}`,
          {
            headers: {
              'X-Current-User-Id': this.currentUserId
            }
          }
        )
        await this.loadMessages()
        this.showDeleteModal = false
        this.messageToDelete = null
      } catch (error) {
        console.error('Error deleting message:', error)
      }
    },
    async loadActiveUsers() {
      try {
        const response = await axiosInstance.get('/users/active')
        this.activeUsers = response.data
      } catch (error) {
        console.error('Error loading active users:', error)
      }
    },
    handleInput(event) {
      const text = event.target.value
      const lastAtIndex = text.lastIndexOf('@')
      
      if (lastAtIndex !== -1 && (lastAtIndex === 0 || text[lastAtIndex - 1] === ' ')) {
        this.mentionStartIndex = lastAtIndex
        this.mentionFilter = text.slice(lastAtIndex + 1)
        this.showMentionPopup = true
      } else if (this.showMentionPopup && this.mentionStartIndex !== -1) {
        this.mentionFilter = text.slice(this.mentionStartIndex + 1)
        if (!this.mentionFilter || text[this.mentionStartIndex] !== '@') {
          this.closeMentionPopup()
        }
      }
    },
    handleKeydown(event) {
      if (!this.showMentionPopup) return

      if (event.key === 'Escape') {
        this.closeMentionPopup()
      }
    },
    selectMention(user) {
      const beforeMention = this.newMessage.slice(0, this.mentionStartIndex)
      const afterMention = this.newMessage.slice(this.mentionStartIndex + this.mentionFilter.length + 1)
      this.newMessage = `${beforeMention}@${user.username} ${afterMention}`
      this.closeMentionPopup()
      this.$refs.messageInput.focus()
    },
    closeMentionPopup() {
      this.showMentionPopup = false
      this.mentionFilter = ''
      this.mentionStartIndex = -1
    },
    handleFileSelect(event) {
      const files = Array.from(event.target.files)
      if (files.length > 3) {
        alert('Можно прикрепить максимум 3 файла')
        return
      }
      this.selectedFiles = files
    },
    removeFile(index) {
      this.selectedFiles.splice(index, 1)
      if (this.selectedFiles.length === 0) {
        this.$refs.fileInput.value = ''
      }
    },
    formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B'
      else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
      else return (bytes / 1048576).toFixed(1) + ' MB'
    },
    toggleEmojiPicker() {
      this.showEmojiPicker = !this.showEmojiPicker
    },
    addEmoji(emoji) {
      const cursorPosition = this.$refs.messageInput.selectionStart
      const textBeforeCursor = this.newMessage.slice(0, cursorPosition)
      const textAfterCursor = this.newMessage.slice(cursorPosition)
      this.newMessage = textBeforeCursor + emoji + textAfterCursor
      
      this.$nextTick(() => {
        const newPosition = cursorPosition + emoji.length
        this.$refs.messageInput.setSelectionRange(newPosition, newPosition)
        this.$refs.messageInput.focus()
      })

      this.showEmojiPicker = false
    },
    async markAsRead(messageId) {
      try {
        await axiosInstance.put(
          `/private-messages/${messageId}/read`,
          null,
          {
            headers: {
              'X-Current-User-Id': this.currentUserId
            }
          }
        )
        await this.loadMessages()
      } catch (error) {
        console.error('Error marking message as read:', error)
      }
    },
    async markAllAsRead() {
      const unreadMessages = this.messages.filter(
        msg => msg.receiver_id === this.currentUserId && !msg.is_read
      )
      
      for (const msg of unreadMessages) {
        await this.markAsRead(msg.id)
      }
      
      this.unreadMessagesCount = 0
    },
    playNotificationSound() {
      try {
        this.notificationSound.currentTime = 0
        this.notificationSound.play()
      } catch (error) {
        console.error('Error playing notification sound:', error)
      }
    },
    showTitleNotification() {
      if (this.titleInterval) return // Уже показывается
      
      this.titleInterval = setInterval(() => {
        document.title = document.title === this.originalTitle 
          ? `(${this.unreadMessagesCount}) Новое сообщение` 
          : this.originalTitle
      }, 1000)
      
      // Добавляем favicon с уведомлением
      this.updateFavicon(true)
    },
    clearTitleNotification() {
      if (this.titleInterval) {
        clearInterval(this.titleInterval)
        this.titleInterval = null
        document.title = this.originalTitle
        
        // Возвращаем обычный favicon
        this.updateFavicon(false)
      }
    },
    updateFavicon(showNotification) {
      const favicon = document.querySelector('link[rel="icon"]')
      if (!favicon) return
      
      if (showNotification) {
        // Сохраняем оригинальный favicon, если еще не сохранен
        if (!favicon.dataset.original) {
          favicon.dataset.original = favicon.href
        }
        
        // Здесь можно использовать готовый favicon с уведомлением
        // или создать его динамически с помощью canvas
        favicon.href = '/favicon-notification.ico' // Путь к favicon с уведомлением
      } else if (favicon.dataset.original) {
        // Возвращаем оригинальный favicon
        favicon.href = favicon.dataset.original
      }
    },
    formatMessageWithLinks(text) {
      if (!text) return ''
      
      // Сначала экранируем HTML
      const escapedText = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;')
      
      // Регулярное выражение для поиска URL и email
      const urlRegex = /(https?:\/\/[^\s<]+[^<.,:;"')\]\s])/g
      const emailRegex = /([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)/gi
      
      // Сначала заменяем URL на HTML-ссылки
      let formattedText = escapedText.replace(urlRegex, (url) => {
        return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="message-link">${url}</a>`
      })
      
      // Затем заменяем email на HTML-ссылки
      formattedText = formattedText.replace(emailRegex, (email) => {
        return `<a href="mailto:${email}" class="message-link email-link">${email}</a>`
      })
      
      return formattedText
    }
  }
}
</script>

<style scoped>
.popup-chat {
  position: fixed;
  bottom: 90px;
  right: 20px;
  width: 300px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  z-index: 998;
}

.chat-header {
  padding: 10px;
  background: #42b983;
  color: white;
  border-radius: 8px 8px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  overflow: hidden;
}

.user-avatar img {
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
  width: 20px;
  height: 20px;
  color: #757575;
}

.chat-controls {
  display: flex;
  gap: 5px;
}

.minimize-btn, .close-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0 5px;
}

.chat-content {
  height: 400px;
  display: flex;
  flex-direction: column;
}

.messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message {
  max-width: 80%;
  padding: 8px;
  border-radius: 8px;
  background: #f5f5f5;
}

.own-message {
  align-self: flex-end;
  background: #e3f2fd;
}

.message-content {
  margin-bottom: 4px;
  word-break: break-word;
}

.message-info {
  display: flex;
  justify-content: flex-end;
  gap: 5px;
  font-size: 0.8em;
  color: #666;
}

.input-area {
  padding: 10px;
  border-top: 1px solid #eee;
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
}

.input-wrapper {
  display: flex;
  gap: 8px;
  position: relative;
}

.attachment-trigger {
  position: absolute;
  right: 40px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #999;
  transition: color 0.2s;
  padding: 5px;
}

.attachment-trigger:hover {
  color: #666;
}

.emoji-trigger {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #999;
  transition: color 0.2s;
  padding: 5px;
}

.emoji-trigger:hover {
  color: #666;
}

.selected-files {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  padding: 4px 8px;
  background: #f8f9fa;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  border: 1px solid #eee;
  border-bottom: none;
  font-size: 0.85em;
}

.file-preview {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 2px 0;
  color: #666;
}

.file-preview i {
  font-size: 0.9em;
  color: #999;
}

.file-name {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: #999;
  font-size: 0.9em;
}

.remove-file {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0;
  font-size: 0.9em;
  margin-left: auto;
}

.remove-file:hover {
  color: #ff4444;
}

.emoji-picker {
  position: absolute;
  bottom: 100%;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.emoji-categories {
  display: flex;
  justify-content: space-around;
  margin-bottom: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid #eee;
}

.emoji-categories button {
  background: none;
  border: none;
  padding: 2px;
  cursor: pointer;
  font-size: 1em;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.emoji-categories button:hover,
.emoji-categories button.active {
  opacity: 1;
}

.emoji-list {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1px;
  max-height: 150px;
  overflow-y: auto;
  padding: 2px;
}

.emoji-button {
  background: none;
  border: none;
  padding: 2px;
  cursor: pointer;
  font-size: 1.2em;
  transition: opacity 0.2s;
  opacity: 0.8;
}

.emoji-button:hover {
  opacity: 1;
}

.minimized {
  height: auto;
}

.minimized .chat-content {
  display: none;
}

.read-status {
  color: #42b983;
}

.delete-btn {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0 5px;
  font-size: 1.2em;
  line-height: 1;
  opacity: 0;
  transition: opacity 0.2s;
}

.message:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: #ff4444;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1100;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 300px;
  text-align: center;
}

.warning {
  color: #ff4444;
  font-size: 0.9em;
  margin: 10px 0;
}

.modal-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

.delete-confirm-btn {
  background: #ff4444;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.delete-confirm-btn:hover {
  background: #ff2222;
}

.cancel-btn {
  background: #666;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn:hover {
  background: #555;
}

.mention-popup {
  position: absolute;
  bottom: 100%;
  left: 0;
  width: 200px;
  max-height: 200px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  z-index: 1000;
}

.mention-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.mention-item:hover {
  background-color: #f5f5f5;
}

.mention-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  overflow: hidden;
}

.mention-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mention-username {
  font-size: 0.9em;
  color: #333;
}

.message-attachments {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 0.9em;
  transition: background-color 0.2s;
}

.attachment:hover {
  background: #e9ecef;
}

.attachment i {
  color: #6c757d;
  font-size: 1.1em;
}

.attachment-link {
  color: #0066cc;
  text-decoration: none;
  flex-grow: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.attachment-link:hover {
  text-decoration: underline;
}

.message-link {
  color: #0066cc;
  text-decoration: none;
  word-break: break-all;
  transition: color 0.2s;
  display: inline-flex;
  align-items: center;
}

.message-link:hover {
  color: #0052a3;
  text-decoration: underline;
}

/* Иконка для внешних ссылок */
.message-link::after {
  content: '↗';
  display: inline-block;
  margin-left: 3px;
  font-size: 0.8em;
  opacity: 0.7;
}

/* Специальная иконка для email-ссылок */
.email-link::after {
  content: '✉';
}

/* Стили для ссылок внутри .message-text */
.message-text :deep(a) {
  color: #0066cc;
  text-decoration: none;
  word-break: break-all;
  transition: color 0.2s;
  display: inline-flex;
  align-items: center;
}

.message-text :deep(a:hover) {
  color: #0052a3;
  text-decoration: underline;
}

.message-text :deep(a.message-link::after) {
  content: '↗';
  display: inline-block;
  margin-left: 3px;
  font-size: 0.8em;
  opacity: 0.7;
}

.message-text :deep(a.email-link::after) {
  content: '✉';
}
</style> 