package com.bvawc.app

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ExampleUnitTest {

    @Test
    fun blockedPatterns_blocksAdminPath() {
        assertTrue(Config.isBlockedUrl("https://example.com/admin"))
        assertTrue(Config.isBlockedUrl("https://example.com/admin/"))
        assertTrue(Config.isBlockedUrl("https://example.com/admin/dashboard"))
        assertTrue(Config.isBlockedUrl("https://example.com/admin?page=1"))
    }

    @Test
    fun blockedPatterns_blocksApiPaths() {
        assertTrue(Config.isBlockedUrl("https://example.com/api/cases"))
        assertTrue(Config.isBlockedUrl("https://example.com/api/cases/123"))
        assertTrue(Config.isBlockedUrl("https://example.com/api/dashboard/stats"))
        assertTrue(Config.isBlockedUrl("https://example.com/api/users"))
        assertTrue(Config.isBlockedUrl("https://example.com/api/notifications"))
        assertTrue(Config.isBlockedUrl("https://example.com/api/evidence/1"))
        assertTrue(Config.isBlockedUrl("https://example.com/api/referrals/1/status"))
        assertTrue(Config.isBlockedUrl("https://example.com/api/register"))
        assertTrue(Config.isBlockedUrl("https://example.com/api/login"))
    }

    @Test
    fun blockedPatterns_allowsPublicPaths() {
        assertFalse(Config.isBlockedUrl("https://example.com/"))
        assertFalse(Config.isBlockedUrl("https://example.com/report"))
        assertFalse(Config.isBlockedUrl("https://example.com/submit_report"))
        assertFalse(Config.isBlockedUrl("https://example.com/view_reports"))
        assertFalse(Config.isBlockedUrl("https://example.com/api/health"))
        assertFalse(Config.isBlockedUrl("https://example.com/static/report.css"))
        assertFalse(Config.isBlockedUrl("https://example.com/static/awareness.js"))
    }
}
