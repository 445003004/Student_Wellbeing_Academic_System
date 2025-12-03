<script setup>
// 在 Vue 3 中使用 script setup 语法糖
// RouterView 是 vue-router 提供的组件，用于渲染匹配到的页面
import { RouterView } from 'vue-router'
</script>

<template>
  <!-- 所有的页面（Login, AcademicDashboard, WellbeingDashboard）都会渲染在这里 -->
  <router-view />
</template>

<style>
/* --- 全局样式 (Global Styles) --- */

/* 1. 重置浏览器默认样式，确保全屏显示 */
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  font-family: 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  background-color: #f0f2f5; /* 统一的浅灰背景色 */
  color: #2c3e50; /* 统一的字体颜色 */
  -webkit-font-smoothing: antialiased; /* 字体抗锯齿优化 */
  -moz-osx-font-smoothing: grayscale;
}

/* 2. 让 Vue 的挂载点也撑满全屏 */
#app {
  width: 100%;
  height: 100%;
}

/* 3. 设置全局盒模型，防止 padding 撑破布局 */
*, *::before, *::after {
  box-sizing: border-box;
}

/* 4. 全局链接和按钮样式 */
a {
  text-decoration: none;
  color: inherit;
}

button {
  font-family: inherit;
}
</style>
<!--<template>-->
<!--  <nav>-->
<!--    <router-link to="/">Home</router-link> |-->
<!--    <router-link to="/about">About</router-link>-->
<!--  </nav>-->
<!--  <router-view/>-->
<!--</template>-->

<!--<style>-->
<!--#app {-->
<!--  font-family: Avenir, Helvetica, Arial, sans-serif;-->
<!--  -webkit-font-smoothing: antialiased;-->
<!--  -moz-osx-font-smoothing: grayscale;-->
<!--  text-align: center;-->
<!--  color: #2c3e50;-->
<!--}-->

<!--nav {-->
<!--  padding: 30px;-->
<!--}-->

<!--nav a {-->
<!--  font-weight: bold;-->
<!--  color: #2c3e50;-->
<!--}-->

<!--nav a.router-link-exact-active {-->
<!--  color: #42b983;-->
<!--}-->
<!--</style>-->
