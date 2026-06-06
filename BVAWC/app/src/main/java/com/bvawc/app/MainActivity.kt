package com.bvawc.app

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.KeyEvent
import android.view.View
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var swipeRefresh: SwipeRefreshLayout
    private lateinit var loadingIndicator: ProgressBar
    private lateinit var errorText: TextView

    private var chromeClient: BVAWCChromeClient? = null

    companion object {
        private const val PERMISSION_REQUEST_CODE = 2000
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webview)
        swipeRefresh = findViewById(R.id.swipe_refresh)
        loadingIndicator = findViewById(R.id.loading_indicator)
        errorText = findViewById(R.id.error_text)

        chromeClient = BVAWCChromeClient(this)

        requestRequiredPermissions()
        configureWebView()
        setupSwipeRefresh()
        loadAppUrl()
    }

    private fun configureWebView() {
        webView.apply {
            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                allowFileAccess = true
                allowContentAccess = true
                setSupportMultipleWindows(false)
                javaScriptCanOpenWindowsAutomatically = false
                builtInZoomControls = false
                displayZoomControls = false
                loadWithOverviewMode = true
                useWideViewPort = true
                setSupportZoom(true)
                allowFileAccessFromFileURLs = false
                allowUniversalAccessFromFileURLs = false
                mixedContentMode = android.webkit.WebSettings.MIXED_CONTENT_NEVER_ALLOW
                cacheMode = android.webkit.WebSettings.LOAD_DEFAULT
                userAgentString = settings.userAgentString
                    .replace("; wv", "")
            }

            setWebViewClient(object : WebViewClient() {
                override fun shouldOverrideUrlLoading(
                    view: WebView,
                    request: WebResourceRequest
                ): Boolean {
                    val url = request.url.toString()
                    return handleUrl(url)
                }

                @Deprecated("Deprecated")
                override fun shouldOverrideUrlLoading(view: WebView, url: String): Boolean {
                    return handleUrl(url)
                }

                override fun onPageStarted(view: WebView, url: String, favicon: Bitmap?) {
                    super.onPageStarted(view, url, favicon)
                    loadingIndicator.visibility = View.VISIBLE
                    errorText.visibility = View.GONE
                }

                override fun onPageFinished(view: WebView, url: String) {
                    super.onPageFinished(view, url)
                    loadingIndicator.visibility = View.GONE
                    swipeRefresh.isRefreshing = false
                }

                override fun onReceivedError(
                    view: WebView,
                    errorCode: Int,
                    description: String,
                    failingUrl: String
                ) {
                    if (failingUrl == view.url) {
                        loadingIndicator.visibility = View.GONE
                        swipeRefresh.isRefreshing = false
                        if (!isNetworkAvailable()) {
                            errorText.text = getString(R.string.error_no_internet)
                            errorText.visibility = View.VISIBLE
                        }
                    }
                }
            })

            setWebChromeClient(chromeClient)

            addJavascriptInterface(
                AndroidInterface(this@MainActivity),
                "Android"
            )
        }
    }

    private fun handleUrl(url: String): Boolean {
        if (Config.isBlockedUrl(url)) {
            runOnUiThread {
                Toast.makeText(
                    this,
                    R.string.dashboard_redirect,
                    Toast.LENGTH_SHORT
                ).show()
            }
            webView.loadUrl(Config.APP_URL)
            return true
        }

        if (url.startsWith("tel:") || url.startsWith("mailto:")) {
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
            return true
        }

        if (url.startsWith("intent://")) {
            return true
        }

        if (url.startsWith("http://") || url.startsWith("https://")) {
            if (!url.startsWith(Config.APP_URL) && !url.startsWith(BuildConfig.DEV_URL)) {
                val externalIntent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                if (externalIntent.resolveActivity(packageManager) != null) {
                    startActivity(externalIntent)
                    return true
                }
            }
            return false
        }

        return false
    }

    private fun setupSwipeRefresh() {
        swipeRefresh.apply {
            setColorSchemeResources(
                R.color.primary
            )
            setOnRefreshListener {
                webView.reload()
            }
        }
    }

    private fun loadAppUrl() {
        errorText.visibility = View.GONE
        webView.loadUrl(Config.APP_URL)
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack()
            return true
        }
        return super.onKeyDown(keyCode, event)
    }

    private fun requestRequiredPermissions() {
        val permissions = mutableListOf<String>()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                != PackageManager.PERMISSION_GRANTED
            ) {
                permissions.add(Manifest.permission.CAMERA)
            }
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_MEDIA_IMAGES)
                != PackageManager.PERMISSION_GRANTED
            ) {
                permissions.add(Manifest.permission.READ_MEDIA_IMAGES)
            }
        } else {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                != PackageManager.PERMISSION_GRANTED
            ) {
                permissions.add(Manifest.permission.CAMERA)
            }
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.READ_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED
            ) {
                permissions.add(Manifest.permission.READ_EXTERNAL_STORAGE)
            }
        }

        if (permissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(
                this,
                permissions.toTypedArray(),
                PERMISSION_REQUEST_CODE
            )
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PERMISSION_REQUEST_CODE) {
            val denied = permissions.filterIndexed { index, _ ->
                grantResults[index] != PackageManager.PERMISSION_GRANTED
            }
            if (denied.isNotEmpty() && denied.contains(Manifest.permission.CAMERA)) {
                showPermissionRationale()
            }
        }
    }

    private fun showPermissionRationale() {
        AlertDialog.Builder(this)
            .setTitle("Camera Permission Needed")
            .setMessage("Camera access is required to upload evidence photos directly from the app.")
            .setPositiveButton("Grant") { _, _ ->
                val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                intent.data = Uri.parse("package:$packageName")
                startActivity(intent)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, intent: Intent?) {
        super.onActivityResult(requestCode, resultCode, intent)
        chromeClient?.handleFileChooserResult(requestCode, resultCode, intent)
    }

    private fun isNetworkAvailable(): Boolean {
        val cm = getSystemService(CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = cm.activeNetwork ?: return false
        val caps = cm.getNetworkCapabilities(network) ?: return false
        return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        webView.saveState(outState)
    }

    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)
        webView.restoreState(savedInstanceState)
    }
}
