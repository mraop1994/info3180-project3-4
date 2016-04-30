class BaseConfig(object):
    """Base configuration."""

    # main config
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # mail accounts
    MAIL_DEFAULT_SENDER = 'someone@gmail.com'