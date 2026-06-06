package com.bvawc.app

import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Environment
import android.provider.MediaStore
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebView
import androidx.core.content.FileProvider
import java.io.File
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class BVAWCChromeClient(
    private val activity: Activity
) : WebChromeClient() {

    private var fileUploadCallback: ValueCallback<Array<Uri>>? = null
    private var cameraImageUri: Uri? = null

    companion object {
        private const val REQUEST_FILE_CHOOSER = 1001
    }

    override fun onShowFileChooser(
        webView: WebView,
        filePathCallback: ValueCallback<Array<Uri>>,
        fileChooserParams: FileChooserParams
    ): Boolean {
        fileUploadCallback?.onReceiveValue(null)
        fileUploadCallback = filePathCallback

        val acceptTypes = fileChooserParams.acceptTypes ?: arrayOf("*/*")
        val isImageOnly = acceptTypes.any { it.startsWith("image") }
        val isVideoOnly = acceptTypes.any { it.startsWith("video") }

        val cameraIntent = if (hasCamera()) {
            Intent(MediaStore.ACTION_IMAGE_CAPTURE).also { intent ->
                try {
                    val photoFile = createImageFile()
                    if (photoFile != null) {
                        cameraImageUri = FileProvider.getUriForFile(
                            activity,
                            "${activity.packageName}.fileprovider",
                            photoFile
                        )
                        intent.putExtra(MediaStore.EXTRA_OUTPUT, cameraImageUri)
                    }
                } catch (e: IOException) {
                    cameraImageUri = null
                }
            }
        } else null

        val galleryIntent = Intent(Intent.ACTION_GET_CONTENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = if (isImageOnly) "image/*"
            else if (isVideoOnly) "video/*"
            else "*/*"
        }

        val chooserIntent = Intent.createChooser(galleryIntent, "Select file").apply {
            if (cameraIntent != null) {
                putExtra(
                    Intent.EXTRA_INITIAL_INTENTS,
                    arrayOf(cameraIntent)
                )
            }
        }

        activity.startActivityForResult(chooserIntent, REQUEST_FILE_CHOOSER)
        return true
    }

    fun handleFileChooserResult(requestCode: Int, resultCode: Int, intent: Intent?) {
        if (requestCode != REQUEST_FILE_CHOOSER) return

        val results: Array<Uri>? = when {
            resultCode != Activity.RESULT_OK -> null
            cameraImageUri != null && intent == null -> arrayOf(cameraImageUri!!)
            intent?.data != null -> arrayOf(intent.data!!)
            intent?.clipData != null -> {
                val uris = mutableListOf<Uri>()
                for (i in 0 until intent.clipData!!.itemCount) {
                    uris.add(intent.clipData!!.getItemAt(i).uri)
                }
                uris.toTypedArray()
            }
            else -> null
        }

        fileUploadCallback?.onReceiveValue(results)
        fileUploadCallback = null
        cameraImageUri = null
    }

    private fun hasCamera(): Boolean {
        return activity.packageManager.hasSystemFeature(PackageManager.FEATURE_CAMERA_ANY)
    }

    @Throws(IOException::class)
    private fun createImageFile(): File? {
        val dir = activity.getExternalFilesDir(Environment.DIRECTORY_PICTURES)
        return File.createTempFile(
            "BVAWC_${SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())}",
            ".jpg",
            dir
        )
    }
}
