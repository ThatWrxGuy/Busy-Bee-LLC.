/**
 * LOIS Chat Component
 * 
 * Copy this file into your LOIS project and import it.
 * Requires: React, useState, useEffect
 * 
 * Usage:
 *   import LOISChat from './LOISChat';
 *   <LOISChat apiUrl="https://your-busybee-api.com" />
 */

import React, { useState, useEffect, useRef } from 'react';

const LOISChat = ({ apiUrl = 'http://localhost:8000' }) => {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: '🐝 Hello! I\'m your Busy Bee Chief of Staff.\n\nI can help you with:\n• Recommendations - "What should I do?"\n• Executive Brief - "Show me my brief"\n• Finance - "Can I afford vacation?"\n• Health - "Create a workout plan"\n• Career - "Help with presentation"\n\nWhat would you like help with?',
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${apiUrl}/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        type: data.type,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([{
      id: 'welcome',
      role: 'assistant',
      content: '🐝 Chat cleared! How can I help you?',
      timestamp: new Date().toISOString()
    }]);
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <span>🐝 Busy Bee Chat</span>
        <button onClick={clearChat} style={styles.clearBtn}>Clear</button>
      </div>
      
      <div style={styles.messages}>
        {messages.map((msg) => (
          <div 
            key={msg.id} 
            style={{
              ...styles.message,
              ...(msg.role === 'user' ? styles.userMessage : styles.assistantMessage)
            }}
          >
            <div style={styles.messageContent}>
              {msg.content.split('\n').map((line, i) => (
                <React.Fragment key={i}>
                  {line}
                  {i < msg.content.split('\n').length - 1 && <br />}
                </React.Fragment>
              ))}
            </div>
            <div style={styles.timestamp}>
              {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          </div>
        ))}
        {isLoading && (
          <div style={styles.typing}>
            <span>●</span><span>●</span><span>●</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={styles.inputArea}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me anything..."
          style={styles.input}
          disabled={isLoading}
        />
        <button 
          onClick={sendMessage} 
          style={styles.sendBtn}
          disabled={isLoading || !input.trim()}
        >
          ➤
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '500px',
    maxWidth: '600px',
    margin: '0 auto',
    border: '1px solid #333',
    borderRadius: '12px',
    backgroundColor: '#1a1a2e',
    fontFamily: 'system-ui, -apple-system, sans-serif',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 16px',
    borderBottom: '1px solid #333',
    backgroundColor: '#16213e',
    borderRadius: '12px 12px 0 0',
    color: '#fff',
    fontWeight: 'bold',
  },
  clearBtn: {
    background: 'transparent',
    border: '1px solid #666',
    color: '#aaa',
    padding: '4px 12px',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
  },
  messages: {
    flex: 1,
    overflowY: 'auto',
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  message: {
    maxWidth: '85%',
    padding: '12px 16px',
    borderRadius: '12px',
    lineHeight: '1.5',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#4a90d9',
    color: '#fff',
    borderBottomRightRadius: '2px',
  },
  assistantMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#2d2d44',
    color: '#e0e0e0',
    borderBottomLeftRadius: '2px',
  },
  messageContent: {
    whiteSpace: 'pre-wrap',
  },
  timestamp: {
    fontSize: '10px',
    opacity: 0.7,
    marginTop: '4px',
  },
  typing: {
    display: 'flex',
    gap: '4px',
    padding: '8px',
    color: '#888',
  },
  inputArea: {
    display: 'flex',
    gap: '8px',
    padding: '12px',
    borderTop: '1px solid #333',
    backgroundColor: '#16213e',
    borderRadius: '0 0 12px 12px',
  },
  input: {
    flex: 1,
    padding: '12px 16px',
    borderRadius: '8px',
    border: '1px solid #444',
    backgroundColor: '#1a1a2e',
    color: '#fff',
    fontSize: '14px',
    outline: 'none',
  },
  sendBtn: {
    padding: '12px 20px',
    borderRadius: '8px',
    border: 'none',
    backgroundColor: '#4a90d9',
    color: '#fff',
    cursor: 'pointer',
    fontSize: '18px',
  },
};

export default LOISChat;
