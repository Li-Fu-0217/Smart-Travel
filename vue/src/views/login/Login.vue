<template>
  <div class="login-page" data-scope="front">
    <div class="login-card">
      <h1>智慧旅游智能助手</h1>
      <el-form @submit.prevent>
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <div class="captcha-row">
            <el-input v-model="form.captchaCode" placeholder="验证码" size="large" />
            <img :src="captchaImage" alt="验证码" class="captcha-img" @click="refreshCaptcha" />
          </div>
        </el-form-item>
        <el-button type="primary" size="large" class="submit" :loading="loading" @click="handleLogin">
          登录
        </el-button>
        <el-button link @click="$router.push('/register')">没有账号？注册</el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../store/user'
import { getCaptcha } from '../../api/auth'

const router = useRouter()
const userStore = useUserStore()
const form = ref({ username: '', password: '', captchaId: '', captchaCode: '' })
const captchaImage = ref('')
const loading = ref(false)

async function refreshCaptcha() {
  const data = await getCaptcha()
  form.value.captchaId = data.captchaId
  captchaImage.value = data.image
}

async function handleLogin() {
  loading.value = true
  try {
    const user = await userStore.login(form.value)
    router.push(user.role === 'ADMIN' ? '/admin/dashboard' : '/user/home')
  } finally {
    loading.value = false
  }
}

onMounted(refreshCaptcha)
</script>

<style scoped>
.login-page { display: flex; align-items: center; justify-content: center; min-height: 100%; background: var(--bg); }
.login-card { width: 360px; max-width: 90vw; background: var(--surface); padding: var(--sp-card-lg); border-radius: var(--r-card-lg); box-shadow: var(--shadow-card); }
h1 { font-family: var(--font-serif); font-size: var(--fs-h1); text-align: center; margin: 0 0 var(--sp-section); color: var(--ink); }
.captcha-row { display: flex; gap: var(--sp-card-gap); width: 100%; }
.captcha-img { height: 44px; width: 120px; border-radius: var(--r-card); cursor: pointer; border: 1px solid var(--line); }
.submit { width: 100%; }
</style>
