/**
 * Cloudflare Worker: Zoom Webhook to GitHub Actions Bridge
 * 
 * このWorkerはZoom WebhookからGitHub Actions repository_dispatchへの橋渡しを行います
 */

// 設定（Cloudflare Workers環境変数で設定）
const GITHUB_TOKEN = GITHUB_PAT; // 環境変数から取得
const GITHUB_OWNER = 'nanameru'; // あなたのGitHubユーザー名
const GITHUB_REPO = 'zoom-discord-workflows'; // リポジトリ名

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

/**
 * メインのリクエストハンドラー
 */
async function handleRequest(request) {
  // CORS対応
  if (request.method === 'OPTIONS') {
    return handleCORS()
  }

  // POSTメソッドのみ受け付ける
  if (request.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 })
  }

  try {
    const body = await request.json()
    
    // Zoomのエンドポイント検証リクエスト（初回設定時）
    if (body.event === 'endpoint.url_validation') {
      console.log('📝 Zoom endpoint validation')
      return handleZoomValidation(body)
    }

    // 録画完了イベント
    if (body.event === 'recording.completed') {
      console.log('🎥 Recording completed event received')
      return await handleRecordingCompleted(body)
    }

    // その他のイベントはログのみ
    console.log(`ℹ️ Received event: ${body.event}`)
    return new Response('Event received but not processed', { status: 200 })

  } catch (error) {
    console.error('❌ Error:', error)
    return new Response(JSON.stringify({ 
      error: 'Internal Server Error',
      message: error.message 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}

/**
 * Zoomのエンドポイント検証を処理
 */
function handleZoomValidation(body) {
  const response = {
    plainToken: body.payload.plainToken,
    encryptedToken: body.payload.encryptedToken
  }
  
  return new Response(JSON.stringify(response), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })
}

/**
 * 録画完了イベントを処理してGitHub Actionsをトリガー
 */
async function handleRecordingCompleted(body) {
  const payload = body.payload.object
  
  // 録画情報を抽出
  const meetingUUID = payload.uuid
  const meetingTopic = payload.topic || 'Untitled Meeting'
  const duration = payload.duration || 0
  const startTime = payload.start_time
  const hostEmail = payload.host_email
  
  console.log(`📊 Meeting: ${meetingTopic}`)
  console.log(`⏱️  Duration: ${duration} minutes`)
  console.log(`🆔 UUID: ${meetingUUID}`)

  // GitHub repository_dispatchをトリガー
  const githubResponse = await triggerGitHubActions({
    meeting_uuid: meetingUUID,
    meeting_topic: meetingTopic,
    duration: duration,
    start_time: startTime,
    host_email: hostEmail
  })

  if (githubResponse.ok) {
    console.log('✅ GitHub Actions triggered successfully')
    return new Response(JSON.stringify({ 
      success: true,
      message: 'GitHub Actions triggered',
      meeting_uuid: meetingUUID
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    })
  } else {
    console.error('❌ Failed to trigger GitHub Actions')
    const errorText = await githubResponse.text()
    console.error('Error details:', errorText)
    
    return new Response(JSON.stringify({ 
      success: false,
      error: 'Failed to trigger GitHub Actions',
      details: errorText
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}

/**
 * GitHub Actions repository_dispatchをトリガー
 */
async function triggerGitHubActions(clientPayload) {
  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/dispatches`
  
  const body = {
    event_type: 'zoom_recording_completed',
    client_payload: clientPayload
  }

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${GITHUB_TOKEN}`,
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'Cloudflare-Worker-Zoom-Bridge',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  })

  return response
}

/**
 * CORSプリフライトリクエストを処理
 */
function handleCORS() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '86400'
    }
  })
}

