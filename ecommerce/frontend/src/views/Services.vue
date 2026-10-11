<template>
  <div class="service-page">
    <section class="support-hero">
      <div class="service-shell support-hero__inner">
        <h1>胖虫服务支持</h1>
        <p>我们在这里帮你处理装机配置、订单售后、配送签收、保修政策与隐私设置。</p>

        <div class="support-search" role="search">
          <DsSearchField
            v-model="supportQuery"
            label="搜索订单、故障、保修或配送问题"
            placeholder="搜索订单、故障、保修或配送问题"
            submit-label="搜索支持内容"
            @submit="handleSupportSearch"
          />
        </div>

        <p v-if="supportSearchFeedback" class="search-feedback">{{ supportSearchFeedback }}</p>
      </div>
    </section>

    <section class="support-product-band" aria-label="服务分类">
      <div class="service-shell product-shortcuts">
        <a
          v-for="category in serviceCategories"
          :key="category.id"
          :href="`#${category.id}`"
          class="support-category"
          @click.prevent="focusSection(category.id)"
        >
          <span class="category-icon">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path :d="category.icon" />
            </svg>
          </span>
          <strong>{{ category.title }}</strong>
          <p>{{ category.description }}</p>
        </a>
      </div>
    </section>

    <main class="support-main">
      <section class="service-shell topic-section">
        <div class="section-heading">
          <h2>热门支持主题</h2>
          <p>从最常见的问题开始，先找到正确处理路径。</p>
        </div>

        <div class="topic-grid">
          <section class="topic-panel">
            <h3>热门问题</h3>
            <ul>
              <li v-for="topic in popularSupportTopics" :key="topic.title">
                <a :href="`#${topic.target}`" @click.prevent="focusSection(topic.target)">
                  <span>{{ topic.title }}</span>
                  <small>{{ topic.description }}</small>
                </a>
              </li>
            </ul>
          </section>

          <section class="topic-panel">
            <h3>常用服务入口</h3>
            <ul>
              <li v-for="link in quickServiceLinks" :key="link.title">
                <a :href="`#${link.target}`" @click.prevent="focusSection(link.target)">
                  <span>{{ link.title }}</span>
                  <small>{{ link.description }}</small>
                </a>
              </li>
            </ul>
          </section>
        </div>
      </section>

      <section class="support-contact-band">
        <div class="service-shell contact-grid">
          <section class="contact-card">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M4 6.5h16v10H4zM7 20h10M12 16.5V20" />
            </svg>
            <h2>提交问题</h2>
            <p>请准备订单号、商品型号、故障照片或视频、报错截图和复现步骤。</p>
            <a href="#tech-support" @click.prevent="focusSection('tech-support')">查看技术支持</a>
          </section>

          <section class="contact-card">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M5 8a7 7 0 0 1 14 0v4a4 4 0 0 1-4 4h-2M5 8v5H3V9a1 1 0 0 1 1-1h1Zm14 0h1a1 1 0 0 1 1 1v4h-2V8ZM9 19h4" />
            </svg>
            <h2>人工支持</h2>
            <p>工作日 9:00 - 18:00；复杂售后由专人持续跟进。</p>
            <a href="mailto:support@pangchong.com">support@pangchong.com</a>
          </section>
        </div>
      </section>

      <section class="service-shell status-strip" aria-label="文档状态">
        <div v-for="item in documentStatus" :key="item.label">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </section>

      <section class="service-shell agreement-layout">
        <aside class="agreement-nav" aria-label="协议目录">
          <strong>服务协议与政策</strong>
          <a
            v-for="section in agreementSections"
            :key="section.id"
            :href="`#${section.id}`"
            @click.prevent="focusSection(section.id)"
          >
            {{ section.title }}
          </a>
          <button type="button" @click="printPage">打印条款</button>
        </aside>

        <div class="service-content">
          <section class="notice-panel" aria-label="重要说明">
          <div>
            <h2>请在下单、收货、寄修或提交个人信息前阅读并确认相关条款</h2>
          </div>
          <p>
            页面内容用于说明平台服务流程和责任边界，不构成对法律强制性权利的排除或限制。
            定制装机、已拆封配件、已激活软件、跨品牌联保等场景可能适用不同处理规则。
          </p>
        </section>

        <ServicePolicyPanel
          v-for="section in agreementSections"
          :key="section.id"
          :section="section"
          :open="openSections[section.id]"
          :faqs="faqs"
          @toggle="toggleSection"
        >
          <template #cookie>
            <ServiceCookiePreferences
              v-if="section.kind === 'cookie'"
              :model-value="cookiePrefs"
              :options="cookieOptions"
              :saved="cookieSaved"
              @update:model-value="updateCookiePrefs"
              @save="saveCookiePrefs"
            />
          </template>
        </ServicePolicyPanel>
        </div>
      </section>

      <section class="service-shell legal-footer" aria-label="legal basis">
        <h2>参考依据</h2>
        <ul>
          <li v-for="law in legalBasis" :key="law">{{ law }}</li>
        </ul>
        <p>具体适用以现行有效文本、司法解释、监管要求及订单页面明示内容为准。</p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DsSearchField } from '@/design-system'
import ServiceCookiePreferences from '@/components/ServiceCookiePreferences.vue'
import ServicePolicyPanel from '@/components/ServicePolicyPanel.vue'

const route = useRoute()
const router = useRouter()

const documentStatus = [
  { label: '当前版本', value: 'V2.4.0' },
  { label: '生效日期', value: '2026-06-02' },
  { label: '适用地区', value: '中国大陆' },
  { label: '争议处理', value: '依法协商 / 诉讼' }
]

const serviceCategories = [
  {
    id: 'tech-support',
    title: '技术支持',
    description: '配置、故障、调试',
    icon: 'M4 6.5h16v10H4zM8 20h8M12 16.5V20'
  },
  {
    id: 'warranty',
    title: '保修政策',
    description: '保修、返修、检测',
    icon: 'M12 3.5 19 6v5.2c0 4.5-3 7.8-7 9.3-4-1.5-7-4.8-7-9.3V6l7-2.5Z'
  },
  {
    id: 'delivery',
    title: '配送说明',
    description: '发货、签收、退换',
    icon: 'M3.5 7h10.5v9H3.5zM14 10h3.8l2.7 3v3h-6zM7 19a2 2 0 1 0 0-4 2 2 0 0 0 0 4ZM17 19a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z'
  },
  {
    id: 'faq',
    title: '常见问题',
    description: '发票、地址、寄修',
    icon: 'M12 18.5h.01M9.3 9a2.8 2.8 0 1 1 4.8 2c-.7.7-1.5 1.1-1.8 2.2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z'
  },
  {
    id: 'cookie-settings',
    title: '隐私与 Cookie',
    description: '隐私、数据、偏好',
    icon: 'M7 11V8a5 5 0 0 1 10 0v3M6.5 11h11v9h-11zM12 15v2'
  },
  {
    id: 'user-agreement',
    title: '用户协议',
    description: '账户、交易、争议',
    icon: 'M7 4.5h7l3 3v12H7zM14 4.5v3h3M9.5 12h5M9.5 15h5M9.5 9h2'
  }
]

const popularSupportTopics = [
  {
    title: '商品出现故障应如何处理？',
    description: '保留照片、视频、报错截图和复现步骤。',
    target: 'faq'
  },
  {
    title: '定制整机通常多久发货？',
    description: '了解装机、压力测试、包装检测和揽收节点。',
    target: 'delivery'
  },
  {
    title: '寄修前是否需要备份数据？',
    description: '寄修、检测、换件前的数据与隐私提醒。',
    target: 'warranty'
  },
  {
    title: '是否支持装机配置咨询？',
    description: '预算、用途、显示器规格和已有配件怎么提交。',
    target: 'tech-support'
  }
]

const quickServiceLinks = [
  {
    title: '查看保修与三包规则',
    description: '整机、配件、品牌联保和不保修情形。',
    target: 'warranty'
  },
  {
    title: '确认签收与退换货规则',
    description: '外包装异常、七日无理由、物流费用。',
    target: 'delivery'
  },
  {
    title: '管理 Cookie 偏好',
    description: '关闭非必要 Cookie 或撤回授权。',
    target: 'cookie-settings'
  },
  {
    title: '阅读隐私政策',
    description: '个人信息收集、共享、保存和用户权利。',
    target: 'privacy'
  }
]

const supportSearchAliases = [
  { id: 'tech-support', words: ['技术', '故障', '蓝屏', '驱动', '配置', '装机', 'bios', '温度', '噪音', '显示'] },
  { id: 'warranty', words: ['保修', '质保', '三包', '返修', '维修', '检测', '人为', '损坏'] },
  { id: 'delivery', words: ['配送', '物流', '签收', '发货', '退货', '七日', '地址', '运费'] },
  { id: 'faq', words: ['常见', '问题', '发票', '多久', '怎么', '如何'] },
  { id: 'privacy', words: ['隐私', '个人信息', '数据', '删除', '共享'] },
  { id: 'cookie-settings', words: ['cookie', 'cookies', '偏好', '营销', '分析'] },
  { id: 'user-agreement', words: ['协议', '账户', '争议', '规则'] }
]

const legalBasis = [
  '《中华人民共和国民法典》合同编',
  '《中华人民共和国消费者权益保护法》',
  '《中华人民共和国产品质量法》',
  '《中华人民共和国电子商务法》',
  '《中华人民共和国个人信息保护法》',
  '《中华人民共和国数据安全法》',
  '《网络购买商品七日无理由退货暂行办法》',
  '《微型计算机商品修理更换退货责任规定》'
]

const agreementSections = [
  {
    id: 'tech-support',
    index: '01',
    eyebrow: 'TECHNICAL SUPPORT',
    title: '技术支持',
    summary: '购买前、装机中与购买后的技术咨询、故障判断和基础调试说明。',
    lead: '本条款适用于胖虫科技向用户提供的售前配置咨询、装机协助、系统基础指导、硬件故障初步判断及售后对接服务。平台将基于用户提供的信息进行合理判断，但远程建议不替代品牌厂商检测、授权维修或法定质量鉴定。',
    clauses: [
      {
        code: '1.1',
        title: '服务范围',
        body: '技术支持主要围绕平台销售的电脑整机、DIY 配件及相关订单展开，覆盖购买前确认、交付前调试和购买后问题排查。',
        items: [
          '配置建议、预算匹配、硬件兼容性核验、功耗与散热方案说明。',
          'BIOS、驱动、系统初始化、压力测试结果和基础性能调校说明。',
          '无法开机、蓝屏、异常噪音、温度异常、显示异常等问题的初步排查路径。'
        ]
      },
      {
        code: '1.2',
        title: '响应方式',
        body: '用户可通过在线客服、订单留言或售后邮箱提交咨询。平台会根据问题复杂程度、证据完整度和厂商协同进度安排处理。',
        items: [
          '普通咨询在工作日内尽量于 24 小时内首次回复。',
          '硬件故障建议同步订单号、商品序列号、故障照片或视频、报错截图及操作复现路径。',
          '需要返厂、返修或品牌检测的事项，以品牌厂商或授权维修点的检测结论为准。'
        ]
      },
      {
        code: '1.3',
        title: '服务边界',
        body: '平台不承诺解决由非平台商品、第三方软件、用户自行改装或超规格使用造成的问题，但可在合理范围内提供排查建议。',
        items: [
          '不提供软件破解、绕过授权、外挂、攻击系统、恶意刷单等违法或违规协助。',
          '用户自行超频、拆机、刷写非官方固件或连接不合规电源设备造成的风险由用户自行承担。',
          '涉及个人数据迁移、数据恢复、商业资料备份的事项，用户应自行做好备份并确认授权范围。'
        ]
      }
    ]
  },
  {
    id: 'warranty',
    index: '02',
    eyebrow: 'WARRANTY POLICY',
    title: '保修政策',
    summary: '整机、配件、品牌联保、三包责任、寄修检测和不保修情形。',
    lead: '保修处理以商品详情页、订单记录、发票或三包凭证、品牌厂商政策及现行法律法规为基础。依法应由经营者承担的质量责任，平台不会以页面规则减轻或免除。',
    clauses: [
      {
        code: '2.1',
        title: '三包与品牌保修',
        body: '整机与配件的保修期、服务方式和检测标准可能因品牌、型号、配件类别、定制程度不同而有所差异。',
        items: [
          '商品页面、订单页面、发票、保修卡或品牌官方说明对保修范围有明确约定的，从其约定；法律另有强制性规定的，从其规定。',
          '蓝天 Clevo 等授权渠道商品按对应品牌、渠道和配件类别执行售后处理。',
          '平台可协助用户对接品牌售后、检测点、返修流程和进度查询。'
        ]
      },
      {
        code: '2.2',
        title: '质量问题处理',
        body: '保修期内因商品本身质量问题导致的故障，经检测确认后，可依法或依约进行维修、更换、退货或其他合理处理。',
        items: [
          '检测前用户应尽量保留完整包装、配件、购机凭证和故障证据。',
          '需拆机检测的商品可能涉及外观、封签、数据与配件完整性确认。',
          '同一故障多次维修、核心部件异常或无法正常使用的情形，将结合检测结论和法律规定处理。'
        ]
      },
      {
        code: '2.3',
        title: '不保修情形',
        body: '以下情形通常不属于免费保修范围，但不影响用户依法主张其他权利。',
        items: [
          '人为损坏、进液、摔落、挤压、烧毁、异物进入、虫害、霉变、腐蚀或不当环境使用。',
          '私自拆改、非授权维修、刷写非官方固件、超规格超频、使用不合规电源或外接设备。',
          '耗材自然损耗、外观正常磨损、赠品或非平台销售商品的责任承担。'
        ]
      },
      {
        code: '2.4',
        title: '数据与隐私提醒',
        body: '寄修或检测前，用户应自行备份并清除重要个人数据。平台在售后处理过程中仅在必要范围内接触与处理设备信息。',
        items: [
          '硬盘、系统盘、缓存文件、浏览器账户和个人资料不承诺原样保留。',
          '如需保留数据，请在寄修前书面说明；能否满足取决于故障类型和检测方案。',
          '涉及个人信息处理的事项按本页隐私政策执行。'
        ]
      }
    ]
  },
  {
    id: 'delivery',
    index: '03',
    eyebrow: 'DELIVERY & RETURNS',
    title: '配送说明',
    summary: '发货时效、物流签收、运输风险、七日无理由与定制商品处理。',
    lead: '平台根据库存、装机排期、压力测试、包装检测和承运能力安排发货。用户应在签收时核验外包装与商品外观，并按要求保留异常证据。',
    clauses: [
      {
        code: '3.1',
        title: '发货条件',
        body: '现货商品通常按页面承诺时效发出；定制整机或特殊配置订单需完成配件到货、装机、稳定性测试和外观确认后发货。',
        items: [
          '订单支付成功不等同于立即发货，实际以订单状态、客服确认和物流揽收信息为准。',
          '显卡、内存、硬盘等配件价格和库存可能随供应链变化而调整，已确认订单按平台规则处理。',
          '不可抗力、自然灾害、交通管制、承运异常、系统维护等可能影响交付时效。'
        ]
      },
      {
        code: '3.2',
        title: '签收检查',
        body: '签收前应检查外包装是否破损、浸湿、变形、二次封箱或重量明显异常。发现异常时请及时拍照、视频留证并联系平台。',
        items: [
          '高价值整机建议在签收现场记录外箱、封签、缓冲材料、机身外观和配件清单。',
          '如承运商要求先签收后验货，请在签收单或客服沟通中备注异常。',
          '未经留证直接拆改、安装或继续使用，可能影响后续责任判断。'
        ]
      },
      {
        code: '3.3',
        title: '七日无理由退货',
        body: '依法适用七日无理由退货的商品，用户可在规定期限内按平台流程申请。定制、拆封影响完好、已激活软件或购买时确认不宜退货的商品，按法律法规及页面明示规则处理。',
        items: [
          '退回商品应保持完好，包含主机、配件、赠品、包装、票据、说明书等。',
          '影响二次销售、缺失配件、外观损伤或激活授权的，可能产生折价或无法按无理由规则处理。',
          '质量问题退换修不受无理由规则限制，按质量责任和三包规定处理。'
        ]
      },
      {
        code: '3.4',
        title: '物流费用',
        body: '因商品质量问题依法产生的合理物流费用按平台规则和法律规定承担；非质量原因退换货的费用承担以页面说明、订单约定和法律规定为准。',
        items: [
          '偏远地区、超大件、保价、上楼、改址、二次派送可能产生额外费用。',
          '寄回前请按客服指引包装，避免运输中造成新的损坏。',
          '未经确认使用到付、超范围承运或不当包装产生的风险由责任方承担。'
        ]
      }
    ]
  },
  {
    id: 'faq',
    index: '04',
    eyebrow: 'SELF SERVICE',
    title: '常见问题',
    summary: '装机咨询、发票、地址修改、故障处理和资料提交的标准问答。',
    kind: 'faq',
    lead: '以下问答用于帮助用户快速确认常见服务路径。若与订单页面、客服书面确认或法律法规不一致，以对用户更有利且依法有效的规则为准。',
    clauses: [
      {
        code: '4.1',
        title: '如何提高处理效率',
        body: '提交问题时请尽量提供完整上下文，包括订单号、商品型号、故障时间、操作步骤、照片视频、系统日志或报错截图。',
        items: [
          '配置咨询请说明预算、用途、显示器规格、散热偏好和已有配件。',
          '售后问题请勿反复拆机或更换关键部件，以免影响故障判断。',
          '涉及隐私数据的截图请先自行遮盖身份证号、手机号、地址等敏感信息。'
        ]
      }
    ]
  },
  {
    id: 'privacy',
    index: '05',
    eyebrow: 'PRIVACY POLICY',
    title: '隐私政策',
    summary: '个人信息收集、使用、共享、保存、删除、用户权利与安全事件处理。',
    lead: '平台仅在实现交易、履行合同、提供售后、保障账户安全、改善服务体验和满足法律法规要求的必要范围内处理个人信息。除法律法规另有规定外，平台不会超出授权目的处理个人信息。',
    clauses: [
      {
        code: '5.1',
        title: '收集的信息',
        body: '在注册、登录、下单、支付、配送、开票、评价、售后和客服沟通过程中，平台可能收集必要信息。',
        items: [
          '账户信息、联系方式、收货地址、订单信息、支付状态、发票信息和客服记录。',
          '设备型号、序列号、故障描述、检测记录、售后进度和寄修信息。',
          '为安全风控和体验优化所需的日志、Cookie 标识、访问时间、页面行为和设备基础信息。'
        ]
      },
      {
        code: '5.2',
        title: '使用目的',
        body: '个人信息处理遵循合法、正当、必要、诚信原则，并尽量控制在实现服务目的所需的最小范围。',
        items: [
          '完成订单履约、物流配送、售后维修、开票、退款和争议处理。',
          '保障账户、交易和系统安全，识别异常登录、恶意攻击、欺诈交易或违规行为。',
          '在用户同意范围内进行偏好设置、体验分析和服务改进。'
        ]
      },
      {
        code: '5.3',
        title: '共享与委托处理',
        body: '平台可能向支付机构、物流承运商、品牌厂商、授权维修点、云服务商或依法有权机关提供必要信息。',
        items: [
          '共享范围限于完成支付、配送、售后、开票、安全保障或法定义务所必需。',
          '平台会要求合作方按照约定目的、处理方式和安全措施处理个人信息。',
          '未经用户同意，平台不会出售个人信息或用于超出授权范围的商业目的。'
        ]
      },
      {
        code: '5.4',
        title: '用户权利',
        body: '用户可依法查询、复制、更正、补充、删除个人信息，撤回同意或注销账户。平台将在核验身份后依法处理请求。',
        items: [
          '订单、支付、发票、售后和争议处理记录可能需按法定期限保存。',
          '撤回同意不影响撤回前基于同意已经进行的个人信息处理活动效力。',
          '如认为个人信息权益受到侵害，可通过本页邮箱联系平台处理。'
        ]
      }
    ]
  },
  {
    id: 'user-agreement',
    index: '06',
    eyebrow: 'USER AGREEMENT',
    title: '用户协议',
    summary: '账户责任、合同成立、价格库存、禁止行为、责任限制和争议解决。',
    lead: '用户使用平台浏览、注册、下单、支付、评价、定制装机工具或售后服务时，应遵守本协议、页面规则、订单约定及相关法律法规。',
    clauses: [
      {
        code: '6.1',
        title: '账户与身份',
        body: '用户应确保提交的信息真实、准确、完整，并妥善保管账户、密码、验证码和支付凭证。',
        items: [
          '因用户保管不当、主动泄露、使用弱密码或授权他人操作造成的损失，由用户依法承担相应责任。',
          '平台发现账户存在异常登录、欺诈、攻击或违反平台规则情形时，可依法采取风险控制措施。',
          '企业采购、开票和售后联系人应保证授权真实有效。'
        ]
      },
      {
        code: '6.2',
        title: '订单与合同成立',
        body: '商品展示、价格、库存、促销信息和服务承诺可能因供应链、系统同步或页面更新发生变化。',
        items: [
          '合同成立通常以用户提交订单、完成支付并经平台确认可以履约为基础。',
          '明显标错价格、库存异常、系统故障、恶意刷单或违反活动规则的订单，平台可依法处理并说明原因。',
          '定制装机需求一经确认进入装配或采购流程后，取消、变更和退换规则可能与普通现货商品不同。'
        ]
      },
      {
        code: '6.3',
        title: '禁止行为',
        body: '用户不得利用平台从事违法违规、侵害他人权益或破坏平台运营秩序的行为。',
        items: [
          '不得实施恶意下单、虚假交易、套取优惠、攻击系统、爬取数据、传播恶意程序或干扰平台服务。',
          '不得发布违法、侵权、侮辱、诽谤、虚假、诱导交易或与商品无关的内容。',
          '不得冒用他人身份、盗用账户、伪造凭证、篡改物流或售后证据。'
        ]
      },
      {
        code: '6.4',
        title: '争议解决',
        body: '发生争议时，双方应优先通过客服、订单留言或书面邮件协商解决。协商不成的，可依法向有管辖权的人民法院提起诉讼。',
        items: [
          '争议处理过程中，订单记录、支付凭证、物流记录、客服沟通、检测报告和双方提交的证据可作为判断依据。',
          '任何责任限制不得排除平台依法应承担的产品质量、消费者权益保护和个人信息保护责任。',
          '不可抗力、监管要求、重大网络安全事件等可能导致服务暂停或延迟，平台将依法采取合理补救措施。'
        ]
      }
    ]
  },
  {
    id: 'cookie-settings',
    index: '07',
    eyebrow: 'COOKIE CONTROL',
    title: 'Cookie 设置',
    summary: '必要、偏好、分析和营销 Cookie 的用途、状态和撤回机制。',
    kind: 'cookie',
    lead: 'Cookie 用于维持登录、保存购物车、保障交易安全、记住偏好和改进页面体验。必要 Cookie 是平台基础功能所需，无法关闭；其他类型可由用户按需开启或关闭。',
    clauses: [
      {
        code: '7.1',
        title: '授权原则',
        body: '非必要 Cookie 将在用户授权后使用，用户可随时调整偏好。关闭部分 Cookie 可能影响个性化设置、统计分析或推荐内容。',
        items: [
          '必要 Cookie 用于登录、购物车、下单、支付安全、风控和会话保持。',
          '偏好 Cookie 用于记住界面设置、地区选择和常用筛选条件。',
          '分析和营销 Cookie 将尽量以去标识化或聚合方式用于服务改进和内容推荐。'
        ]
      },
      {
        code: '7.2',
        title: '撤回与清除',
        body: '用户可通过本页面开关、浏览器设置或清除浏览数据管理 Cookie。撤回授权不影响撤回前基于授权已经进行的处理活动。',
        items: [
          '更换浏览器、设备或清除缓存后，偏好设置可能需要重新确认。',
          '关闭非必要 Cookie 后，平台仍可能保留依法或履约所需的必要日志。',
          '如需行使个人信息相关权利，可通过 support@pangchong.com 联系平台。'
        ]
      }
    ]
  }
]

const faqs = [
  {
    question: '是否支持装机配置咨询？',
    answer: '支持。请说明预算、主要用途、显示器规格、游戏或生产软件需求、外观偏好和已有配件，我们会从兼容性、功耗、散热、性能释放和预算优先级给出建议。'
  },
  {
    question: '定制整机通常多久发货？',
    answer: '定制订单需完成配件确认、装机、系统基础配置、压力测试和外观检查。实际时效以订单页面、客服书面确认和物流揽收信息为准。'
  },
  {
    question: '商品出现故障应如何处理？',
    answer: '请先停止高风险操作，保留故障照片或视频、报错截图和复现步骤，并通过订单售后或邮箱提交。平台会安排远程排查、寄修检测或品牌售后对接。'
  },
  {
    question: '可以修改收货地址吗？',
    answer: '未发货前可联系客服尝试修改；已出库或已交付承运商后，需结合物流状态、承运商规则和风险责任确认是否可改。'
  },
  {
    question: '是否支持开具发票？',
    answer: '支持按订单规则申请发票。企业抬头、税号、开票内容和邮箱请在提交前核对准确，已开具发票的更正或红冲需按税务规则处理。'
  },
  {
    question: '寄修前是否需要备份数据？',
    answer: '需要。检测、维修、换件、重装系统或返厂过程可能导致数据丢失。请在寄修前自行备份并退出个人账户，平台不承诺保留本地数据。'
  }
]

const cookieOptions = [
  {
    key: 'necessary',
    title: '必要 Cookie',
    description: '用于登录状态、购物车、下单流程、支付安全、CSRF 防护和异常访问识别。',
    purpose: '法律基础：履行合同、保障网络与交易安全。',
    required: true
  },
  {
    key: 'preference',
    title: '偏好 Cookie',
    description: '用于记住地区、展示密度、最近浏览、筛选条件和界面偏好。',
    purpose: '法律基础：用户同意；可随时撤回。',
    required: false
  },
  {
    key: 'analytics',
    title: '分析 Cookie',
    description: '用于统计页面访问、功能使用、转化路径和异常性能，以改进商品与服务体验。',
    purpose: '法律基础：用户同意；尽量使用聚合或去标识化数据。',
    required: false
  },
  {
    key: 'marketing',
    title: '营销 Cookie',
    description: '用于展示更相关的活动、优惠、内容推荐和广告效果评估。',
    purpose: '法律基础：用户同意；关闭后仍可能看到非个性化内容。',
    required: false
  }
]

const openSections = reactive({
  'tech-support': true,
  warranty: true,
  delivery: false,
  faq: false,
  privacy: true,
  'user-agreement': false,
  'cookie-settings': true
})

const cookiePrefs = reactive({
  necessary: true,
  preference: true,
  analytics: false,
  marketing: false
})

const cookieSaved = ref(false)
const supportQuery = ref('')
const supportSearchFeedback = ref('')

function updateCookiePrefs(nextPrefs) {
  Object.keys(cookiePrefs).forEach((key) => {
    if (key !== 'necessary' && typeof nextPrefs[key] === 'boolean') {
      cookiePrefs[key] = nextPrefs[key]
    }
  })
}

function focusSection(id) {
  openSections[id] = true

  if (typeof window === 'undefined') {
    return
  }

  const hash = `#${id}`
  if (route.hash === hash) {
    scrollToSection(id)
    return
  }

  void router.replace({
    path: route.path,
    query: route.query,
    hash
  })
}

function scrollToSection(id, behavior = 'smooth') {
  window.setTimeout(() => {
    const target = document.getElementById(id)
    if (!target) return

    const navOffset = 86
    const top = target.getBoundingClientRect().top + window.scrollY - navOffset
    window.scrollTo({
      top: Math.max(0, top),
      behavior
    })
  }, 80)
}

function handleSupportSearch() {
  const keyword = supportQuery.value.trim().toLowerCase()

  if (!keyword) {
    supportSearchFeedback.value = '请输入关键词，例如“蓝屏”“保修”“签收”或“发票”。'
    return
  }

  const matchedAlias = supportSearchAliases.find((item) =>
    item.words.some((word) => keyword.includes(word) || word.includes(keyword))
  )
  const matchedSection = matchedAlias || agreementSections.find((section) =>
    [section.title, section.summary, section.lead].some((text) => text.toLowerCase().includes(keyword))
  )

  if (!matchedSection) {
    supportSearchFeedback.value = '没有找到精确匹配，已为你打开常见问题。'
    focusSection('faq')
    return
  }

  const section = agreementSections.find((item) => item.id === matchedSection.id)
  supportSearchFeedback.value = section
    ? `已定位到「${section.title}」。`
    : '已定位到相关服务内容。'
  focusSection(matchedSection.id)
}

function openSection(id) {
  openSections[id] = true
}

function toggleSection(id) {
  openSections[id] = !openSections[id]
}

function saveCookiePrefs() {
  localStorage.setItem('pangchong-cookie-preferences', JSON.stringify(cookiePrefs))
  cookieSaved.value = true
  window.setTimeout(() => {
    cookieSaved.value = false
  }, 2800)
}

function printPage() {
  window.print()
}

function openHashSection(hash) {
  if (!hash) {
    return
  }

  let id = hash.slice(1)
  try {
    id = decodeURIComponent(id)
  } catch {
    // Keep the raw hash id if it is not URI encoded cleanly.
  }

  if (Object.prototype.hasOwnProperty.call(openSections, id)) {
    openSections[id] = true
  }
}

watch(() => route.hash, openHashSection, { immediate: true })

onMounted(() => {
  const savedPrefs = localStorage.getItem('pangchong-cookie-preferences')

  if (savedPrefs) {
    try {
      const parsedPrefs = JSON.parse(savedPrefs)
      Object.keys(cookiePrefs).forEach((key) => {
        if (typeof parsedPrefs[key] === 'boolean' && key !== 'necessary') {
          cookiePrefs[key] = parsedPrefs[key]
        }
      })
    } catch {
      localStorage.removeItem('pangchong-cookie-preferences')
    }
  }
})
</script>

<style scoped>
/* Active service-center theme */
.service-page {
  min-height: 100vh;
  overflow-x: hidden;
  background: var(--pc-color-theme-service-canvas);
  color: var(--pc-color-theme-service-text-secondary);
}

.service-shell {
  width: min(1180px, calc(100% - 48px));
  margin: 0 auto;
}

.support-hero {
  position: relative;
  overflow: hidden;
  display: flex;
  min-height: 430px;
  align-items: center;
  border-bottom: 1px solid var(--pc-color-theme-service-border-subtle);
  background:
    linear-gradient(180deg, rgb(var(--pc-color-theme-service-hero-rgb) / 0.78), rgb(var(--pc-color-theme-service-canvas-rgb) / 0.96)),
    radial-gradient(circle at 50% 0%, rgb(var(--pc-color-theme-service-spark-rgb) / 0.18), transparent 42%),
    var(--pc-color-theme-service-canvas);
}

.support-hero::before {
  position: absolute;
  inset: 0;
  content: "";
  background:
    linear-gradient(90deg, rgb(var(--pc-color-theme-service-text-primary-rgb) / 0.035) 1px, transparent 1px),
    linear-gradient(180deg, rgb(var(--pc-color-theme-service-text-primary-rgb) / 0.03) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: linear-gradient(180deg, rgb(var(--pc-color-theme-service-contact-rgb) / 0.68), transparent 78%);
  pointer-events: none;
}

.support-hero__inner {
  display: grid;
  justify-items: center;
  padding: 72px 0 64px;
  text-align: center;
}

.support-hero h1 {
  margin: 0;
  color: var(--pc-color-theme-service-text-primary);
  font-size: clamp(44px, 6vw, 76px);
  line-height: 1.04;
  font-weight: 760;
}

.support-hero p {
  max-width: 690px;
  margin: 18px 0 0;
  color: var(--pc-color-theme-service-text-body);
  font-size: 18px;
  line-height: 1.75;
}

.support-search {
  display: grid;
  grid-template-columns: 24px minmax(0, 1fr) 88px;
  gap: 14px;
  align-items: center;
  width: min(720px, 100%);
  min-height: 58px;
  margin-top: 34px;
  padding: 7px 7px 7px 20px;
  border: 1px solid rgb(var(--pc-color-theme-service-text-primary-rgb) / 0.22);
  border-radius: 8px;
  background: rgb(var(--pc-color-theme-service-search-rgb) / 0.92);
  box-shadow: 0 20px 70px rgb(var(--pc-color-theme-service-contact-rgb) / 0.38);
}

.support-search:focus-within {
  border-color: rgb(var(--pc-color-brand-400-rgb) / 0.72);
  box-shadow: 0 28px 90px rgb(var(--pc-color-theme-service-focus-glow-rgb) / 0.12), inset 0 1px 0 rgb(var(--pc-color-theme-service-text-primary-rgb) / 0.08);
}

.support-search svg,
.contact-card svg,
.category-icon svg,
.summary-icon {
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2;
}

.support-search svg {
  width: 21px;
  height: 21px;
  color: var(--pc-color-theme-service-text-muted);
}

.support-search input {
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--pc-color-theme-service-text-primary);
  font-size: 16px;
}

.support-search input::placeholder {
  color: var(--pc-color-theme-service-text-subtle);
}

.support-search button,
.agreement-nav button,
.contact-card a,
.cookie-footer button {
  display: inline-flex;
  min-height: 44px;
  cursor: pointer;
  align-items: center;
  justify-content: center;
  border-radius: 7px;
  font-size: 14px;
  font-weight: 700;
  transition: transform var(--pc-motion-duration-micro) var(--pc-motion-ease-standard), background-color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard), border-color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard), color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard);
}

.support-search button,
.contact-card a,
.cookie-footer button {
  border: 1px solid var(--pc-color-semantic-action-primary);
  background: var(--pc-color-semantic-action-primary);
  color: var(--pc-color-theme-service-canvas);
}

.support-search button:hover,
.agreement-nav button:hover,
.contact-card a:hover,
.cookie-footer button:hover {
  transform: translateY(-1px);
}

.search-feedback {
  margin: 14px 0 0;
  color: var(--pc-color-semantic-text-accent);
  font-size: 14px;
  font-weight: 700;
}

.support-product-band {
  border-bottom: 1px solid var(--pc-color-theme-service-border-subtle);
  background: var(--pc-color-theme-service-rail);
}

.product-shortcuts {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 0;
}

.support-category {
  display: grid;
  min-height: 172px;
  justify-items: center;
  align-content: center;
  gap: 10px;
  border-left: 1px solid var(--pc-color-theme-service-divider);
  color: var(--pc-color-theme-service-text-secondary);
  text-align: center;
  transition: background-color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard), color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard);
}

.support-category:last-child {
  border-right: 1px solid var(--pc-color-theme-service-divider);
}

.support-category:hover {
  background: var(--pc-color-theme-service-category-hover);
  color: var(--pc-color-theme-service-text-primary);
}

.category-icon {
  display: inline-flex;
  width: 58px;
  height: 58px;
  align-items: center;
  justify-content: center;
  color: var(--pc-color-theme-service-text-secondary);
}

.category-icon svg {
  width: 44px;
  height: 44px;
  stroke-width: 1.55;
}

.support-category strong {
  color: inherit;
  font-size: 16px;
  line-height: 1.25;
  font-weight: 720;
}

.support-category p {
  max-width: 128px;
  margin: 0;
  color: var(--pc-color-theme-service-text-category);
  font-size: 12px;
  line-height: 1.45;
}

.support-main {
  background: var(--pc-color-theme-service-canvas);
}

.topic-section {
  padding: 64px 0 40px;
}

.section-heading {
  text-align: center;
}

.section-heading h2 {
  margin: 0;
  color: var(--pc-color-theme-service-text-primary);
  font-size: clamp(30px, 4vw, 44px);
  line-height: 1.14;
  font-weight: 740;
}

.section-heading p {
  margin: 12px 0 0;
  color: var(--pc-color-theme-service-text-muted);
  font-size: 16px;
}

.topic-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  margin-top: 34px;
}

.topic-panel {
  border: 1px solid var(--pc-color-theme-service-border);
  border-radius: 8px;
  background: var(--pc-color-theme-service-surface);
}

.topic-panel h3 {
  margin: 0;
  padding: 24px 28px 18px;
  color: var(--pc-color-theme-service-text-primary);
  font-size: 25px;
  line-height: 1.25;
  font-weight: 720;
}

.topic-panel ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.topic-panel li {
  border-top: 1px solid var(--pc-color-theme-service-border);
}

.topic-panel a {
  position: relative;
  display: grid;
  gap: 6px;
  padding: 18px 56px 18px 28px;
  color: var(--pc-color-theme-service-text-secondary);
}

.topic-panel a::after {
  position: absolute;
  top: 50%;
  right: 28px;
  content: "›";
  color: var(--pc-color-semantic-text-accent);
  font-size: 28px;
  line-height: 1;
  transform: translateY(-50%);
}

.topic-panel a:hover {
  background: var(--pc-color-theme-service-surface-hover);
}

.topic-panel span {
  font-size: 16px;
  font-weight: 720;
}

.topic-panel small {
  color: var(--pc-color-theme-service-text-muted);
  font-size: 13px;
  line-height: 1.55;
}

.support-contact-band {
  margin-top: 24px;
  border-top: 1px solid var(--pc-color-theme-service-border-subtle);
  border-bottom: 1px solid var(--pc-color-theme-service-border-subtle);
  background: var(--pc-color-theme-service-contact);
}

.contact-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.contact-card {
  display: grid;
  min-height: 264px;
  justify-items: center;
  align-content: center;
  padding: 42px 28px;
  text-align: center;
}

.contact-card + .contact-card {
  border-left: 1px solid var(--pc-color-theme-service-divider-strong);
}

.contact-card svg {
  width: 58px;
  height: 58px;
  color: var(--pc-color-theme-service-text-secondary);
  stroke-width: 1.7;
}

.contact-card h2 {
  margin: 18px 0 0;
  color: var(--pc-color-theme-service-text-primary);
  font-size: 30px;
  line-height: 1.2;
  font-weight: 740;
}

.contact-card p {
  max-width: 430px;
  margin: 12px 0 0;
  color: var(--pc-color-theme-service-text-muted);
  font-size: 14px;
  line-height: 1.75;
}

.contact-card a {
  min-width: 172px;
  margin-top: 22px;
  padding: 0 18px;
}

.status-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1px;
  margin-top: 56px;
  overflow: hidden;
  border: 1px solid var(--pc-color-theme-service-border);
  border-radius: 8px;
  background: var(--pc-color-theme-service-border);
}

.status-strip div {
  min-height: 92px;
  padding: 20px 22px;
  background: var(--pc-color-theme-service-surface);
}

.status-strip span {
  display: block;
  color: var(--pc-color-theme-service-text-subtle);
  font-size: 12px;
  font-weight: 700;
}

.status-strip strong {
  display: block;
  margin-top: 9px;
  color: var(--pc-color-theme-service-text-secondary);
  font-size: 20px;
  line-height: 1.2;
  font-weight: 760;
}

.agreement-layout {
  display: grid;
  grid-template-columns: 245px minmax(0, 1fr);
  gap: 24px;
  padding: 36px 0 42px;
}

.agreement-nav {
  position: sticky;
  top: 88px;
  align-self: start;
  display: grid;
  gap: 4px;
  padding: 18px;
  border: 1px solid var(--pc-color-theme-service-border);
  border-radius: 8px;
  background: var(--pc-color-theme-service-surface);
}

.agreement-nav strong {
  margin-bottom: 10px;
  color: var(--pc-color-theme-service-text-primary);
  font-size: 16px;
  font-weight: 740;
}

.agreement-nav a {
  border-radius: 7px;
  padding: 10px 12px;
  color: var(--pc-color-theme-service-text-legal);
  font-size: 14px;
  transition: background-color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard), color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard);
}

.agreement-nav a:hover {
  background: var(--pc-color-theme-service-surface-hover);
  color: var(--pc-color-theme-service-text-primary);
}

.agreement-nav button {
  margin-top: 12px;
  border: 1px solid var(--pc-color-theme-service-control-border);
  background: transparent;
  color: var(--pc-color-theme-service-text-secondary);
}

.service-content {
  display: grid;
  gap: 12px;
  min-width: 0;
}

.notice-panel {
  display: grid;
  grid-template-columns: minmax(240px, 0.65fr) minmax(0, 1fr);
  gap: 26px;
  align-items: start;
  padding: 26px 28px;
  border: 1px solid var(--pc-color-theme-service-border);
  border-radius: 8px;
  background: var(--pc-color-theme-service-surface);
}

.notice-panel h2 {
  margin: 0;
  color: var(--pc-color-theme-service-text-primary);
  font-size: 24px;
  line-height: 1.36;
  font-weight: 740;
}

.notice-panel p {
  margin: 0;
  color: var(--pc-color-theme-service-text-muted);
  font-size: 14px;
  line-height: 1.85;
}

.policy-panel {
  scroll-margin-top: 92px;
  overflow: hidden;
  border: 1px solid var(--pc-color-theme-service-border);
  border-radius: 8px;
  background: var(--pc-color-theme-service-surface);
  box-shadow: none;
  backdrop-filter: none;
}

.policy-panel__summary {
  display: grid;
  grid-template-columns: 52px minmax(152px, 0.3fr) minmax(0, 1fr) 32px;
  gap: 18px;
  align-items: center;
  width: 100%;
  min-height: 78px;
  cursor: pointer;
  border: 0;
  background: transparent;
  padding: 16px 22px;
  text-align: left;
}

.policy-panel__summary:hover {
  background: var(--pc-color-theme-service-surface-hover);
}

.summary-index {
  display: inline-flex;
  width: 40px;
  height: 40px;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--pc-color-theme-service-control-border);
  border-radius: 8px;
  background: var(--pc-color-theme-service-rail);
  color: var(--pc-color-semantic-text-accent);
  font-size: 13px;
  font-weight: 760;
}

.summary-title {
  display: grid;
  gap: 5px;
}

.summary-title strong {
  color: var(--pc-color-theme-service-text-primary);
  font-size: 20px;
  line-height: 1.18;
  font-weight: 740;
}

.summary-title small {
  color: var(--pc-color-theme-service-text-subtle);
  font-size: 11px;
  font-weight: 760;
  letter-spacing: 0.06em;
}

.summary-copy {
  color: var(--pc-color-theme-service-text-muted);
  font-size: 14px;
  line-height: 1.72;
}

.summary-icon {
  width: 21px;
  height: 21px;
  color: var(--pc-color-theme-service-text-subtle);
  transition: transform var(--pc-motion-duration-micro) var(--pc-motion-ease-standard), color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard);
}

.policy-panel__summary[aria-expanded="true"] .summary-icon {
  color: var(--pc-color-semantic-text-accent);
  transform: rotate(180deg);
}

.policy-panel__body,
.clause-list,
.faq-list,
.cookie-control {
  border-top: 1px solid var(--pc-color-theme-service-border);
}

.policy-lead {
  margin: 0;
  padding: 24px 28px;
  color: var(--pc-color-theme-service-text-body);
  font-size: 15px;
  line-height: 1.9;
}

.clause-list {
  display: grid;
}

.clause-row {
  display: grid;
  grid-template-columns: 206px minmax(0, 1fr);
  gap: 26px;
  padding: 24px 28px;
  border-bottom: 1px solid var(--pc-color-theme-service-border);
}

.clause-row:last-child {
  border-bottom: 0;
}

.clause-row__title {
  display: grid;
  align-content: start;
  gap: 9px;
}

.clause-row__title span {
  color: var(--pc-color-semantic-text-accent);
  font-size: 12px;
  font-weight: 760;
}

.clause-row__title h3 {
  margin: 0;
  color: var(--pc-color-theme-service-text-primary);
  font-size: 17px;
  line-height: 1.4;
  font-weight: 720;
}

.clause-row__body p {
  margin: 0;
  color: var(--pc-color-theme-service-text-legal);
  font-size: 14px;
  line-height: 1.86;
}

.clause-row__body ul {
  display: grid;
  gap: 8px;
  margin: 14px 0 0;
  padding: 0;
  list-style: none;
}

.clause-row__body li {
  position: relative;
  padding-left: 17px;
  color: var(--pc-color-theme-service-text-muted);
  font-size: 13px;
  line-height: 1.75;
}

.clause-row__body li::before {
  position: absolute;
  top: 0.75em;
  left: 0;
  width: 5px;
  height: 5px;
  content: "";
  border-radius: 999px;
  background: var(--pc-color-semantic-action-primary);
}

.faq-list {
  display: grid;
}

.faq-list details,
.cookie-option {
  border-bottom: 1px solid var(--pc-color-theme-service-border);
}

.faq-list details:last-child {
  border-bottom: 0;
}

.faq-list summary {
  display: flex;
  min-height: 60px;
  cursor: pointer;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 0 28px;
  color: var(--pc-color-theme-service-text-primary);
  font-size: 15px;
  font-weight: 720;
  list-style: none;
}

.faq-list summary::-webkit-details-marker {
  display: none;
}

.faq-list summary::after {
  content: "+";
  color: var(--pc-color-semantic-text-accent);
  font-size: 24px;
  line-height: 1;
}

.faq-list details[open] summary::after {
  content: "-";
}

.faq-list p {
  margin: 0;
  padding: 0 28px 22px;
  color: var(--pc-color-theme-service-text-muted);
  font-size: 14px;
  line-height: 1.85;
}

.cookie-table {
  display: grid;
}

.cookie-option {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 142px;
  gap: 24px;
  align-items: center;
  min-height: 98px;
  padding: 18px 28px;
}

.cookie-option__text {
  display: grid;
  gap: 6px;
}

.cookie-option strong {
  color: var(--pc-color-theme-service-text-primary);
  font-size: 15px;
  font-weight: 720;
}

.cookie-option small,
.cookie-option em {
  color: var(--pc-color-theme-service-text-muted);
  font-size: 13px;
  font-style: normal;
  line-height: 1.6;
}

.cookie-option em {
  color: var(--pc-color-semantic-text-accent);
}

.cookie-toggle {
  display: grid;
  justify-items: end;
  gap: 8px;
}

.cookie-toggle input {
  position: relative;
  width: 52px;
  height: 28px;
  margin: 0;
  cursor: pointer;
  appearance: none;
  border: 1px solid var(--pc-color-theme-service-control);
  border-radius: 999px;
  background: var(--pc-color-theme-service-rail);
  transition: background-color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard), border-color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard);
}

.cookie-toggle input::after {
  position: absolute;
  top: 4px;
  left: 4px;
  width: 18px;
  height: 18px;
  content: "";
  border-radius: 999px;
  background: var(--pc-color-theme-service-text-subtle);
  transition: transform var(--pc-motion-duration-micro) var(--pc-motion-ease-standard), background-color var(--pc-motion-duration-micro) var(--pc-motion-ease-standard);
}

.cookie-toggle input:checked {
  border-color: var(--pc-color-semantic-action-primary);
  background: var(--pc-color-semantic-action-primary);
}

.cookie-toggle input:checked::after {
  transform: translateX(24px);
  background: var(--pc-color-theme-service-text-primary);
}

.cookie-toggle input:disabled {
  cursor: not-allowed;
}

.cookie-toggle span {
  color: var(--pc-color-theme-service-text-muted);
  font-size: 12px;
  font-weight: 700;
}

.cookie-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 20px 28px 24px;
}

.cookie-footer p {
  margin: 0;
  color: var(--pc-color-theme-service-text-muted);
  font-size: 13px;
  line-height: 1.7;
}

.cookie-footer button {
  min-width: 160px;
  padding: 0 18px;
}

.legal-footer {
  margin-bottom: 76px;
  padding: 26px 28px;
  border: 1px solid var(--pc-color-theme-service-border);
  border-radius: 8px;
  background: var(--pc-color-theme-service-rail);
}

.legal-footer h2 {
  margin: 0;
  color: var(--pc-color-theme-service-text-primary);
  font-size: 22px;
  font-weight: 740;
}

.legal-footer ul {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 22px;
  margin: 18px 0 0;
  padding: 0;
  list-style: none;
}

.legal-footer li {
  color: var(--pc-color-theme-service-text-legal);
  font-size: 13px;
  line-height: 1.55;
}

.legal-footer p {
  margin: 18px 0 0;
  color: var(--pc-color-theme-service-text-subtle);
  font-size: 13px;
  line-height: 1.7;
}

@media (max-width: 1080px) {
  .product-shortcuts {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .support-category:nth-child(n) {
    border-right: 0;
  }

  .support-category:nth-child(3n),
  .support-category:last-child {
    border-right: 1px solid var(--pc-color-theme-service-divider);
  }

  .agreement-layout {
    grid-template-columns: 1fr;
  }

  .agreement-nav {
    position: static;
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .agreement-nav strong,
  .agreement-nav button {
    grid-column: 1 / -1;
  }
}

@media (max-width: 760px) {
  .service-shell {
    width: min(100% - 28px, 1180px);
  }

  .support-hero {
    min-height: 380px;
  }

  .support-hero__inner {
    padding: 54px 0 48px;
  }

  .support-hero h1 {
    font-size: 42px;
  }

  .support-hero p {
    font-size: 15px;
  }

  .support-search {
    grid-template-columns: 22px minmax(0, 1fr);
  }

  .support-search button {
    grid-column: 1 / -1;
    width: 100%;
  }

  .product-shortcuts,
  .topic-grid,
  .contact-grid,
  .status-strip,
  .notice-panel,
  .legal-footer ul,
  .cookie-option,
  .cookie-footer {
    grid-template-columns: 1fr;
  }

  .support-category {
    min-height: 136px;
    border-right: 1px solid var(--pc-color-theme-service-divider);
  }

  .contact-card + .contact-card {
    border-top: 1px solid var(--pc-color-theme-service-divider-strong);
    border-left: 0;
  }

  .agreement-nav {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .policy-panel__summary {
    grid-template-columns: 42px minmax(0, 1fr) 24px;
    gap: 12px;
    padding: 14px 16px;
  }

  .summary-copy {
    grid-column: 2 / 3;
  }

  .summary-icon {
    grid-row: 1 / 3;
    grid-column: 3;
  }

  .clause-row {
    grid-template-columns: 1fr;
    gap: 12px;
    padding: 20px 18px;
  }

  .notice-panel,
  .policy-lead,
  .faq-list summary,
  .faq-list p,
  .cookie-option,
  .cookie-footer {
    padding-right: 18px;
    padding-left: 18px;
  }

  .cookie-footer {
    display: grid;
  }

  .cookie-toggle {
    justify-items: start;
  }
}

@media (max-width: 460px) {
  .agreement-nav {
    grid-template-columns: 1fr;
  }
}

@media print {
  .service-page {
    background: var(--pc-color-theme-service-print-canvas);
    color: var(--pc-color-theme-service-print-text);
  }

  .service-nav,
  .legal-rail,
  .service-command,
  .command-actions,
  .cookie-footer button {
    display: none;
  }

  .service-shell,
  .service-dashboard {
    width: 100%;
    display: block;
  }

  .policy-panel,
  .notice-panel,
  .compliance-strip {
    break-inside: avoid;
    border-color: var(--pc-color-theme-service-print-border);
    background: var(--pc-color-theme-service-print-canvas);
    color: var(--pc-color-theme-service-print-text);
  }
}
</style>
