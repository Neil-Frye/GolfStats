/**
 * Creates a button element with the given options.
 *
 * @param {object} options - The options for creating the button.
 * @param {string} [options.id] - The ID of the button.
 * @param {string} [options.label] - The label text of the button.
 * @param {string} [options.iconClass] - The Font Awesome icon class for the button.
 * @param {function} [options.onClick] - The click event handler for the button.
 * @param {string} [options.variant] - The variant of the button (e.g., 'primary', 'accent').
 * @param {boolean} [options.isActive] - Whether the button is active.
 * @param {string} [options.ariaLabel] - The ARIA label for the button.
 * @returns {HTMLButtonElement} The created button element.
 */
export function createButton(options) {
  const { id, label, iconClass, onClick, variant, isActive, ariaLabel } = options;

  const button = document.createElement('button');
  button.classList.add('custom-btn');

  if (variant) {
    button.classList.add(`variant-${variant}`);
  }

  if (isActive) {
    button.classList.add('active');
  }

  if (id) {
    button.id = id;
  }

  if (iconClass) {
    const icon = document.createElement('i');
    icon.classList.add('fas', iconClass);
    button.appendChild(icon);
  }

  if (label) {
    const span = document.createElement('span');
    span.textContent = label;
    button.appendChild(span);
  }

  if (onClick && typeof onClick === 'function') {
    button.addEventListener('click', onClick);
  }

  if (ariaLabel) {
    button.setAttribute('aria-label', ariaLabel);
  } else if (label) {
    button.setAttribute('aria-label', label);
  }

  return button;
}
