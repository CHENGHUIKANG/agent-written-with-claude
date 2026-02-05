<template>
  <div class="chat-container">
    <el-card class="chat-card">
      <div class="chat-messages" ref="messagesContainer">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role]"
        >
          <div class="message-content">
            <div class="message-role">{{ message.role === 'user' ? '我' : 'AI' }}</div>
            <div v-if="message.reasoning && message.role === 'assistant'" class="reasoning-toggle">
              <el-button
                text
                size="small"
                type="info"
                @click="toggleReasoning(index)"
              >
                <el-icon>
                  <component :is="message.showReasoning ? ArrowUp : ArrowDown" />
                </el-icon>
                思考
              </el-button>
            </div>
            <div v-if="message.reasoning && message.showReasoning && message.role === 'assistant'" class="reasoning-content">
              <pre class="reasoning-text">{{ message.reasoning }}</pre>
            </div>
            <div class="message-text">{{ message.content }}</div>
            <div v-if="message.tool_calls" class="tool-calls">
              <div v-for="(tool, idx) in message.tool_calls" :key="idx" class="tool-call">
                <el-tag size="small" type="info">{{ tool.function.name }}</el-tag>
                <pre>{{ tool.function.arguments }}</pre>
              </div>
            </div>
          </div>
        </div>
        <div v-if="loading" class="message assistant">
          <div class="message-content">
            <div class="message-role">AI</div>
            <div class="message-text">
              <el-icon class="is-loading"><Loading /></el-icon>
              思考中...
            </div>
          </div>
        </div>
      </div>
      <div class="chat-input">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="3"
          placeholder="输入消息..."
          @keydown.ctrl.enter="sendStreamMessage"
        />
        <el-button
          type="primary"
          :loading="loading"
          @click="sendStreamMessage"
          style="margin-top: 10px; width: 100%"
        >
          发送 (Ctrl+Enter)
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Loading, ArrowDown, ArrowUp } from '@element-plus/icons-vue';
import api from '@/api';

const messages = ref([]);
const inputMessage = ref('');
const loading = ref(false);
const messagesContainer = ref(null);

function toggleReasoning(index) {
  messages.value[index].showReasoning = !messages.value[index].showReasoning;
}

async function sendMessage() {
  if (!inputMessage.value.trim()) {
    ElMessage.warning('请输入消息');
    return;
  }

  const userMessage = inputMessage.value;
  messages.value.push({
    role: 'user',
    content: userMessage
  });
  inputMessage.value = '';

  await scrollToBottom();

  loading.value = true;
  try {
    const response = await api.post('/agent/chat', {
      message: userMessage,
      conversation_id: null
    });

    messages.value.push({
      role: 'assistant',
      content: response.content,
      reasoning: response.reasoning,
      tool_calls: response.tool_calls,
      showReasoning: false
    });

    await scrollToBottom();
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发送消息失败');
  } finally {
    loading.value = false;
  }
}

async function sendStreamMessage() {
  if (!inputMessage.value.trim()) {
    ElMessage.warning('请输入消息');
    return;
  }

  const userMessage = inputMessage.value;
  messages.value.push({
    role: 'user',
    content: userMessage
  });
  inputMessage.value = '';

  await scrollToBottom();

  loading.value = true;
  const assistantMessage = {
    role: 'assistant',
    content: '',
    reasoning: '',
    tool_calls: [],
    showReasoning: false
  };
  messages.value.push(assistantMessage);

  let inReasoning = false;
  let reasoningBuffer = '';
  let contentBuffer = '';

  try {
    const response = await api.post('/agent/chat/stream', {
      message: userMessage,
      conversation_id: null
    }, {
      responseType: 'stream'
    });

    const reader = response.data.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          
          if (data === '[DONE]') {
            if (reasoningBuffer && !inReasoning) {
              assistantMessage.reasoning = reasoningBuffer;
            }
            break;
          }

          if (data.startsWith('[ERROR:')) {
            ElMessage.error(data.slice(7));
            break;
          }

          if (data.startsWith('[TOOL_CALL:')) {
            const toolCallMatch = data.match(/\[TOOL_CALL:(.+?):(.+)\]/);
            if (toolCallMatch) {
              assistantMessage.tool_calls.push({
                function: {
                  name: toolCallMatch[1],
                  arguments: toolCallMatch[2]
                }
              });
            }
            continue;
          }

          if (data.includes('<思考>')) {
            inReasoning = true;
            reasoningBuffer = '';
            continue;
          }

          if (data.includes('</思考>')) {
            inReasoning = false;
            assistantMessage.reasoning = reasoningBuffer;
            reasoningBuffer = '';
            continue;
          }

          if (inReasoning) {
            reasoningBuffer += data;
          } else {
            assistantMessage.content += data;
          }

          await scrollToBottom();
        }
      }
    }

    if (assistantMessage.reasoning) {
      assistantMessage.showReasoning = false;
    }

  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发送消息失败');
  } finally {
    loading.value = false;
  }
}

async function scrollToBottom() {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
}

onMounted(() => {
  messages.value.push({
    role: 'assistant',
    content: '你好！我是 AI 助手，有什么可以帮助你的吗？'
  });
});
</script>

<style scoped>
.chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f7fa;
}

.message {
  margin-bottom: 20px;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message.user .message-content {
  background-color: #409eff;
  color: #fff;
}

.message-role {
  font-size: 12px;
  margin-bottom: 4px;
  opacity: 0.8;
}

.reasoning-toggle {
  margin-bottom: 8px;
}

.reasoning-toggle .el-button {
  padding: 4px 8px;
  font-size: 12px;
}

.reasoning-content {
  margin-bottom: 12px;
  padding: 10px;
  background-color: #f8f9fa;
  border-left: 3px solid #909399;
  border-radius: 4px;
}

.reasoning-label {
  font-size: 12px;
  font-weight: 500;
  color: #909399;
  margin-bottom: 6px;
}

.reasoning-text {
  margin: 0;
  padding: 8px;
  background-color: #fff;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.5;
  color: #606266;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 300px;
  overflow-y: auto;
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
}

.tool-calls {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.tool-call {
  margin-bottom: 8px;
}

.tool-call pre {
  margin: 4px 0 0 0;
  padding: 8px;
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
}

.chat-input {
  padding: 20px;
  border-top: 1px solid #e4e7ed;
  background-color: #fff;
}
</style>
