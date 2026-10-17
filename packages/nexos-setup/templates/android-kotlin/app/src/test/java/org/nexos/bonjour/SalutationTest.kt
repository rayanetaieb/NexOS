package org.nexos.bonjour

import org.junit.Assert.assertEquals
import org.junit.Test

class SalutationTest {
    @Test
    fun message() = assertEquals("Bonjour depuis NexOS !", Salutation.message("NexOS"))
}
