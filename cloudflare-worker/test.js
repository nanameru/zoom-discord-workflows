/**
 * ローカルテスト用スクリプト
 * 
 * 使い方:
 * 1. wrangler dev でWorkerを起動
 * 2. node test.js を実行
 */

const WORKER_URL = 'http://localhost:8787'

// カラー出力
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m'
}

async function test(name, testFn) {
  console.log(`\n${colors.blue}Testing: ${name}${colors.reset}`)
  try {
    await testFn()
    console.log(`${colors.green}✅ PASSED${colors.reset}`)
  } catch (error) {
    console.log(`${colors.red}❌ FAILED: ${error.message}${colors.reset}`)
  }
}

async function testEndpointValidation() {
  const response = await fetch(WORKER_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event: 'endpoint.url_validation',
      payload: {
        plainToken: 'test_plain_token',
        encryptedToken: 'test_encrypted_token'
      }
    })
  })

  const data = await response.json()
  
  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`)
  }
  
  if (data.plainToken !== 'test_plain_token') {
    throw new Error('plainToken mismatch')
  }
  
  if (data.encryptedToken !== 'test_encrypted_token') {
    throw new Error('encryptedToken mismatch')
  }
  
  console.log('Response:', data)
}

async function testRecordingCompleted() {
  const response = await fetch(WORKER_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event: 'recording.completed',
      payload: {
        object: {
          uuid: 'test-uuid-12345',
          topic: 'テスト講義タイトル',
          duration: 45,
          start_time: '2025-01-10T10:00:00Z',
          host_email: 'test@example.com'
        }
      }
    })
  })

  const data = await response.json()
  
  console.log('Response:', data)
  
  if (response.status !== 200 && response.status !== 500) {
    throw new Error(`Expected status 200 or 500, got ${response.status}`)
  }
  
  // GitHub APIが失敗してもWorker自体は動作している
  if (data.success === false) {
    console.log(`${colors.yellow}⚠️  GitHub API call failed (expected if token not set)${colors.reset}`)
  }
}

async function testInvalidMethod() {
  const response = await fetch(WORKER_URL, {
    method: 'GET'
  })

  if (response.status !== 405) {
    throw new Error(`Expected status 405, got ${response.status}`)
  }
}

async function testUnknownEvent() {
  const response = await fetch(WORKER_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event: 'unknown.event',
      payload: {}
    })
  })

  if (response.status !== 200) {
    throw new Error(`Expected status 200, got ${response.status}`)
  }
}

async function runTests() {
  console.log(`${colors.blue}=== Cloudflare Worker Tests ===${colors.reset}`)
  console.log(`Testing against: ${WORKER_URL}`)
  console.log(`Make sure 'wrangler dev' is running!\n`)

  await test('Endpoint Validation', testEndpointValidation)
  await test('Recording Completed', testRecordingCompleted)
  await test('Invalid HTTP Method', testInvalidMethod)
  await test('Unknown Event', testUnknownEvent)

  console.log(`\n${colors.blue}=== Tests Complete ===${colors.reset}\n`)
}

runTests().catch(error => {
  console.error(`${colors.red}Test runner error:${colors.reset}`, error)
  process.exit(1)
})

