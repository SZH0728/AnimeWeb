<script setup lang="ts">
import { ref, watch } from 'vue';

const props = withDefaults(
  defineProps<{
    modelValue: number;
    id?: string;
    disabled?: boolean;
  }>(),
  {
    id: 'min-total',
    disabled: false,
  },
);

const emit = defineEmits<{
  'min-total-changed': [value: number];
}>();

const inputValue = ref(String(props.modelValue));
const errorMessage = ref('');

watch(
  () => props.modelValue,
  (value) => {
    inputValue.value = String(value);
    errorMessage.value = '';
  },
);

function handleSubmit(): void {
  if (!/^\d+$/.test(inputValue.value)) {
    errorMessage.value = '请输入大于或等于 0 的整数。';
    return;
  }

  const value = Number(inputValue.value);
  if (!Number.isSafeInteger(value) || value < 0) {
    errorMessage.value = '请输入大于或等于 0 的整数。';
    return;
  }

  errorMessage.value = '';
  emit('min-total-changed', value);
}
</script>

<template>
  <form
    class="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:items-end"
    @submit.prevent="handleSubmit"
  >
    <div class="flex min-w-0 flex-1 flex-col gap-1">
      <label class="text-sm font-medium" :for="id">最低评价人数</label>
      <input
        :id="id"
        v-model="inputValue"
        :aria-describedby="errorMessage ? `${id}-error` : undefined"
        :aria-invalid="Boolean(errorMessage)"
        :disabled="disabled"
        class="input w-full"
        inputmode="numeric"
        min="0"
        name="min-total"
        step="1"
        type="number"
      />
      <p v-if="errorMessage" :id="`${id}-error`" class="text-error text-sm" role="alert">
        {{ errorMessage }}
      </p>
    </div>
    <button class="btn" :disabled="disabled" type="submit">应用</button>
  </form>
</template>
