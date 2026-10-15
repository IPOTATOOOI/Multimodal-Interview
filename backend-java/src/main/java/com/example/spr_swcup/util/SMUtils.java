package com.example.spr_swcup.util;

import cn.hutool.crypto.SmUtil;
import cn.hutool.crypto.asymmetric.KeyType;
import cn.hutool.crypto.asymmetric.SM2;
import cn.hutool.crypto.symmetric.SM4;
/**
 * 国密算法工具类（SM2/SM4）
 */
public class SMUtils {

    private static final SM2 sm2;
    private static final SM4 sm4;

    static {
        sm2 = SmUtil.sm2();
        byte[] sm4Key = cn.hutool.core.util.RandomUtil.randomBytes(16);
        sm4 = SmUtil.sm4(sm4Key);
    }

    /**
     * SM2加密（用于加密SM4密钥）
     */
    public static String sm2Encrypt(String content) {
        return sm2.encryptBase64(content, KeyType.PublicKey);
    }

    /**
     * SM2解密（用于解密SM4密钥）
     */
    public static String sm2Decrypt(String encryptedContent) {
        return sm2.decryptStr(encryptedContent, KeyType.PrivateKey);
    }

    /**
     * SM4加密（用于加密敏感个人信息）
     */
    public static String sm4Encrypt(String content) {
        if (content == null) {
            return null;
        }
        return sm4.encryptHex(content);
    }

    /**
     * SM4解密（用于解密敏感个人信息）
     */
    public static String sm4Decrypt(String encryptedContent) {
        if (encryptedContent == null) {
            return null;
        }
        return sm4.decryptStr(encryptedContent);
    }
}