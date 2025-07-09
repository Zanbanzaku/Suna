import React, {useEffect, useState} from 'react';
import {
  SafeAreaView,
  StatusBar,
  StyleSheet,
  useColorScheme,
} from 'react-native';
import {NavigationContainer} from '@react-navigation/native';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';

import ChatScreen from './src/screens/ChatScreen';
import SettingsScreen from './src/screens/SettingsScreen';
import StatusScreen from './src/screens/StatusScreen';
import {SunaProvider} from './src/context/SunaContext';
import {Colors} from 'react-native/Libraries/NewAppScreen';

const Tab = createBottomTabNavigator();

function App(): JSX.Element {
  const isDarkMode = useColorScheme() === 'dark';

  const backgroundStyle = {
    backgroundColor: isDarkMode ? Colors.darker : Colors.lighter,
    flex: 1,
  };

  return (
    <SunaProvider>
      <SafeAreaView style={backgroundStyle}>
        <StatusBar
          barStyle={isDarkMode ? 'light-content' : 'dark-content'}
          backgroundColor={backgroundStyle.backgroundColor}
        />
        <NavigationContainer>
          <Tab.Navigator
            screenOptions={({route}) => ({
              tabBarIcon: ({focused, color, size}) => {
                let iconName: string;

                if (route.name === 'Chat') {
                  iconName = 'chat';
                } else if (route.name === 'Status') {
                  iconName = 'dashboard';
                } else if (route.name === 'Settings') {
                  iconName = 'settings';
                } else {
                  iconName = 'help';
                }

                return <Icon name={iconName} size={size} color={color} />;
              },
              tabBarActiveTintColor: '#4f46e5',
              tabBarInactiveTintColor: 'gray',
              headerStyle: {
                backgroundColor: '#4f46e5',
              },
              headerTintColor: '#fff',
              headerTitleStyle: {
                fontWeight: 'bold',
              },
            })}>
            <Tab.Screen 
              name="Chat" 
              component={ChatScreen}
              options={{
                title: '🤖 Suna Chat',
              }}
            />
            <Tab.Screen 
              name="Status" 
              component={StatusScreen}
              options={{
                title: '📊 Status',
              }}
            />
            <Tab.Screen 
              name="Settings" 
              component={SettingsScreen}
              options={{
                title: '⚙️ Settings',
              }}
            />
          </Tab.Navigator>
        </NavigationContainer>
      </SafeAreaView>
    </SunaProvider>
  );
}

export default App;