package com.example.spr_swcup.rmi;

import com.example.spr_swcup.dto.history.UserHistoryResponse;
import java.rmi.Remote;
import java.rmi.RemoteException;

/**
 * 远程Excel导出服务接口
 * 定义生成用户历史记录Excel的远程方法
 */
public interface ExcelExportRemoteService extends Remote {
    byte[] generateHistoryExcel(UserHistoryResponse userHistory) throws RemoteException;
}