/**
 * Creates an icon button element with the given options.
 *
 * @param {object} options - The options for creating the icon button.
 * @param {string} [options.id] - The ID of the button.
 * @param {string} options.iconClass - The Font Awesome icon class for the button. (Required)
 * @param {function} [options.onClick] - The click event handler for the button.
 * @param {string} [options.variant] - The variant of the button (e.g., 'primary', 'accent').
 * @param {boolean} [options.isActive] - Whether the button is active.
 * @param {string} [options.tooltip] - The tooltip text for the button.
 * @param {string} [options.ariaLabel] - The ARIA label for the button.
 * @returns {HTMLButtonElement} The created icon button element.
 */
export function createIconButton(options) {
  const { id, iconClass, onClick, variant, isActive, tooltip, ariaLabel } = options;

  if (!iconClass) {
    throw new Error("iconClass is a required option for createIconButton.");
  }

  const button = document.createElement('button');
  button.classList.add('custom-icon-btn');

  if (variant) {
    button.classList.add(`variant-${variant}`);
  }

  if (isActive) {
    button.classList.add('active');
  }

  if (id) {
    button.id = id;
  }

  const icon = document.createElement('i');
  icon.classList.add('fas', iconClass);
  button.appendChild(icon);

  if (onClick && typeof onClick === 'function') {
    button.addEventListener('click', onClick);
  }

  if (tooltip) {
    button.title = tooltip;
  }

  if (ariaLabel) {
    button.setAttribute('aria-label', ariaLabel);
  } else if (tooltip) {
    button.setAttribute('aria-label', tooltip);
  } else {
    // Fallback aria-label if none is provided
    button.setAttribute('aria-label', 'Icon button');
  }

  return button;
}
