---
layout: post
title: React Native Stylesheet Cheat Sheet
date: "2024-01-20 00:00:00 +0530"
slug: react-native-stylesheet-cheat-sheet
description: "Creating a cheat sheet for React Native’s StyleSheet can be very useful for quick reference. Here’s a concise overview of some of the most commonly used style properties in React Native: Layout…"
categories: ["Programming", "wiki"]
tags: ["react native", "stylesheet", "cheatsheet", "mobile development", "javascript", "flex", "layout", "styling", "tutorial", "react"]
---

Creating a cheat sheet for React Native’s StyleSheet can be very useful for quick reference. Here’s a concise overview of some of the most commonly used style properties in React Native:

### Layout

- **`flex`**: Defines how a component will grow or shrink to fit the space available in its parent container.
- **`flexDirection`**: Defines the direction of children elements (`row`, `column`).
- **`justifyContent`**: Aligns children in the main direction (`flex-start`, `center`, `flex-end`, `space-around`, `space-between`).
- **`alignItems`**: Aligns children in the cross direction (`flex-start`, `center`, `flex-end`, `stretch`).
- **`alignSelf`**: Overrides `alignItems` for specific children.
- **`margin`**, **`padding`**: Space outside and inside of an element, respectively.
- **`width`**, **`height`**: Size of the element.

### Positioning

- **`position`**: Type of positioning (`absolute`, `relative`).
- **`top`**, **`right`**, **`bottom`**, **`left`**: Position of an element with `position: absolute`.

### Text

- **`fontSize`**: Size of the font.
- **`fontWeight`**: Weight of the font (`normal`, `bold`, `100`, `200`, …, `900`).
- **`textAlign`**: Alignment of text (`center`, `left`, `right`).
- **`color`**: Color of the text.

### View Styles

- **`backgroundColor`**: Background color of an element.
- **`borderWidth`**, **`borderColor`**: Width and color of the border.
- **`borderRadius`**: Radius of element corners.
- **`opacity`**: Opacity of the element.

### Image

- **`resizeMode`**: Determines how to resize the image (`cover`, `contain`, `stretch`, `repeat`, `center`).

### Flexbox

- **`flexWrap`**: Wrapping of children (`wrap`, `nowrap`).
- **`alignContent`**: Alignment of multiple lines or children in a flex container.

### Miscellaneous

- **`elevation`**: Elevation/shadow of an element (Android).
- **`shadowColor`**, **`shadowOffset`**, **`shadowOpacity`**, **`shadowRadius`**: Shadow properties (iOS).

These properties are used within the `StyleSheet.create` function to define styles in React Native. Remember, React Native uses camelCase for the CSS properties instead of kebab-case used in regular CSS.

```javascript
const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5FCFF',
  },
  text: {
    fontSize: 20,
    textAlign: 'center',
    margin: 10,
  },
});

```

This is just a basic overview, and React Native’s styling capabilities are much more extensive, supporting most of what you can do in regular CSS and more.
