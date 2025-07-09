import React, {createContext, useContext, useEffect, useState, ReactNode} from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {Alert} from 'react-native';
import {Platform} from 'react-native';

interface SunaConfig {
  serverUrl: string;
  mobilePort: string;
  autoConnect: boolean;
}

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'error';
  content: string;
  timestamp: string;
}

interface SunaContextType {
  config: SunaConfig;
  updateConfig: (newConfig: Partial<SunaConfig>) => void;
  isConnected: boolean;
  connectionStatus: string;
  messages: Message[];
  currentChatId: string | null;
  isLoading: boolean;
  sendMessage: (message: string, files?: any[]) => Promise<void>;
  newChat: () => Promise<void>;
  clearChat: () => void;
  checkConnection: () => Promise<void>;
}

const defaultConfig: SunaConfig = {
  serverUrl: '192.168.1.100', // Default IP - user needs to change this
  mobilePort: '5000',
  autoConnect: true,
};

const SunaContext = createContext<SunaContextType | undefined>(undefined);

export const useSuna = () => {
  const context = useContext(SunaContext);
  if (!context) {
    throw new Error('useSuna must be used within a SunaProvider');
  }
  return context;
};

interface SunaProviderProps {
  children: ReactNode;
}

export const SunaProvider: React.FC<SunaProviderProps> = ({children}) => {
  const [config, setConfig] = useState<SunaConfig>(defaultConfig);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('Checking...');
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Load config from storage on startup
  useEffect(() => {
    loadConfig();
  }, []);

  // Auto-connect if enabled
  useEffect(() => {
    if (config.autoConnect) {
      checkConnection();
    }
  }, [config]);

  const loadConfig = async () => {
    try {
      const savedConfig = await AsyncStorage.getItem('sunaConfig');
      if (savedConfig) {
        setConfig({...defaultConfig, ...JSON.parse(savedConfig)});
      }
    } catch (error) {
      console.error('Failed to load config:', error);
    }
  };

  const updateConfig = async (newConfig: Partial<SunaConfig>) => {
    const updatedConfig = {...config, ...newConfig};
    setConfig(updatedConfig);
    
    try {
      await AsyncStorage.setItem('sunaConfig', JSON.stringify(updatedConfig));
    } catch (error) {
      console.error('Failed to save config:', error);
    }
  };

  const getBaseUrl = () => {
    // Input validation for URL construction
    const cleanServerUrl = config.serverUrl.replace(/[^a-zA-Z0-9.-]/g, '');
    const cleanPort = config.mobilePort.replace(/[^0-9]/g, '');
    
    if (!cleanServerUrl || !cleanPort) {
      throw new Error('Invalid server configuration');
    }
    
    return `http://${cleanServerUrl}:${cleanPort}`;
  };

  const checkConnection = async () => {
    try {
      setConnectionStatus('Connecting...');
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`${getBaseUrl()}/api/health`, {
        method: 'GET',
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      
      clearTimeout(timeoutId);

      if (response.ok) {
        setIsConnected(true);
        setConnectionStatus('Connected');
        
        // Check Suna backend status
        const sunaController = new AbortController();
        const sunaTimeoutId = setTimeout(() => sunaController.abort(), 5000);
        
        const sunaResponse = await fetch(`${getBaseUrl()}/api/suna/health`, {
          signal: sunaController.signal,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
        });
        
        clearTimeout(sunaTimeoutId);
        const sunaData = await sunaResponse.json();
        
        if (sunaData.status === 'connected') {
          setConnectionStatus('Connected to Suna');
        } else {
          setConnectionStatus('Mobile connected, Suna offline');
        }
      } else {
        throw new Error('Server not responding');
      }
    } catch (error) {
      setIsConnected(false);
      setConnectionStatus('Disconnected');
      if (error.name === 'AbortError') {
        console.error('Connection check timed out');
      } else {
        console.error('Connection check failed:', error);
      }
    }
  };

  const newChat = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      
      const response = await fetch(`${getBaseUrl()}/api/chat/new`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        setCurrentChatId(data.chat_id);
        setMessages([]);
        addMessage('system', 'New conversation started!');
      } else {
        throw new Error('Failed to start new chat');
      }
    } catch (error) {
      console.error('New chat failed:', error);
      Alert.alert('Error', 'Failed to start new chat');
    }
  };

  const clearChat = () => {
    setMessages([]);
    addMessage('system', 'Chat cleared. Messages are still saved on server.');
  };

  const addMessage = (role: Message['role'], content: string) => {
    const message: Message = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      role,
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, message]);
  };

  const sendMessage = async (message: string, files?: any[]) => {
    if (!isConnected) {
      Alert.alert('Error', 'Not connected to Suna Desktop');
      return;
    }
    
    // Input validation
    if (!message || typeof message !== 'string' || message.trim().length === 0) {
      Alert.alert('Error', 'Message cannot be empty');
      return;
    }
    
    if (message.length > 10000) {
      Alert.alert('Error', 'Message too long (max 10,000 characters)');
      return;
    }

    if (!currentChatId) {
      await newChat();
    }

    // Add user message
    addMessage('user', message);
    setIsLoading(true);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);
      
      const response = await fetch(`${getBaseUrl()}/api/chat/${currentChatId}/send`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
        body: JSON.stringify({
          message: message.trim(),
          files: files || [],
        }),
      });
      
      clearTimeout(timeoutId);

      if (response.ok) {
        // Add loading message
        const loadingId = addMessage('system', 'Suna is thinking...');
        
        // Wait for response (simplified - in real app you'd want streaming)
        setTimeout(async () => {
          try {
            const msgController = new AbortController();
            const msgTimeoutId = setTimeout(() => msgController.abort(), 10000);
            
            const messagesResponse = await fetch(`${getBaseUrl()}/api/chat/${currentChatId}/messages`, {
              signal: msgController.signal,
              headers: {
                'Accept': 'application/json',
              },
            });
            
            clearTimeout(msgTimeoutId);
            const messagesData = await messagesResponse.json();
            
            // Remove loading message and add response
            setMessages(prev => prev.filter(msg => msg.id !== loadingId.toString()));
            
            const lastMessage = messagesData.messages?.[messagesData.messages.length - 1];
            if (lastMessage && lastMessage.role === 'assistant') {
              addMessage('assistant', lastMessage.content);
            } else {
              addMessage('assistant', 'Response received from Suna.');
            }
          } catch (error) {
            if (error.name === 'AbortError') {
              addMessage('error', 'Response timed out');
            } else {
              addMessage('error', 'Failed to get response');
            }
          }
          
          setIsLoading(false);
        }, 2000);
      } else {
        let errorData;
        try {
          errorData = await response.json();
        } catch {
          errorData = { error: 'Server error' };
        }
        addMessage('error', errorData.error || 'Failed to send message');
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Send message failed:', error);
      if (error.name === 'AbortError') {
        addMessage('error', 'Request timed out');
      } else {
        addMessage('error', 'Failed to send message');
      }
      setIsLoading(false);
    }
  };

  const value: SunaContextType = {
    config,
    updateConfig,
    isConnected,
    connectionStatus,
    messages,
    currentChatId,
    isLoading,
    sendMessage,
    newChat,
    clearChat,
    checkConnection,
  };

  return <SunaContext.Provider value={value}>{children}</SunaContext.Provider>;
};