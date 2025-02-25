<template>
  <div class="chat-container">
    <div class="chat">
      <div class="chat-messages" ref="messagesContainer">
        <div v-if="messages.length === 0" class="no-messages">
          Нет сообщений
        </div>
        <div v-else v-for="message in sortedMessages" :key="message.id" class="message">
          <div class="message-header">
            <div class="user-info">
              <div v-if="message.avatar_url" class="message-avatar">
                <img 
                  :src="`http://localhost:8000${message.avatar_url}`" 
                  alt="Аватар"
                >
              </div>
              <div v-else class="message-avatar default-avatar">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              </div>
              <span class="username">{{ message.username }}</span>
            </div>
            <div class="message-controls">
              <span class="timestamp">{{ formatDate(message.created_at) }}</span>
              <button 
                v-if="canDeleteMessage(message)" 
                @click="confirmDelete(message)"
                class="control-btn delete-btn"
              >
                ✕
              </button>
            </div>
          </div>
          <div class="message-content">
            <div v-if="message.content" class="message-text" v-html="formatMessageWithLinks(message.content)"></div>
            <div v-if="message.attachments && message.attachments.length > 0" class="message-attachments">
              <div v-for="(attachment, index) in message.attachments" :key="index" class="attachment">
                <i class="fas fa-file"></i>
                <a 
                  :href="`http://localhost:8000${attachment.file_path}`" 
                  target="_blank"
                  class="attachment-link"
                >
                  {{ attachment.file_name }} ({{ formatFileSize(attachment.file_size) }})
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="chat-input">
        <div class="mention-popup" v-if="showMentionPopup" ref="mentionPopup">
          <div 
            v-for="user in filteredUsers" 
            :key="user.id" 
            class="mention-item"
            @click="selectMention(user)"
          >
            <div v-if="user.avatar_url" class="mention-avatar">
              <img :src="`http://localhost:8000${user.avatar_url}`" alt="Аватар">
            </div>
            <div v-else class="mention-avatar default-avatar">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            </div>
            <span class="mention-username">{{ user.username }}</span>
          </div>
        </div>
        
        <!-- Добавляем панель эмодзи -->
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

        <!-- Добавляем превью выбранных файлов -->
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
          <div class="input-actions">
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
        </div>

        <button 
          @click="sendMessage" 
          :disabled="(newMessage.trim() === '' && selectedFiles.length === 0) || loading"
        >
          {{ loading ? 'Отправка...' : 'Отправить' }}
        </button>
      </div>

      <div v-if="showDeleteModal" class="modal">
        <div class="modal-content">
          <h3>Подтверждение удаления</h3>
          <p>Вы действительно хотите удалить это сообщение?</p>
          <div class="modal-buttons">
            <button @click="deleteMessage" class="delete-confirm-btn">Удалить</button>
            <button @click="cancelDelete" class="cancel-btn">Отмена</button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="users-list">
      <h3>Участники чата</h3>
      <div class="users">
        <div v-for="user in activeUsers" :key="user.id" class="user-item" @click="showUserMenu(user, $event)">
          <div v-if="user.avatar_url" class="user-avatar">
            <img 
              :src="`http://localhost:8000${user.avatar_url}`" 
              alt="Аватар"
            >
          </div>
          <div v-else class="user-avatar default-avatar">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
          </div>
          <div class="user-info-container">
            <span class="user-status"></span>
            <span class="user-name">{{ user.username }}</span>
            <span 
              v-if="unreadCounts[user.id]" 
              class="unread-badge"
              @click.stop="openPrivateChat(user)"
            >
              {{ unreadCounts[user.id] }}
            </span>
          </div>
        </div>
      </div>

      <!-- Контекстное меню пользователя -->
      <div v-if="showContextMenu" 
           class="user-context-menu"
           :style="{ top: contextMenuPosition.y + 'px', left: contextMenuPosition.x + 'px' }">
        <div class="menu-item" @click="mentionUser">
          <i class="fas fa-at"></i> Упомянуть
        </div>
        <div class="menu-item" @click="sendPrivateMessage">
          <i class="fas fa-envelope"></i> Личное сообщение
        </div>
        <div class="menu-item" @click="viewProfile">
          <i class="fas fa-user"></i> Просмотреть профиль
        </div>
      </div>
    </div>

    <!-- Добавляем всплывающие чаты -->
    <div class="popup-chats">
      <PopupChat
        v-for="chat in activeChats"
        :key="chat.userId"
        :receiver-id="chat.userId"
        @close="closeChat(chat.userId)"
      />
    </div>

    <!-- Добавляем кнопку для открытия всех личных сообщений -->
    <div class="messages-button" @click="toggleAllMessages" :class="{ active: showAllMessages }">
      <i class="fas fa-envelope"></i>
      <span v-if="totalUnreadCount" class="total-unread">{{ totalUnreadCount }}</span>
    </div>

    <!-- Добавляем панель со всеми личными сообщениями -->
    <div v-if="showAllMessages" class="all-messages-panel">
      <div class="panel-header">
        <h3>Личные сообщения</h3>
        <button class="close-btn" @click="showAllMessages = false">✕</button>
      </div>
      <div class="messages-list">
        <div v-if="privateChats.length === 0" class="no-chats">
          У вас пока нет личных сообщений
        </div>
        <div v-else v-for="chat in privateChats" :key="chat.userId" class="chat-item" @click="openPrivateChat(chat.user)">
          <div class="chat-avatar">
            <div v-if="chat.user.avatar_url" class="user-avatar">
              <img :src="`http://localhost:8000${chat.user.avatar_url}`" alt="Аватар">
            </div>
            <div v-else class="default-avatar">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            </div>
          </div>
          <div class="chat-info">
            <div class="chat-header">
              <span class="username">{{ chat.user.username }}</span>
              <span class="timestamp">{{ formatDate(chat.lastMessage.created_at) }}</span>
            </div>
            <div class="last-message" :class="{ unread: chat.unreadCount }">
              {{ chat.lastMessage.content }}
            </div>
          </div>
          <div v-if="chat.unreadCount" class="unread-count">
            {{ chat.unreadCount }}
          </div>
        </div>
      </div>
    </div>

    <!-- Добавляем модальное окно для подтверждения активности -->
    <div v-if="showInactivityModal" class="modal inactivity-modal">
      <div class="modal-content">
        <h3>Вы еще здесь?</h3>
        <p>Вы неактивны уже некоторое время.</p>
        <p>Хотите продолжить работу?</p>
        <div class="modal-timer">
          Автоматический выход через: {{ formatInactivityTimer }}
        </div>
        <div class="modal-buttons">
          <button @click="continueSession" class="continue-btn">Продолжить работу</button>
          <button @click="logout" class="logout-btn">Выйти</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { axiosInstance } from '../store/modules/auth'
import PopupChat from './PopupChat.vue'

export default {
  name: 'Chat',
  components: {
    PopupChat
  },
  data() {
    return {
      messages: [],
      newMessage: '',
      polling: null,
      loading: false,
      error: null,
      showDeleteModal: false,
      messageToDelete: null,
      activeUsers: [],
      showContextMenu: false,
      contextMenuPosition: { x: 0, y: 0 },
      selectedUser: null,
      activeChats: [],
      unreadCounts: {},
      unreadPolling: null,
      readMessagesByUser: {},
      showAllMessages: false,
      privateChats: [],
      showMentionPopup: false,
      mentionFilter: '',
      mentionStartIndex: -1,
      showEmojiPicker: false,
      currentCategory: 'smileys',
      emojiCategories: {
        smileys: {
          icon: '😊',
          emojis: ['😀', '😊', '😅', '😂', '🤣', '😇', '🙂', '😉', '😍', '🥰', '😘', '😋', '😜', '😴', '😎']
        },
        hearts: {
          icon: '❤️',
          emojis: ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '💯', '💢', '💥', '✨', '💫', '💝', '💕']
        },
        hands: {
          icon: '👍',
          emojis: ['👍', '👎', '👌', '✌️', '🤞', '👊', '🤝', '🙏', '💪', '🤲', '👐', '🙌', '👏', '🤌', '🫶']
        }
      },
      showReactionPickerFor: null,
      quickReactions: ['👍', '❤️', '😊', '😂', '😮', '😢', '👏', '🎉'],
      selectedFiles: [],
      isFirstLoad: true,
      lastActivityTime: Date.now(),
      inactivityCheckInterval: null,
      showInactivityModal: false,
      inactivityTimer: 300, // 5 минут в секундах
      inactivityTimerInterval: null,
      isInactivityWarningShown: false
    }
  },
  computed: {
    userId() {
      return this.$store.state.auth.userId
    },
    totalUnreadCount() {
      return Object.values(this.unreadCounts).reduce((sum, count) => sum + count, 0)
    },
    filteredUsers() {
      if (!this.mentionFilter) return this.activeUsers
      const filter = this.mentionFilter.toLowerCase()
      return this.activeUsers.filter(user => 
        user.username.toLowerCase().includes(filter)
      )
    },
    sortedMessages() {
      return [...this.messages].sort((a, b) => {
        return new Date(a.created_at) - new Date(b.created_at)
      })
    },
    currentEmojis() {
      return this.emojiCategories[this.currentCategory].emojis
    },
    formatInactivityTimer() {
      const minutes = Math.floor(this.inactivityTimer / 60)
      const seconds = this.inactivityTimer % 60
      return `${minutes}:${seconds.toString().padStart(2, '0')}`
    }
  },
  async created() {
    await this.loadMessages()
    await this.loadActiveUsers()
    this.startPolling()
    this.startUsersPolling()
    this.startActivityTracking()
    await this.updateUserActivity()
    this.startUnreadPolling()
    this.startInactivityCheck()
  },
  beforeUnmount() {
    this.stopPolling()
    this.stopUsersPolling()
    this.stopActivityTracking()
    document.removeEventListener('click', this.hideContextMenu)
    this.stopUnreadPolling()
    document.removeEventListener('click', this.handleClickOutside)
    this.stopInactivityCheck()
  },
  mounted() {
    // Закрываем меню при клике вне его
    document.addEventListener('click', this.hideContextMenu)
    document.addEventListener('click', this.handleClickOutside)
  },
  methods: {
    startPolling() {
      this.pollInterval = setInterval(async () => {
        await this.loadMessages()
        // Убираем автопрокрутку при обновлении через polling
      }, 3000)
    },
    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },
    async loadMessages() {
      try {
        const response = await axiosInstance.get('/messages')
        if (response.data) {
          this.messages = response.data
          // Прокручиваем только при первой загрузке
          if (this.isFirstLoad) {
            this.$nextTick(() => {
              this.scrollToBottom()
              this.isFirstLoad = false
            })
          }
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
              'X-Current-User-Id': this.userId
            }
          })
          attachments = response.data.attachments
        }

        const messageData = {
          content: this.newMessage.trim() || '',
          user_id: parseInt(this.userId),
          attachments: attachments
        }
        
        await axiosInstance.post('/messages', messageData)
        await this.updateUserActivity()
        this.newMessage = ''
        this.selectedFiles = []
        this.$refs.fileInput.value = ''
        await this.loadMessages()
        // Прокручиваем к низу только при отправке своего сообщения
        this.scrollToBottom()
      } catch (error) {
        console.error('Error sending message:', error)
        alert('Ошибка при отправке сообщения')
      } finally {
        this.loading = false
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      try {
        const date = new Date(dateStr)
        return date.toLocaleString('ru-RU', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          timeZone: 'Europe/Moscow'
        })
      } catch (e) {
        console.error('Error formatting date:', e)
        return 'Некорректная дата'
      }
    },
    scrollToBottom() {
      const container = this.$refs.messagesContainer
      if (container) {
        container.scrollTo({
          top: container.scrollHeight,
          behavior: 'smooth'
        })
      }
    },
    canDeleteMessage(message) {
      return message.user_id === parseInt(this.userId)
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
        await axiosInstance.delete(`/messages/${this.messageToDelete.id}?current_user_id=${this.userId}`)
        await this.loadMessages()
        this.showDeleteModal = false
        this.messageToDelete = null
      } catch (error) {
        console.error('Error deleting message:', error)
        alert('Ошибка при удалении сообщения')
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
    startUsersPolling() {
      this.usersPolling = setInterval(this.loadActiveUsers, 10000)
    },
    stopUsersPolling() {
      if (this.usersPolling) {
        clearInterval(this.usersPolling)
        this.usersPolling = null
      }
    },
    async updateUserActivity() {
      try {
        await axiosInstance.post(`/users/${this.userId}/heartbeat`)
        this.updateLastActivity()
      } catch (error) {
        console.error('Error updating user activity:', error)
      }
    },
    startActivityTracking() {
      this.activityInterval = setInterval(this.updateUserActivity, 30000)
      window.addEventListener('mousemove', this.updateUserActivity)
      window.addEventListener('keydown', this.updateUserActivity)
    },
    stopActivityTracking() {
      if (this.activityInterval) {
        clearInterval(this.activityInterval)
        this.activityInterval = null
      }
      window.removeEventListener('mousemove', this.updateUserActivity)
      window.removeEventListener('keydown', this.updateUserActivity)
    },
    showUserMenu(user, event) {
      event.preventDefault()
      event.stopPropagation()
      
      this.selectedUser = user
      this.contextMenuPosition = {
        x: event.clientX,
        y: event.clientY
      }
      this.showContextMenu = true
    },
    hideContextMenu(event) {
      if (!event.target.closest('.user-context-menu')) {
        this.showContextMenu = false
      }
    },
    mentionUser() {
      if (this.selectedUser) {
        this.newMessage = `${this.newMessage}@${this.selectedUser.username} `
        this.$refs.messageInput?.focus()
      }
      this.showContextMenu = false
    },
    async openPrivateChat(user) {
      const userId = user.id
      if (!this.activeChats.find(chat => chat.userId === userId)) {
        this.activeChats.push({ userId })
        
        try {
          const response = await axiosInstance.get(
            `/private-messages/${userId}`,
            { 
              headers: {
                'X-Current-User-Id': this.userId
              }
            }
          )
          
          const unreadMessages = response.data.filter(
            msg => msg.receiver_id === this.userId && !msg.is_read
          )
          
          // Отмечаем все непрочитанные сообщения как прочитанные
          for (const msg of unreadMessages) {
            await axiosInstance.put(
              `/private-messages/${msg.id}/read`,
              null,
              {
                headers: {
                  'X-Current-User-Id': this.userId
                }
              }
            )
          }

          // Сохраняем последнее прочитанное время для этого пользователя
          this.readMessagesByUser[userId] = new Date().toISOString()
          
          await this.loadUnreadCounts()
        } catch (error) {
          console.error('Error marking messages as read:', error)
        }
      }
      
      // Закрываем окно списка личных сообщений
      this.showAllMessages = false
    },
    sendPrivateMessage() {
      this.openPrivateChat(this.selectedUser)
      this.showContextMenu = false
    },
    viewProfile() {
      this.$router.push(`/profile/${this.selectedUser.id}`)
      this.showContextMenu = false
    },
    closeChat(userId) {
      // Сохраняем время закрытия чата как время последнего прочтения
      this.readMessagesByUser[userId] = new Date().toISOString()
      this.activeChats = this.activeChats.filter(chat => chat.userId !== userId)
      this.loadUnreadCounts()
    },
    async loadUnreadCounts() {
      try {
        const response = await axiosInstance.get('/private-messages-unread', {
          headers: {
            'X-Current-User-Id': this.userId
          }
        })
        
        // Получаем все сообщения для каждого пользователя с непрочитанными сообщениями
        const counts = { ...response.data }
        
        // Проверяем каждого пользователя с непрочитанными сообщениями
        for (const userId in counts) {
          try {
            const messagesResponse = await axiosInstance.get(
              `/private-messages/${userId}`,
              { 
                headers: {
                  'X-Current-User-Id': this.userId
                }
              }
            )
            
            // Фильтруем только те сообщения, которые пришли после последнего прочтения
            const lastReadTime = this.readMessagesByUser[userId]
            if (lastReadTime) {
              const unreadCount = messagesResponse.data.filter(msg => 
                msg.receiver_id === this.userId && 
                msg.created_at > lastReadTime
              ).length
              
              if (unreadCount === 0) {
                delete counts[userId]
              } else {
                counts[userId] = unreadCount
              }
            }
          } catch (error) {
            console.error('Error loading messages for user:', userId, error)
          }
        }
        
        // Исключаем открытые чаты
        this.activeChats.forEach(chat => {
          delete counts[chat.userId]
        })
        
        this.unreadCounts = counts
      } catch (error) {
        console.error('Error loading unread counts:', error)
      }
    },
    startUnreadPolling() {
      this.loadUnreadCounts()
      this.unreadPolling = setInterval(this.loadUnreadCounts, 3000)
    },
    stopUnreadPolling() {
      if (this.unreadPolling) {
        clearInterval(this.unreadPolling)
        this.unreadPolling = null
      }
    },
    async toggleAllMessages() {
      this.showAllMessages = !this.showAllMessages
      if (this.showAllMessages) {
        await this.loadPrivateChats()
      }
    },
    async loadPrivateChats() {
      try {
        const response = await axiosInstance.get('/pm-chats', {
          headers: {
            'X-Current-User-Id': this.userId
          }
        })
        this.privateChats = response.data
        console.log('Loaded chats:', this.privateChats) // Для отладки
      } catch (error) {
        console.error('Error loading private chats:', error)
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
    toggleEmojiPicker() {
      this.showEmojiPicker = !this.showEmojiPicker
    },
    addEmoji(emoji) {
      const cursorPosition = this.$refs.messageInput.selectionStart
      const textBeforeCursor = this.newMessage.slice(0, cursorPosition)
      const textAfterCursor = this.newMessage.slice(cursorPosition)
      this.newMessage = textBeforeCursor + emoji + textAfterCursor
      
      // Устанавливаем курсор после вставленного эмодзи
      this.$nextTick(() => {
        const newPosition = cursorPosition + emoji.length
        this.$refs.messageInput.setSelectionRange(newPosition, newPosition)
        this.$refs.messageInput.focus()
      })
    },
    handleClickOutside(event) {
      const emojiPicker = this.$refs.emojiPicker
      const emojiTrigger = event.target.closest('.emoji-trigger')
      
      if (emojiPicker && !emojiPicker.contains(event.target) && !emojiTrigger) {
        this.showEmojiPicker = false
      }
    },
    handleFileSelect(event) {
      const files = Array.from(event.target.files)
      if (files.length > 3) {
        alert('Можно прикрепить максимум 3 файла')
        this.$refs.fileInput.value = ''
        return
      }

      const totalSize = files.reduce((sum, file) => sum + file.size, 0)
      const maxSize = 10 * 1024 * 1024 // 10MB

      for (const file of files) {
        if (file.size > maxSize) {
          alert(`Файл ${file.name} превышает максимальный размер 10MB`)
          this.$refs.fileInput.value = ''
          return
        }
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
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    updateLastActivity() {
      this.lastActivityTime = Date.now()
      
      // Если показано предупреждение о неактивности, скрываем его
      if (this.isInactivityWarningShown) {
        this.hideInactivityWarning()
      }
    },
    startInactivityCheck() {
      // Проверяем активность каждую минуту
      this.inactivityCheckInterval = setInterval(() => {
        const inactiveTime = (Date.now() - this.lastActivityTime) / 1000 // в секундах
        
        // Если прошло 30 минут и предупреждение еще не показано
        if (inactiveTime >= 1800 && !this.isInactivityWarningShown) {
          this.showInactivityWarning()
        }
      }, 60000) // проверка каждую минуту
      
      // Добавляем слушатели событий для отслеживания активности
      const events = ['mousemove', 'mousedown', 'keypress', 'scroll', 'touchstart']
      events.forEach(event => {
        window.addEventListener(event, this.updateLastActivity)
      })
    },
    stopInactivityCheck() {
      if (this.inactivityCheckInterval) {
        clearInterval(this.inactivityCheckInterval)
        this.inactivityCheckInterval = null
      }
      
      if (this.inactivityTimerInterval) {
        clearInterval(this.inactivityTimerInterval)
        this.inactivityTimerInterval = null
      }
      
      const events = ['mousemove', 'mousedown', 'keypress', 'scroll', 'touchstart']
      events.forEach(event => {
        window.removeEventListener(event, this.updateLastActivity)
      })
    },
    showInactivityWarning() {
      this.isInactivityWarningShown = true
      this.showInactivityModal = true
      this.inactivityTimer = 300 // 5 минут
      
      // Запускаем таймер обратного отсчета
      this.inactivityTimerInterval = setInterval(() => {
        this.inactivityTimer--
        
        if (this.inactivityTimer <= 0) {
          this.logout()
        }
      }, 1000)
    },
    hideInactivityWarning() {
      this.isInactivityWarningShown = false
      this.showInactivityModal = false
      
      if (this.inactivityTimerInterval) {
        clearInterval(this.inactivityTimerInterval)
        this.inactivityTimerInterval = null
      }
    },
    continueSession() {
      this.updateLastActivity()
      this.hideInactivityWarning()
    },
    async logout() {
      try {
        await this.$store.dispatch('auth/logout')
        this.$router.push('/login')
      } catch (error) {
        console.error('Error during logout:', error)
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
    },
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 100px);
  padding: 20px;
}

.chat {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  margin-bottom: 20px;
  padding: 10px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.no-messages {
  text-align: center;
  color: #666;
  padding: 20px;
}

.message {
  margin-bottom: 15px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
  position: relative;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.message-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.message-avatar,
.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.message-avatar img,
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
  width: 24px;
  height: 24px;
  color: #757575;
}

.username {
  font-weight: bold;
  color: #42b983;
}

.timestamp {
  color: #666;
  font-size: 0.8em;
}

.message-content {
  margin-left: 50px;
  word-break: break-word;
}

.message-text {
  margin-bottom: 8px;
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

.chat-input {
  padding: 10px;
  border-top: 1px solid #eee;
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  flex-grow: 1;
}

input {
  width: 100%;
  padding: 10px;
  padding-right: 80px; /* Место для иконок */
  border: 1px solid #ddd;
  border-radius: 4px;
}

.input-actions {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  gap: 10px;
  align-items: center;
}

.attachment-trigger, .emoji-trigger {
  color: #999;
  cursor: pointer;
  transition: color 0.2s;
  padding: 5px;
}

.attachment-trigger:hover, .emoji-trigger:hover {
  color: #666;
}

.attachment-trigger i, .emoji-trigger i {
  font-size: 1.2em;
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
  width: 300px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 10px;
  padding: 10px;
  z-index: 1000;
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
  margin-bottom: 5px;
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

.chat-input button {
  min-width: 100px;
  padding: 10px 20px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.chat-input button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.control-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s;
  font-size: 14px;
  color: #666;
}

.control-btn:hover {
  opacity: 1;
}

.delete-btn {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0 5px;
  font-size: 1.2em;
  line-height: 1;
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
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 300px;
  text-align: center;
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

.users-list {
  width: 250px;
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.users-list h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 1.1em;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.users {
  overflow-y: auto;
  max-height: calc(100% - 50px);
}

.user-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
  gap: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.user-item:hover {
  background-color: #f5f5f5;
}

.user-info-container {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-grow: 1;
  padding-right: 8px;
}

.user-status {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #42b983;
  flex-shrink: 0;
}

.user-name {
  color: #333;
  font-size: 0.9em;
}

.user-context-menu {
  position: fixed;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 8px 0;
  z-index: 1000;
  min-width: 200px;
}

.menu-item {
  padding: 8px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.menu-item:hover {
  background-color: #f5f5f5;
}

.menu-item i {
  width: 16px;
  color: #666;
}

.popup-chats {
  position: fixed;
  bottom: 0;
  right: 0;
  display: flex;
  flex-direction: row-reverse;
  gap: 20px;
  padding: 0 20px;
  pointer-events: none;
}

.popup-chats > * {
  pointer-events: auto;
}

.unread-badge {
  background-color: #ff4444;
  color: white;
  border-radius: 50%;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: auto;
  cursor: pointer;
  transition: background-color 0.2s;
}

.unread-badge:hover {
  background-color: #ff2222;
}

.messages-button {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #42b983;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s;
  z-index: 1000;
}

.messages-button:hover {
  transform: scale(1.1);
}

.messages-button.active {
  background: #3aa876;
}

.messages-button i {
  font-size: 24px;
}

.total-unread {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff4444;
  color: white;
  border-radius: 50%;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.all-messages-panel {
  position: fixed;
  bottom: 90px;
  right: 20px;
  width: 300px;
  height: 400px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  z-index: 999;
}

.panel-header {
  padding: 15px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  color: #333;
}

.messages-list {
  flex-grow: 1;
  overflow-y: auto;
  padding: 10px;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.chat-item:hover {
  background-color: #f5f5f5;
}

.chat-avatar {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

.chat-info {
  flex-grow: 1;
  min-width: 0;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.chat-header .timestamp {
  font-size: 0.8em;
  color: #666;
}

.last-message {
  color: #666;
  font-size: 0.9em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.last-message.unread {
  color: #333;
  font-weight: bold;
}

.unread-count {
  background: #42b983;
  color: white;
  border-radius: 50%;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-chats {
  text-align: center;
  color: #666;
  padding: 20px;
  font-style: italic;
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
  background: none;
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
  display: flex;
  align-items: center;
  justify-content: center;
}

.emoji-button:hover {
  opacity: 1;
  background: none;
}

/* Стилизация скроллбара для более компактного вида */
.emoji-list::-webkit-scrollbar {
  width: 6px;
}

.emoji-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.emoji-list::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}

.emoji-list::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}

.inactivity-modal .modal-content {
  max-width: 400px;
}

.modal-timer {
  margin: 15px 0;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 1.2em;
  font-weight: bold;
  color: #dc3545;
}

.continue-btn {
  background: #42b983;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.continue-btn:hover {
  background: #3aa876;
}

.logout-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.logout-btn:hover {
  background: #5a6268;
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