import React, {useState} from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {useSuna} from '../context/SunaContext';

const SettingsScreen: React.FC = () => {
  const {config, updateConfig, checkConnection} = useSuna();
  const [tempConfig, setTempConfig] = useState(config);

  const handleSave = async () => {
    await updateConfig(tempConfig);
    Alert.alert('Success', 'Settings saved successfully!');
    // Test connection with new settings
    setTimeout(checkConnection, 500);
  };

  const handleReset = () => {
    Alert.alert(
      'Reset Settings',
      'Reset all settings to default values?',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Reset',
          style: 'destructive',
          onPress: () => {
            const defaultConfig = {
              serverUrl: '192.168.1.100',
              mobilePort: '5000',
              autoConnect: true,
            };
            setTempConfig(defaultConfig);
          },
        },
      ]
    );
  };

  const findMyIP = () => {
    Alert.alert(
      'Find Your Computer\'s IP',
      'To find your computer\'s IP address:\n\n' +
      'Windows:\n1. Open Command Prompt\n2. Type: ipconfig\n3. Look for "IPv4 Address"\n\n' +
      'Mac/Linux:\n1. Open Terminal\n2. Type: ifconfig\n3. Look for "inet" address\n\n' +
      'Make sure your phone and computer are on the same WiFi network.',
      [{text: 'OK'}]
    );
  };

  return (
    <ScrollView style={styles.container}>
      {/* Connection Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Connection Settings</Text>
        
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Server IP Address</Text>
          <View style={styles.inputContainer}>
            <TextInput
              style={styles.textInput}
              value={tempConfig.serverUrl}
              onChangeText={(text) => setTempConfig({...tempConfig, serverUrl: text})}
              placeholder="192.168.1.100"
              keyboardType="numeric"
            />
            <TouchableOpacity onPress={findMyIP} style={styles.helpButton}>
              <Icon name="help" size={20} color="#6b7280" />
            </TouchableOpacity>
          </View>
          <Text style={styles.inputHint}>
            Your computer's IP address on the local network
          </Text>
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Mobile Port</Text>
          <TextInput
            style={styles.textInput}
            value={tempConfig.mobilePort}
            onChangeText={(text) => setTempConfig({...tempConfig, mobilePort: text})}
            placeholder="5000"
            keyboardType="numeric"
          />
          <Text style={styles.inputHint}>
            Port for mobile web interface (default: 5000)
          </Text>
        </View>

        <View style={styles.switchGroup}>
          <View style={styles.switchLabel}>
            <Text style={styles.inputLabel}>Auto Connect</Text>
            <Text style={styles.inputHint}>
              Automatically connect when app starts
            </Text>
          </View>
          <Switch
            value={tempConfig.autoConnect}
            onValueChange={(value) => setTempConfig({...tempConfig, autoConnect: value})}
            trackColor={{false: '#d1d5db', true: '#a5b4fc'}}
            thumbColor={tempConfig.autoConnect ? '#4f46e5' : '#f3f4f6'}
          />
        </View>
      </View>

      {/* Quick Setup */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Setup</Text>
        
        <TouchableOpacity style={styles.quickButton} onPress={findMyIP}>
          <Icon name="network-check" size={24} color="#4f46e5" />
          <View style={styles.quickButtonText}>
            <Text style={styles.quickButtonTitle}>Find Computer IP</Text>
            <Text style={styles.quickButtonSubtitle}>
              Help finding your computer's IP address
            </Text>
          </View>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.quickButton}
          onPress={() => {
            setTempConfig({...tempConfig, serverUrl: '192.168.1.100'});
          }}
        >
          <Icon name="router" size={24} color="#4f46e5" />
          <View style={styles.quickButtonText}>
            <Text style={styles.quickButtonTitle}>Default Home Network</Text>
            <Text style={styles.quickButtonSubtitle}>
              Set to common home network IP (192.168.1.100)
            </Text>
          </View>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.quickButton}
          onPress={() => {
            setTempConfig({...tempConfig, serverUrl: '192.168.0.100'});
          }}
        >
          <Icon name="wifi" size={24} color="#4f46e5" />
          <View style={styles.quickButtonText}>
            <Text style={styles.quickButtonTitle}>Alternative Network</Text>
            <Text style={styles.quickButtonSubtitle}>
              Set to alternative network IP (192.168.0.100)
            </Text>
          </View>
        </TouchableOpacity>
      </View>

      {/* About */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        
        <View style={styles.aboutCard}>
          <Text style={styles.aboutTitle}>Suna Desktop Mobile</Text>
          <Text style={styles.aboutVersion}>Version 1.0.0</Text>
          <Text style={styles.aboutDescription}>
            Mobile companion app for Suna Desktop AI Agent Platform.
            Connect to your self-hosted Suna instance from anywhere on your local network.
          </Text>
        </View>

        <TouchableOpacity 
          style={styles.linkButton}
          onPress={() => Alert.alert('Info', 'Visit https://github.com/kortix-ai/suna for more information')}
        >
          <Icon name="info" size={20} color="#4f46e5" />
          <Text style={styles.linkButtonText}>Learn More About Suna</Text>
        </TouchableOpacity>
      </View>

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <TouchableOpacity style={styles.resetButton} onPress={handleReset}>
          <Text style={styles.resetButtonText}>Reset to Defaults</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
          <Text style={styles.saveButtonText}>Save Settings</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  section: {
    margin: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 16,
  },
  inputGroup: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 16,
    backgroundColor: '#ffffff',
    color: '#374151',
  },
  helpButton: {
    marginLeft: 8,
    padding: 8,
  },
  inputHint: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 4,
  },
  switchGroup: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 16,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  switchLabel: {
    flex: 1,
  },
  quickButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  quickButtonText: {
    marginLeft: 12,
    flex: 1,
  },
  quickButtonTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
  },
  quickButtonSubtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 2,
  },
  aboutCard: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 16,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    marginBottom: 12,
  },
  aboutTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#374151',
  },
  aboutVersion: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 2,
    marginBottom: 8,
  },
  aboutDescription: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
  linkButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 16,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  linkButtonText: {
    fontSize: 16,
    color: '#4f46e5',
    marginLeft: 8,
  },
  actionButtons: {
    flexDirection: 'row',
    margin: 16,
    gap: 12,
  },
  resetButton: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 16,
    borderWidth: 1,
    borderColor: '#ef4444',
    alignItems: 'center',
  },
  resetButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ef4444',
  },
  saveButton: {
    flex: 1,
    backgroundColor: '#4f46e5',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
  },
  saveButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
});

export default SettingsScreen;