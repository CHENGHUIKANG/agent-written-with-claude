<template>
  <div class="mcp-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>MCP 服务器配置</span>
          <el-button type="primary" @click="showAddDialog = true">添加服务器</el-button>
        </div>
      </template>
      
      <el-table :data="mcpServers" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="server_type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.server_type === 'stdio' ? 'success' : 'primary'">
              {{ row.server_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'connected' ? 'success' : 'danger'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="handleTest(row)">测试</el-button>
            <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" :title="editingServer ? '编辑服务器' : '添加服务器'" width="600px">
      <el-form :model="serverForm" :rules="rules" ref="serverFormRef" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="serverForm.name" placeholder="请输入服务器名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="serverForm.description" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="类型" prop="server_type">
          <el-select v-model="serverForm.server_type" placeholder="请选择类型" style="width: 100%">
            <el-option label="STDIO" value="stdio" />
            <el-option label="STREAMABLE_HTTP" value="streamable_http" />
          </el-select>
        </el-form-item>
        <el-form-item label="连接参数" prop="connection_params">
          <el-input
            v-model="connectionParamsJson"
            type="textarea"
            :rows="4"
            placeholder='{"url": "https://example.com/mcp", "key": "xxx"}'
          />
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
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import api from '@/api';

const loading = ref(false);
const submitLoading = ref(false);
const showAddDialog = ref(false);
const editingServer = ref(null);
const mcpServers = ref([]);
const serverFormRef = ref(null);

const serverForm = reactive({
  name: '',
  description: '',
  server_type: 'streamable_http',
  connection_params: {}
});

const connectionParamsJson = computed({
  get: () => JSON.stringify(serverForm.connection_params, null, 2),
  set: (value) => {
    try {
      serverForm.connection_params = JSON.parse(value);
    } catch (e) {
      ElMessage.error('JSON 格式错误');
    }
  }
});

const rules = {
  name: [{ required: true, message: '请输入服务器名称', trigger: 'blur' }],
  server_type: [{ required: true, message: '请选择服务器类型', trigger: 'change' }],
  connection_params: [{ required: true, message: '请输入连接参数', trigger: 'blur' }]
};

async function loadMcpServers() {
  loading.value = true;
  try {
    mcpServers.value = await api.get('/mcp/servers');
  } catch (error) {
    ElMessage.error('加载 MCP 服务器列表失败');
  } finally {
    loading.value = false;
  }
}

async function handleSubmit() {
  if (!serverFormRef.value) return;
  
  await serverFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true;
      try {
        if (editingServer.value) {
          await api.put(`/mcp/servers/${editingServer.value.id}`, serverForm);
          ElMessage.success('更新成功');
        } else {
          await api.post('/mcp/servers', serverForm);
          ElMessage.success('添加成功');
        }
        showAddDialog.value = false;
        await loadMcpServers();
      } catch (error) {
        ElMessage.error(error.response?.data?.detail || '操作失败');
      } finally {
        submitLoading.value = false;
      }
    }
  });
}

function handleEdit(server) {
  editingServer.value = server;
  serverForm.name = server.name;
  serverForm.description = server.description;
  serverForm.server_type = server.server_type;
  serverForm.connection_params = server.connection_params;
  showAddDialog.value = true;
}

async function handleDelete(server) {
  try {
    await ElMessageBox.confirm('确定要删除这个服务器吗？', '提示', {
      type: 'warning'
    });
    await api.delete(`/mcp/servers/${server.id}`);
    ElMessage.success('删除成功');
    await loadMcpServers();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
    }
  }
}

async function handleTest(server) {
  try {
    const result = await api.post(`/mcp/servers/${server.id}/test`);
    ElMessage.success(`测试成功: ${result.message || '连接正常'}`);
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '测试失败');
  }
}

onMounted(() => {
  loadMcpServers();
});
</script>

<style scoped>
.mcp-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
