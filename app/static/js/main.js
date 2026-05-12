async function requestItem(itemId) {
  const res = await fetch(`/api/transactions/request/${itemId}`, { method: 'POST' });
  const data = await res.json();
  alert(data.success ? 'Request sent to seller.' : data.error);
  if (data.success) location.reload();
}

async function updateTxn(txnId, status) {
  const res = await fetch(`/api/transactions/${txnId}/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  });
  const data = await res.json();
  alert(data.success ? 'Transaction updated.' : data.error);
  if (data.success) location.reload();
}

async function sendMessage(userId) {
  const input = document.getElementById('chatInput');
  const button = document.getElementById('chatSendButton');
  const content = input.value.trim();
  if (!content) return;

  const pendingId = `pending-${Date.now()}`;
  if (window.appendChatMessage) {
    window.appendChatMessage({
      id: pendingId,
      sender_id: window.currentChatUserId,
      sender_name: window.currentChatUserName || 'Me',
      content
    });
  }
  input.value = '';
  input.disabled = true;
  if (button) button.disabled = true;
  try {
    const res = await fetch(`/api/messages/${userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    });
    const data = await res.json();
    if (!data.success) {
      document.getElementById(`message-${pendingId}`)?.remove();
      input.value = content;
      alert(data.error || 'Failed to send message.');
      return;
    }
    document.getElementById(`message-${pendingId}`)?.remove();
    if (window.appendChatMessage && data.message) {
      window.appendChatMessage(data.message);
    }
  } catch (error) {
    document.getElementById(`message-${pendingId}`)?.remove();
    input.value = content;
    alert('Failed to send message. Please try again.');
  } finally {
    input.disabled = false;
    if (button) button.disabled = false;
    input.focus();
  }
}

function startChatPolling(otherUserId, currentUserId, currentUserName) {
  const box = document.getElementById('chatBox');
  const input = document.getElementById('chatInput');
  const form = document.getElementById('chatForm');
  if (!box) return;

  window.currentChatUserId = currentUserId;
  window.currentChatUserName = currentUserName;

  const appendMessage = (message) => {
    if (document.getElementById(`message-${message.id}`)) return;
    const div = document.createElement('div');
    div.id = `message-${message.id}`;
    div.className = `chat-msg ${message.sender_id === currentUserId ? 'me' : 'them'}`;
    const sender = document.createElement('small');
    sender.textContent = `${message.sender_name}: `;
    div.appendChild(sender);
    div.append(document.createTextNode(message.content));
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
  };

  const render = (messages) => {
    for (const m of messages) appendMessage(m);
  };

  const poll = async () => {
    const res = await fetch(`/api/messages/${otherUserId}`);
    if (!res.ok) return;
    const data = await res.json();
    render(data);
  };

  window.refreshChatMessages = poll;
  window.appendChatMessage = appendMessage;
  if (form) {
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      sendMessage(otherUserId);
    });
  }

  poll();
  setInterval(poll, 3000);
}

document.addEventListener('DOMContentLoaded', () => {
  const chatPage = document.getElementById('chatPage');
  if (!chatPage) return;

  startChatPolling(
    Number(chatPage.dataset.otherUserId),
    Number(chatPage.dataset.currentUserId),
    chatPage.dataset.currentUserName
  );
});

async function rateUser(ratedUserId, transactionId) {
  const score = prompt('Give rating (1-5):');
  if (!score) return;
  const comment = prompt('Optional comment:') || '';

  const res = await fetch('/api/ratings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rated_user_id: ratedUserId, transaction_id: transactionId, score: Number(score), comment })
  });
  const data = await res.json();
  alert(data.success ? 'Rating submitted.' : data.error);
}
