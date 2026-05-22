#include <jni.h>
#include "llama.h"

extern "C"
JNIEXPORT jstring JNICALL
Java_com_mohammad_myai_AIEngine_runModel(
        JNIEnv *env,
        jobject thiz,
        jstring prompt) {

    const char *input = env->GetStringUTFChars(prompt, 0);

    // اینجا فعلاً mock می‌زنیم
    std::string output = "AI response: ";
    output += input;

    return env->NewStringUTF(output.c_str());
}
