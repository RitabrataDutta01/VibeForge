(function () {
  var FALLBACK = "Sorry, I couldn't process that. Please try again.";

  function getCsrfToken() {
    var input = document.querySelector('#chatbot-form input[name=csrfmiddlewaretoken]');
    return input ? input.value : '';
  }

  function fetchReply(message) {
    return fetch('/chatbot/reply/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ message: message }),
    })
      .then(function (res) {
        if (!res.ok) throw new Error('Request failed');
        return res.json();
      })
      .then(function (data) {
        return data.reply || FALLBACK;
      })
      .catch(function () {
        return FALLBACK;
      });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var launcher = document.getElementById('chatbot-launcher');
    var panel = document.getElementById('chatbot-panel');
    var closeBtn = document.getElementById('chatbot-close');
    var messagesEl = document.getElementById('chatbot-messages');
    var suggestionsEl = document.getElementById('chatbot-suggestions');
    var form = document.getElementById('chatbot-form');
    var input = document.getElementById('chatbot-input');
    var sendBtn = document.getElementById('chatbot-send');
    var statusEl = document.getElementById('chatbot-status');

    if (!launcher || !panel) return;

    var messages = [];
    var typing = false;

    function renderMessages() {
      messagesEl.innerHTML = '';
      messages.forEach(function (m) {
        var bubble = document.createElement('div');
        bubble.className = 'bubble bubble--' + m.from;
        bubble.textContent = m.text;
        messagesEl.appendChild(bubble);
      });
      if (typing) {
        var typingBubble = document.createElement('div');
        typingBubble.className = 'bubble bubble--bot bubble--typing';
        typingBubble.innerHTML = '<span></span><span></span><span></span>';
        messagesEl.appendChild(typingBubble);
      }
      messagesEl.scrollTop = messagesEl.scrollHeight;
      if (suggestionsEl) {
        suggestionsEl.style.display = messages.length < 2 ? 'flex' : 'none';
      }
    }

    function addMessage(from, text) {
      messages.push({ from: from, text: text });
      renderMessages();
    }

    function setTyping(val) {
      typing = val;
      if (statusEl) {
        statusEl.textContent = typing ? 'typing…' : 'HR assistant · online';
      }
      renderMessages();
    }

    function send(text) {
      var trimmed = (text || '').trim();
      if (!trimmed) return;
      addMessage('user', trimmed);
      input.value = '';
      sendBtn.disabled = true;
      setTyping(true);
      fetchReply(trimmed).then(function (reply) {
        setTyping(false);
        addMessage('bot', reply);
        sendBtn.disabled = !input.value.trim();
      });
    }

    launcher.addEventListener('click', function () {
      panel.classList.add('chatbot__panel--open');
      launcher.classList.add('chatbot__launcher--hidden');
      input.focus();
    });

    closeBtn.addEventListener('click', function () {
      panel.classList.remove('chatbot__panel--open');
      launcher.classList.remove('chatbot__launcher--hidden');
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      send(input.value);
    });

    input.addEventListener('input', function () {
      sendBtn.disabled = !input.value.trim();
    });

    if (suggestionsEl) {
      Array.prototype.forEach.call(suggestionsEl.querySelectorAll('.chatbot__chip'), function (chip) {
        chip.addEventListener('click', function () {
          send(chip.textContent);
        });
      });
    }

    var greetName = launcher.getAttribute('data-username') || 'there';
    addMessage('bot', "Hi " + greetName + ", I'm Ember. Ask me anything.");
  });
})();