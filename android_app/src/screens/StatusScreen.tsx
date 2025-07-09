import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
  Linking,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import {useSuna} from '../context/SunaContext';

interface ServiceStatus {
  name: string;
  status: 'online' | 'offline' | 'unknown';
  description: string;
  port?: string;
}

const StatusScreen: React.FC = () => {
  const {config, isConnected, connectionStatus, checkConnection} = useSuna();
  const [refreshing, setRefreshing] = useState(false);
  const [services, setServices] = useState<ServiceStatus[]>([
    {
      name: 'Mobile Interface',
      status: 'unknown',
      description: 'Mobile web interface for Suna Desktop',
      port: config.mobilePort,
    },
    {
      name: 'Suna Backend',
      status: 'unknown',
      description: 'Main Suna AI agent backend',
      port: '8000',
    },
    {
      name: 'Web Interface',
      status: 'unknown',
      description: 'Full Suna web application',
      port: '3000',
    },
    {
      name: 'Docker Services',
      status: 'unknown',
      description: 'Redis, RabbitMQ, and other services',
    },
  ]);

  useEffect(() => {
    checkAllServices();
  }, [isConnected]);

  const checkAllServices = async () => {
    const baseUrl = `http://${config.serverUrl}`;
    const updatedServices = [...services];

    // Check mobile interface
    updatedServices[0].status = isConnected ? 'online' : 'offline';

    // Check other services
    try {
      // Check Suna backend
      const sunaResponse = await fetch(`${baseUrl}:${config.mobilePort}/api/suna/health`, {
        timeout: 5000,
      });
      const sunaData = await sunaResponse.json();
      updatedServices[1].status = sunaData.status === 'connected' ? 'online' : 'offline';
    } catch {
      updatedServices[1].status = 'offline';
    }

    try {
      // Check web interface
      const webResponse = await fetch(`${baseUrl}:3000`, {timeout: 5000});
      updatedServices[2].status = webResponse.ok ? 'online' : 'offline';
    } catch {
      updatedServices[2].status = 'offline';
    }

    // Docker services status is inferred from backend status
    updatedServices[3].status = updatedServices[1].status;

    setServices(updatedServices);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await checkConnection();
    await checkAllServices();
    setRefreshing(false);
  };

  const openWebInterface = () => {
    const url = `http://${config.serverUrl}:3000`;
    Linking.openURL(url).catch(() => {
      Alert.alert('Error', 'Could not open web interface');
    });
  };

  const openApiDocs = () => {
    const url = `http://${config.serverUrl}:8000/docs`;
    Linking.openURL(url).catch(() => {
      Alert.alert('Error', 'Could not open API documentation');
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return '#10b981';
      case 'offline':
        return '#ef4444';
      default:
        return '#f59e0b';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return 'check-circle';
      case 'offline':
        return 'error';
      default:
        return 'help';
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Connection Overview */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Connection Status</Text>
        <View style={styles.connectionCard}>
          <View style={styles.connectionHeader}>
            <Icon
              name={isConnected ? 'wifi' : 'wifi-off'}
              size={24}
              color={isConnected ? '#10b981' : '#ef4444'}
            />
            <Text style={styles.connectionStatus}>{connectionStatus}</Text>
          </View>
          <Text style={styles.connectionDetails}>
            Server: {config.serverUrl}:{config.mobilePort}
          </Text>
        </View>
      </View>

      {/* Services Status */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Services</Text>
        {services.map((service, index) => (
          <View key={index} style={styles.serviceCard}>
            <View style={styles.serviceHeader}>
              <Icon
                name={getStatusIcon(service.status)}
                size={20}
                color={getStatusColor(service.status)}
              />
              <Text style={styles.serviceName}>{service.name}</Text>
              {service.port && (
                <Text style={styles.servicePort}>:{service.port}</Text>
              )}
            </View>
            <Text style={styles.serviceDescription}>{service.description}</Text>
          </View>
        ))}
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        
        <TouchableOpacity
          style={[styles.actionButton, !isConnected && styles.actionButtonDisabled]}
          onPress={openWebInterface}
          disabled={!isConnected}
        >
          <Icon name="web" size={24} color={isConnected ? '#4f46e5' : '#9ca3af'} />
          <Text style={[styles.actionButtonText, !isConnected && styles.actionButtonTextDisabled]}>
            Open Web Interface
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionButton, !isConnected && styles.actionButtonDisabled]}
          onPress={openApiDocs}
          disabled={!isConnected}
        >
          <Icon name="description" size={24} color={isConnected ? '#4f46e5' : '#9ca3af'} />
          <Text style={[styles.actionButtonText, !isConnected && styles.actionButtonTextDisabled]}>
            API Documentation
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={onRefresh}
        >
          <Icon name="refresh" size={24} color="#4f46e5" />
          <Text style={styles.actionButtonText}>Refresh Status</Text>
        </TouchableOpacity>
      </View>

      {/* System Information */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>System Information</Text>
        <View style={styles.infoCard}>
          <Text style={styles.infoLabel}>Mobile App Version:</Text>
          <Text style={styles.infoValue}>1.0.0</Text>
        </View>
        <View style={styles.infoCard}>
          <Text style={styles.infoLabel}>Server Address:</Text>
          <Text style={styles.infoValue}>{config.serverUrl}</Text>
        </View>
        <View style={styles.infoCard}>
          <Text style={styles.infoLabel}>Mobile Port:</Text>
          <Text style={styles.infoValue}>{config.mobilePort}</Text>
        </View>
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
    marginBottom: 12,
  },
  connectionCard: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 16,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  connectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  connectionStatus: {
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
    color: '#374151',
  },
  connectionDetails: {
    fontSize: 14,
    color: '#6b7280',
  },
  serviceCard: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  serviceHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  serviceName: {
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
    color: '#374151',
    flex: 1,
  },
  servicePort: {
    fontSize: 14,
    color: '#6b7280',
    fontFamily: 'monospace',
  },
  serviceDescription: {
    fontSize: 14,
    color: '#6b7280',
    marginLeft: 28,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  actionButtonDisabled: {
    opacity: 0.5,
  },
  actionButtonText: {
    fontSize: 16,
    marginLeft: 12,
    color: '#374151',
  },
  actionButtonTextDisabled: {
    color: '#9ca3af',
  },
  infoCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  infoLabel: {
    fontSize: 14,
    color: '#6b7280',
  },
  infoValue: {
    fontSize: 14,
    color: '#374151',
    fontWeight: '500',
  },
});

export default StatusScreen;