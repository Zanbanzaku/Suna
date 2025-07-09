import React, {useState, useRef, useEffect} from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {useSuna} from '../context/SunaContext';

const ChatScreen: React.FC = () => {
  const {
    messages,
    isConnected,
    connectionStatus,
    isLoading,
    sendMessage,
    newChat,
    clearChat,
    checkConnection,
  } = useSuna();
  
  const [inputText, setInputText] = useState('');
  const flatListRef = useRef<FlatList>(null);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({animated: true});
      }, 100);
    }
  }, [messages]);

  const handleSend = async () => {
    if (!inputText.trim()) {
      return;
    }

    if (!isConnected) {
      Alert.alert('Error', 'Not connected to Suna Desktop. Check your settings.');
      return;
    }

    const message = inputText.trim();
    setInputText('');
    await sendMessage(message);
  };

  const handleNewChat = async () => {
    Alert.alert(
      'New Chat',
      'Start a new conversation? Current chat will be saved on the server.',
      [
        {text: 'Cancel', style: 'cancel'},
        {text: 'New Chat', onPress: newChat},
      ]
    );
  };

  const handleClearChat = () => {
    Alert.alert(
      'Clear Chat',
      'Clear the current chat display? Messages are still saved on the server.',
      [
        {text: 'Cancel', style: 'cancel'},
        {text: 'Clear', onPress: clearChat},
      ]
    );
  };

  const renderMessage = ({item}: {item: any}) => {
    const isUser = item.role === 'user';
    const isSystem = item.role === 'system';
    const isError = item.role === 'error';

    return (
      <View style={[
        styles.messageContainer,
        isUser && styles.userMessage,
        isSystem && styles.systemMessage,
        isError && styles.errorMessage,
      ]}>
        <Text style={[
          styles.messageText,
          isUser && styles.userMessageText,
          isSystem && styles.systemMessageText,
          isError && styles.errorMessageText,
        ]}>
          {item.content}
        </Text>
        <Text style={styles.timestamp}>
          {new Date(item.timestamp).toLocaleTimeString()}
        </Text>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      {/* Connection Status */}
      <View style={styles.statusBar}>
        <View style={styles.statusIndicator}>
          <View style={[
            styles.statusDot,
            {backgroundColor: isConnected ? '#10b981' : '#ef4444'}
          ]} />
          <Text style={styles.statusText}>{connectionStatus}</Text>
        </View>
        <TouchableOpacity onPress={checkConnection} style={styles.refreshButton}>
          <Icon name="refresh" size={20} color="#6b7280" />
        </TouchableOpacity>
      </View>

      {/* Chat Messages */}
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={item => item.id}
        style={styles.messagesList}
        contentContainerStyle={styles.messagesContainer}
        showsVerticalScrollIndicator={false}
      />

      {/* Input Area */}
      <View style={styles.inputContainer}>
        <View style={styles.inputRow}>
          <TouchableOpacity 
            onPress={handleNewChat}
            style={styles.actionButton}
            disabled={!isConnected}
          >
            <Icon name="add" size={24} color={isConnected ? "#4f46e5" : "#9ca3af"} />
          </TouchableOpacity>
          
          <TouchableOpacity 
            onPress={handleClearChat}
            style={styles.actionButton}
            disabled={!isConnected}
          >
            <Icon name="clear" size={24} color={isConnected ? "#4f46e5" : "#9ca3af"} />
          </TouchableOpacity>
        </View>
        
        <View style={styles.messageInputContainer}>
          <TextInput
            style={styles.messageInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Type your message..."
            placeholderTextColor="#9ca3af"
            multiline
            maxLength={2000}
            editable={!isLoading && isConnected}
          />
          <TouchableOpacity
            onPress={handleSend}
            style={[
              styles.sendButton,
              (!inputText.trim() || isLoading || !isConnected) && styles.sendButtonDisabled
            ]}
            disabled={!inputText.trim() || isLoading || !isConnected}
          >
            <Icon 
              name={isLoading ? "hourglass-empty" : "send"} 
              size={24} 
              color="white" 
            />
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  statusBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  statusIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    fontSize: 14,
    color: '#374151',
  },
  refreshButton: {
    padding: 4,
  },
  messagesList: {
    flex: 1,
  },
  messagesContainer: {
    padding: 16,
  },
  messageContainer: {
    marginBottom: 16,
    padding: 12,
    borderRadius: 12,
    maxWidth: '85%',
  },
  userMessage: {
    backgroundColor: '#4f46e5',
    alignSelf: 'flex-end',
  },
  systemMessage: {
    backgroundColor: '#fef3c7',
    alignSelf: 'center',
    borderWidth: 1,
    borderColor: '#f59e0b',
  },
  errorMessage: {
    backgroundColor: '#fee2e2',
    borderWidth: 1,
    borderColor: '#ef4444',
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
    color: '#374151',
  },
  userMessageText: {
    color: '#ffffff',
  },
  systemMessageText: {
    color: '#92400e',
    fontStyle: 'italic',
    textAlign: 'center',
  },
  errorMessageText: {
    color: '#dc2626',
  },
  timestamp: {
    fontSize: 12,
    color: '#9ca3af',
    marginTop: 4,
    textAlign: 'right',
  },
  inputContainer: {
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
    padding: 16,
  },
  inputRow: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  actionButton: {
    marginRight: 12,
    padding: 8,
  },
  messageInputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
  },
  messageInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 16,
    maxHeight: 100,
    marginRight: 12,
    color: '#374151',
  },
  sendButton: {
    backgroundColor: '#4f46e5',
    borderRadius: 8,
    padding: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#9ca3af',
  },
});

export default ChatScreen;