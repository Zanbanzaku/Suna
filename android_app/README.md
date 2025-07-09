# Suna Desktop Mobile App

A React Native mobile companion app for Suna Desktop AI Agent Platform.

## Features

- **Chat Interface** - Full conversation capabilities with Suna AI
- **Real-time Status** - Monitor your Suna Desktop services
- **Easy Setup** - Simple IP configuration for local network access
- **Cross-platform** - Works on Android and iOS devices

## Prerequisites

- **Node.js 16+** and npm/yarn
- **React Native CLI** (`npm install -g react-native-cli`)
- **Android Studio** (for Android development)
- **Xcode** (for iOS development, macOS only)
- **Suna Desktop** running on your computer

## Quick Start

### 1. Install Dependencies

```bash
cd android_app
npm install
```

### 2. Android Setup

```bash
# Start Metro bundler
npm start

# Run on Android (device or emulator)
npm run android
```

### 3. iOS Setup (macOS only)

```bash
# Install iOS dependencies
cd ios && pod install && cd ..

# Run on iOS simulator
npm run ios
```

## Configuration

### Connect to Suna Desktop

1. **Find your computer's IP address:**
   - Windows: `ipconfig` in Command Prompt
   - Mac/Linux: `ifconfig` in Terminal
   - Look for your local network IP (usually 192.168.x.x)

2. **Configure the app:**
   - Open the app and go to Settings tab
   - Enter your computer's IP address
   - Ensure Mobile Port is set to 5000 (default)
   - Enable Auto Connect if desired

3. **Start Suna Desktop:**
   - Make sure Suna Desktop is running on your computer
   - Start the services from the Dashboard tab
   - The mobile web interface should be accessible

### Network Requirements

- Both devices must be on the same WiFi network
- Firewall should allow connections on port 5000
- Suna Desktop services must be running

## Building for Production

### Android APK

```bash
# Debug APK
npm run build:android-debug

# Release APK (requires signing setup)
npm run build:android
```

### iOS App

```bash
# Open in Xcode for building
open ios/SunaDesktopMobile.xcworkspace
```

## App Structure

```
src/
├── context/
│   └── SunaContext.tsx     # Global state management
├── screens/
│   ├── ChatScreen.tsx      # Main chat interface
│   ├── StatusScreen.tsx    # Service status monitoring
│   └── SettingsScreen.tsx  # Configuration settings
└── components/             # Reusable components
```

## API Integration

The app connects to Suna Desktop through the mobile web interface:

- **Health Check**: `GET /api/health`
- **Suna Status**: `GET /api/suna/health`
- **New Chat**: `POST /api/chat/new`
- **Send Message**: `POST /api/chat/{id}/send`
- **Get Messages**: `GET /api/chat/{id}/messages`

## Troubleshooting

### Connection Issues

1. **"Disconnected" status:**
   - Verify IP address is correct
   - Check if Suna Desktop is running
   - Ensure both devices are on same network
   - Check firewall settings

2. **"Mobile connected, Suna offline":**
   - Start Suna services from Desktop Dashboard
   - Check Docker is running on computer
   - Verify API keys are configured

3. **App crashes or errors:**
   - Check React Native logs: `npx react-native log-android`
   - Clear app data and restart
   - Reinstall the app

### Performance Issues

- **Slow responses:** Normal for complex AI tasks
- **High battery usage:** Reduce auto-refresh frequency
- **Network timeouts:** Check WiFi signal strength

## Development

### Adding New Features

1. **New API endpoints:** Update `SunaContext.tsx`
2. **UI components:** Add to `src/components/`
3. **New screens:** Add to `src/screens/` and navigation

### Testing

```bash
# Run tests
npm test

# Run on device for testing
npm run android
npm run ios
```

### Debugging

```bash
# Enable debugging
npm start -- --reset-cache

# View logs
npx react-native log-android
npx react-native log-ios
```

## Deployment

### Google Play Store

1. Generate signed APK
2. Create Play Console account
3. Upload APK and complete store listing
4. Submit for review

### Apple App Store

1. Build in Xcode with release configuration
2. Archive and upload to App Store Connect
3. Complete app information and submit for review

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on both platforms
5. Submit a pull request

## License

This project is licensed under the Apache License, Version 2.0.

## Support

- **Issues:** Report bugs and request features on GitHub
- **Documentation:** See main Suna repository for detailed docs
- **Community:** Join the Suna Discord for support and discussions

---

**Made with ❤️ for the Suna AI community**