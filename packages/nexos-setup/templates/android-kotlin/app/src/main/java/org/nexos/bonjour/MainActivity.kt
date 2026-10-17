package org.nexos.bonjour

import android.app.Activity
import android.os.Bundle
import android.view.Gravity
import android.widget.TextView

/** Application minimale : aucune bibliothèque externe, seulement le SDK Android. */
class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(TextView(this).apply {
            text = Salutation.message("NexOS")
            textSize = 28f
            gravity = Gravity.CENTER
        })
    }
}

object Salutation {
    fun message(nom: String): String = "Bonjour depuis $nom !"
}
