package com.example.spr_swcup.service;

import com.example.spr_swcup.common.Result;
import com.example.spr_swcup.dto.positionInfo.PositionInfoDTO;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
public interface PositionInfoService {
    Result<PositionInfoDTO> getPositionInfo(String domainName, String positionName);
}
