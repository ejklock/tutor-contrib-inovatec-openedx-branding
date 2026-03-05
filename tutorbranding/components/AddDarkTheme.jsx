
let themeVariant = 'selected-paragon-theme-variant';

const AddDarkTheme = () => {
  const isThemeToggleEnabled = getConfig().BRANDING_ENABLE_DARK_TOGGLE;

  const addDarkThemeToIframes = () => {
    const iframes = document.getElementsByTagName('iframe');
    const iframesLength = iframes.length;
    if (iframesLength > 0) {
      Array.from({ length: iframesLength }).forEach((_, index) => {
        const style = document.createElement('style');
        style.textContent = `
          body {
            background-color: #0D0D0E;
            color: #ccc;
          }
          a { color: #ccc; }
          a:hover { color: #d3d3d3; }
        `;
        if (iframes[index].contentDocument) {
          iframes[index].contentDocument.head.appendChild(style);
        }
      });
    }
  };

  useEffect(() => {
    const theme = window.localStorage.getItem(themeVariant);

    const observer = new MutationObserver(() => {
      addDarkThemeToIframes();
    });

    if (isThemeToggleEnabled && theme === 'dark') {
      document.documentElement.setAttribute('data-paragon-theme-variant', 'dark');
      observer.observe(document.body, { childList: true, subtree: true });
      setTimeout(() => observer?.disconnect(), 15000);
    }

    return () => observer?.disconnect();
  }, []);

  return (<div />);
};
