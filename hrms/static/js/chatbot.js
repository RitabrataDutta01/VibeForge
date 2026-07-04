
(function () {
  var RULES = [
    {
      keywords: ['pending leave', 'pending request', 'leave approvals', 'awaiting approval'],
      reply: "There are 6 leave requests awaiting your review — 4 Paid, 1 Sick, 1 Unpaid. Want me to open the approvals queue?",
    },
    {
      keywords: ['approve', 'reject', 'decision on'],
      reply: "I can pull up any request by employee name so you can approve or reject it with a comment. Who would you like to review first?",
    },
    {
      keywords: ['attendance today', 'who is absent', 'absentees', 'checked in today', 'team attendance'],
      reply: "Today: 42 checked in, 3 on approved leave, 2 absent without a request — Rohit Sen and Priya Nair. Want their contact details?",
    },
    {
      keywords: ['attendance summary', 'monthly attendance', 'attendance report'],
      reply: "This month's average attendance across the team is 94%. Engineering is highest at 97%, Sales is lowest at 88%.",
    },
    {
      keywords: ['payroll', 'salary', 'payslip', 'ctc', 'update salary', 'salary structure'],
      reply: "Payroll for June has been processed for all 47 employees. To update a salary structure, tell me the employee's name and the new figures.",
    },
    {
      keywords: ['new employee', 'onboard', 'add employee', 'employee list'],
      reply: "There are 47 active employees, with 2 pending onboarding — their documents are still under verification. Want the full list?",
    },
    {
      keywords: ['holiday', 'holidays', 'public holiday'],
      reply: "The next company holiday is Independence Day on Aug 15th. Want to publish it to the team calendar?",
    },
    {
      keywords: ['hello', 'hi', 'hey'],
      reply: "Hey — I'm Ember, your HR assistant. Ask me about approvals, attendance, or payroll for the team.",
    },
    {
      keywords: ['thank', 'thanks'],
      reply: "Anytime — that's what I'm here for. \uD83C\uDF3F",
    },
  ];

  var FALLBACK = "I don't have an answer for that yet. Try asking about pending approvals, team attendance, or payroll.";

  function getReply(message) {
    var text = message.toLowerCase();
    for (var i = 0; i < RULES.length; i++) {
      var rule = RULES[i];
      for (var j = 0; j < rule.keywords.length; j++) {
        if (text.indexOf(rule.keywords[j]) !== -1) {
          return rule.reply;
        }
      }
    }
    return FALLBACK;
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
      var delay = 500 + Math.random() * 500;
      setTimeout(function () {
        var reply = getReply(trimmed);
        setTyping(false);
        addMessage('bot', reply);
      }, delay);
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
    addMessage('bot', "Hi " + greetName + ", I'm Ember. Ask me about pending approvals, team attendance, or payroll.");
  });
})();