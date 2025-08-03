<!-- components/BaseNavbar.vue -->
<script setup lang="ts">
defineEmits<{
  (e: 'back'): void
}>()
</script>

<template>
  <nav class="bg-white border-b border-gray-200 fixed top-0 w-full">
    <div
      class="max-w-6xl mx-auto w-full flex items-center justify-between px-4 lg:px-8 py-3 sm:py-5"
    >
      <div class="flex items-center gap-2">
        <slot name="left" />
      </div>

      <div class="flex items-center">
        <slot name="center" />
      </div>

      <div class="flex items-center gap-2">
        <slot name="right" />
      </div>
    </div>
  </nav>
</template>
