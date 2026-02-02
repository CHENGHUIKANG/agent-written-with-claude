<template>
  <div class="config-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>LLM 配置</span>
          <el-button type="primary" @click="showAddDialog = true">添加配置</el-button>
        </div>
      </template>
      
      <el-table :data="llmConfigs" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="provider" label="提供商" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.provider }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model_name" label="模型名称" />
        <el-table-column prop="base_url" label="API 地址" show-overflow-tooltip />
        <el-table-column prop="is_default" label="默认" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="success">是</el-tag>
            <el-tag v-else type="info">否</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" :title="editingConfig ? '编辑配置' : '添加配置'" width="600px">
      <el-form :model="configForm" :rules="rules" ref="configFormRef" label-width="100px">
        <el-form-item label="提供商" prop="provider">
          <el-select v-model="configForm.provider" placeholder="请选择提供商" style="width: 100%">
            <el-option label="Custom" value="custom" />
            <el-option label="Local" value="local" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型名称" prop="model_name">
          <el-input v-model="configForm.model_name" placeholder="如: QwQ-32B" />
        </el-form-item>
        <el-form-item label="API 密钥" prop="api_key">
          <el-input v-model="configForm.api_key" placeholder="请输入 API 密钥" show-password />
        </el-form-item>
        <el-form-item label="API 地址" prop="base_url">
          <el-input v-model="configForm.base_url" placeholder="如: http://localhost:8000/v1" />
        </el-form-item>
        <el-form-item label="最大令牌" prop="max_tokens">
          <el-input-number v-model="configForm.max_tokens" :min="1" :max="100000" />
        </el-form-item>
        <el-form-item label="温度" prop="temperature">
          <el-slider v-model="configForm.temperature" :min="0" :max="2" :step="0.1" show-input />
        </el-form-item>
        <el-form-item label="Top P" prop="top_p">
          <el-slider v-model="configForm.top_p" :min="0" :max="1" :step="0.05" show-input />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="configForm.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import api from '@/api';

const loading = ref(false);
const submitLoading = ref(false);
const showAddDialog = ref(false);
const editingConfig = ref(null);
const llmConfigs = ref([]);
const configFormRef = ref(null);

const configForm = reactive({
  provider: 'custom',
  model_name: '',
  api_key: '',
  base_url: '',
  max_tokens: 4096,
  temperature: 0.7,
  top_p: 0.9,
  is_default: false
});

const rules = {
  provider: [{ required: true, message: '请选择提供商', trigger: 'change' }],
  model_name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  base_url: [{ required: true, message: '请输入 API 地址', trigger: 'blur' }]
};

async function loadLlmConfigs() {
  loading.value = true;
  try {
    llmConfigs.value = await api.get('/llm/configs');
  } catch (error) {
    ElMessage.error('加载 LLM 配置列表失败');
  } finally {
    loading.value = false;
  }
}

async function handleSubmit() {
  if (!configFormRef.value) return;
  
  await configFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true;
      try {
        if (editingConfig.value) {
          await api.put(`/llm/configs/${editingConfig.value.id}`, configForm);
          ElMessage.success('更新成功');
        } else {
          await api.post('/llm/configs', configForm);
          ElMessage.success('添加成功');
        }
        showAddDialog.value = false;
        await loadLlmConfigs();
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '操作失败');
      } finally {
        submitLoading.value = false;
      }
    }
  });
}

function handleEdit(config) {
  editingConfig.value = config;
  configForm.provider = config.provider;
  configForm.model_name = config.model_name;
  configForm.api_key = config.api_key || '';
  configForm.base_url = config.base_url;
  configForm.max_tokens = config.max_tokens;
  configForm.temperature = config.temperature;
  configForm.top_p = config.top_p;
  configForm.is_default = config.is_default;
  showAddDialog.value = true;
}

async function handleDelete(config) {
  try {
    await ElMessageBox.confirm('确定要删除这个配置吗？', '提示', {
      type: 'warning'
    });
    await api.delete(`/llm/configs/${config.id}`);
    ElMessage.success('删除成功');
    await loadLlmConfigs();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
    }
  }
}

onMounted(() => {
  loadLlmConfigs();
});
</script>

<style scoped>
.config-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
