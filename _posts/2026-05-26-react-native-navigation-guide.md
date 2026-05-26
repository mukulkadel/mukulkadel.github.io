---
layout: post
title: "React Native Navigation: Stack, Tab, and Drawer Explained"
date: "2026-05-26 00:00:00 +0530"
slug: react-native-navigation-guide
description: "A practical guide to React Native Navigation — setting up React Navigation, Stack, Tab, and Drawer navigators, passing params, and nesting navigators."
categories: ["Programming", "Tutorials"]
tags: ["react native", "navigation", "stack navigator", "tab navigator", "drawer", "mobile", "javascript", "ios", "android"]
---

Navigation in React Native is not built-in the way routing is in web frameworks. You choose a library, and the de facto standard is React Navigation — a JavaScript-based navigation library that works on both iOS and Android. Understanding how to compose its three core navigators (Stack, Tab, Drawer) and how they nest together covers 95% of what any mobile app needs.

## Installation

```bash
$ npm install @react-navigation/native

# Required peer dependencies
$ npm install react-native-screens react-native-safe-area-context

# On iOS, install native deps
$ cd ios && pod install
```

Then wrap your entire app in a `NavigationContainer`:

```jsx
// App.tsx
import { NavigationContainer } from '@react-navigation/native';

export default function App() {
    return (
        <NavigationContainer>
            {/* navigators go here */}
        </NavigationContainer>
    );
}
```

## Stack Navigator

Stack Navigator mimics iOS navigation — screens slide in from the right; the back button pops them off. Install it:

```bash
$ npm install @react-navigation/stack
$ npm install react-native-gesture-handler  # required dependency
```

```jsx
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from './screens/HomeScreen';
import DetailScreen from './screens/DetailScreen';

const Stack = createStackNavigator();

function AppStack() {
    return (
        <Stack.Navigator initialRouteName="Home">
            <Stack.Screen
                name="Home"
                component={HomeScreen}
                options={{ title: 'My App' }}
            />
            <Stack.Screen
                name="Detail"
                component={DetailScreen}
                options={({ route }) => ({ title: route.params.title })}
            />
        </Stack.Navigator>
    );
}
```

### Navigating Between Screens

Every screen component receives a `navigation` prop automatically:

```jsx
// HomeScreen.tsx
function HomeScreen({ navigation }) {
    return (
        <View>
            <Text>Home</Text>
            <Button
                title="Go to Detail"
                onPress={() =>
                    navigation.navigate('Detail', { id: 42, title: 'Item 42' })
                }
            />
        </View>
    );
}
```

### Receiving Params

```jsx
// DetailScreen.tsx
function DetailScreen({ route, navigation }) {
    const { id, title } = route.params;

    return (
        <View>
            <Text>ID: {id}</Text>
            <Text>Title: {title}</Text>
            <Button title="Go Back" onPress={() => navigation.goBack()} />
        </View>
    );
}
```

### Stack Navigation Methods

```javascript
navigation.navigate('ScreenName');                    // go to screen
navigation.navigate('ScreenName', { key: 'value' }); // with params
navigation.push('ScreenName');                        // push even if already in stack
navigation.goBack();                                  // pop current screen
navigation.popToTop();                                // pop to first screen
navigation.replace('ScreenName');                     // replace current screen
```

### Customizing the Header

```jsx
<Stack.Screen
    name="Profile"
    component={ProfileScreen}
    options={{
        title: 'Profile',
        headerStyle: { backgroundColor: '#6200ea' },
        headerTintColor: '#fff',
        headerRight: () => (
            <Button title="Edit" onPress={() => alert('Edit pressed')} />
        ),
        headerLeft: () => null,  // remove back button
    }}
/>
```

## Bottom Tab Navigator

Tab Navigator shows a persistent tab bar at the bottom — the standard pattern for top-level navigation sections.

```bash
$ npm install @react-navigation/bottom-tabs
```

```jsx
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';

const Tab = createBottomTabNavigator();

function AppTabs() {
    return (
        <Tab.Navigator
            screenOptions={({ route }) => ({
                tabBarIcon: ({ focused, color, size }) => {
                    const icons = {
                        Home: 'home',
                        Search: 'search',
                        Profile: 'person',
                    };
                    return <Icon name={icons[route.name]} size={size} color={color} />;
                },
                tabBarActiveTintColor: '#6200ea',
                tabBarInactiveTintColor: '#9e9e9e',
            })}
        >
            <Tab.Screen name="Home" component={HomeScreen} />
            <Tab.Screen name="Search" component={SearchScreen} />
            <Tab.Screen
                name="Profile"
                component={ProfileScreen}
                options={{ tabBarBadge: 3 }}  // notification badge
            />
        </Tab.Navigator>
    );
}
```

## Drawer Navigator

Drawer slides in from the left (or right) — common for settings, account switching, or secondary navigation sections.

```bash
$ npm install @react-navigation/drawer
$ npm install react-native-reanimated react-native-gesture-handler
```

```jsx
import { createDrawerNavigator } from '@react-navigation/drawer';

const Drawer = createDrawerNavigator();

function AppDrawer() {
    return (
        <Drawer.Navigator
            initialRouteName="Home"
            screenOptions={{
                drawerStyle: { backgroundColor: '#f5f5f5', width: 260 },
                drawerActiveTintColor: '#6200ea',
            }}
        >
            <Drawer.Screen name="Home" component={HomeScreen} />
            <Drawer.Screen name="Settings" component={SettingsScreen} />
            <Drawer.Screen name="About" component={AboutScreen} />
        </Drawer.Navigator>
    );
}
```

Open/close the drawer programmatically:

```javascript
navigation.openDrawer();
navigation.closeDrawer();
navigation.toggleDrawer();
```

## Nesting Navigators

Real apps need multiple navigator types together. The typical pattern is tabs at the top level, each tab containing a stack:

```jsx
function HomeStack() {
    return (
        <Stack.Navigator>
            <Stack.Screen name="HomeFeed" component={HomeFeedScreen} />
            <Stack.Screen name="PostDetail" component={PostDetailScreen} />
        </Stack.Navigator>
    );
}

function ProfileStack() {
    return (
        <Stack.Navigator>
            <Stack.Screen name="ProfileMain" component={ProfileMainScreen} />
            <Stack.Screen name="EditProfile" component={EditProfileScreen} />
        </Stack.Navigator>
    );
}

function AppTabs() {
    return (
        <Tab.Navigator screenOptions={{ headerShown: false }}>
            <Tab.Screen name="Home" component={HomeStack} />
            <Tab.Screen name="Profile" component={ProfileStack} />
        </Tab.Navigator>
    );
}

// Root — tabs with optional full-screen modal on top
const RootStack = createStackNavigator();

function App() {
    return (
        <NavigationContainer>
            <RootStack.Navigator screenOptions={{ headerShown: false }}>
                <RootStack.Screen name="Main" component={AppTabs} />
                <RootStack.Screen
                    name="Modal"
                    component={ModalScreen}
                    options={{ presentation: 'modal' }}
                />
            </RootStack.Navigator>
        </NavigationContainer>
    );
}
```

`headerShown: false` on the Tab navigator prevents double headers — the Stack within each tab handles its own header.

## TypeScript: Typed Navigation

```typescript
// types/navigation.ts
export type RootStackParamList = {
    Home: undefined;
    Detail: { id: number; title: string };
    Modal: { message: string };
};

export type TabParamList = {
    Home: undefined;
    Profile: undefined;
};
```

```typescript
import { NativeStackScreenProps } from '@react-navigation/native-stack';

type Props = NativeStackScreenProps<RootStackParamList, 'Detail'>;

function DetailScreen({ route, navigation }: Props) {
    const { id, title } = route.params;  // fully typed
    // ...
}
```

## Useful Hooks

Outside of screen components, use hooks to access navigation:

```javascript
import { useNavigation, useRoute, useFocusEffect } from '@react-navigation/native';

function SomeComponent() {
    const navigation = useNavigation();
    const route = useRoute();

    // Runs when screen comes into focus
    useFocusEffect(() => {
        fetchFreshData();
        return () => cancelFetch();  // cleanup when losing focus
    });

    return <Button title="Go Home" onPress={() => navigation.navigate('Home')} />;
}
```

## Conclusion

React Navigation's three navigators — Stack for hierarchical depth, Tab for top-level sections, Drawer for secondary navigation — cover every pattern you'll encounter in mobile apps. Nest them together (tabs containing stacks is the most common combination), use `screenOptions` to set consistent styling, and add TypeScript types to your param lists from the start to avoid prop typo bugs. The `useFocusEffect` hook is particularly useful for refreshing data when a user returns to a screen after navigating away.
