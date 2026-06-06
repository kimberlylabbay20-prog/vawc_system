package com.bvawc.app

object Config {
    val APP_URL: String
        get() = if (BuildConfig.USE_DEV_URL) BuildConfig.DEV_URL else BuildConfig.APP_URL

    const val SPLASH_DURATION_MS: Long = 2000L

    val BLOCKED_PATTERNS: List<Regex> = listOf(
        Regex(".*/admin($|[?#/].*)", RegexOption.IGNORE_CASE),
        Regex(".*/api/cases.*", RegexOption.IGNORE_CASE),
        Regex(".*/api/dashboard.*", RegexOption.IGNORE_CASE),
        Regex(".*/api/users.*", RegexOption.IGNORE_CASE),
        Regex(".*/api/notifications.*", RegexOption.IGNORE_CASE),
        Regex(".*/api/evidence.*", RegexOption.IGNORE_CASE),
        Regex(".*/api/referrals.*", RegexOption.IGNORE_CASE),
        Regex(".*/api/register.*", RegexOption.IGNORE_CASE),
        Regex(".*/api/login.*", RegexOption.IGNORE_CASE),
    )

    fun isBlockedUrl(url: String): Boolean {
        return BLOCKED_PATTERNS.any { it.matches(url) }
    }
}
