package com.mohammad.myai;

public class AIEngine {

    static {
        System.loadLibrary("llama");
    }

    public native String runModel(String prompt);
}
