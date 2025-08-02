<script setup lang="ts">
defineOptions({
  inheritAttrs: false,
})
</script>

<template>
  <button v-bind="$attrs" class="cursor-pointer">
    <slot />
  </button>
</template>
