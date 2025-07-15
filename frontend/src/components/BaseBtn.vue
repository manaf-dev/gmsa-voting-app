<script setup lang="ts">
defineOptions({
  inheritAttrs: false,
})
</script>

<template>
  <button v-bind="$attrs">
    <slot></slot>
  </button>
</template>
