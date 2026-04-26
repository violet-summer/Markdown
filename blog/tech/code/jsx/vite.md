
# Vite使用手册

代理可以在开发中避免同源访问的限制问题，利好，不需要我搞两个ip地址。

1. 使用/根路径，避免相对页面的路径补全干扰
2. vite server是在服务端，其代理可在服务端向java端发送请求，而不是直接在客户端。

## Vite 代理完全指南

### 第一部分：核心概念


#### 1.1 什么是 Vite 代理？
Vite 代理是在**开发服务器端**运行的请求转发机制。它接收浏览器的请求，根据配置的路径规则，将请求转发到其他后端服务。

#### 1.2 两个独立的过程
```
[浏览器端]              [Vite服务器端]              [目标服务]
    ↓                         ↓                         ↓
路径补全规则             代理匹配规则                实际处理
    ↓                         ↓                         ↓
相对路径 → 完整URL      请求路径 → 转发目标        Java/文件服务
```

### 第二部分：Vite 代理配置详解

#### 2.1 基础配置结构
```typescript
// vite.config.ts
import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    proxy: {
      // 路径前缀: 配置对象
      '/api': {
        target: 'http：//localhost:8080',  // 目标服务器地址
        changeOrigin: true,                 // 改变请求头中的Origin
        // 其他选项...
      }
    }
  }
})
```

#### 2.2 完整配置选项
```typescript
proxy: {
  '/api': {
    // 必需：目标服务器地址
    target: 'http：//localhost:8080',
    
    // 可选：改变请求头中的Origin字段（解决跨域）
    changeOrigin: true,
    
    // 可选：重写路径
    rewrite: (path) => path.replace(/^\/api/, ''),
    
    // 可选：添加请求头
    headers: {
      'X-Proxy-By': 'Vite',
      'X-Forwarded-For': 'proxy'
    },
    
    // 可选：超时设置（毫秒）
    timeout: 5000,
    proxyTimeout: 5000,
    
    // 可选：WebSocket支持
    ws: true,
    
    // 可选：忽略SSL证书错误
    secure: false,
    
    // 可选：cookie域名重写
    cookieDomainRewrite: {
      '*': '',  // 移除所有cookie域名
      'localhost': 'mysite.com'
    },
    
    // 可选：自定义代理行为
    configure: (proxy, options) => {
      // 监听代理事件
      proxy.on('proxyReq', (proxyReq, req, res) => {
        console.log('代理请求：', req.method, req.url)
      })
      
      proxy.on('proxyRes', (proxyRes, req, res) => {
        console.log('代理响应：', proxyRes.statusCode)
      })
      
      proxy.on('error', (err, req, res) => {
        console.error('代理错误：', err)
      })
    }
  }
}
```

### 第三部分：路径匹配规则

#### 3.1 前缀匹配（最常用）
```typescript
proxy: {
  // 匹配所有以 /api 开头的请求
  '/api': {
    target: 'http：//localhost:8080'
  },
  
  // 匹配所有以 /files 开头的请求
  '/files': {
    target: 'http：//localhost:9000'
  }
}

// 示例匹配：
// /api/users      → 匹配
// /api/login      → 匹配  
// /api/v1/products → 匹配
// /files/123.pdf  → 匹配
// /index.html     → 不匹配
```

#### 3.2 通配符匹配
```typescript
proxy: {
  // 匹配所有以 /api/ 开头的请求
  '/api/**': {
    target: 'http：//localhost:8080'
  },
  
  // 匹配 /user 或 /users
  '/user[s]?': {
    target: 'http：//localhost:8081'
  },
  
  // 匹配任意三级路径
  '/*/api/**': {
    target: 'http：//localhost:8082'
  }
}
```

#### 3.3 多路径匹配
```typescript
proxy: {
  // 方法1：分别配置
  '/api': { target: 'http：//localhost:8080' },
  '/rest': { target: 'http：//localhost:8080' },
  
  // 方法2：正则表达式
  '^/(api|rest)/.*': {
    target: 'http：//localhost:8080'
  }
}
```

#### 3.4 排除特定路径
```typescript
proxy: {
  // 匹配所有 /api 开头的，除了 /api/public
  '/api': {
    target: 'http：//localhost:8080',
    bypass: (req, res, options) => {
      if (req.url.startsWith('/api/public')) {
        return false  // 不代理，直接返回
      }
    }
  }
}
```

### 第四部分：路径重写规则

#### 4.1 移除前缀
```typescript
proxy: {
  '/api': {
    target: 'http：//localhost:8080',
    rewrite: (path) => path.replace(/^\/api/, '')
  }
}

// 请求：/api/users/123
// 转发：http：//localhost:8080/users/123
```

#### 4.2 替换路径
```typescript
proxy: {
  '/files': {
    target: 'http：//localhost:9000',
    rewrite: (path) => path.replace(/^\/files/, '/download')
  }
}

// 请求：/files/123.pdf
// 转发：http：//localhost:9000/download/123.pdf
```

#### 4.3 添加前缀
```typescript
proxy: {
  '/api': {
    target: 'http：//localhost:8080',
    rewrite: (path) => `/v1${path}`
  }
}

// 请求：/api/users
// 转发：http：//localhost:8080/v1/api/users
```

#### 4.4 条件重写
```typescript
proxy: {
  '/api': {
    target: 'http：//localhost:8080',
    rewrite: (path) => {
      if (path.startsWith('/api/v1')) {
        return path.replace('/api/v1', '/v1')
      }
      if (path.startsWith('/api/v2')) {
        return path.replace('/api/v2', '/v2')
      }
      return path.replace('/api', '/legacy')
    }
  }
}
```

### 第五部分：浏览器路径补全（与代理的配合）

#### 5.1 路径补全规则表
```javascript
// 当前页面：http：//frp.com:12345/layout/dashboard

写法               补全后路径                    代理匹配
─────────────────────────────────────────────────────────
'/files/123.pdf' → '/files/123.pdf'            ✅ 匹配
'files/123.pdf'  → '/layout/dashboard/files/123.pdf' ❌ 不匹配
'./files/123.pdf' → '/layout/dashboard/files/123.pdf' ❌ 不匹配
'../files/123.pdf' → '/layout/files/123.pdf'    ❌ 不匹配
```

#### 5.2 为什么只有 `/files` 能匹配？
```typescript
// 代理规则基于路径前缀
'/files' 规则匹配以 /files 开头的路径

✅ /files/123.pdf          → 以 /files 开头
✅ /files/list/all         → 以 /files 开头
❌ /layout/files/123.pdf   → 以 /layout 开头
❌ /api/files/123.pdf      → 以 /api 开头
```

### 第六部分：完整工作流程

#### 6.1 通过 frp 访问的场景
```
[主机B浏览器]
页面地址：http：//frp-server.com:12345/layout
    ↓ 执行 fetch('/files/123.pdf')
    ↓ 浏览器补全
完整URL：http：//frp-server.com:12345/files/123.pdf
    ↓
[frp 转发]
目标：主机A的Vite服务器 (192.168.1.100:5173)
    ↓
[Vite服务器]
收到请求：http：//192.168.1.100:5173/files/123.pdf
    ↓ 提取路径：/files/123.pdf
    ↓ 匹配代理规则：'/files' → 'http：//127.0.0.1:9000'
    ↓ 转发
[内容服务器]
http：//127.0.0.1:9000/files/123.pdf
    ↓ 处理请求
返回文件数据
    ↓
[响应原路返回]
内容服务器 → Vite → frp → 主机B浏览器 ✅
```

#### 6.2 本地直接访问的场景
```
[主机A浏览器]
页面地址：http：//localhost:5173/layout
    ↓ 执行 fetch('/files/123.pdf')
    ↓ 浏览器补全
完整URL：http：//localhost:5173/files/123.pdf
    ↓ 直接发送
[Vite服务器]
收到请求：http：//localhost:5173/files/123.pdf
    ↓ 提取路径：/files/123.pdf
    ↓ 匹配代理规则：'/files' → 'http：//127.0.0.1:9000'
    ↓ 转发
[内容服务器]
http：//127.0.0.1:9000/files/123.pdf
    ↓ 处理请求
返回文件数据
    ↓
[响应]
内容服务器 → Vite → 主机A浏览器 ✅
```

### 第七部分：多服务代理配置

#### 7.1 基础多服务配置
```typescript
proxy: {
  // Java后端服务
  '/api': {
    target: 'http：//127.0.0.1:8080',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '')
  },
  
  // 文件服务
  '/files': {
    target: 'http：//127.0.0.1:9000',
    changeOrigin: true
  },
  
  // 静态资源
  '/assets': {
    target: 'http：//127.0.0.1:5173',
    changeOrigin: true
  },
  
  // 地图服务
  '/maps': {
    target: 'http：//127.0.0.1:8082',
    changeOrigin: true
  }
}
```

#### 7.2 带版本号的 API
```typescript
proxy: {
  // v1 API
  '/api/v1': {
    target: 'http：//127.0.0.1:8080',
    rewrite: (path) => path.replace(/^\/api\/v1/, '/v1')
  },
  
  // v2 API
  '/api/v2': {
    target: 'http：//127.0.0.1:8081',
    rewrite: (path) => path.replace(/^\/api\/v2/, '/v2')
  }
}
```

#### 7.3 微服务架构
```typescript
proxy: {
  // 用户服务
  '/api/users': {
    target: 'http：//127.0.0.1:8081',
    rewrite: (path) => path.replace(/^\/api\/users/, '')
  },
  
  // 订单服务
  '/api/orders': {
    target: 'http：//127.0.0.1:8082',
    rewrite: (path) => path.replace(/^\/api\/orders/, '')
  },
  
  // 支付服务
  '/api/payments': {
    target: 'http：//127.0.0.1:8083',
    rewrite: (path) => path.replace(/^\/api\/payments/, '')
  },
  
  // 文件服务
  '/files': {
    target: 'http：//127.0.0.1:9000'
  }
}
```

### 第八部分：环境配置

#### 8.1 不同环境不同配置
```typescript
// vite.config.ts
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ command, mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd())
  
  // 根据环境配置代理
  const proxyConfig = {
    // 开发环境
    development: {
      '/api': {
        target: 'http：//127.0.0.1:8080',
        changeOrigin: true
      },
      '/files': {
        target: 'http：//127.0.0.1:9000',
        changeOrigin: true
      }
    },
    
    // 测试环境
    staging: {
      '/api': {
        target: 'http：//test-server:8080',
        changeOrigin: true
      },
      '/files': {
        target: 'http：//test-files:9000',
        changeOrigin: true
      }
    },
    
    // 生产环境（生产环境通常用nginx，这里只是示例）
    production: {
      '/api': {
        target: 'http：//backend:8080',
        changeOrigin: true
      }
    }
  }
  
  return {
    server: {
      proxy: proxyConfig[mode] || proxyConfig.development
    }
  }
})
```

#### 8.2 使用环境变量
```typescript
// .env.development
VITE_API_TARGET=http：//127.0.0.1:8080
VITE_FILES_TARGET=http：//127.0.0.1:9000
VITE_API_PREFIX=/api
VITE_FILES_PREFIX=/files

// .env.staging
VITE_API_TARGET=http：//staging-api:8080
VITE_FILES_TARGET=http：//staging-files:9000
VITE_API_PREFIX=/api
VITE_FILES_PREFIX=/files

// vite.config.ts
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  
  return {
    server: {
      proxy: {
        [env.VITE_API_PREFIX]: {
          target: env.VITE_API_TARGET,
          changeOrigin: true
        },
        [env.VITE_FILES_PREFIX]: {
          target: env.VITE_FILES_TARGET,
          changeOrigin: true
        }
      }
    }
  }
})
```

### 第九部分：高级功能

#### 9.1 WebSocket 代理
```typescript
proxy: {
  '/ws': {
    target: 'ws：//127.0.0.1:8080',
    ws: true,  // 启用 WebSocket 代理
    changeOrigin: true,
    // WebSocket 特定配置
    onProxyReqWs: (proxyReq, req, socket, options, head) => {
      console.log('WebSocket 连接：', req.url)
    }
  }
}
```

#### 9.2 HTTPS 代理
```typescript
proxy: {
  '/api': {
    target: 'https：//secure-server:8443',
    secure: false,  // 忽略自签名证书错误
    changeOrigin: true,
    // HTTPS 特定配置
    agent: new https.Agent({
      rejectUnauthorized: false
    })
  }
}
```

#### 9.3 负载均衡
```typescript
proxy: {
  '/api': {
    target: 'http：//127.0.0.1:8080',
    changeOrigin: true,
    // 简单的轮询负载均衡
    configure: (proxy) => {
      const targets = [
        'http：//127.0.0.1:8081',
        'http：//127.0.0.1:8082',
        'http：//127.0.0.1:8083'
      ]
      let current = 0
      
      proxy.on('proxyReq', (proxyReq, req) => {
        const target = targets[current]
        current = (current + 1) % targets.length
        proxyReq.setHeader('X-Target-Server', target)
      })
    }
  }
}
```

#### 9.4 请求/响应拦截
```typescript
proxy: {
  '/api': {
    target: 'http：//127.0.0.1:8080',
    configure: (proxy) => {
      // 请求拦截
      proxy.on('proxyReq', (proxyReq, req, res) => {
        // 添加认证token
        proxyReq.setHeader('Authorization', 'Bearer xxx')
        
        // 记录请求
        console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`)
      })
      
      // 响应拦截
      proxy.on('proxyRes', (proxyRes, req, res) => {
        // 添加自定义响应头
        proxyRes.headers['X-Proxy-Cache'] = 'HIT'
        
        // 修改响应内容
        let body = []
        proxyRes.on('data', (chunk) => {
          body.push(chunk)
        })
        
        proxyRes.on('end', () => {
          body = Buffer.concat(body).toString()
          // 可以在这里修改响应内容
          console.log(`响应大小：${body.length} bytes`)
        })
      })
    }
  }
}
```

### 第十部分：调试与问题排查

#### 10.1 开启代理调试
```bash
# 命令行启动时
vite --debug proxy

# 或设置环境变量
DEBUG=vite:proxy vite
```

#### 10.2 配置详细日志
```typescript
proxy: {
  '/api': {
    target: 'http：//127.0.0.1:8080',
    configure: (proxy) => {
      // 记录所有代理事件
      proxy.on('proxyReq', (proxyReq, req) => {
        console.log('\n=== 代理请求 ===')
        console.log('方法：', req.method)
        console.log('原始URL：', req.url)
        console.log('转发URL：', proxyReq.path)
        console.log('头部：', proxyReq.getHeaders())
      })
      
      proxy.on('proxyRes', (proxyRes, req) => {
        console.log('\n=== 代理响应 ===')
        console.log('状态码：', proxyRes.statusCode)
        console.log('状态消息：', proxyRes.statusMessage)
        console.log('头部：', proxyRes.headers)
      })
      
      proxy.on('error', (err, req, res) => {
        console.error('\n=== 代理错误 ===')
        console.error('错误：', err)
      })
    }
  }
}
```

#### 10.3 常见问题排查表

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 404 Not Found | 路径不匹配或重写错误 | 检查代理规则和 rewrite 配置 |
| ECONNREFUSED | 目标服务未启动 | 启动目标服务或检查端口 |
| CORS 错误 | 未设置 changeOrigin | 设置 `changeOrigin: true` |
| 请求超时 | 服务响应慢 | 增加 timeout 配置 |
| WebSocket 失败 | 未启用 ws 选项 | 设置 `ws: true` |
| 无限重定向 | 路径重写错误 | 检查 rewrite 逻辑 |
| 证书错误 | 自签名证书 | 设置 `secure: false` |
| Cookie 丢失 | cookieDomainRewrite | 配置 cookieDomainRewrite |

#### 10.4 浏览器端调试
```javascript
// 在浏览器控制台执行
function debugProxy(path) {
  console.log('测试路径：', path)
  
  // 查看补全后的完整URL
  const fullUrl = new URL(path, window.location.href)
  console.log('完整URL：', fullUrl.href)
  console.log('请求路径：', fullUrl.pathname)
  
  // 判断是否能匹配代理
  const hasProxy = fullUrl.pathname.startsWith('/files') ||
                   fullUrl.pathname.startsWith('/api')
  console.log('代理匹配：', hasProxy ? '✅' : '❌')
  
  // 发送测试请求
  fetch(path, { method: 'HEAD' })
    .then(res => {
      console.log('响应状态：', res.status)
      console.log('响应URL：', res.url)
      console.log('是否通过代理：', res.url.includes('127.0.0.1') ? '是' : '否')
    })
    .catch(err => {
      console.log('请求失败：', err.message)
    })
}

// 测试不同写法
debugProxy('/files/test.txt')
debugProxy('files/test.txt')
debugProxy('./files/test.txt')
debugProxy('../files/test.txt')
```

### 第十一部分：前端最佳实践

#### 11.1 封装请求函数
```typescript
// api/client.ts
class ApiClient {
  private baseURL: string
  
  constructor() {
    // 使用相对路径，让Vite代理处理
    this.baseURL = ''
  }
  
  // GET请求
  async get(path: string) {
    // 确保路径以 / 开头
    const safePath = path.startsWith('/') ? path : `/${path}`
    const response = await fetch(safePath)
    return response.json()
  }
  
  // 文件下载
  async download(fileId: string) {
    const response = await fetch(`/files/${fileId}`)
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = fileId
    a.click()
    window.URL.revokeObjectURL(url)
  }
  
  // 上传文件
  async upload(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    const response = await fetch('/files/upload', {
      method: 'POST',
      body: formData
    })
    return response.json()
  }
}

export const api = new ApiClient()
```

#### 11.2 服务化封装
```typescript
// services/api.service.ts
export const ApiService = {
  // 用户服务
  users: {
    list: () => fetch('/api/users').then(r => r.json()),
    get: (id: number) => fetch(`/api/users/${id}`).then(r => r.json()),
    create: (data: any) => fetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
  },
  
  // 文件服务
  files: {
    get: (id: string) => fetch(`/files/${id}`),
    upload: (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return fetch('/files/upload', {
        method: 'POST',
        body: formData
      })
    },
    delete: (id: string) => fetch(`/files/${id}`, { method: 'DELETE' })
  },
  
  // 订单服务
  orders: {
    list: () => fetch('/api/orders').then(r => r.json()),
    get: (id: number) => fetch(`/api/orders/${id}`).then(r => r.json())
  }
}
```

#### 11.3 类型安全的请求
```typescript
// types/api.ts
interface User {
  id: number
  name: string
  email: string
}

interface FileInfo {
  id: string
  name: string
  size: number
  type: string
}

// services/typed-api.ts
export const TypedApi = {
  users: {
    list: (): Promise<User[]> => 
      fetch('/api/users').then(r => r.json()),
    
    get: (id: number): Promise<User> => 
      fetch(`/api/users/${id}`).then(r => r.json())
  },
  
  files: {
    info: (id: string): Promise<FileInfo> => 
      fetch(`/files/${id}/info`).then(r => r.json()),
    
    download: (id: string): Promise<Blob> => 
      fetch(`/files/${id}`).then(r => r.blob())
  }
}
```

### 第十二部分：完整配置示例

#### 12.1 开发环境完整配置
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  
  server: {
    // 服务器配置
    host: '0.0.0.0',  // 监听所有网络接口
    port: 5173,        // 开发服务器端口
    strictPort: true,  // 端口被占用时退出
    
    // CORS配置
    cors: true,
    
    // 代理配置
    proxy: {
      // Java后端API
      '/api': {
        target: 'http：//127.0.0.1:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        configure: (proxy) => {
          proxy.on('proxyReq', (proxyReq, req) => {
            console.log(`[API] ${req.method} ${req.url}`)
          })
        }
      },
      
      // 文件服务
      '/files': {
        target: 'http：//127.0.0.1:9000',
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on('proxyReq', (proxyReq, req) => {
            console.log(`[FILES] ${req.method} ${req.url}`)
          })
        }
      },
      
      // 静态资源（图片等）
      '/assets': {
        target: 'http：//127.0.0.1:5173',
        changeOrigin: true
      },
      
      // WebSocket
      '/ws': {
        target: 'ws：//127.0.0.1:8080',
        ws: true,
        changeOrigin: true
      }
    },
    
    // 文件监听配置
    watch: {
      usePolling: true,
      interval: 1000
    }
  },
  
  // 构建配置
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true
  }
})
```

#### 12.2 前端入口文件
```typescript
// main.ts
import { createApp } from 'vue'
import App from './App.vue'

// 全局请求配置
const app = createApp(App)

// 添加全局请求方法
app.config.globalProperties.$api = {
  // Java服务
  java: (path: string) => fetch(`/api${path}`),
  
  // 文件服务  
  file: (id: string) => fetch(`/files/${id}`),
  
  // 上传
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return fetch('/files/upload', {
      method: 'POST',
      body: formData
    })
  }
}

app.mount('#app')
```

### 第十三部分：核心原则总结

#### 13.1 Vite代理配置三要素
```typescript
1. 路径前缀：'/api'、'/files' 等
2. 目标地址：target: 'http：//127.0.0.1:8080'
3. 跨域设置：changeOrigin: true
```

#### 13.2 前端请求黄金法则
```javascript
// ✅ 总是用 / 开头
fetch('/api/users')        // Java服务
fetch('/files/123.pdf')    // 文件服务
fetch('/assets/logo.png')  // 静态资源

// ❌ 永远不要
fetch('api/users')         // 受当前路径影响
fetch('./files/123.pdf')   // 受当前路径影响
fetch('../files/123.pdf')  // 依赖页面层级
```

#### 13.3 代理工作流程图
```
[前端代码]
    ↓ 使用 / 开头路径
[浏览器补全]
    ↓ 补全为当前域名 + 路径
[Vite服务器]
    ↓ 匹配路径前缀
    ↓ 转发到目标服务
[后端服务]
    ↓ 处理请求
    ↓ 返回响应
[Vite服务器]
    ↓ 转发响应
[浏览器]
```

#### 13.4 最终检查清单
- [ ] 代理配置中的路径前缀是否与前端请求一致？
- [ ] 前端请求是否都以 `/` 开头？
- [ ] 目标服务是否已启动且端口正确？
- [ ] `changeOrigin` 是否设置为 `true`？
- [ ] 是否需要路径重写？
- [ ] 是否开启了代理调试以便排查问题？

**记住**：Vite代理是开发环境的利器，正确使用能让前后端分离开发变得简单高效。关键是理解**路径补全**和**代理匹配**这两个独立的过程，并始终使用以 `/` 开头的绝对路径。