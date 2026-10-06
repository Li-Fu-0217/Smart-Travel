<template>
  <div class="page">
    <el-tabs v-model="tab">
      <el-tab-pane label="预约订单" name="orders">
        <div class="toolbar">
          <el-select v-model="orderStatus" class="status" placeholder="全部状态" clearable @change="loadOrders">
            <el-option label="待确认" value="pending" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="已完成" value="done" />
          </el-select>
          <el-button type="primary" @click="loadOrders">刷新</el-button>
        </div>
        <div class="table-wrap">
          <el-table :data="orders" v-loading="loading">
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="catalogName" label="项目" width="140" />
            <el-table-column prop="travelerId" label="旅行者ID" width="90" />
            <el-table-column prop="slot" label="时段" width="150" />
            <el-table-column prop="guestCount" label="人数" width="70" />
            <el-table-column label="状态" width="90">
              <template #default="{ row }"><StatusBadge type="booking" :value="row.status" /></template>
            </el-table-column>
            <el-table-column label="操作" width="170">
              <template #default="{ row }">
                <el-button v-if="row.status === 'pending'" link type="primary" @click="changeOrder(row, 'confirmed')">确认</el-button>
                <el-button v-if="row.status === 'confirmed'" link type="success" @click="changeOrder(row, 'done')">完成</el-button>
                <el-button v-if="row.status === 'pending' || row.status === 'confirmed'" link type="danger" @click="changeOrder(row, 'cancelled')">取消</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div class="pager">
          <el-pagination v-model:current-page="orderCurrent" v-model:page-size="size" :total="orderTotal" layout="total, prev, pager, next" @current-change="loadOrders" />
        </div>
      </el-tab-pane>

      <el-tab-pane label="可预约项目" name="catalog">
        <div class="toolbar">
          <el-button type="primary" @click="openCatalogCreate">新增项目</el-button>
        </div>
        <div class="table-wrap">
          <el-table :data="catalogs" v-loading="loading">
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="name" label="名称" />
            <el-table-column label="类型" width="100">
              <template #default="{ row }">{{ ITEM_TYPE[row.itemType] || row.itemType }}</template>
            </el-table-column>
            <el-table-column prop="durationMinutes" label="时长(分)" width="100" />
            <el-table-column prop="price" label="价格" width="100" />
            <el-table-column label="状态" width="90">
              <template #default="{ row }"><StatusBadge type="catalog" :value="row.status" /></template>
            </el-table-column>
            <el-table-column label="操作" width="140">
              <template #default="{ row }">
                <el-button link type="primary" @click="openCatalogEdit(row)">编辑</el-button>
                <el-button link type="danger" @click="confirmCatalogDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="catalogDialog.visible" :title="catalogDialog.id ? '编辑项目' : '新增项目'" width="440px">
      <el-form label-width="90px">
        <el-form-item label="名称"><el-input v-model="catalogDialog.form.name" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="catalogDialog.form.itemType">
            <el-option v-for="(label, val) in ITEM_TYPE" :key="val" :label="label" :value="val" />
          </el-select>
        </el-form-item>
        <el-form-item label="时长(分)"><el-input-number v-model="catalogDialog.form.durationMinutes" :min="0" /></el-form-item>
        <el-form-item label="价格"><el-input-number v-model="catalogDialog.form.price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="catalogDialog.form.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="catalogDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="saveCatalog">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminOrders, updateAdminOrder, getAdminCatalog, createAdminCatalog, updateAdminCatalog, deleteAdminCatalog } from '../../api/booking'
import StatusBadge from '../../components/StatusBadge.vue'

const ITEM_TYPE = { guide: '导游', homestay: '民宿', experience: '当地体验', ticket: '门票' }
const tab = ref('orders')
const loading = ref(false)
const size = ref(10)

const orders = ref([])
const orderTotal = ref(0)
const orderCurrent = ref(1)
const orderStatus = ref('')

const catalogs = ref([])
const catalogDialog = reactive({ visible: false, id: null, form: { name: '', itemType: 'guide', durationMinutes: null, price: null, description: '' } })

async function loadOrders() {
  loading.value = true
  try {
    const data = await getAdminOrders({ current: orderCurrent.value, size: size.value, status: orderStatus.value || undefined })
    orders.value = data.records
    orderTotal.value = data.total
  } finally {
    loading.value = false
  }
}

async function loadCatalogs() {
  loading.value = true
  try {
    const data = await getAdminCatalog({ current: 1, size: 100 })
    catalogs.value = data.records
  } finally {
    loading.value = false
  }
}

async function changeOrder(row, next) {
  try { await ElMessageBox.confirm(`确认将订单 ${row.id} 置为「${next}」？`, '提示', { type: 'warning' }) } catch { return }
  await updateAdminOrder(row.id, { status: next, version: row.version })
  ElMessage.success('已更新')
  loadOrders()
}

function openCatalogCreate() {
  catalogDialog.id = null
  catalogDialog.form = { name: '', itemType: 'guide', durationMinutes: null, price: null, description: '' }
  catalogDialog.visible = true
}

function openCatalogEdit(row) {
  catalogDialog.id = row.id
  catalogDialog.form = { name: row.name, itemType: row.itemType, durationMinutes: row.durationMinutes, price: row.price, description: row.description }
  catalogDialog.visible = true
}

async function saveCatalog() {
  if (catalogDialog.id) await updateAdminCatalog(catalogDialog.id, catalogDialog.form)
  else await createAdminCatalog(catalogDialog.form)
  catalogDialog.visible = false
  ElMessage.success('已保存')
  loadCatalogs()
}

async function confirmCatalogDelete(row) {
  try { await ElMessageBox.confirm(`确认删除项目「${row.name}」？`, '提示', { type: 'warning' }) } catch { return }
  await deleteAdminCatalog(row.id)
  ElMessage.success('已删除')
  loadCatalogs()
}

onMounted(() => { loadOrders(); loadCatalogs() })
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.toolbar { display: flex; gap: var(--sp-card-gap); align-items: center; }
.status { width: 160px; }
.table-wrap { overflow-x: auto; }
.pager { display: flex; justify-content: flex-end; }
</style>
