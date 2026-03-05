
const InovatecFooter = () => {
  const intl = useIntl();
  const config = getConfig();

  const footerNavLinks = config.BRANDING_FOOTER_NAV_LINKS || [];

  const messages = {
    "footer.poweredby.text": {
      id: "footer.poweredby.text",
      defaultMessage: "Powered by",
      description: "text for the footer",
    },
    "footer.tutorlogo.altText": {
      id: "footer.tutorlogo.altText",
      defaultMessage: "Runs on Tutor",
      description: "alt text for the footer tutor logo",
    },
    "footer.logo.altText": {
      id: "footer.logo.altText",
      defaultMessage: "Powered by Open edX",
      description: "alt text for the footer logo.",
    },
    "footer.copyright.text": {
      id: "footer.copyright.text",
      defaultMessage: `Copyrights ©${new Date().getFullYear()}. All Rights Reserved.`,
      description: "copyright text for the footer",
    },
  };

  return (
    <div className="wrapper wrapper-footer">
      <footer id="footer" className="tutor-container">
        <div className="footer-top">
          <div className="powered-area">
            <ul className="logo-list">
              <li>{intl.formatMessage(messages["footer.poweredby.text"])}</li>
              <li>
                <a href="https://open.edx.org" rel="noreferrer" target="_blank">
                  <img
                    src={`${config.LMS_BASE_URL}/theming/asset/images/openedx-logo.png`}
                    alt={intl.formatMessage(messages["footer.logo.altText"])}
                    width="79"
                  />
                </a>
              </li>
            </ul>
          </div>
          <nav className="nav-colophon">
            <ol>
              {footerNavLinks.map((link) => (
                <li key={link.url}>
                  <a href={`${config.LMS_BASE_URL}${link.url}`}>{link.title}</a>
                </li>
              ))}
            </ol>
          </nav>
        </div>
        <span className="copyright-site">
          {intl.formatMessage(messages["footer.copyright.text"])}
        </span>
      </footer>
    </div>
  );
};
