// Internal state object
let state = {
  isRecording: false,
  currentSessionId: null,
  activeMode: 'Practice', // e.g., 'Practice', 'Challenge', 'OnCourse'
  selectedShotId: null,
  allShots: [], // Array to hold all recorded shots
  shotSettings: {}, // Settings related to shot tracking (e.g., club, target distance)
};

// Internal listeners object
const listeners = {};

/**
 * Returns a deep copy of the current state.
 * @returns {object} A deep copy of the state.
 */
export function getState() {
  return JSON.parse(JSON.stringify(state));
}

/**
 * Merges the newState object into the current state and notifies listeners.
 * @param {object} newState - The new state properties to merge.
 */
export function setState(newState) {
  const prevState = JSON.parse(JSON.stringify(state));
  state = { ...state, ...newState };

  // Notify listeners for specific changed keys
  for (const key in newState) {
    if (newState.hasOwnProperty(key) && prevState[key] !== state[key]) {
      publish(key, state[key]);
    }
  }

  // Notify general state change listeners
  publish('stateChange', getState());
}

/**
 * Adds a callback to an array for the given event in the listeners object.
 * @param {string} event - The event to subscribe to.
 * @param {function} callback - The callback function to execute.
 */
export function subscribe(event, callback) {
  if (!listeners[event]) {
    listeners[event] = [];
  }
  listeners[event].push(callback);
}

/**
 * Calls all callbacks registered for the event, passing the data to them.
 * @param {string} event - The event to publish.
 * @param {*} data - The data to pass to the callbacks.
 */
function publish(event, data) {
  if (!listeners[event]) {
    return;
  }
  listeners[event].forEach(callback => {
    try {
      callback(data);
    } catch (error) {
      console.error(`Error in listener for event "${event}":`, error);
    }
  });
}
