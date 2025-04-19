document.addEventListener('DOMContentLoaded', function() {
  const chatbotMessages = document.getElementById('chatbotMessages');
  const questionButtons = document.querySelectorAll('.question-btn');
  const voiceBtn = document.getElementById('voiceBtn');
  const langSelect = document.getElementById('langSelect');
  const genderSelect = document.getElementById('genderSelect');

  // Set Hindi as default language
  langSelect.value = 'hi-IN';

  const responses = {
      "What are common plant diseases?": {
          hi: "पौधों की आम बीमारियों में ओइडियम, पत्तियों पर धब्बे, झुलसा और जड़ों का सड़ना शामिल हैं।",
          en: "Common plant diseases include powdery mildew, leaf spot, blight, and root rot."
      },
      "How to treat yellow leaves?": {
          hi: "पीली पत्तियाँ अक्सर अधिक पानी देने या पोषक तत्वों की कमी का संकेत होती हैं। मिट्टी की नमी जांचें।",
          en: "Yellow leaves often mean overwatering or nutrient deficiency. Check soil moisture."
      },
      "Watering frequency for plants?": {
          hi: "जब मिट्टी की ऊपरी परत सूखी हो तो पानी दें। यह पौधे और वातावरण पर निर्भर करता है।",
          en: "Water when the top inch of soil is dry. It varies by plant type and environment."
      },
      "Best fertilizer for plants?": {
          hi: "10-10-10 जैसे संतुलित उर्वरक का उपयोग करें। जैविक खाद भी एक अच्छा विकल्प है।",
          en: "Use a balanced fertilizer like 10-10-10. Organic compost is also a great choice."
      },
      "How much sunlight do plants need?": {
          hi: "अधिकतर पौधों को प्रतिदिन 4-6 घंटे धूप की आवश्यकता होती है।",
          en: "Most plants need 4–6 hours of sunlight daily."
      },
      "Why are my plants drooping?": {
          hi: "पौधों का झुकना पानी की कमी, अधिक धूप या जड़ की समस्या का संकेत हो सकता है।",
          en: "Drooping can be due to lack of water, too much sun, or root issues."
      },
      "Can I use kitchen waste for compost?": {
          hi: "हाँ, आप रसोई के कचरे से खाद बना सकते हैं। छिलके, चाय की पत्तियाँ आदि उपयुक्त हैं।",
          en: "Yes, kitchen waste like peels and used tea leaves can be composted."
      },
      "How to revive a dying plant?": {
          hi: "पौधे को नई मिट्टी दें, ठीक से पानी दें और धूप में रखें। ध्यानपूर्वक निगरानी करें।",
          en: "Repot the plant, water properly, and ensure enough sunlight. Monitor carefully."
      }
  };

  // Initialize with welcome message
  addMessage("Plant Assistant: नमस्ते! मैं आपके पौधों से संबंधित किसी भी प्रश्न में आपकी सहायता कर सकता हूँ।<br>Hello! I can help with any plant-related questions.", 'bot-message');

  // Handle question buttons
  questionButtons.forEach(button => {
      button.addEventListener('click', () => {
          const question = button.getAttribute('data-question');
          const userLang = langSelect.value || 'hi-IN';
          const langCode = userLang.slice(0, 2); // 'hi' or 'en'
          const response = responses[question][langCode] || responses[question]['hi'];

          addMessage(`You: ${question}`, 'user-message');
          setTimeout(() => {
              addMessage(`Plant Assistant: ${response}`, 'bot-message');
              speak(response, userLang, genderSelect.value);
          }, 500);
      });
  });

  // Add message function with improved styling
  function addMessage(text, className) {
      const msg = document.createElement('div');
      msg.classList.add('message', className);
      
      // Create message bubble
      const bubble = document.createElement('div');
      bubble.classList.add('message-bubble');
      bubble.innerHTML = text;
      
      msg.appendChild(bubble);
      chatbotMessages.appendChild(msg);
      chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  }

  // Voice input with better error handling
  voiceBtn.addEventListener('click', () => {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
          addMessage("Plant Assistant: Your browser doesn't support voice recognition.", 'bot-message');
          return;
      }

      const recognition = new SpeechRecognition();
      recognition.lang = langSelect.value || 'hi-IN';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;
      
      // Show listening indicator
      voiceBtn.innerHTML = '<i class="fas fa-circle-notch fa-spin me-2"></i> Listening...';
      voiceBtn.disabled = true;

      recognition.start();

      recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          addMessage(`You (Voice): ${transcript}`, 'user-message');
          handleVoiceQuestion(transcript);
      };

      recognition.onerror = (e) => {
          const errorMsg = langSelect.value === 'hi-IN' 
              ? "आवाज पहचान में त्रुटि: कृपया पुनः प्रयास करें" 
              : `Voice error: ${e.error}. Please try again.`;
          addMessage(`Plant Assistant: ${errorMsg}`, 'bot-message');
      };

      recognition.onend = () => {
          voiceBtn.innerHTML = '<i class="fas fa-microphone me-2"></i> आवाज़ में पूछें (Ask by Voice)';
          voiceBtn.disabled = false;
      };
  });

  // Improved voice question matching
  function handleVoiceQuestion(question) {
      const lower = question.toLowerCase();
      const langCode = langSelect.value.slice(0, 2);
      let reply = langCode === 'hi' 
          ? "माफ़ कीजिए, मैं यह नहीं समझ पाया। कृपया एक पौधों से संबंधित प्रश्न पूछें।" 
          : "Sorry, I couldn't understand. Please ask a plant-related question.";

      // Check for keywords in the question
      const keywordMap = {
          "disease": "What are common plant diseases?",
          "yellow": "How to treat yellow leaves?",
          "water": "Watering frequency for plants?",
          "fertilizer": "Best fertilizer for plants?",
          "sunlight": "How much sunlight do plants need?",
          "droop": "Why are my plants drooping?",
          "compost": "Can I use kitchen waste for compost?",
          "revive": "How to revive a dying plant?"
      };

      for (const [keyword, responseKey] of Object.entries(keywordMap)) {
          if (lower.includes(keyword)) {
              reply = responses[responseKey][langCode] || responses[responseKey]['hi'];
              break;
          }
      }

      setTimeout(() => {
          addMessage(`Plant Assistant: ${reply}`, 'bot-message');
          speak(reply, langSelect.value, genderSelect.value);
      }, 800);
  }

  // Enhanced text-to-speech with fallback
  function speak(text, lang = 'hi-IN', gender = 'female') {
      if (!window.speechSynthesis) {
          console.log("Text-to-speech not supported");
          return;
      }

      const synth = window.speechSynthesis;
      
      // Cancel any ongoing speech
      synth.cancel();

      // Wait for voices to be loaded if not available
      let voices = synth.getVoices();
      if (voices.length === 0) {
          synth.onvoiceschanged = function() {
              voices = synth.getVoices();
              speakText(text, lang, gender, voices);
          };
          return;
      }

      speakText(text, lang, gender, voices);
  }

  function speakText(text, lang, gender, voices) {
      const synth = window.speechSynthesis;
      
      // Filter voices by language and gender preference
      let preferredVoices = voices.filter(v => v.lang === lang);
      
      if (gender === 'female') {
          preferredVoices = preferredVoices.filter(v => 
              v.name.toLowerCase().includes('female') || 
              v.name.toLowerCase().includes('woman') ||
              v.name.includes('Zira') || // English female
              v.name.includes('Madhu')  // Hindi female
          );
      } else {
          preferredVoices = preferredVoices.filter(v => 
              v.name.toLowerCase().includes('male') || 
              v.name.toLowerCase().includes('man') ||
              v.name.includes('David') || // English male
              v.name.includes('Hemant')   // Hindi male
          );
      }

      const selectedVoice = preferredVoices[0] || 
                          voices.find(v => v.lang === lang) || 
                          voices[0];

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.voice = selectedVoice;
      utterance.lang = lang;
      utterance.rate = 0.9;
      utterance.pitch = gender === 'female' ? 1.2 : 1;

      synth.speak(utterance);
  }

  // Language change handler
  langSelect.addEventListener('change', function() {
      const lang = this.value;
      const message = lang === 'hi-IN' 
          ? "भाषा हिंदी में बदली गई" 
          : "Language changed to English";
      addMessage(`Plant Assistant: ${message}`, 'bot-message');
  });
});