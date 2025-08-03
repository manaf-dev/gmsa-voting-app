<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

const props = defineProps<{
  type: string
  placeholder?: string
  required?: boolean
  modelValue?: any
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const updateValue = (e: Event) => {
  const target = e.target as HTMLInputElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <input
    :type="props.type"
    :placeholder="props.placeholder"
    :required="props.required"
    :value="props.modelValue"
    @input="updateValue"
    class="py-2 px-4 mt-1 mb-4 rounded-lg border-2 border-gray-300 focus:border-green-500 outline-none w-full"
  />
</template>
