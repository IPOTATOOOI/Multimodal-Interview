// ExcelRmiServer.java
package com.example.spr_swcup.rmi;

import com.example.spr_swcup.rmi.ExcelExportRemoteService;
import com.example.spr_swcup.rmi.ExcelExportRemoteServiceImpl;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

/**
 * 远程服务注册类
 * 负责启动RMI注册表并绑定Excel导出服务
 */
public class ExcelRmiServer {
    public static void main(String[] args) {
        try {
            ExcelExportRemoteService service = new ExcelExportRemoteServiceImpl();

            LocateRegistry.createRegistry(1099);

            Registry registry = LocateRegistry.getRegistry();
            registry.rebind("ExcelExportService", service);

            String serverIp = java.net.InetAddress.getLocalHost().getHostAddress();
            System.out.println("Excel导出远程服务启动成功！");
            System.out.println("服务地址：rmi://" + serverIp + ":1099/ExcelExportService");
        } catch (Exception e) {
            System.err.println("远程服务启动失败：" + e.getMessage());
            e.printStackTrace();
        }
    }
}