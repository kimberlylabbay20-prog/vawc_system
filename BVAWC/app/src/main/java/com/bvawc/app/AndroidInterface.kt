package com.bvawc.app

import android.content.Context
import android.webkit.JavascriptInterface
import android.widget.Toast

class AndroidInterface(private val context: Context) {

    @JavascriptInterface
    fun showToast(message: String) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }

    @JavascriptInterface
    fun getAppVersion(): String {
        return BuildConfig.VERSION_NAME
    }

    @JavascriptInterface
    fun isAndroid(): Boolean {
        return true
    }
}
