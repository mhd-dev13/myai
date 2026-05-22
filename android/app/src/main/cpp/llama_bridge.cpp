#include <jni.h>
#include <string>

extern "C"
JNIEXPORT jstring JNICALL
Java_com_mohammad_myai_AIEngine_runModel(
        JNIEnv *env,
        jobject thiz,
        jstring prompt) {

    const char *input = env->GetStringUTFChars(prompt, 0);

    std::string output = "AI Core Active: ";
    output += input;

    return env->NewStringUTF(output.c_str());
}
