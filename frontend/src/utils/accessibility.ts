interface FocusTrapOptions {
  onEscape?: () => void;
  onOutsideClick?: () => void;
  initialFocus?: HTMLElement;
}

class AccessibilityManager {
  private focusableElements = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
  private activeFocusTrap: HTMLElement | null = null;
  private previousActiveElement: HTMLElement | null = null;

  public setupFocusTrap(container: HTMLElement, options: FocusTrapOptions = {}) {
    this.activeFocusTrap = container;
    this.previousActiveElement = document.activeElement as HTMLElement;

    // Focus the initial element or the first focusable element
    const initialFocus = options.initialFocus || this.getFirstFocusableElement(container);
    if (initialFocus) {
      initialFocus.focus();
    }

    // Handle escape key
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && options.onEscape) {
        options.onEscape();
      }
    };

    // Handle outside clicks
    const handleOutsideClick = (event: MouseEvent) => {
      if (
        options.onOutsideClick &&
        container &&
        !container.contains(event.target as Node)
      ) {
        options.onOutsideClick();
      }
    };

    // Handle tab key
    const handleTab = (event: KeyboardEvent) => {
      if (!container) return;

      const focusableElements = this.getFocusableElements(container);
      const firstFocusable = focusableElements[0];
      const lastFocusable = focusableElements[focusableElements.length - 1];

      if (event.shiftKey) {
        if (document.activeElement === firstFocusable) {
          lastFocusable.focus();
          event.preventDefault();
        }
      } else {
        if (document.activeElement === lastFocusable) {
          firstFocusable.focus();
          event.preventDefault();
        }
      }
    };

    document.addEventListener('keydown', handleEscape);
    document.addEventListener('keydown', handleTab);
    document.addEventListener('mousedown', handleOutsideClick);

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('keydown', handleTab);
      document.removeEventListener('mousedown', handleOutsideClick);
      this.releaseFocusTrap();
    };
  }

  public releaseFocusTrap() {
    if (this.previousActiveElement) {
      this.previousActiveElement.focus();
    }
    this.activeFocusTrap = null;
    this.previousActiveElement = null;
  }

  private getFocusableElements(container: HTMLElement): HTMLElement[] {
    return Array.from(
      container.querySelectorAll<HTMLElement>(this.focusableElements)
    ).filter((element) => {
      const style = window.getComputedStyle(element);
      return (
        style.display !== 'none' &&
        style.visibility !== 'hidden' &&
        !element.hasAttribute('disabled') &&
        !element.hasAttribute('aria-hidden')
      );
    });
  }

  private getFirstFocusableElement(container: HTMLElement): HTMLElement | null {
    const focusableElements = this.getFocusableElements(container);
    return focusableElements[0] || null;
  }

  public announceToScreenReader(message: string, politeness: 'polite' | 'assertive' = 'polite') {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', politeness);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.setAttribute('class', 'sr-only');
    announcement.textContent = message;

    document.body.appendChild(announcement);
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }

  public setAriaLabel(element: HTMLElement, label: string) {
    element.setAttribute('aria-label', label);
  }

  public setAriaDescribedBy(element: HTMLElement, descriptionId: string) {
    element.setAttribute('aria-describedby', descriptionId);
  }

  public setAriaControls(element: HTMLElement, controlledId: string) {
    element.setAttribute('aria-controls', controlledId);
  }

  public setAriaExpanded(element: HTMLElement, expanded: boolean) {
    element.setAttribute('aria-expanded', expanded.toString());
  }

  public setAriaHidden(element: HTMLElement, hidden: boolean) {
    element.setAttribute('aria-hidden', hidden.toString());
  }

  public setAriaInvalid(element: HTMLElement, invalid: boolean) {
    element.setAttribute('aria-invalid', invalid.toString());
  }

  public setAriaRequired(element: HTMLElement, required: boolean) {
    element.setAttribute('aria-required', required.toString());
  }

  public setAriaSelected(element: HTMLElement, selected: boolean) {
    element.setAttribute('aria-selected', selected.toString());
  }

  public setAriaChecked(element: HTMLElement, checked: boolean) {
    element.setAttribute('aria-checked', checked.toString());
  }

  public setAriaPressed(element: HTMLElement, pressed: boolean) {
    element.setAttribute('aria-pressed', pressed.toString());
  }

  public setAriaCurrent(element: HTMLElement, current: boolean | 'page' | 'step' | 'location' | 'date' | 'time') {
    element.setAttribute('aria-current', current.toString());
  }
}

// Create singleton instance
export const accessibilityManager = new AccessibilityManager();

// Export convenience functions
export const setupFocusTrap = accessibilityManager.setupFocusTrap.bind(accessibilityManager);
export const announceToScreenReader = accessibilityManager.announceToScreenReader.bind(accessibilityManager);
export const setAriaLabel = accessibilityManager.setAriaLabel.bind(accessibilityManager);
export const setAriaDescribedBy = accessibilityManager.setAriaDescribedBy.bind(accessibilityManager);
export const setAriaControls = accessibilityManager.setAriaControls.bind(accessibilityManager);
export const setAriaExpanded = accessibilityManager.setAriaExpanded.bind(accessibilityManager);
export const setAriaHidden = accessibilityManager.setAriaHidden.bind(accessibilityManager);
export const setAriaInvalid = accessibilityManager.setAriaInvalid.bind(accessibilityManager);
export const setAriaRequired = accessibilityManager.setAriaRequired.bind(accessibilityManager);
export const setAriaSelected = accessibilityManager.setAriaSelected.bind(accessibilityManager);
export const setAriaChecked = accessibilityManager.setAriaChecked.bind(accessibilityManager);
export const setAriaPressed = accessibilityManager.setAriaPressed.bind(accessibilityManager);
export const setAriaCurrent = accessibilityManager.setAriaCurrent.bind(accessibilityManager); 