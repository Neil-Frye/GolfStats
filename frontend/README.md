# GolfStats Frontend

This is the frontend for the GolfStats application, a comprehensive golf performance tracking and analysis tool. The frontend provides an intuitive user interface for viewing golf statistics, managing rounds, and gaining insights into your golf game.

## Features

- **Dashboard**: Get a quick overview of your golf performance with key metrics.
- **Rounds Management**: Record and view your golf rounds with detailed statistics.
- **Performance Analytics**: Track improvements in your game over time with intuitive visualizations.
- **Club Statistics**: Monitor performance with each club in your bag.
- **Game Insights**: Get AI-powered recommendations to improve your game.
- **Goals Tracking**: Set and track improvement goals for different aspects of your game.
- **Mobile Responsive**: Fully responsive design that works on desktop, tablet, and mobile devices.

## Technologies Used

- **HTML5/CSS3**: Modern web standards for structure and styling.
- **JavaScript (ES6 Modules)**: Modern JavaScript with module pattern for better organization.
- **Chart.js**: For data visualization.
- **FontAwesome**: For icons.
- **Google Fonts**: For typography.

## Project Structure

The frontend codebase has been refactored into a modular structure following ES6 module patterns. This improves maintainability, reduces file sizes, and makes the codebase easier to navigate and debug.

### Directory Structure

```
frontend/
├── index.html         # Main HTML entry point
├── styles.css         # Main CSS file
├── login.html         # Login page
├── login.css          # Login-specific styles
├── login.js           # Login-specific JavaScript
├── js/                # JavaScript modules
│   ├── app.js         # Main application entry point
│   ├── api/           # API service modules
│   │   └── api.js     # Core API service
│   ├── auth/          # Authentication modules
│   │   └── auth.js    # Authentication functions
│   ├── ui/            # UI-related modules
│   │   └── ui.js      # Common UI functions
│   ├── dashboard/     # Dashboard-specific modules
│   │   └── dashboard.js # Dashboard functionality
│   ├── rounds/        # Rounds-related modules
│   │   └── rounds.js  # Rounds functionality
│   ├── clubs/         # Clubs-related modules (to be implemented)
│   ├── stats/         # Statistics-related modules (to be implemented)  
│   ├── charts/        # Chart-related modules (to be implemented)
│   ├── integrations/  # Integration-related modules (to be implemented)
│   └── utils/         # Utility functions (to be implemented)
```

### Module Organization

The codebase has been split into logical modules:

- **api.js**: Contains all API service methods for communicating with the backend
- **auth.js**: Handles user authentication, login/logout, and profile management
- **ui.js**: Contains common UI functions like navigation, modal dialogs, and toast notifications
- **dashboard.js**: Dashboard-specific functionality including charts and stats display
- **rounds.js**: Rounds functionality including listing, details, and creating new rounds

### Benefits of the Modular Approach

1. **Smaller File Sizes**: Each module is focused on a specific function, making files smaller and easier to maintain.
2. **Better Organization**: Code is organized by feature or responsibility.
3. **Improved Tooling Support**: Smaller files enable better handling by AI code assistants and developer tools.
4. **Enhanced Maintainability**: Isolated functionality makes debugging and extending features easier.
5. **Reduced Merge Conflicts**: Team members can work on different modules with fewer conflicts.
6. **Better Code Reuse**: Modular code promotes reusability across the application.

## Getting Started

1. Ensure the backend server is running (see the main project README).
2. Open `index.html` in a web browser to view the application.

## Development Notes

### How to Add New Features

1. **New Module**: Create a new JavaScript file in the appropriate subdirectory.
2. **Export Functions**: Use ES6 export syntax for functions that need to be accessible.
3. **Import Dependencies**: Import only what you need from other modules.
4. **Register in app.js**: For major features, import and initialize them in app.js.

### Coding Standards

- Use ES6 module syntax (import/export)
- Follow the file organization pattern
- Maintain separation of concerns between modules
- Avoid circular dependencies between modules

## Design Decisions

- **Modern UI**: Clean, intuitive interface inspired by modern web applications but tailored specifically for golfers.
- **Card-based Layout**: Information is organized in cards for better visual separation and focus.
- **Performance-First**: Optimized for speed and responsiveness, even with large datasets.
- **Data Visualization**: Emphasis on charts and visualizations to make statistics more meaningful.
- **User Experience**: Designed with the golfer's journey in mind, making it easy to track progress over time.

## Future Enhancements

- Integration with more golf tracking devices and apps
- Enhanced shot tracking with detailed analytics
- Course management features
- Social features to compare with friends
- Advanced AI-powered swing and strategy recommendations
- Tournament mode for tracking competitive rounds

## Screenshots

(Screenshots will be added as the project develops)

## Comparison with Clippd

While inspired by Clippd's functionality, GolfStats improves upon it in several ways:

1. **More Intuitive Interface**: Streamlined design that puts key information front and center
2. **Faster Performance**: Optimized for speed even on mobile devices
3. **Better Data Visualization**: More meaningful charts that show progress over time
4. **Actionable Insights**: Clearer recommendations for game improvement
5. **Custom Goal Tracking**: Better tools for setting and monitoring golf improvement goals
6. **Club-specific Analysis**: More detailed insights for each club in your bag
7. **Open Platform**: Designed to work with data from multiple sources and systems