<template>
  <div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
      <div>
        <label class="text-sm text-dark-400 block mb-1.5">收货人姓名 <span class="text-red-500">*</span></label>
        <input v-model="form.recipient_name" placeholder="请输入收货人姓名"
          class="w-full bg-dark-800 text-dark-200 border rounded-lg px-4 py-2.5 text-sm focus:border-primary-500 outline-none"
          :class="errors.recipient_name ? 'border-red-500' : 'border-dark-700'" />
        <p v-if="errors.recipient_name" class="text-red-400 text-xs mt-1">{{ errors.recipient_name }}</p>
      </div>
      <div>
        <label class="text-sm text-dark-400 block mb-1.5">手机号码 <span class="text-red-500">*</span></label>
        <input v-model="form.phone" placeholder="11位手机号" maxlength="11"
          class="w-full bg-dark-800 text-dark-200 border rounded-lg px-4 py-2.5 text-sm focus:border-primary-500 outline-none"
          :class="errors.phone ? 'border-red-500' : 'border-dark-700'" />
        <p v-if="errors.phone" class="text-red-400 text-xs mt-1">{{ errors.phone }}</p>
      </div>
    </div>

    <!-- 省市区三级联动 -->
    <div class="grid grid-cols-3 gap-3 mb-4">
      <div>
        <label class="text-sm text-dark-400 block mb-1.5">省份 <span class="text-red-500">*</span></label>
        <select v-model="form.province" @change="onProvinceChange"
          class="w-full bg-dark-800 text-dark-200 border rounded-lg px-3 py-2.5 text-sm focus:border-primary-500 outline-none"
          :class="errors.province ? 'border-red-500' : 'border-dark-700'">
          <option value="">选择省份</option>
          <option v-for="p in provinces" :key="p" :value="p">{{ p }}</option>
        </select>
        <p v-if="errors.province" class="text-red-400 text-xs mt-1">{{ errors.province }}</p>
      </div>
      <div>
        <label class="text-sm text-dark-400 block mb-1.5">城市 <span class="text-red-500">*</span></label>
        <select v-model="form.city" @change="onCityChange" :disabled="!form.province"
          class="w-full bg-dark-800 text-dark-200 border rounded-lg px-3 py-2.5 text-sm focus:border-primary-500 outline-none disabled:opacity-50"
          :class="errors.city ? 'border-red-500' : 'border-dark-700'">
          <option value="">选择城市</option>
          <option v-for="c in cities" :key="c" :value="c">{{ c }}</option>
        </select>
        <p v-if="errors.city" class="text-red-400 text-xs mt-1">{{ errors.city }}</p>
      </div>
      <div>
        <label class="text-sm text-dark-400 block mb-1.5">区县</label>
        <select v-model="form.district" :disabled="!form.city"
          class="w-full bg-dark-800 text-dark-200 border border-dark-700 rounded-lg px-3 py-2.5 text-sm focus:border-primary-500 outline-none disabled:opacity-50">
          <option value="">选择区县</option>
          <option v-for="d in districts" :key="d" :value="d">{{ d }}</option>
        </select>
      </div>
    </div>

    <div class="mb-4">
      <label class="text-sm text-dark-400 block mb-1.5">详细地址 <span class="text-red-500">*</span></label>
      <input v-model="form.address" placeholder="街道、门牌号等详细地址"
        class="w-full bg-dark-800 text-dark-200 border rounded-lg px-4 py-2.5 text-sm focus:border-primary-500 outline-none"
        :class="errors.address ? 'border-red-500' : 'border-dark-700'" />
      <p v-if="errors.address" class="text-red-400 text-xs mt-1">{{ errors.address }}</p>
    </div>

    <div class="mb-4">
      <label class="text-sm text-dark-400 block mb-1.5">邮编（可选）</label>
      <input v-model="form.postal_code" placeholder="邮政编码" maxlength="6"
        class="w-full bg-dark-800 text-dark-200 border border-dark-700 rounded-lg px-4 py-2.5 text-sm focus:border-primary-500 outline-none" />
    </div>

    <label class="flex items-center gap-2 mb-4 cursor-pointer">
      <input type="checkbox" v-model="form.is_default" class="accent-primary-500" />
      <span class="text-sm text-dark-400">设为默认地址</span>
    </label>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { getProvinces, getCities, getDistricts } from '@/data/regions'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      recipient_name: '',
      phone: '',
      province: '',
      city: '',
      district: '',
      address: '',
      postal_code: '',
      is_default: false,
    })
  },
  errors: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const form = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const provinces = getProvinces()

const cities = computed(() => {
  if (!form.value.province) return []
  return getCities(form.value.province)
})

const districts = computed(() => {
  if (!form.value.province || !form.value.city) return []
  return getDistricts(form.value.province, form.value.city)
})

// 省份变化时清空城市和区县
function onProvinceChange() {
  form.value.city = ''
  form.value.district = ''
}

// 城市变化时清空区县
function onCityChange() {
  form.value.district = ''
}

// 验证表单
function validate() {
  const errs = {}
  if (!form.value.recipient_name?.trim()) errs.recipient_name = '请输入收货人姓名'
  if (!form.value.phone?.trim()) errs.phone = '请输入手机号码'
  else if (!/^1\d{10}$/.test(form.value.phone)) errs.phone = '手机号格式不正确'
  if (!form.value.province) errs.province = '请选择省份'
  if (!form.value.city) errs.city = '请选择城市'
  if (!form.value.address?.trim()) errs.address = '请输入详细地址'
  return errs
}

defineExpose({ validate })
</script>
