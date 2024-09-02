<template>
  <div v-if="loading" class="alert alert-info d-flex w-100">
    <strong>正在加载...</strong>
  </div>
  <div v-if="errorMessage.length !== 0" class="alert alert-danger d-flex w-100">
    <strong>错误!</strong> 访问数据失败: {{ errorMessage }}
  </div>
</template>

<script setup>
import {defineProps} from "vue";

defineProps({
  loading: Boolean,
  errorMessage: String
})
</script>