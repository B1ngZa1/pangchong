<template>
  <footer class="border-t border-dark-800 bg-dark-900">
    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div class="grid gap-8 md:grid-cols-4">
        <div>
          <div class="mb-4 flex items-center gap-3">
            <span class="inline-flex h-7 w-7 items-center justify-center rounded-md border border-primary-500/60 bg-primary-500/10">
              <span class="h-3 w-3 rounded-sm bg-primary-500" />
            </span>
            <span class="text-lg font-semibold tracking-[0.12em] text-white">PANGCHONG</span>
          </div>
          <p class="mb-4 text-sm leading-6 text-dark-400">
            极致性能，由你定义。<br>
            胖虫科技专注高性能整机与 DIY 定制服务。
          </p>
          <div class="flex gap-4 text-sm text-dark-400">
            <a href="https://v.douyin.com/hYq_ldkfZQ4/" target="_blank" rel="noopener" class="transition-colors hover:text-primary-500">抖音</a>
            <a href="https://mall.jd.com/index-1000651190.html" target="_blank" rel="noopener" class="transition-colors hover:text-primary-500">京东</a>
            <a href="https://www.bilibili.com" target="_blank" rel="noopener" class="transition-colors hover:text-primary-500">Bilibili</a>
          </div>
        </div>

        <div>
          <h3 class="mb-4 text-sm font-semibold text-white">产品</h3>
          <ul class="space-y-2 text-sm text-dark-400">
            <li><router-link to="/products" class="transition-colors hover:text-white">全部产品</router-link></li>
            <li><router-link to="/diy" class="transition-colors hover:text-white">DIY 装机</router-link></li>
            <li><router-link to="/cart" class="transition-colors hover:text-white">购物车</router-link></li>
          </ul>
        </div>

        <div>
          <h3 class="mb-4 text-sm font-semibold text-white">服务</h3>
          <ul class="space-y-2 text-sm text-dark-400">
            <li><router-link to="/store" class="transition-colors hover:text-white">武汉线下门店</router-link></li>
            <li><router-link to="/services#tech-support" class="transition-colors hover:text-white">技术支持</router-link></li>
            <li><router-link to="/services#warranty" class="transition-colors hover:text-white">保修政策</router-link></li>
            <li><router-link to="/services#delivery" class="transition-colors hover:text-white">配送说明</router-link></li>
            <li><router-link to="/services#faq" class="transition-colors hover:text-white">常见问题</router-link></li>
          </ul>
        </div>

        <div>
          <h3 class="mb-4 text-sm font-semibold text-white">联系我们</h3>
          <ul class="space-y-2 text-sm text-dark-400">
            <li>客服邮箱：support@pangchong.com</li>
            <li>服务时间：周一至周六 09:00-21:00</li>
            <li>门店地址：武汉市武昌区江盛路19号3号楼2楼</li>
          </ul>
        </div>
      </div>

      <div class="mt-8 flex flex-col items-start justify-between gap-3 border-t border-dark-800 pt-6 text-xs text-dark-500 md:flex-row md:items-center">
        <p>© {{ new Date().getFullYear() }} PANGCHONG. All rights reserved.</p>
        <div class="flex flex-wrap gap-6">
          <router-link to="/services#privacy" class="transition-colors hover:text-white">隐私政策</router-link>
          <router-link to="/services#user-agreement" class="transition-colors hover:text-white">用户协议</router-link>
          <router-link to="/services#cookie-settings" class="transition-colors hover:text-white">Cookie 设置</router-link>
        </div>
      </div>
    </div>
  </footer>
</template>
