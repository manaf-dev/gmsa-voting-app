<script setup lang="ts">
const props = defineProps<{
  modelValue?: string
  placeholder?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const onInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <textarea
    rows="3"
    class="py-2 px-4 mt-1 rounded-lg border-2 border-gray-300 focus:border-green-500 outline-none w-full resize-none mb-4"
    :value="props.modelValue"
    @input="onInput"
    :placeholder="props.placeholder"
  ></textarea>
</template>
