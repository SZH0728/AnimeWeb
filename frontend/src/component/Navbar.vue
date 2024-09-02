<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light-blue">
    <div class="container-fluid">

      <a class="navbar-brand text-white" href="#">AnimeScrapy</a>

      <button class="navbar-toggler"
              style="margin-bottom: 10px"
              type="button" data-bs-toggle="collapse"
              data-bs-target="#navbarNavDropdown"
              aria-controls="navbarNavDropdown"
              aria-expanded="false"
              aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNavDropdown">

        <!-- 小屏搜索框 -->
        <form class="d-flex d-lg-none mb-2" @submit.prevent="search">
          <input
              v-model="searchTerm"
              class="form-control me-2"
              type="search"
              placeholder="搜索"
              aria-label="Search"
              @keyup.enter="search"
          >
          <button class="btn btn-outline-success" type="submit">搜索</button>
        </form>

        <!-- 目录列表 -->
        <ul class="navbar-nav d-lg-flex">
          <li class="nav-item">
            <router-link class="nav-link text-white" to="/">首页</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link text-white" to="/list">排名</router-link>
          </li>
          <!-- 更多链接 -->
        </ul>

        <!-- 大屏搜索框 -->
        <form class="d-none d-lg-flex ms-auto"  @submit.prevent="search">
          <input
              v-model="searchTerm"
              class="form-control me-2"
              type="search"
              placeholder="搜索"
              aria-label="Search"
              @keyup.enter="search"
          >
          <button class="btn btn-outline-success" type="submit">搜索</button>
        </form>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const searchTerm = ref('');
const router = useRouter();

function search() {
  if (searchTerm.value.trim()) {
    router.push(`/search/${searchTerm.value.trim()}`);
    searchTerm.value = searchTerm.value.trim();
  }
}
</script>

<style scoped>
.bg-light-blue {
  background-color: #61cee7;
}

.navbar {
  color: white;
}

.navbar-brand {
  font-weight: bold;
  color: white;
}

.nav-link {
  color: white !important;
  border-radius: 4px;
  padding: 10px 15px;
}

.nav-link:hover {
  background-color: #0056b3;
  border-radius: 4px;
}

.btn.btn-outline-success {
  min-width: fit-content; /* 最小宽度为内容宽度 */
  max-width: 100%; /* 最大宽度为 100% */
  padding: 0.375rem 0.75rem; /* 保持默认内边距 */
}

/* 小屏设备上的样式 */
@media (max-width: 992px) {
  .navbar-nav {
    flex-direction: column;
    align-items: flex-start;
    display: block;
    width: 100%;
  }

  .navbar-nav .nav-link {
    margin-bottom: 10px;
    width: 100%;
  }

  .navbar-nav .nav-link:last-child {
    margin-bottom: 0;
  }
}

/* 大屏设备上的样式 */
@media (min-width: 993px) {
  .navbar-nav {
    flex-direction: row;
    align-items: center;
  }

  .navbar-nav .nav-link {
    margin-right: 10px;
  }

  .navbar-nav .nav-link:last-child {
    margin-right: 0;
  }
}
</style>
