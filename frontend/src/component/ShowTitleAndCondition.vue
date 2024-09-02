
<template>
  <!-- 右上角标题 -->
  <div class="d-flex align-items-center">
    <h2 class="text-info">{{ title }}</h2>
    <span class="ms-2 text-secondary">(一共{{ totalAnime }}部动画)</span>
  </div>
</template>

<script setup>
import {defineProps} from "vue";

const props = defineProps({
  title: String,
  totalAnime: Number
})
</script>