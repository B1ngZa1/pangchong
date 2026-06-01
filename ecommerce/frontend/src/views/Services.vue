<template>
  <div class="service-page">
    <section class="service-hero">
      <div class="service-shell service-hero__grid">
        <div class="service-hero__copy">
          <p class="service-kicker">PANGCHONG SERVICE DESK</p>
          <h1>服务协议中心</h1>
          <p>
            将技术支持、保修政策、配送说明、常见问题、隐私政策、用户协议和 Cookie 设置集中说明，
            让购买前后的关键规则更清楚、更容易查找。
          </p>
          <div class="service-hero__actions">
            <a href="#tech-support">查看服务内容</a>
            <a href="#cookie-settings">管理 Cookie</a>
          </div>
        </div>

        <div class="service-brief" aria-label="service summary">
          <div v-for="item in serviceSummary" :key="item.label" class="service-brief__item">
            <span>{{ item.value }}</span>
            <p>{{ item.label }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="service-shell service-layout">
      <aside class="service-nav" aria-label="service navigation">
        <a
          v-for="section in navSections"
          :key="section.id"
          :href="`#${section.id}`"
        >
          <span>{{ section.index }}</span>
          {{ section.title }}
        </a>
      </aside>

      <div class="service-content">
        <article
          v-for="section in policySections"
          :id="section.id"
          :key="section.id"
          class="policy-block"
        >
          <div class="policy-block__head">
            <span>{{ section.index }}</span>
            <div>
              <p>{{ section.eyebrow }}</p>
              <h2>{{ section.title }}</h2>
            </div>
          </div>

          <p class="policy-block__lead">{{ section.lead }}</p>

          <div class="policy-grid">
            <div v-for="point in section.points" :key="point.title" class="policy-point">
              <h3>{{ point.title }}</h3>
              <p>{{ point.body }}</p>
            </div>
          </div>
        </article>

        <article id="faq" class="policy-block">
          <div class="policy-block__head">
            <span>04</span>
            <div>
              <p>SELF SERVICE</p>
              <h2>常见问题</h2>
            </div>
          </div>

          <div class="faq-list">
            <details v-for="faq in faqs" :key="faq.question">
              <summary>{{ faq.question }}</summary>
              <p>{{ faq.answer }}</p>
            </details>
          </div>
        </article>

        <article
          v-for="section in legalSections"
          :id="section.id"
          :key="section.id"
          class="policy-block"
        >
          <div class="policy-block__head">
            <span>{{ section.index }}</span>
            <div>
              <p>{{ section.eyebrow }}</p>
              <h2>{{ section.title }}</h2>
            </div>
          </div>

          <p class="policy-block__lead">{{ section.lead }}</p>

          <div class="policy-grid">
            <div v-for="point in section.points" :key="point.title" class="policy-point">
              <h3>{{ point.title }}</h3>
              <p>{{ point.body }}</p>
            </div>
          </div>
        </article>

        <article id="cookie-settings" class="policy-block cookie-panel">
          <div class="policy-block__head">
            <span>07</span>
            <div>
              <p>COOKIE CONTROL</p>
              <h2>Cookie 设置</h2>
            </div>
          </div>

          <p class="policy-block__lead">
            Cookie 用于维持登录、保存购物车、记住偏好和分析页面体验。必要 Cookie 是网站基础功能所需，
            其余类型可由用户按需开启或关闭。
          </p>

          <div class="cookie-options">
            <label v-for="option in cookieOptions" :key="option.key" class="cookie-option">
              <span>
                <strong>{{ option.title }}</strong>
                <small>{{ option.description }}</small>
              </span>
              <input
                v-model="cookiePrefs[option.key]"
                type="checkbox"
                :disabled="option.required"
              >
            </label>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const serviceSummary = [
  { value: '7', label: '类服务与协议集中说明' },
  { value: '24h', label: '工作日咨询响应参考' },
  { value: '1v1', label: '订单售后跟进机制' }
]

const navSections = [
  { id: 'tech-support', index: '01', title: '技术支持' },
  { id: 'warranty', index: '02', title: '保修政策' },
  { id: 'delivery', index: '03', title: '配送说明' },
  { id: 'faq', index: '04', title: '常见问题' },
  { id: 'privacy', index: '05', title: '隐私政策' },
  { id: 'user-agreement', index: '06', title: '用户协议' },
  { id: 'cookie-settings', index: '07', title: 'Cookie 设置' }
]

const policySections = [
  {
    id: 'tech-support',
    index: '01',
    eyebrow: 'TECHNICAL SUPPORT',
    title: '技术支持',
    lead: '胖虫科技提供覆盖购买前、装机中与购买后的技术咨询，帮助用户确认配置、排查问题并完成基础调试。',
    points: [
      {
        title: '支持范围',
        body: '包括整机配置建议、硬件兼容性确认、系统与驱动基础指导、性能调校建议、远程故障排查和检测流程说明。'
      },
      {
        title: '响应方式',
        body: '用户可通过在线客服、售后邮箱或订单留言发起咨询；复杂硬件问题会根据检测进度同步处理结果。'
      },
      {
        title: '服务边界',
        body: '不包含第三方软件破解、非授权系统修改、用户自行超频造成的不稳定或非本店销售硬件的责任承担。'
      }
    ]
  },
  {
    id: 'warranty',
    index: '02',
    eyebrow: 'WARRANTY POLICY',
    title: '保修政策',
    lead: '整机与配件保修以商品详情页、订单记录及品牌厂商政策为准，平台提供故障判断、返修协助和进度同步。',
    points: [
      {
        title: '质量问题处理',
        body: '保修期内因产品本身质量问题导致的故障，可根据检测结果进行维修、更换或按平台规则处理。'
      },
      {
        title: '不保修情形',
        body: '人为损坏、进液、摔落、私自拆改、非授权维修、不可抗力及耗材自然损耗不在免费保修范围内。'
      },
      {
        title: '数据提醒',
        body: '寄修前请备份个人数据；涉及硬盘或系统盘检测时，平台不承诺保留本地数据。'
      }
    ]
  },
  {
    id: 'delivery',
    index: '03',
    eyebrow: 'DELIVERY GUIDE',
    title: '配送说明',
    lead: '订单发货会结合库存、定制装机、压力测试和物流覆盖情况安排，发货前进行必要的包装与外观确认。',
    points: [
      {
        title: '发货时效',
        body: '现货商品通常按页面承诺时效发出；定制整机或特殊配置订单会根据配件到货与测试结果安排。'
      },
      {
        title: '物流方式',
        body: '默认使用顺丰、京东物流或平台支持的其他承运商，偏远地区、超大件或保价需求可能产生额外费用。'
      },
      {
        title: '签收检查',
        body: '签收时请检查外包装是否破损、浸湿或变形；如有异常，建议拍照留证并及时联系客服。'
      }
    ]
  }
]

const legalSections = [
  {
    id: 'privacy',
    index: '05',
    eyebrow: 'PRIVACY POLICY',
    title: '隐私政策',
    lead: '平台仅在完成交易、履行合同、提供售后、保障账户安全、改进体验及符合法律法规要求的范围内使用用户信息。',
    points: [
      {
        title: '信息收集',
        body: '注册、登录、下单、支付、配送和售后过程中可能收集账号信息、联系方式、收货地址、订单信息与客服记录。'
      },
      {
        title: '使用原则',
        body: '未经用户同意，不会将个人信息出售给第三方；必要共享仅限交易履约、物流配送、支付结算和合规要求。'
      },
      {
        title: '用户权利',
        body: '用户可依法申请查询、更正、删除个人信息或注销账号；部分订单与支付记录需按法定期限保存。'
      }
    ]
  },
  {
    id: 'user-agreement',
    index: '06',
    eyebrow: 'USER AGREEMENT',
    title: '用户协议',
    lead: '用户在注册、下单、支付、评价、使用定制装机工具或售后服务时，应遵守平台规则与相关法律法规。',
    points: [
      {
        title: '账号责任',
        body: '用户需确保提交的信息真实、准确、完整，并妥善保管账号与密码，因保管不当造成的损失由用户自行承担。'
      },
      {
        title: '交易规则',
        body: '商品价格、库存、活动与服务承诺可能因供应链或系统同步变化，最终以订单确认页和支付结果为准。'
      },
      {
        title: '禁止行为',
        body: '不得利用平台从事违法、欺诈、攻击系统、恶意刷单、干扰交易秩序或侵害他人权益的行为。'
      }
    ]
  }
]

const faqs = [
  {
    question: '是否支持装机配置咨询？',
    answer: '支持。用户可以说明预算、用途、显示器规格和偏好的品牌，我们会提供兼容性与性能方向建议。'
  },
  {
    question: '定制订单通常多久发货？',
    answer: '定制订单需要等待配件确认、装机、系统调试和压力测试，实际时效以订单页面或客服确认结果为准。'
  },
  {
    question: '收到机器后需要自己安装系统吗？',
    answer: '如订单包含系统与驱动调试服务，机器会完成基础环境配置；特殊软件、账号登录和个人数据迁移需用户自行处理。'
  },
  {
    question: '商品出现故障应该怎么处理？',
    answer: '请先保留故障现象、照片或视频，并联系售后客服。客服会根据情况安排远程排查、寄修或品牌售后对接。'
  },
  {
    question: '是否支持开具发票？',
    answer: '支持按订单规则申请发票。企业抬头、税号和开票内容请在提交前核对准确。'
  },
  {
    question: '付款后可以修改收货地址吗？',
    answer: '未发货前可联系客服尝试修改；已出库或已交付承运商后，需要根据物流状态确认是否可改。'
  }
]

const cookieOptions = [
  {
    key: 'necessary',
    title: '必要 Cookie',
    description: '用于登录状态、购物车、下单流程和安全校验，无法关闭。',
    required: true
  },
  {
    key: 'preference',
    title: '偏好 Cookie',
    description: '用于记住界面偏好、地区选择和常用设置。',
    required: false
  },
  {
    key: 'analytics',
    title: '分析 Cookie',
    description: '用于了解页面访问效果，帮助改进商品与服务体验。',
    required: false
  },
  {
    key: 'marketing',
    title: '营销 Cookie',
    description: '用于展示更相关的活动、优惠和内容推荐。',
    required: false
  }
]

const cookiePrefs = reactive({
  necessary: true,
  preference: true,
  analytics: false,
  marketing: false
})
</script>

<style scoped>
.service-page {
  min-height: 100vh;
  background: #f6f8f3;
  color: #17211f;
}

.service-shell {
  width: min(1120px, calc(100% - 32px));
  margin: 0 auto;
}

.service-hero {
  position: relative;
  overflow: hidden;
  background:
    linear-gradient(135deg, rgba(14, 116, 144, 0.16), transparent 38%),
    linear-gradient(100deg, #fff8e4 0%, #f6f8f3 48%, #e8f7f2 100%);
  border-bottom: 1px solid #d9e1d6;
}

.service-hero::after {
  position: absolute;
  right: max(24px, 8vw);
  bottom: -72px;
  width: 260px;
  height: 260px;
  content: "";
  background: repeating-linear-gradient(135deg, rgba(232, 93, 79, 0.25) 0 10px, transparent 10px 22px);
  border-radius: 50%;
}

.service-hero__grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 48px;
  align-items: center;
  min-height: 440px;
  padding: 72px 0;
}

.service-kicker,
.policy-block__head p {
  margin: 0;
  color: #0f766e;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.14em;
}

.service-hero h1 {
  margin: 14px 0 18px;
  max-width: 720px;
  color: #16201c;
  font-size: clamp(40px, 7vw, 76px);
  line-height: 0.98;
  font-weight: 900;
}

.service-hero__copy > p:last-of-type {
  max-width: 640px;
  margin: 0;
  color: #52605b;
  font-size: 17px;
  line-height: 1.8;
}

.service-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 30px;
}

.service-hero__actions a {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding: 0 20px;
  border: 1px solid #17211f;
  border-radius: 6px;
  background: #17211f;
  color: #fffdf6;
  font-size: 14px;
  font-weight: 800;
}

.service-hero__actions a + a {
  background: transparent;
  color: #17211f;
}

.service-brief {
  display: grid;
  gap: 12px;
}

.service-brief__item {
  padding: 22px;
  border: 1px solid #d7dfd2;
  border-radius: 8px;
  background: rgba(255, 253, 246, 0.82);
  box-shadow: 0 18px 45px rgba(23, 33, 31, 0.08);
}

.service-brief__item span {
  color: #e85d4f;
  font-size: 34px;
  line-height: 1;
  font-weight: 900;
}

.service-brief__item p {
  margin: 8px 0 0;
  color: #52605b;
  font-size: 14px;
}

.service-layout {
  display: grid;
  grid-template-columns: 240px minmax(0, 1fr);
  gap: 32px;
  padding: 40px 0 72px;
}

.service-nav {
  position: sticky;
  top: 88px;
  display: grid;
  align-self: start;
  gap: 8px;
}

.service-nav a {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border: 1px solid transparent;
  border-radius: 8px;
  color: #52605b;
  font-size: 14px;
  font-weight: 700;
}

.service-nav a:hover {
  border-color: #cbd8d3;
  background: #fffdf6;
  color: #17211f;
}

.service-nav span {
  color: #e85d4f;
  font-size: 12px;
  font-weight: 900;
}

.service-content {
  display: grid;
  gap: 24px;
}

.policy-block {
  scroll-margin-top: 92px;
  padding: 30px;
  border: 1px solid #d9e1d6;
  border-radius: 8px;
  background: #fffdf6;
  box-shadow: 0 16px 44px rgba(23, 33, 31, 0.06);
}

.policy-block__head {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.policy-block__head > span {
  display: inline-flex;
  width: 42px;
  height: 42px;
  flex: 0 0 42px;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  background: #f2c94c;
  color: #17211f;
  font-size: 13px;
  font-weight: 900;
}

.policy-block h2 {
  margin: 4px 0 0;
  color: #17211f;
  font-size: 28px;
  font-weight: 900;
}

.policy-block__lead {
  margin: 20px 0 0;
  color: #52605b;
  font-size: 16px;
  line-height: 1.8;
}

.policy-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 24px;
}

.policy-point {
  padding: 18px;
  border-left: 4px solid #0e7490;
  border-radius: 6px;
  background: #f2f7f4;
}

.policy-point h3 {
  margin: 0;
  color: #17211f;
  font-size: 16px;
  font-weight: 900;
}

.policy-point p {
  margin: 10px 0 0;
  color: #52605b;
  font-size: 14px;
  line-height: 1.75;
}

.faq-list {
  display: grid;
  gap: 10px;
  margin-top: 24px;
}

.faq-list details {
  border: 1px solid #d9e1d6;
  border-radius: 8px;
  background: #f8fbf5;
}

.faq-list summary {
  cursor: pointer;
  padding: 16px 18px;
  color: #17211f;
  font-weight: 900;
}

.faq-list p {
  margin: 0;
  padding: 0 18px 18px;
  color: #52605b;
  line-height: 1.8;
}

.cookie-options {
  display: grid;
  gap: 12px;
  margin-top: 24px;
}

.cookie-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 16px 18px;
  border: 1px solid #d9e1d6;
  border-radius: 8px;
  background: #f8fbf5;
}

.cookie-option span {
  display: grid;
  gap: 6px;
}

.cookie-option strong {
  color: #17211f;
  font-size: 15px;
}

.cookie-option small {
  color: #52605b;
  font-size: 13px;
  line-height: 1.6;
}

.cookie-option input {
  width: 22px;
  height: 22px;
  accent-color: #e85d4f;
}

@media (max-width: 900px) {
  .service-hero__grid,
  .service-layout,
  .policy-grid {
    grid-template-columns: 1fr;
  }

  .service-hero__grid {
    gap: 28px;
    min-height: auto;
    padding: 52px 0;
  }

  .service-nav {
    position: static;
    display: flex;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .service-nav a {
    flex: 0 0 auto;
    background: #fffdf6;
  }
}

@media (max-width: 560px) {
  .service-shell {
    width: min(100% - 24px, 1120px);
  }

  .service-hero__actions,
  .cookie-option {
    align-items: stretch;
    flex-direction: column;
  }

  .service-hero__actions a {
    justify-content: center;
  }

  .policy-block {
    padding: 22px;
  }

  .policy-block h2 {
    font-size: 24px;
  }
}
</style>
