<template>
  <div>
    <div class="grid grid-cols-1 gap-4 mb-4 sm:grid-cols-2">
      <DsField
        v-model="form.recipient_name"
        label="收货人姓名"
        name="recipient_name"
        autocomplete="name"
        placeholder="请输入收货人姓名"
        required
        :error="errors.recipient_name"
      />
      <DsField
        v-model="form.phone"
        label="手机号码"
        name="phone"
        type="tel"
        maxlength="11"
        inputmode="tel"
        autocomplete="tel"
        placeholder="11位手机号"
        required
        :error="errors.phone"
      />
    </div>

    <div class="grid grid-cols-3 gap-3 mb-4">
      <DsField
        v-model="form.province"
        as="select"
        label="省份"
        name="province"
        autocomplete="address-level1"
        :options="provinces"
        placeholder="选择省份"
        required
        :error="errors.province"
        @change="onProvinceChange"
      />
      <DsField
        v-model="form.city"
        as="select"
        label="城市"
        name="city"
        autocomplete="address-level2"
        :options="cities"
        placeholder="选择城市"
        required
        :disabled="!form.province"
        :error="errors.city"
        @change="onCityChange"
      />
      <DsField
        v-model="form.district"
        as="select"
        label="区县"
        name="district"
        autocomplete="address-level3"
        :options="districts"
        placeholder="选择区县"
        :disabled="!form.city"
      />
    </div>

    <DsField
      v-model="form.address"
      class="mb-4"
      label="详细地址"
      name="address"
      autocomplete="street-address"
      placeholder="街道、门牌号等详细地址"
      required
      :error="errors.address"
    />

    <DsField
      v-model="form.postal_code"
      class="mb-4"
      label="邮编（可选）"
      name="postal_code"
      type="text"
      maxlength="6"
      inputmode="numeric"
      autocomplete="postal-code"
      placeholder="邮政编码"
    />

    <label class="flex items-center gap-2 mb-4 cursor-pointer">
      <input v-model="form.is_default" type="checkbox" class="accent-primary-500" />
      <span class="text-sm text-dark-400">设为默认地址</span>
    </label>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getProvinces, getCities, getDistricts } from '@/data/regions'
import { DsField } from '@/design-system'

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
    }),
  },
  errors: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:modelValue'])

const form = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const provinces = getProvinces()
const cities = computed(() => form.value.province ? getCities(form.value.province) : [])
const districts = computed(() => form.value.province && form.value.city ? getDistricts(form.value.province, form.value.city) : [])

function onProvinceChange() {
  form.value.city = ''
  form.value.district = ''
}

function onCityChange() {
  form.value.district = ''
}

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
