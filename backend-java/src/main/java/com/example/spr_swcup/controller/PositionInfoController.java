package com.example.spr_swcup.controller;

import com.example.spr_swcup.common.Result;
import com.example.spr_swcup.dto.positionInfo.PositionInfoDTO;
import com.example.spr_swcup.dto.positionInfo.PositionRequest;
import com.example.spr_swcup.service.PositionInfoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
@RestController
@RequestMapping("/api/position")
@CrossOrigin(origins = "${CORS_ORIGINS:http://localhost:5173}")
public class PositionInfoController {

    private final PositionInfoService positionInfoService;

    @Autowired
    public PositionInfoController(PositionInfoService positionInfoService) {
        this.positionInfoService = positionInfoService;
    }

    @PostMapping("/info")
    public Result<PositionInfoDTO> getPositionInfo(
            @RequestBody PositionRequest request
    ) {
        return positionInfoService.getPositionInfo(request.getDomainName(), request.getPositionName());
    }
}
