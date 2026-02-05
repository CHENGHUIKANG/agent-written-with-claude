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
            <div v-if="message.reasoning && (message.showReasoning !== false) && message.role === 'assistant'" class="reasoning-content">
              <pre class="reasoning-text">{{ message.reasoning }}</pre>
            </div>
            <div class="message-text">{{ message.content }}</div>
            <div v-if="message.tool_calls" class="tool-calls">
              <div v-for="(tool, idx) in message.tool_calls" :key="idx" class="tool-call">
                <el-tag size="small" type="info">{{ tool.function.name }}</el-tag>
                <pre>{{ tool.function.arguments }}</pre>
              </div>
            </div>
            <!-- 显示工具执行状态 -->
            <div v-if="message.tool_status" class="tool-status">
              <el-tag size="small" type="success">{{ message.tool_status }}</el-tag>
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
  console.log('[Chat] ========== 开始发送消息 ==========');
  console.log('[Chat] 用户消息:', userMessage);

  messages.value.push({
    role: 'user',
    content: userMessage
  });
  inputMessage.value = '';

  await scrollToBottom();

  // 使用 ref 创建响应式消息对象，确保实时更新
  const assistantMessageIndex = messages.value.length;
  console.log('[Chat] 创建AI消息, 索引:', assistantMessageIndex);

  messages.value.push({
    role: 'assistant',
    content: '',
    reasoning: '',
    tool_calls: [],
    tool_status: '', // 添加工具状态字段
    showReasoning: true  // 默认显示思考内容，用户可以点击按钮隐藏
  });

  // 流式接收过程中不需要显示 loading，因为已经有 AI 消息框在实时更新了
  loading.value = false;

  let inReasoning = false;
  let reasoningBuffer = '';
  let contentBuffer = '';
  let buffer = '';

  // 强制更新消息的辅助函数
  const updateMessage = (updates) => {
    const msg = messages.value[assistantMessageIndex];
    Object.assign(msg, updates);
    // 强制触发 Vue 响应式更新
    messages.value = [...messages.value];
  };

  try {
    console.log('[Chat] 发起流式请求到后端...');
    // 使用 Fetch API 处理 SSE 流式响应
    const authStore = JSON.parse(localStorage.getItem('auth') || '{}');
    const token = authStore.token || localStorage.getItem('token');

    const response = await fetch('http://localhost:8000/api/v1/agent/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      body: JSON.stringify({
        message: userMessage,
        conversation_id: null
      })
    });

    console.log('[Chat] 收到响应, status:', response.status);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('[Chat] 请求失败:', errorData);
      throw new Error(errorData.detail || '发送消息失败');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let chunkCount = 0;

    console.log('[Chat] 开始读取流式数据...');

    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log('[Chat] 流式数据读取完成, 总块数:', chunkCount);
        break;
      }

      chunkCount++;
      const chunk = decoder.decode(value, { stream: true });
      console.log(`[Chat] 收到第${chunkCount}块数据, 长度:`, chunk.length);
      buffer += chunk;

      // 处理缓冲区中的完整行
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          console.log('[Chat] 处理数据:', data.substring(0, 100));

          if (data === '[DONE]') {
            console.log('[Chat] 收到 [DONE] 标记');
            if (reasoningBuffer && !inReasoning) {
              updateMessage({ reasoning: reasoningBuffer });
            }
            break;
          }

          if (data.startsWith('[ERROR:')) {
            console.error('[Chat] 收到错误:', data);
            ElMessage.error(data.slice(7));
            break;
          }

          if (data.startsWith('[TOOL_CALL:')) {
            console.log('[Chat] 收到工具调用:', data);
            const toolCallMatch = data.match(/\[TOOL_CALL:(.+?):(.+)\]/);
            if (toolCallMatch) {
              const currentTools = messages.value[assistantMessageIndex].tool_calls || [];
              console.log('[Chat] 添加工具调用:', toolCallMatch[1]);
              updateMessage({
                tool_calls: [...currentTools, {
                  function: {
                    name: toolCallMatch[1],
                    arguments: toolCallMatch[2]
                  }
                }]
              });
            }
            continue;
          }

          // 处理工具状态消息
          if (data.startsWith('[TOOL_STATUS:')) {
            console.log('[Chat] 收到工具状态:', data);
            const statusMatch = data.match(/\[TOOL_STATUS:(.*)\]/);
            if (statusMatch) {
              const statusText = statusMatch[1];
              console.log('[Chat] 更新工具状态:', statusText);
              updateMessage({ tool_status: statusText });
            }
            continue;
          }

          // 处理工具结果消息（保持兼容性）
          if (data.startsWith('[TOOL_RESULT:')) {
            console.log('[Chat] 收到工具结果:', data.substring(0, 100));
            continue;
          }

          if (data.includes('<think>')) {
            console.log('[Chat] 进入思考模式');
            inReasoning = true;
            reasoningBuffer = '';
            continue;
          }

          if (data.includes('</think>')) {
            console.log('[Chat] 退出思考模式, 思考内容长度:', reasoningBuffer.length);
            inReasoning = false;
            updateMessage({ reasoning: reasoningBuffer });
            reasoningBuffer = '';
            continue;
          }

          if (inReasoning) {
            reasoningBuffer += data;
            // 实时更新思考内容
            updateMessage({ reasoning: reasoningBuffer });
          } else {
            contentBuffer += data;
            // 实时更新内容
            updateMessage({ content: contentBuffer });
          }

          // 使用 requestAnimationFrame 优化滚动性能
          requestAnimationFrame(() => {
            scrollToBottom();
          });
        }
      }
    }

    // 处理剩余缓冲区
    if (buffer.startsWith('data: ')) {
      const data = buffer.slice(6);
      console.log('[Chat] 处理剩余缓冲区:', data.substring(0, 50));
      if (!data.startsWith('[') && !data.includes('<think>') && !data.includes('</think>')) {
        if (inReasoning) {
          reasoningBuffer += data;
          updateMessage({ reasoning: reasoningBuffer });
        } else {
          contentBuffer += data;
          updateMessage({ content: contentBuffer });
        }
      }
    }

    // 最终更新
    console.log('[Chat] ========== 流式响应结束 ==========');
    console.log('[Chat] 最终内容长度:', contentBuffer.length);
    console.log('[Chat] 最终思考长度:', reasoningBuffer.length);

    const finalUpdates = {};
    if (reasoningBuffer) finalUpdates.reasoning = reasoningBuffer;
    if (contentBuffer) finalUpdates.content = contentBuffer;
    if (Object.keys(finalUpdates).length > 0) {
      updateMessage(finalUpdates);
    }

  } catch (error) {
    console.error('[Chat] 发送消息失败:', error);
    ElMessage.error(error.message || '发送消息失败');
  } finally {
    loading.value = false;
    console.log('[Chat] loading状态已重置');
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
    content: '你好！我是 AI 助手，有什么可以帮助你的吗？',
    tool_status: ''
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

.tool-status {
  margin-top: 8px;
  padding: 4px 0;
}

.chat-input {
  padding: 20px;
  border-top: 1px solid #e4e7ed;
  background-color: #fff;
}
</style>
