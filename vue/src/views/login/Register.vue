<template>
  <div class="register-page" data-scope="front">
    <div class="register-card">
      <h1>注册账号</h1>
      <el-form @submit.prevent>
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码（≥6 位）" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <div class="captcha-row">
            <el-input v-model="form.captchaCode" placeholder="验证码" size="large" />
            <img :src="captchaImage" alt="验证码" class="captcha-img" @click="refreshCaptcha" />
          </div>
        </el-form-item>
        <el-button type="primary" size="large" class="submit" :loading="loading" @click="handleRegister">
          注册
        </el-button>
        <el-button link @click="$router.push('/login')">已有账号？登录</el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../store/user'
import { getCaptcha, register } from '../../api/auth'

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

async function handleRegister() {
  loading.value = true
  try {
    const data = await register(form.value)
    userStore.token = data.token
    userStore.userInfo = data.user
    router.push('/user/home')
  } finally {
    loading.value = false
  }
}

onMounted(refreshCaptcha)
</script>

<style scoped>
.register-page { display: flex; align-items: center; justify-content: center; min-height: 100%; background: var(--bg); }
.register-card { width: 360px; max-width: 90vw; background: var(--surface); padding: var(--sp-card-lg); border-radius: var(--r-card-lg); box-shadow: var(--shadow-card); }
h1 { font-family: var(--font-serif); font-size: var(--fs-h1); text-align: center; margin: 0 0 var(--sp-section); color: var(--ink); }
.captcha-row { display: flex; gap: var(--sp-card-gap); width: 100%; }
.captcha-img { height: 44px; width: 120px; border-radius: var(--r-card); cursor: pointer; border: 1px solid var(--line); }
.submit { width: 100%; }
</style>
