"""
Tutor plugin to brand your Open edX instance with the Inovatec theme.
Includes full dark-mode toggle, custom footer, logo slot, and MFE styling.
"""
import itertools
import json
import os
import typing as t
from glob import glob

import click
import importlib_resources
from tutormfe.hooks import MFE_APPS, MFE_ATTRS_TYPE, PLUGIN_SLOTS

from tutor import config as tutor_config
from tutor import fmt, hooks

from .__about__ import __version__

# Configuration
config = {
    # Add here your new settings
    "defaults": {
        "VERSION": __version__,
        "WELCOME_MESSAGE": "Welcome to Open edX®",
        # Enable/disable dark theme toggle in MFEs
        "ENABLE_DARK_TOGGLE": True,
        # Footer links are dictionaries with a "title" and "url"
        # To remove all links, run:
        # tutor config save --set BRANDING_FOOTER_NAV_LINKS=[] --set BRANDING_FOOTER_LEGAL_LINKS=[]
        "FOOTER_NAV_LINKS": [
            {"title": "About", "url": "/about"},
            {"title": "Contact", "url": "/contact"},
        ],
        "FOOTER_LEGAL_LINKS": [
            {"title": "Terms of service", "url": "/tos"},
        ],
        "BACKGROUND": "#ffffff",
        "BG_PRIMARY": "#ffffff",
        "BODY": "#FFFFFF",
        "PRIMARY": "#244FFF",
        "SECONDARY": "#262F99",
        "FONT_FAMILY": "",
        "BRAND": "#1D3FCF",
        "SUCCESS": "#178253",
        "INFO": "#D3F2FF",
        "DANGER": "#C32D3A",
        "WARNING": "#FFD900",
        "LIGHT": "#D3DCFF",
        "DARK": "#0B1541",
        "ACCENT_A": "#A7B9FF",
        "ACCENT_B": "#D3DCFF",
        "HOMEPAGE_BG_IMAGE": "",
        # EXTRAS: additional CSS for html theme
        "EXTRAS": "",
        # OVERRIDES: additional CSS for mfe branding
        "OVERRIDES": "",
        "FONTS": "",
        "LMS_IMAGES": [],
        "CMS_IMAGES": [],
        "FONTS_URLS": [],

        "MFE": {},
        "MFE_LOGO_URL": '',
        "MFE_LOGO_WHITE_URL": '',
        "MFE_LOGO_TRADEMARK_URL": '',

        # Repos
        "MFE_PLATFORM_REPO": None,

        # Customizations of the learner dashboard in Quince. May not apply if the MFE is redesigned.
        "HIDE_DASHBOARD_SIDEBAR": False,
        "HIDE_LOOKING_FOR_CHALLENGE_WIDGET": False,
        "FIT_COURSE_IMAGE": True,

        # static page templates
        "STATIC_TEMPLATE_404": None,
        "STATIC_TEMPLATE_429": None,
        "STATIC_TEMPLATE_ABOUT": None,
        "STATIC_TEMPLATE_BLOG": None,
        "STATIC_TEMPLATE_CONTACT": None,
        "STATIC_TEMPLATE_DONATE": None,
        "STATIC_TEMPLATE_EMBARGO": None,
        "STATIC_TEMPLATE_FAQ": None,
        "STATIC_TEMPLATE_HELP": None,
        "STATIC_TEMPLATE_HONOR": None,
        "STATIC_TEMPLATE_JOBS": None,
        "STATIC_TEMPLATE_MEDIA_KIT": None,
        "STATIC_TEMPLATE_NEWS": None,
        "STATIC_TEMPLATE_PRESS": None,
        "STATIC_TEMPLATE_PRIVACY": None,
        "STATIC_TEMPLATE_SERVER_DOWN": None,
        "STATIC_TEMPLATE_SERVER_ERROR": None,
        "STATIC_TEMPLATE_SERVER_OVERLOADED": None,
        "STATIC_TEMPLATE_SITEMAP": None,
        "STATIC_TEMPLATE_TOS": None,
    },
    "unique": {},
    "overrides": {},
}

hooks.Filters.CONFIG_DEFAULTS.add_items(
    [(f"BRANDING_{key}", value) for key, value in config["defaults"].items()]
)

hooks.Filters.CONFIG_UNIQUE.add_items(
    [(f"BRANDING_{key}", value) for key, value in config["unique"].items()]
)

hooks.Filters.CONFIG_OVERRIDES.add_items(
    list(config["overrides"].items())
)

# Initialization tasks
# To run the script from templates/panorama/tasks/myservice/init, add:
with open(
        str(importlib_resources.files("tutorbranding") / "templates" / "tasks" / "lms" / "init"),
        encoding="utf-8",
) as task_file:
    hooks.Filters.CLI_DO_INIT_TASKS.add_item(("lms", task_file.read()))

# Add the "templates" folder as a template root
hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    str(importlib_resources.files("tutorbranding") / "templates")
)

hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("inovatec", "build/openedx/themes"),
        ("brand-openedx", "plugins/mfe/build/mfe"),
        ("brand-openedx-learner-dashboard", "plugins/mfe/build/mfe"),
    ],
)

# Force the rendering of scss files, even though they are included in a "partials" directory
hooks.Filters.ENV_PATTERNS_INCLUDE.add_items([
    r"inovatec/lms/static/sass/partials/lms/theme/",
    r"inovatec/cms/static/sass/partials/cms/theme/",
])

# ---- MFE styled with the Inovatec brand package ----
inovatec_styled_mfes = [
    "learning",
    "learner-dashboard",
    "profile",
    "account",
    "discussions",
]

for mfe in inovatec_styled_mfes:
    hooks.Filters.ENV_PATCHES.add_item((
        f"mfe-dockerfile-post-npm-install-{mfe}",
        "RUN npm install '@edx/brand@file:/openedx/brand-openedx'",
    ))

hooks.Filters.ENV_PATCHES.add_item((
    "mfe-dockerfile-post-npm-install-authn",
    "RUN npm install '@edx/brand@file:/openedx/brand-openedx'",
))

# ---- Pipeline JS patches (adds dark-theme.js to LMS pages) ----
hooks.Filters.ENV_PATCHES.add_items([
    (
        "openedx-common-assets-settings",
        """
javascript_files = ['base_application', 'application', 'certificates_wv']
dark_theme_filepath = ['inovatec/js/dark-theme.js']

for filename in javascript_files:
    if filename in PIPELINE['JAVASCRIPT']:
        PIPELINE['JAVASCRIPT'][filename]['source_filenames'] += dark_theme_filepath
""",
    ),
    (
        "openedx-lms-development-settings",
        """
javascript_files = ['base_application', 'application', 'certificates_wv']
dark_theme_filepath = ['inovatec/js/dark-theme.js']

for filename in javascript_files:
    if filename in PIPELINE['JAVASCRIPT']:
        PIPELINE['JAVASCRIPT'][filename]['source_filenames'] += dark_theme_filepath

MFE_CONFIG['BRANDING_ENABLE_DARK_TOGGLE'] = {{ BRANDING_ENABLE_DARK_TOGGLE }}
MFE_CONFIG['BRANDING_FOOTER_NAV_LINKS'] = {{ BRANDING_FOOTER_NAV_LINKS }}
""",
    ),
    (
        "openedx-lms-production-settings",
        """
MFE_CONFIG['BRANDING_ENABLE_DARK_TOGGLE'] = {{ BRANDING_ENABLE_DARK_TOGGLE }}
MFE_CONFIG['BRANDING_FOOTER_NAV_LINKS'] = {{ BRANDING_FOOTER_NAV_LINKS }}
""",
    ),
])

# ---- Plugin Slots: footer, dark theme reader, toggle button, mobile header ----
for mfe in inovatec_styled_mfes:
    PLUGIN_SLOTS.add_item((
        mfe,
        "org.openedx.frontend.layout.footer.v1",
        """
        {
            op: PLUGIN_OPERATIONS.Hide,
            widgetId: 'default_contents',
        },
        {
            op: PLUGIN_OPERATIONS.Insert,
            widget: {
                id: 'inovatec_footer',
                type: DIRECT_PLUGIN,
                priority: 1,
                RenderWidget: InovatecFooter,
            },
        },
        {
            op: PLUGIN_OPERATIONS.Insert,
            widget: {
                id: 'read_theme_cookie',
                type: DIRECT_PLUGIN,
                priority: 2,
                RenderWidget: AddDarkTheme,
            },
        },
        """,
    ))
    if mfe != "learning":
        PLUGIN_SLOTS.add_item((
            mfe,
            "desktop_secondary_menu_slot",
            """
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'theme_switch_button',
                    type: DIRECT_PLUGIN,
                    RenderWidget: ToggleThemeButton,
                },
            },
            """,
        ))
        PLUGIN_SLOTS.add_items([
            (
                mfe,
                "mobile_header_slot",
                """
            {
                op: PLUGIN_OPERATIONS.Hide,
                widgetId: 'default_contents',
            }
            """,
            ),
            (
                mfe,
                "mobile_header_slot",
                """
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'theme_switch_button',
                    type: DIRECT_PLUGIN,
                    RenderWidget: MobileViewHeader,
                },
            },
            """,
            ),
        ])

PLUGIN_SLOTS.add_items([
    (
        "learning",
        "learning_help_slot",
        """
    {
        op: PLUGIN_OPERATIONS.Hide,
        widgetId: 'default_contents',
    }
    """,
    ),
    (
        "learning",
        "learning_help_slot",
        """
    {
        op: PLUGIN_OPERATIONS.Insert,
        widget: {
            id: 'theme_switch_button',
            type: DIRECT_PLUGIN,
            RenderWidget: ToggleThemeButton,
        },
    },
    """,
    ),
])

# ---- Paragon theme URLs (light + dark CSS) ----
paragon_theme_urls: t.Dict[str, t.Any] = {
    "variants": {
        "light": {
            "urls": {
                "default": "https://raw.githubusercontent.com/edly-io/brand-openedx/refs/heads/ulmo/indigo/dist/light.min.css",
                "brandOverride": "https://raw.githubusercontent.com/edly-io/brand-openedx/refs/heads/ulmo/indigo/dist/light.min.css",
            },
        },
        "dark": {
            "urls": {
                "default": "https://raw.githubusercontent.com/edly-io/brand-openedx/refs/heads/ulmo/indigo/dist/dark.min.css",
                "brandOverride": "https://raw.githubusercontent.com/edly-io/brand-openedx/refs/heads/ulmo/indigo/dist/dark.min.css",
            },
        },
    }
}

hooks.Filters.ENV_PATCHES.add_item((
    "mfe-lms-common-settings",
    f'MFE_CONFIG["PARAGON_THEME_URLS"] = {json.dumps(paragon_theme_urls)}\n'
    + '{% if BRANDING_MFE_LOGO_URL %}MFE_CONFIG["LOGO_URL"] = "{{ BRANDING_MFE_LOGO_URL }}"{% endif %}\n'
    + '{% if BRANDING_MFE_LOGO_WHITE_URL %}MFE_CONFIG["LOGO_WHITE_URL"] = "{{ BRANDING_MFE_LOGO_WHITE_URL }}"{% endif %}\n'
    + '{% if BRANDING_MFE_LOGO_TRADEMARK_URL %}MFE_CONFIG["LOGO_TRADEMARK_URL"] = "{{ BRANDING_MFE_LOGO_TRADEMARK_URL }}"{% endif %}\n',
))

# ---- Logo slot: swap default logo for ThemedLogo in every MFE ----
@MFE_APPS.add()
def _add_themed_logo(mfes: dict[str, MFE_ATTRS_TYPE]) -> dict[str, MFE_ATTRS_TYPE]:
    for mfe in mfes:
        PLUGIN_SLOTS.add_item((
            str(mfe),
            "logo_slot",
            """
            {
                op: PLUGIN_OPERATIONS.Hide,
                widgetId: 'default_contents',
            },
            {
                op: PLUGIN_OPERATIONS.Insert,
                widget: {
                    id: 'custom_logo',
                    type: DIRECT_PLUGIN,
                    RenderWidget: ThemedLogo,
                }
            }
            """,
        ))
    return mfes


# ---- Custom MFE support (add or override MFE repos/ports) ----
@MFE_APPS.add()
def _add_custom_mfes(mfes: dict[str, MFE_ATTRS_TYPE]) -> dict[str, MFE_ATTRS_TYPE]:
    current_context = click.get_current_context()
    root = current_context.params.get('root')
    if root:
        configuration = tutor_config.load(root)
        for mfe_name, mfe_config in configuration['BRANDING_MFE'].items():
            if mfe_name not in mfes:
                if 'repository' not in mfe_config:
                    fmt.echo_error(f"Custom MFE {mfe_name} must have a repository")
                    exit(1)
                if 'port' not in mfe_config:
                    fmt.echo_error(f"Custom MFE {mfe_name} must have a port")
                    exit(1)
                for base_mfe_name, base_mfe_config in mfes.items():
                    if base_mfe_config['port'] == mfe_config['port']:
                        fmt.echo_error(f"Custom MFE {mfe_name} port {mfe_config['port']} already taken by {base_mfe_name}")
                        exit(1)
                fmt.echo_info(f"Adding custom MFE {mfe_name} with repository {mfe_config['repository']} and port {mfe_config['port']}")
                mfes[mfe_name] = mfe_config
            else:
                mfes[mfe_name].update(mfe_config)
    return mfes


# ---- Load all patches and components from files ----
for path in itertools.chain(
    glob(str(importlib_resources.files("tutorbranding") / "components" / "*")),
    glob(str(importlib_resources.files("tutorbranding") / "patches" / "*")),
):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))

